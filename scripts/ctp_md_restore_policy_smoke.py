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


BASELINE = "md-restore-policy-v1"


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
    parser = argparse.ArgumentParser(description="Run the MD restore policy live smoke.")
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
            default_file_name="md_restore_policy.json",
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

        result = data_client.capture_md_restore_policy_mainline(
            timeout_seconds=args.timeout_seconds,
            flow_path=args.flow_path,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if not result.startup_truth.ready:
        failure_reason = "startup_not_ready"
    elif not result.restore_result.triggered:
        failure_reason = "restore_not_triggered"
    elif not result.restore_succeeded:
        failure_reason = "restore_not_succeeded"
    elif result.restored_truth.first_tick_symbol is None:
        failure_reason = "restored_tick_missing"
    elif result.disposition not in {
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
        "flow_mode": flow_mode,
        "session_label": session_label,
        "disposition": result.disposition,
        "restore_triggered": result.restore_result.triggered,
        "restore_succeeded": result.restore_succeeded,
        "startup_truth": {
            "flow_path": result.startup_truth.flow_path,
            "flow_mode": result.startup_truth.flow_mode,
            "selected_symbols": list(result.startup_truth.selected_symbols),
            "ready": result.startup_truth.ready,
            "first_tick_symbol": result.startup_truth.first_tick_symbol,
            "first_tick_ts_epoch_us": result.startup_truth.first_tick_ts_epoch_us,
        },
        "restored_truth": {
            "flow_path": result.restored_truth.flow_path,
            "flow_mode": result.restored_truth.flow_mode,
            "selected_symbols": list(result.restored_truth.selected_symbols),
            "ready": result.restored_truth.ready,
            "first_tick_symbol": result.restored_truth.first_tick_symbol,
            "first_tick_ts_epoch_us": result.restored_truth.first_tick_ts_epoch_us,
        },
        "restored_symbols": list(result.restore_result.restored_symbols),
        "findings": [
            {
                "code": finding.code,
                "severity": finding.severity,
                "action": finding.action,
                "metric": finding.metric,
                "metric_value": finding.metric_value,
                "threshold": finding.threshold,
                "message": finding.message,
            }
            for finding in result.findings
        ],
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
