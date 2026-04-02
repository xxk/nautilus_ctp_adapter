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
    parser = argparse.ArgumentParser(description="Bootstrap the Nautilus CTP live data client from a live instrument query.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--instrument-timeout-seconds", type=int, default=20)
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
    instrument_events = runtime_bridge.drain_events()

    bootstrap_result = data_client.bootstrap_live_data_client_mainline(load_result)
    bootstrap_commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "instrument_request_id": load_result.request_id,
        "instrument_loaded": load_result.loaded,
        "instrument_count": load_result.instrument_count,
        "instrument_symbols": [instrument.display_symbol for instrument in load_result.instruments[:5]],
        "selected_symbols": list(bootstrap_result.selected_symbols),
        "bootstrap_started": bootstrap_result.bootstrap_state.started,
        "connect_request_id": bootstrap_result.bootstrap_state.connect_request_id,
        "subscribe_request_ids": list(bootstrap_result.bootstrap_state.subscribe_request_ids),
        "bootstrap_command_kinds": [command.kind.value for command in bootstrap_commands],
        "bootstrap_subscribe_symbols": [
            command.venue_symbol
            for command in bootstrap_commands
            if command.venue_symbol
        ],
        "instrument_event_kinds_tail": [event.kind.value for event in instrument_events[-5:]],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = (
        load_result.loaded
        and load_result.instrument_count > 0
        and bootstrap_result.bootstrap_state.started
        and args.symbol in bootstrap_result.selected_symbols
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
