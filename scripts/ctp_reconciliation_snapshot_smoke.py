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
    resolve_session_label,
    write_json_payload,
)


BASELINE = "reconciliation-snapshot-v1"


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
    parser = argparse.ArgumentParser(description="Run the reconciliation snapshot smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    try:
        session_label = resolve_session_label(session_label=args.session_label, flow_path=None)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="reconciliation_snapshot.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        adapter = stack["reconciliation_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        snapshot = adapter.capture_snapshot_mainline(
            timeout_seconds=args.timeout_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        summary = adapter.summarize_snapshot(snapshot)
        policy_result = adapter.evaluate_summary(summary)
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if snapshot.query_snapshot.positions.query_code != 0:
        failure_reason = "positions_query_failed"
    elif snapshot.query_snapshot.positions.timed_out:
        failure_reason = "positions_timed_out"
    elif not snapshot.query_snapshot.positions.completed:
        failure_reason = "positions_incomplete"
    elif snapshot.query_snapshot.account.query_code != 0:
        failure_reason = "account_query_failed"
    elif snapshot.query_snapshot.account.timed_out:
        failure_reason = "account_timed_out"
    elif not snapshot.query_snapshot.account.completed:
        failure_reason = "account_incomplete"
    elif summary.account_id is None:
        failure_reason = "account_id_missing"
    elif summary.account_balance is None:
        failure_reason = "account_balance_missing"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "session_label": session_label,
        "positions": {
            "request_id": snapshot.query_snapshot.positions.request_id,
            "query_code": snapshot.query_snapshot.positions.query_code,
            "completed": snapshot.query_snapshot.positions.completed,
            "timed_out": snapshot.query_snapshot.positions.timed_out,
            "no_positions": snapshot.query_snapshot.positions.no_positions,
            "position_count": snapshot.query_snapshot.positions.position_count,
        },
        "account": {
            "request_id": snapshot.query_snapshot.account.request_id,
            "query_code": snapshot.query_snapshot.account.query_code,
            "completed": snapshot.query_snapshot.account.completed,
            "timed_out": snapshot.query_snapshot.account.timed_out,
            "account_id": None if snapshot.query_snapshot.account.account is None else snapshot.query_snapshot.account.account.account_id,
        },
        "position_request_id": summary.position_request_id,
        "account_request_id": summary.account_request_id,
        "account_id": summary.account_id,
        "position_line_count": summary.position_line_count,
        "symbol_count": summary.symbol_count,
        "total_long_qty": summary.total_long_qty,
        "total_short_qty": summary.total_short_qty,
        "gross_position_qty": summary.gross_position_qty,
        "total_position_cost": summary.total_position_cost,
        "account_balance": summary.account_balance,
        "account_available": summary.account_available,
        "account_margin": summary.account_margin,
        "available_ratio": summary.available_ratio,
        "margin_ratio": summary.margin_ratio,
        "dominant_exposure_symbol": summary.dominant_exposure_symbol,
        "dominant_exposure_exchange": summary.dominant_exposure_exchange,
        "dominant_exposure_abs_net_qty": summary.dominant_exposure_abs_net_qty,
        "disposition": policy_result.disposition,
        "requires_manual_review": policy_result.requires_manual_review,
        "finding_count": len(policy_result.findings),
        "manual_review_codes": [
            finding.code for finding in policy_result.findings if finding.action == "manual_review_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in policy_result.findings if finding.action == "evidence_only"
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
            for finding in policy_result.findings
        ],
        "top_exposures": [
            {
                "venue_symbol": exposure.venue_symbol,
                "exchange_id": exposure.exchange_id,
                "long_qty": exposure.long_qty,
                "short_qty": exposure.short_qty,
                "gross_qty": exposure.gross_qty,
                "net_qty": exposure.net_qty,
                "abs_net_qty": exposure.abs_net_qty,
                "position_cost": exposure.position_cost,
            }
            for exposure in summary.exposures[:10]
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
