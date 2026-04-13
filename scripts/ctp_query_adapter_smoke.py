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
from nautilus_ctp_adapter.adapters.ctp.reconciliation import CtpReconciliationSnapshot
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
)


BASELINE = "nautilus-query-adapter-v1"


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


def _instrument_matches_requested_symbol(*, requested_symbol: str, venue_symbol: str, display_symbol: str) -> bool:
    requested = requested_symbol.strip().lower()
    if not requested:
        return False
    candidates = {
        venue_symbol.strip().lower(),
        display_symbol.strip().lower(),
        display_symbol.split(".", 1)[0].strip().lower(),
    }
    return requested in candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Nautilus-facing query adapter baseline smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--flow-path", type=Path)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--instrument-symbol")
    parser.add_argument("--include-reconciliation", action="store_true")
    parser.add_argument("--include-order-truth", action="store_true")
    parser.add_argument("--include-order-trade-snapshot", action="store_true")
    parser.add_argument("--include-merged-policy", action="store_true")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=20)
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
            default_file_name="aggregated_query.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        query_adapter = stack["query_adapter"]
        instrument_provider = stack["instrument_provider"]
        execution_client = stack["execution_client"]
        reconciliation_adapter = stack["reconciliation_adapter"] if args.include_reconciliation else None
        truth_merge_adapter = stack["truth_merge_adapter"] if args.include_merged_policy else None
        runtime_bridge = stack["runtime_bridge"]

        snapshot = query_adapter.query_snapshot_mainline(
            timeout_seconds=args.timeout_seconds,
            flow_path=args.flow_path,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        instrument_result = None
        order_truth_result = None
        order_trade_snapshot_result = None
        reconciliation_summary = None
        reconciliation_policy = None
        reconciliation_evidence = None
        merged_policy_result = None
        if args.instrument_symbol:
            instrument_result = instrument_provider.run_live_instrument_smoke(
                symbol=args.instrument_symbol,
                timeout_seconds=args.timeout_seconds,
                flow_path=args.flow_path,
            )
        if reconciliation_adapter is not None:
            reconciliation_snapshot = CtpReconciliationSnapshot(query_snapshot=snapshot)
            reconciliation_summary = reconciliation_adapter.summarize_snapshot(reconciliation_snapshot)
            reconciliation_policy = reconciliation_adapter.evaluate_summary(reconciliation_summary)
            reconciliation_evidence = reconciliation_adapter.build_evidence(reconciliation_policy)
        if args.include_order_truth:
            order_truth_result = execution_client.capture_historical_callback_boundary_policy_mainline(
                timeout_seconds=args.timeout_seconds,
                flow_path=args.flow_path,
                observation_grace_seconds=args.observation_grace_seconds,
            )
        if args.include_order_trade_snapshot:
            order_trade_snapshot_result = execution_client.capture_td_order_trade_snapshot_mainline(
                timeout_seconds=args.timeout_seconds,
                flow_path=args.flow_path,
                observation_grace_seconds=args.observation_grace_seconds,
            )
        if truth_merge_adapter is not None:
            merged_policy_result = truth_merge_adapter.capture_merged_reconciliation_policy_mainline(
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
    if snapshot.positions.query_code != 0:
        failure_reason = "positions_query_failed"
    elif snapshot.positions.timed_out:
        failure_reason = "positions_timed_out"
    elif not snapshot.positions.completed:
        failure_reason = "positions_incomplete"
    elif snapshot.account.query_code != 0:
        failure_reason = "account_query_failed"
    elif snapshot.account.timed_out:
        failure_reason = "account_timed_out"
    elif not snapshot.account.completed:
        failure_reason = "account_incomplete"
    elif snapshot.account.account is None:
        failure_reason = "account_missing"

    matched_symbols: list[str] = []
    exact_symbol_found = False
    if instrument_result is not None:
        matched_symbols = [
            item.display_symbol
            for item in instrument_result.instruments
            if _instrument_matches_requested_symbol(
                requested_symbol=args.instrument_symbol or "",
                venue_symbol=item.venue_symbol,
                display_symbol=item.display_symbol,
            )
        ]
        exact_symbol_found = len(matched_symbols) > 0
        if failure_reason is None:
            if not instrument_result.loaded:
                failure_reason = "instrument_query_incomplete"
            elif instrument_result.instrument_count == 0:
                failure_reason = "instrument_missing"
            elif not exact_symbol_found:
                failure_reason = "instrument_symbol_mismatch"

    if failure_reason is None and order_truth_result is not None:
        if order_truth_result.disposition == "manual_review_required":
            failure_reason = "order_truth_manual_review_required"

    if failure_reason is None and order_trade_snapshot_result is not None:
        if order_trade_snapshot_result.disposition == "manual_review_required":
            failure_reason = "order_trade_snapshot_manual_review_required"

    if failure_reason is None and reconciliation_policy is not None:
        if reconciliation_policy.disposition == "manual_review_required":
            failure_reason = "reconciliation_manual_review_required"

    if failure_reason is None and merged_policy_result is not None:
        if merged_policy_result.disposition == "manual_review_required":
            failure_reason = "merged_policy_manual_review_required"

    manual_review_codes: list[str] = []
    boundary_codes: list[str] = []
    evidence_only_codes: list[str] = []
    if order_truth_result is not None:
        manual_review_codes = [
            finding.code for finding in order_truth_result.findings if finding.action == "manual_review_required"
        ]
        boundary_codes = [
            finding.code for finding in order_truth_result.findings if finding.action == "boundary_required"
        ]
        evidence_only_codes = [
            finding.code for finding in order_truth_result.findings if finding.action == "evidence_only"
        ]

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": None if args.flow_path is None else str(args.flow_path),
        "flow_mode": flow_mode,
        "session_label": session_label,
        "positions": {
            "request_id": snapshot.positions.request_id,
            "query_code": snapshot.positions.query_code,
            "completed": snapshot.positions.completed,
            "timed_out": snapshot.positions.timed_out,
            "no_positions": snapshot.positions.no_positions,
            "position_count": snapshot.positions.position_count,
        },
        "account": {
            "request_id": snapshot.account.request_id,
            "query_code": snapshot.account.query_code,
            "completed": snapshot.account.completed,
            "timed_out": snapshot.account.timed_out,
            "account_id": None if snapshot.account.account is None else snapshot.account.account.account_id,
            "balance": None if snapshot.account.account is None else snapshot.account.account.balance,
            "available": None if snapshot.account.account is None else snapshot.account.account.available,
        },
        "instrument": None
        if instrument_result is None
        else {
            "requested_symbol": args.instrument_symbol,
            "request_id": instrument_result.request_id,
            "loaded": instrument_result.loaded,
            "instrument_count": instrument_result.instrument_count,
            "symbols": [item.display_symbol for item in instrument_result.instruments],
            "matched_symbols": matched_symbols,
            "exact_symbol_found": exact_symbol_found,
            "first_instrument": None
            if not instrument_result.instruments
            else {
                "display_symbol": instrument_result.instruments[0].display_symbol,
                "underlying": instrument_result.instruments[0].underlying,
                "contract_month": instrument_result.instruments[0].contract_month,
                "product_kind": instrument_result.instruments[0].product_kind.value,
                "price_tick": instrument_result.instruments[0].price_tick,
                "volume_multiple": instrument_result.instruments[0].volume_multiple,
            },
        },
        "order_truth": None
        if order_truth_result is None
        else {
            "account_id": getattr(config, "user_id", None) or None,
            "ready": order_truth_result.baseline.ready,
            "login_success": order_truth_result.baseline.login_success,
            "settlement_code": order_truth_result.baseline.settlement_code,
            "disposition": order_truth_result.disposition,
            "observed_callback_count": order_truth_result.baseline.observed_callback_count,
            "observed_order_event_count": order_truth_result.baseline.observed_order_event_count,
            "observed_trade_event_count": order_truth_result.baseline.observed_trade_event_count,
            "no_callbacks_observed": order_truth_result.baseline.no_callbacks_observed,
            "historical_callback_count": order_truth_result.historical_callback_count,
            "delayed_callback_count": order_truth_result.delayed_callback_count,
            "current_session_callback_count": order_truth_result.current_session_callback_count,
            "first_order_id": order_truth_result.baseline.first_order_id,
            "first_order_ref": order_truth_result.baseline.first_order_ref,
            "first_is_trade": order_truth_result.baseline.first_is_trade,
            "first_historical_order_id": order_truth_result.first_historical_order_id,
            "first_current_session_order_id": order_truth_result.first_current_session_order_id,
            "manual_review_codes": manual_review_codes,
            "boundary_codes": boundary_codes,
            "evidence_only_codes": evidence_only_codes,
        },
        "order_trade_snapshot": None
        if order_trade_snapshot_result is None
        else {
            "account_id": getattr(config, "user_id", None) or None,
            "flow_path": order_trade_snapshot_result.baseline.flow_path,
            "flow_mode": order_trade_snapshot_result.baseline.flow_mode,
            "ready": order_trade_snapshot_result.baseline.ready,
            "login_success": order_trade_snapshot_result.baseline.login_success,
            "settlement_code": order_trade_snapshot_result.baseline.settlement_code,
            "disposition": order_trade_snapshot_result.disposition,
            "observed_callback_count": order_trade_snapshot_result.baseline.observed_callback_count,
            "observed_order_event_count": order_trade_snapshot_result.observed_order_event_count,
            "observed_trade_event_count": order_trade_snapshot_result.observed_trade_event_count,
            "no_order_events": order_trade_snapshot_result.no_order_events,
            "no_trade_events": order_trade_snapshot_result.no_trade_events,
            "historical_order_count": order_trade_snapshot_result.historical_order_count,
            "historical_trade_count": order_trade_snapshot_result.historical_trade_count,
            "delayed_order_count": order_trade_snapshot_result.delayed_order_count,
            "delayed_trade_count": order_trade_snapshot_result.delayed_trade_count,
            "historical_residue_order_count": order_trade_snapshot_result.historical_residue_order_count,
            "historical_residue_trade_count": order_trade_snapshot_result.historical_residue_trade_count,
            "current_session_order_count": order_trade_snapshot_result.current_session_order_count,
            "current_session_trade_count": order_trade_snapshot_result.current_session_trade_count,
            "first_order_event_id": order_trade_snapshot_result.first_order_event_id,
            "first_trade_event_id": order_trade_snapshot_result.first_trade_event_id,
            "first_historical_order_id": order_trade_snapshot_result.first_historical_order_id,
            "first_historical_trade_id": order_trade_snapshot_result.first_historical_trade_id,
            "first_current_session_order_id": order_trade_snapshot_result.first_current_session_order_id,
            "first_current_session_trade_id": order_trade_snapshot_result.first_current_session_trade_id,
            "manual_review_codes": [
                finding.code
                for finding in order_trade_snapshot_result.findings
                if finding.action == "manual_review_required"
            ],
            "boundary_codes": [
                finding.code
                for finding in order_trade_snapshot_result.findings
                if finding.action == "boundary_required"
            ],
            "evidence_only_codes": [
                finding.code
                for finding in order_trade_snapshot_result.findings
                if finding.action == "evidence_only"
            ],
        },
        "reconciliation": None
        if reconciliation_summary is None or reconciliation_policy is None or reconciliation_evidence is None
        else {
            "account_id": reconciliation_summary.account_id,
            "position_request_id": reconciliation_summary.position_request_id,
            "account_request_id": reconciliation_summary.account_request_id,
            "position_line_count": reconciliation_summary.position_line_count,
            "symbol_count": reconciliation_summary.symbol_count,
            "total_long_qty": reconciliation_summary.total_long_qty,
            "total_short_qty": reconciliation_summary.total_short_qty,
            "gross_position_qty": reconciliation_summary.gross_position_qty,
            "total_position_cost": reconciliation_summary.total_position_cost,
            "account_balance": reconciliation_summary.account_balance,
            "account_available": reconciliation_summary.account_available,
            "account_margin": reconciliation_summary.account_margin,
            "available_ratio": reconciliation_summary.available_ratio,
            "margin_ratio": reconciliation_summary.margin_ratio,
            "dominant_exposure_symbol": reconciliation_summary.dominant_exposure_symbol,
            "dominant_exposure_exchange": reconciliation_summary.dominant_exposure_exchange,
            "dominant_exposure_abs_net_qty": reconciliation_summary.dominant_exposure_abs_net_qty,
            "disposition": reconciliation_policy.disposition,
            "requires_manual_review": reconciliation_policy.requires_manual_review,
            "finding_count": len(reconciliation_policy.findings),
            "manual_review_codes": list(reconciliation_evidence.manual_review_codes),
            "evidence_only_codes": list(reconciliation_evidence.evidence_only_codes),
            "captured_at_utc": reconciliation_evidence.captured_at_utc,
            "evidence_version": reconciliation_evidence.evidence_version,
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
                for finding in reconciliation_policy.findings
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
                for exposure in reconciliation_evidence.top_exposures
            ],
        },
        "merged_policy": None
        if merged_policy_result is None
        else {
            "account_id": merged_policy_result.snapshot.order_truth.account_id,
            "order_truth": {
                "account_id": merged_policy_result.snapshot.order_truth.account_id,
                "disposition": merged_policy_result.snapshot.order_truth.disposition,
                "observed_callback_count": merged_policy_result.snapshot.order_truth.observed_callback_count,
                "historical_callback_count": merged_policy_result.snapshot.order_truth.historical_callback_count,
                "delayed_callback_count": merged_policy_result.snapshot.order_truth.delayed_callback_count,
                "current_session_callback_count": merged_policy_result.snapshot.order_truth.current_session_callback_count,
                "first_historical_order_id": merged_policy_result.snapshot.order_truth.first_historical_order_id,
                "first_current_session_order_id": merged_policy_result.snapshot.order_truth.first_current_session_order_id,
                "manual_review_codes": list(merged_policy_result.snapshot.order_truth.manual_review_codes),
                "boundary_codes": list(merged_policy_result.snapshot.order_truth.boundary_codes),
                "evidence_only_codes": list(merged_policy_result.snapshot.order_truth.evidence_only_codes),
            },
            "positions": {
                "request_id": merged_policy_result.snapshot.positions.request_id,
                "query_code": merged_policy_result.snapshot.positions.query_code,
                "completed": merged_policy_result.snapshot.positions.completed,
                "timed_out": merged_policy_result.snapshot.positions.timed_out,
                "no_positions": merged_policy_result.snapshot.positions.no_positions,
                "position_count": merged_policy_result.snapshot.positions.position_count,
            },
            "account": {
                "request_id": merged_policy_result.snapshot.account.request_id,
                "query_code": merged_policy_result.snapshot.account.query_code,
                "completed": merged_policy_result.snapshot.account.completed,
                "timed_out": merged_policy_result.snapshot.account.timed_out,
                "account_present": merged_policy_result.snapshot.account.account is not None,
                "account_id": None
                if merged_policy_result.snapshot.account.account is None
                else merged_policy_result.snapshot.account.account.account_id,
                "balance": None
                if merged_policy_result.snapshot.account.account is None
                else merged_policy_result.snapshot.account.account.balance,
                "available": None
                if merged_policy_result.snapshot.account.account is None
                else merged_policy_result.snapshot.account.account.available,
                "margin": None
                if merged_policy_result.snapshot.account.account is None
                else merged_policy_result.snapshot.account.account.margin,
            },
            "disposition": merged_policy_result.disposition,
            "position_count": merged_policy_result.snapshot.positions.position_count,
            "observed_callback_count": merged_policy_result.snapshot.order_truth.observed_callback_count,
            "historical_callback_count": merged_policy_result.snapshot.order_truth.historical_callback_count,
            "current_session_callback_count": merged_policy_result.snapshot.order_truth.current_session_callback_count,
            "available_ratio": merged_policy_result.available_ratio,
            "margin_ratio": merged_policy_result.margin_ratio,
            "manual_review_codes": [
                finding.code for finding in merged_policy_result.findings if finding.action == "manual_review_required"
            ],
            "boundary_codes": [
                finding.code for finding in merged_policy_result.findings if finding.action == "boundary_required"
            ],
            "evidence_only_codes": [
                finding.code for finding in merged_policy_result.findings if finding.action == "evidence_only"
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
                for finding in merged_policy_result.findings
            ],
        },
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
