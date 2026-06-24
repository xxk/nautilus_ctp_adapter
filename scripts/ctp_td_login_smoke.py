from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
)
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    TD_LOGIN_SMOKE_BASELINE,
    build_td_login_smoke_payload,
)
from nautilus_ctp_adapter.native import CtpTdApi


BASELINE = TD_LOGIN_SMOKE_BASELINE


def _emit_payload(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def _emit_exception(*, stage: str, exc: Exception) -> int:
    _emit_payload(
        {
            "baseline": BASELINE,
            "success": False,
            "failure_reason": "exception",
            "error_stage": stage,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repository-owned Python TD auth/login readiness smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    try:
        flow_mode = resolve_flow_mode(flow_path=args.flow_path)
        session_label = resolve_session_label(session_label=args.session_label, flow_path=args.flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="td_login_smoke.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        api = CtpTdApi.load(REPO_ROOT)
        flow_path = args.flow_path or (REPO_ROOT / "var" / "td_flow_smoke")
        flow_path.mkdir(parents=True, exist_ok=True)
        handle = api.create(flow_path)
    except Exception as exc:
        return _emit_exception(stage="bootstrap", exc=exc)

    state: dict[str, object] = {"login": None, "disconnects": []}

    try:
        api.set_login_callback(handle, lambda resp: state.__setitem__("login", resp))
        api.set_front_disconnected_callback(
            handle,
            lambda reason: state["disconnects"].append(reason),
        )

        init_code = api.init(handle, config.td_front)
        authenticate_code = api.authenticate(handle, config.app_id, config.auth_code, config.product_info)
        login_code = api.login(handle, config.broker_id, config.user_id, config.password)

        deadline = time.time() + args.timeout_seconds
        while time.time() < deadline:
            if state["login"] is not None:
                break
            time.sleep(0.1)

        login = state["login"]
        settlement_code = -1
        if login is not None and login.success:
            settlement_code = api.confirm_settlement(handle)

        payload = build_td_login_smoke_payload(
            login=login,
            settlement_code=settlement_code,
            init_code=init_code,
            authenticate_code=authenticate_code,
            login_code=login_code,
            flow_path=str(flow_path),
            flow_mode=flow_mode,
            session_label=session_label,
            disconnects=state["disconnects"],
            export=build_export_metadata(
                export_path=export_path,
                evidence_root=args.evidence_root,
                session_label=session_label,
                explicit_path=args.output_json is not None,
            ),
        )
        if export_path is not None:
            try:
                write_json_payload(path=export_path, payload=payload)
            except Exception as exc:
                return _emit_exception(stage="export_payload", exc=exc)
        _emit_payload(payload)
        return 0 if payload["success"] else 1
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)
    finally:
        api.dispose(handle)


if __name__ == "__main__":
    raise SystemExit(main())
