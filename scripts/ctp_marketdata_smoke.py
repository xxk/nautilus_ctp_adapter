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


BASELINE = "marketdata-smoke-v1"


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
    parser = argparse.ArgumentParser(description="Run the formal Nautilus marketdata smoke baseline.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--instrument-timeout-seconds", type=int, default=20)
    parser.add_argument("--md-timeout-seconds", type=int, default=20)
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
            default_file_name="marketdata_smoke.json",
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
        runtime_bridge.drain_events()

        result = data_client.run_marketdata_smoke_baseline(
            load_result,
            timeout_seconds=args.md_timeout_seconds,
            flow_path=args.flow_path,
        )
        bridge_events = runtime_bridge.drain_events()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if not result.instrument_loaded:
        failure_reason = "instrument_not_loaded"
    elif args.symbol not in result.selected_symbols:
        failure_reason = "symbol_not_selected"
    elif not result.bootstrap_state.started:
        failure_reason = "bootstrap_not_started"
    elif not result.md_smoke.login_success:
        failure_reason = "login_failed"
    elif result.md_smoke.subscribe_code != 0:
        failure_reason = "subscribe_failed"
    elif result.md_smoke.first_tick_symbol is None:
        failure_reason = "first_tick_missing"
    elif result.md_smoke.first_tick_symbol != args.symbol:
        failure_reason = "unexpected_tick_symbol"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": None if args.flow_path is None else str(args.flow_path),
        "requested_symbol": args.symbol,
        "instrument_request_id": result.instrument_request_id,
        "instrument_loaded": result.instrument_loaded,
        "source_instrument_count": result.source_instrument_count,
        "selected_symbols": list(result.selected_symbols),
        "bootstrap_started": result.bootstrap_state.started,
        "connect_request_id": result.bootstrap_state.connect_request_id,
        "subscribe_request_ids": list(result.bootstrap_state.subscribe_request_ids),
        "md": {
            "init_code": result.md_smoke.init_code,
            "login_request_code": result.md_smoke.login_request_code,
            "subscribe_code": result.md_smoke.subscribe_code,
            "login_success": result.md_smoke.login_success,
            "login_error_id": result.md_smoke.login_error_id,
            "login_error_message": result.md_smoke.login_error_message,
            "first_tick_symbol": result.md_smoke.first_tick_symbol,
            "first_tick_last": result.md_smoke.first_tick_last,
            "first_tick_bid": result.md_smoke.first_tick_bid,
            "first_tick_ask": result.md_smoke.first_tick_ask,
            "first_tick_ts_epoch_us": result.md_smoke.first_tick_ts_epoch_us,
        },
        "marketdata_batch_event_kinds": [event.kind.value for event in result.event_batch.events],
        "marketdata_batch_should_restore": result.event_batch.should_restore,
        "bridge_event_kinds": [event.kind.value for event in bridge_events],
        "bridge_tick_symbol": next((event.venue_symbol for event in bridge_events if event.venue_symbol), None),
        "export": build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
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
