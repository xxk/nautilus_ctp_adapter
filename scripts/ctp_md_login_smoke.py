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
from nautilus_ctp_adapter.adapters.ctp.data_client import CtpDataClient


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repository-owned Python MD login smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    client = CtpDataClient(config)
    result = client.run_live_md_smoke(timeout_seconds=args.timeout_seconds)
    events = client.runtime_bridge.drain_events()
    print(
        json.dumps(
            {
                "init_code": result.init_code,
                "login_request_code": result.login_request_code,
                "subscribe_code": result.subscribe_code,
                "login_success": result.login_success,
                "login_error_id": result.login_error_id,
                "login_error_message": result.login_error_message,
                "first_tick_symbol": result.first_tick_symbol,
                "first_tick_last": result.first_tick_last,
                "first_tick_bid": result.first_tick_bid,
                "first_tick_ask": result.first_tick_ask,
                "first_tick_ts_epoch_us": result.first_tick_ts_epoch_us,
            },
            ensure_ascii=False,
        )
    )
    print(
        json.dumps(
            {
                "bridge_event_kinds": [event.kind for event in events],
                "bridge_tick_symbol": next(
                    (event.venue_symbol for event in events if event.kind == "tick"),
                    None,
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result.login_success and result.first_tick_symbol else 1


if __name__ == "__main__":
    raise SystemExit(main())
