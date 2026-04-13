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


BASELINE = "md-truth-evidence-matrix-v1"


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
    parser = argparse.ArgumentParser(description="Run the MD truth evidence matrix live smoke.")
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
            default_file_name="md_truth_evidence_matrix.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        data_client = stack["data_client"]
        runtime_bridge = stack["runtime_bridge"]

        evidence = data_client.capture_md_truth_evidence_matrix_mainline(
            timeout_seconds=args.timeout_seconds,
            flow_path=args.flow_path,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if evidence.account_id is None:
        failure_reason = "account_id_missing"
    elif evidence.symbol is None:
        failure_reason = "symbol_missing"
    elif not evidence.restore_succeeded:
        failure_reason = "restore_not_succeeded"
    elif evidence.disposition not in {
        "clear",
        "manual_review_required",
        "restore_required",
        "evidence_only",
    }:
        failure_reason = "unexpected_disposition"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "evidence_version": evidence.evidence_version,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "symbol": evidence.symbol,
        "disposition": evidence.disposition,
        "startup_ready": evidence.startup_ready,
        "restore_triggered": evidence.restore_triggered,
        "restore_succeeded": evidence.restore_succeeded,
        "startup_flow_path": evidence.startup_flow_path,
        "restored_flow_path": evidence.restored_flow_path,
        "startup_first_tick_ts_epoch_us": evidence.startup_first_tick_ts_epoch_us,
        "restored_first_tick_ts_epoch_us": evidence.restored_first_tick_ts_epoch_us,
        "manual_review_codes": list(evidence.manual_review_codes),
        "restore_required_codes": list(evidence.restore_required_codes),
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
