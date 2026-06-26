from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
)
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    LIVE_DATA_CLIENT_BOOTSTRAP_BASELINE,
    build_live_data_client_bootstrap_payload,
)


BASELINE = LIVE_DATA_CLIENT_BOOTSTRAP_BASELINE


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
    parser = argparse.ArgumentParser(description="Bootstrap the Nautilus CTP live data client from a live instrument query.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--instrument-timeout-seconds", type=int, default=20)
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
            default_file_name="live_data_client_bootstrap.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        provider = stack["instrument_provider"]
        data_client = stack["data_client"]
        runtime_bridge = stack["runtime_bridge"]

        load_result = provider.run_live_instrument_smoke(
            symbol=args.symbol,
            timeout_seconds=args.instrument_timeout_seconds,
            flow_path=args.flow_path,
        )

        runtime_bridge.drain_submitted_commands()
        instrument_events = runtime_bridge.drain_events()

        bootstrap_result = data_client.bootstrap_live_data_client_mainline(load_result)
        bootstrap_commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    payload = build_live_data_client_bootstrap_payload(
        load_result=load_result,
        bootstrap_result=bootstrap_result,
        requested_symbol=args.symbol,
        flow_path=None if args.flow_path is None else str(args.flow_path),
        flow_mode=flow_mode,
        session_label=session_label,
        export=build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
        bootstrap_commands=bootstrap_commands,
        instrument_events=instrument_events,
    )

    if export_path is not None:
        try:
            write_json_payload(path=export_path, payload=payload)
        except Exception as exc:
            return _emit_exception(stage="export_payload", exc=exc)

    _emit_payload(payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
