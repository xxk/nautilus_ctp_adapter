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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the formal Nautilus marketdata smoke baseline.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--instrument-timeout-seconds", type=int, default=20)
    parser.add_argument("--md-timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    data_client = stack["data_client"]
    runtime_bridge = stack["runtime_bridge"]

    load_result = provider.run_live_instrument_smoke(
        symbol=args.symbol,
        timeout_seconds=args.instrument_timeout_seconds,
    )
    runtime_bridge.drain_submitted_commands()
    runtime_bridge.drain_events()

    result = data_client.run_marketdata_smoke_baseline(
        load_result,
        timeout_seconds=args.md_timeout_seconds,
    )
    bridge_events = runtime_bridge.drain_events()

    payload = {
        "baseline": "nautilus-marketdata-smoke-v1",
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
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = (
        result.instrument_loaded
        and args.symbol in result.selected_symbols
        and result.md_smoke.login_success
        and result.md_smoke.first_tick_symbol == args.symbol
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
