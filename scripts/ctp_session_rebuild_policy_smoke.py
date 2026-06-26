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


BASELINE = "td-session-rebuild-policy-v1"


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
    parser = argparse.ArgumentParser(description="Run the TD session rebuild policy live smoke.")
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
            default_file_name="session_rebuild_policy.json",
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

        result = adapter.capture_session_rebuild_policy_mainline(
            timeout_seconds=args.timeout_seconds,
            shared_flow_path=args.shared_flow_path,
            isolated_flow_path=args.isolated_flow_path,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if not result.shared_truth.ready:
        failure_reason = "shared_bootstrap_not_ready"
    elif not result.isolated_truth.ready:
        failure_reason = "isolated_bootstrap_not_ready"
    elif len(result.findings) == 0:
        failure_reason = "findings_missing"
    elif result.disposition not in {
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
        "disposition": result.disposition,
        "shared_flow_reuse_allowed": result.shared_flow_reuse_allowed,
        "session_rotated": result.session_rotated,
        "max_order_ref_reset": result.max_order_ref_reset,
        "shared_truth": {
            "flow_path": result.shared_truth.flow_path,
            "flow_mode": result.shared_truth.flow_mode,
            "ready": result.shared_truth.ready,
            "login_success": result.shared_truth.login_success,
            "settlement_code": result.shared_truth.settlement_code,
            "front_id": result.shared_truth.front_id,
            "session_id": result.shared_truth.session_id,
            "max_order_ref": result.shared_truth.max_order_ref,
            "disconnect_count": result.shared_truth.disconnect_count,
        },
        "isolated_truth": {
            "flow_path": result.isolated_truth.flow_path,
            "flow_mode": result.isolated_truth.flow_mode,
            "ready": result.isolated_truth.ready,
            "login_success": result.isolated_truth.login_success,
            "settlement_code": result.isolated_truth.settlement_code,
            "front_id": result.isolated_truth.front_id,
            "session_id": result.isolated_truth.session_id,
            "max_order_ref": result.isolated_truth.max_order_ref,
            "disconnect_count": result.isolated_truth.disconnect_count,
        },
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
