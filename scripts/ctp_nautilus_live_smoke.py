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
    parser = argparse.ArgumentParser(description="Run the formal Nautilus-facing live smoke baseline.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--md-timeout-seconds", type=int, default=20)
    parser.add_argument("--td-timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    execution_client = stack["execution_client"]
    runtime_bridge = stack["runtime_bridge"]

    bootstrap = data_client.bootstrap_market_data_mainline()
    md_result = data_client.run_live_md_smoke(timeout_seconds=args.md_timeout_seconds)
    td_result = execution_client.run_live_td_readiness_smoke(timeout_seconds=args.td_timeout_seconds)
    events = runtime_bridge.drain_events()

    payload = {
        "baseline": "nautilus-live-smoke-v1",
        "bootstrap_started": bootstrap.started,
        "connect_request_id": bootstrap.connect_request_id,
        "subscribe_request_ids": list(bootstrap.subscribe_request_ids),
        "md": {
            "init_code": md_result.init_code,
            "login_request_code": md_result.login_request_code,
            "subscribe_code": md_result.subscribe_code,
            "login_success": md_result.login_success,
            "login_error_id": md_result.login_error_id,
            "first_tick_symbol": md_result.first_tick_symbol,
            "first_tick_last": md_result.first_tick_last,
            "first_tick_bid": md_result.first_tick_bid,
            "first_tick_ask": md_result.first_tick_ask,
            "first_tick_ts_epoch_us": md_result.first_tick_ts_epoch_us,
        },
        "td": {
            "init_code": td_result.init_code,
            "authenticate_code": td_result.authenticate_code,
            "login_code": td_result.login_code,
            "settlement_code": td_result.settlement_code,
            "login_success": td_result.login_success,
            "login_error_id": td_result.login_error_id,
            "front_id": td_result.front_id,
            "session_id": td_result.session_id,
            "max_order_ref": td_result.max_order_ref,
            "disconnects": td_result.disconnects,
        },
        "bridge_event_kinds": [event.kind.value for event in events],
        "bridge_tick_symbol": next((event.venue_symbol for event in events if event.venue_symbol), None),
        "bridge_td_login_seen": any(
            event.kind.value == "login_succeeded" and event.payload.get("channel") == "td"
            for event in events
        ),
        "bridge_settlement_seen": any(event.kind.value == "settlement_confirmed" for event in events),
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = (
        md_result.login_success
        and md_result.first_tick_symbol in config.instruments
        and td_result.login_success
        and td_result.settlement_code == 0
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
