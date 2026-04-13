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


BASELINE = "td-merged-reconciliation-policy-v1"


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
    parser = argparse.ArgumentParser(description="Run the TD merged reconciliation policy live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    try:
        flow_mode = resolve_flow_mode(flow_path=args.flow_path)
        session_label = resolve_session_label(session_label=args.session_label, flow_path=args.flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="td_merged_reconciliation_policy.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        adapter = stack["truth_merge_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        result = adapter.capture_merged_reconciliation_policy_mainline(
            timeout_seconds=args.timeout_seconds,
            flow_path=args.flow_path,
            observation_grace_seconds=args.observation_grace_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if result.snapshot.positions.query_code != 0:
        failure_reason = "positions_query_failed"
    elif result.snapshot.positions.timed_out:
        failure_reason = "positions_timed_out"
    elif not result.snapshot.positions.completed:
        failure_reason = "positions_incomplete"
    elif result.snapshot.account.query_code != 0:
        failure_reason = "account_query_failed"
    elif result.snapshot.account.timed_out:
        failure_reason = "account_timed_out"
    elif not result.snapshot.account.completed:
        failure_reason = "account_incomplete"
    elif result.snapshot.account.account is None:
        failure_reason = "account_missing"
    elif result.disposition not in {"clear", "manual_review_required", "boundary_required", "evidence_only"}:
        failure_reason = "unexpected_disposition"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": None if args.flow_path is None else str(args.flow_path),
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": result.snapshot.order_truth.account_id,
        "order_truth": {
            "account_id": result.snapshot.order_truth.account_id,
            "disposition": result.snapshot.order_truth.disposition,
            "observed_callback_count": result.snapshot.order_truth.observed_callback_count,
            "historical_callback_count": result.snapshot.order_truth.historical_callback_count,
            "delayed_callback_count": result.snapshot.order_truth.delayed_callback_count,
            "current_session_callback_count": result.snapshot.order_truth.current_session_callback_count,
            "first_historical_order_id": result.snapshot.order_truth.first_historical_order_id,
            "first_current_session_order_id": result.snapshot.order_truth.first_current_session_order_id,
            "manual_review_codes": list(result.snapshot.order_truth.manual_review_codes),
            "boundary_codes": list(result.snapshot.order_truth.boundary_codes),
            "evidence_only_codes": list(result.snapshot.order_truth.evidence_only_codes),
        },
        "positions": {
            "request_id": result.snapshot.positions.request_id,
            "query_code": result.snapshot.positions.query_code,
            "completed": result.snapshot.positions.completed,
            "timed_out": result.snapshot.positions.timed_out,
            "no_positions": result.snapshot.positions.no_positions,
            "position_count": result.snapshot.positions.position_count,
        },
        "account": {
            "request_id": result.snapshot.account.request_id,
            "query_code": result.snapshot.account.query_code,
            "completed": result.snapshot.account.completed,
            "timed_out": result.snapshot.account.timed_out,
            "account_present": result.snapshot.account.account is not None,
            "account_id": None if result.snapshot.account.account is None else result.snapshot.account.account.account_id,
            "balance": None if result.snapshot.account.account is None else result.snapshot.account.account.balance,
            "available": None if result.snapshot.account.account is None else result.snapshot.account.account.available,
            "margin": None if result.snapshot.account.account is None else result.snapshot.account.account.margin,
        },
        "disposition": result.disposition,
        "position_count": result.snapshot.positions.position_count,
        "observed_callback_count": result.snapshot.order_truth.observed_callback_count,
        "historical_callback_count": result.snapshot.order_truth.historical_callback_count,
        "current_session_callback_count": result.snapshot.order_truth.current_session_callback_count,
        "available_ratio": result.available_ratio,
        "margin_ratio": result.margin_ratio,
        "manual_review_codes": [
            finding.code for finding in result.findings if finding.action == "manual_review_required"
        ],
        "boundary_codes": [
            finding.code for finding in result.findings if finding.action == "boundary_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in result.findings if finding.action == "evidence_only"
        ],
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
