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


BASELINE = "td-startup-truth-evidence-matrix-v1"


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
    parser = argparse.ArgumentParser(description="Run the startup truth evidence matrix live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--shared-flow-path", type=Path, default=None)
    parser.add_argument("--isolated-flow-path", type=Path, default=None)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    effective_flow_path = args.isolated_flow_path or args.shared_flow_path
    try:
        flow_mode = resolve_flow_mode(flow_path=effective_flow_path)
        session_label = resolve_session_label(session_label=args.session_label, flow_path=effective_flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="startup_truth_evidence_matrix.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        adapter = stack["startup_truth_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        evidence = adapter.capture_evidence_matrix_mainline(
            timeout_seconds=args.timeout_seconds,
            shared_flow_path=args.shared_flow_path,
            isolated_flow_path=args.isolated_flow_path,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if evidence.account_id is None:
        failure_reason = "account_id_missing"
    elif evidence.disposition not in {
        "clear",
        "manual_review_required",
        "rebuild_required",
        "evidence_only",
    }:
        failure_reason = "unexpected_disposition"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "evidence_version": evidence.evidence_version,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "disposition": evidence.disposition,
        "shared_flow_reuse_allowed": evidence.shared_flow_reuse_allowed,
        "session_rotated": evidence.session_rotated,
        "max_order_ref_reset": evidence.max_order_ref_reset,
        "shared_flow_path": evidence.shared_flow_path,
        "isolated_flow_path": evidence.isolated_flow_path,
        "shared_session_id": evidence.shared_session_id,
        "isolated_session_id": evidence.isolated_session_id,
        "shared_max_order_ref": evidence.shared_max_order_ref,
        "isolated_max_order_ref": evidence.isolated_max_order_ref,
        "shared_disconnect_count": evidence.shared_disconnect_count,
        "isolated_disconnect_count": evidence.isolated_disconnect_count,
        "manual_review_codes": list(evidence.manual_review_codes),
        "rebuild_required_codes": list(evidence.rebuild_required_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "export": build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }

    if export_path is not None:
        try:
            write_json_payload(path=export_path, payload=payload)
        except Exception as exc:
            return _emit_exception(stage="export_payload", exc=exc)

    _emit_payload(payload)

    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
