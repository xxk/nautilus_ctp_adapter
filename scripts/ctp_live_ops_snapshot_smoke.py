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


BASELINE = "live-ops-snapshot-v1"


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
    parser = argparse.ArgumentParser(description="Run the live ops snapshot baseline smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--td-shared-flow-path", type=Path, default=None)
    parser.add_argument("--td-isolated-flow-path", type=Path, default=None)
    parser.add_argument("--md-flow-path", type=Path, default=None)
    parser.add_argument("--td-flow-path", type=Path, default=None)
    parser.add_argument("--query-flow-path", type=Path, default=None)
    args = parser.parse_args()

    effective_flow_path = (
        args.td_isolated_flow_path
        or args.md_flow_path
        or args.td_flow_path
        or args.query_flow_path
        or args.td_shared_flow_path
    )
    try:
        flow_mode = resolve_flow_mode(flow_path=effective_flow_path)
        session_label = resolve_session_label(session_label=args.session_label, flow_path=effective_flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="live_ops_snapshot.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        adapter = stack["live_ops_snapshot_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        snapshot = adapter.capture_live_ops_snapshot_mainline(
            timeout_seconds=args.timeout_seconds,
            td_shared_flow_path=args.td_shared_flow_path,
            td_isolated_flow_path=args.td_isolated_flow_path,
            md_flow_path=args.md_flow_path,
            td_flow_path=args.td_flow_path,
            query_flow_path=args.query_flow_path,
            observation_grace_seconds=args.observation_grace_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        summary = adapter.summarize_live_ops_snapshot(snapshot)
        policy_result = adapter.evaluate_live_ops_policy(summary)
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if summary.account_id is None:
        failure_reason = "account_id_missing"
    elif summary.symbol is None:
        failure_reason = "symbol_missing"
    elif policy_result.disposition not in {
        "clear",
        "manual_review_required",
        "rebuild_required",
        "restore_required",
        "boundary_required",
        "evidence_only",
    }:
        failure_reason = "unexpected_disposition"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": summary.account_id,
        "symbol": summary.symbol,
        "startup": {
            "account_id": snapshot.startup_truth.account_id,
            "disposition": snapshot.startup_truth.disposition,
            "shared_flow_reuse_allowed": snapshot.startup_truth.shared_flow_reuse_allowed,
            "session_rotated": snapshot.startup_truth.session_rotated,
            "manual_review_codes": list(snapshot.startup_truth.manual_review_codes),
            "rebuild_required_codes": list(snapshot.startup_truth.rebuild_required_codes),
            "evidence_only_codes": list(snapshot.startup_truth.evidence_only_codes),
        },
        "md": {
            "account_id": snapshot.md_truth.account_id,
            "symbol": snapshot.md_truth.symbol,
            "disposition": snapshot.md_truth.disposition,
            "startup_ready": snapshot.md_truth.startup_ready,
            "restore_triggered": snapshot.md_truth.restore_triggered,
            "restore_succeeded": snapshot.md_truth.restore_succeeded,
            "manual_review_codes": list(snapshot.md_truth.manual_review_codes),
            "restore_required_codes": list(snapshot.md_truth.restore_required_codes),
            "evidence_only_codes": list(snapshot.md_truth.evidence_only_codes),
        },
        "td": {
            "account_id": snapshot.td_truth.account_id,
            "disposition": snapshot.td_truth.disposition,
            "position_count": snapshot.td_truth.position_count,
            "observed_callback_count": snapshot.td_truth.observed_callback_count,
            "historical_callback_count": snapshot.td_truth.historical_callback_count,
            "current_session_callback_count": snapshot.td_truth.current_session_callback_count,
            "available_ratio": snapshot.td_truth.available_ratio,
            "margin_ratio": snapshot.td_truth.margin_ratio,
            "manual_review_codes": list(snapshot.td_truth.manual_review_codes),
            "boundary_codes": list(snapshot.td_truth.boundary_codes),
            "evidence_only_codes": list(snapshot.td_truth.evidence_only_codes),
        },
        "reconciliation": {
            "account_id": snapshot.reconciliation.account_id,
            "disposition": snapshot.reconciliation.disposition,
            "requires_manual_review": snapshot.reconciliation.requires_manual_review,
            "finding_count": snapshot.reconciliation.finding_count,
            "position_line_count": snapshot.reconciliation.position_line_count,
            "symbol_count": snapshot.reconciliation.symbol_count,
            "gross_position_qty": snapshot.reconciliation.gross_position_qty,
            "available_ratio": snapshot.reconciliation.available_ratio,
            "margin_ratio": snapshot.reconciliation.margin_ratio,
            "manual_review_codes": list(snapshot.reconciliation.manual_review_codes),
            "evidence_only_codes": list(snapshot.reconciliation.evidence_only_codes),
        },
        "startup_disposition": summary.startup_disposition,
        "md_disposition": summary.md_disposition,
        "td_disposition": summary.td_disposition,
        "reconciliation_disposition": summary.reconciliation_disposition,
        "disposition": policy_result.disposition,
        "requires_manual_review": policy_result.disposition == "manual_review_required",
        "finding_count": len(policy_result.findings),
        "startup_shared_flow_reuse_allowed": summary.startup_shared_flow_reuse_allowed,
        "startup_session_rotated": summary.startup_session_rotated,
        "md_restore_succeeded": summary.md_restore_succeeded,
        "position_count": summary.position_count,
        "observed_callback_count": summary.observed_callback_count,
        "historical_callback_count": summary.historical_callback_count,
        "current_session_callback_count": summary.current_session_callback_count,
        "available_ratio": summary.available_ratio,
        "margin_ratio": summary.margin_ratio,
        "manual_review_codes": list(summary.manual_review_codes),
        "rebuild_required_codes": list(summary.rebuild_required_codes),
        "restore_required_codes": list(summary.restore_required_codes),
        "boundary_codes": list(summary.boundary_codes),
        "evidence_only_codes": list(summary.evidence_only_codes),
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
            for finding in policy_result.findings
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
