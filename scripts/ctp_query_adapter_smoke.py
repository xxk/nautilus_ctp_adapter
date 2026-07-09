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
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    QUERY_ADAPTER_BASELINE,
    build_query_adapter_payload,
)
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
)


BASELINE = QUERY_ADAPTER_BASELINE


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

    payload = build_query_adapter_payload(
        snapshot=snapshot,
        flow_path=None if args.flow_path is None else str(args.flow_path),
        flow_mode=flow_mode,
        session_label=session_label,
        instrument_result=instrument_result,
        requested_instrument_symbol=args.instrument_symbol,
        account_id=getattr(config, "user_id", None) or None,
        order_truth_result=order_truth_result,
        order_trade_snapshot_result=order_trade_snapshot_result,
        reconciliation_summary=reconciliation_summary,
        reconciliation_policy=reconciliation_policy,
        reconciliation_evidence=reconciliation_evidence,
        merged_policy_result=merged_policy_result,
        export=build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
        bridge_commands=commands,
        bridge_events=events,
    )

    if export_path is not None:
        try:
            write_json_payload(path=export_path, payload=payload)
        except Exception as exc:
            return _emit_exception(stage="export_payload", exc=exc)

    _emit_payload(payload)
    return 0 if payload["failure_reason"] is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
