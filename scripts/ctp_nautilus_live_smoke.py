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


BASELINE = "nautilus-live-smoke-v1"


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
    parser = argparse.ArgumentParser(description="Run the formal Nautilus-facing live smoke baseline.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--md-timeout-seconds", type=int, default=20)
    parser.add_argument("--td-timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        data_client = stack["data_client"]
        execution_client = stack["execution_client"]
        runtime_bridge = stack["runtime_bridge"]

        bootstrap = data_client.bootstrap_market_data_mainline()
        md_result = data_client.run_live_md_smoke(timeout_seconds=args.md_timeout_seconds)
        td_result = execution_client.run_live_td_readiness_smoke(timeout_seconds=args.td_timeout_seconds)
        events = runtime_bridge.drain_events()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if not bootstrap.started:
        failure_reason = "md_bootstrap_not_started"
    elif md_result.login_success is not True:
        failure_reason = "md_login_failed"
    elif md_result.first_tick_symbol not in config.instruments:
        failure_reason = "md_first_tick_missing"
    elif td_result.login_success is not True:
        failure_reason = "td_login_failed"
    elif td_result.settlement_code != 0:
        failure_reason = "td_settlement_not_confirmed"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
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
    _emit_payload(payload)

    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
