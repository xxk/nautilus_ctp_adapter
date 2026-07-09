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
from nautilus_ctp_adapter.runtime import CtpRuntimeEvent, CtpRuntimeEventKind


def _serialize_exec_event(event: CtpRuntimeEvent) -> dict[str, object]:
    return {
        "kind": event.kind.value,
        "client_order_id": event.client_order_id,
        "venue_symbol": event.venue_symbol,
        "message": event.message,
        "native_order_id": event.payload.get("native_order_id", event.payload.get("order_id")),
        "native_order_ref": event.payload.get("native_order_ref", event.payload.get("order_ref")),
        "status": event.payload.get("status"),
        "trade_volume": event.payload.get("trade_volume"),
        "leaves_qty": event.payload.get("leaves_qty"),
        "match_reason": event.payload.get("match_reason"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the execution order-lifecycle smoke baseline.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--instrument", default="c2609")
    parser.add_argument("--side", default="BUY")
    parser.add_argument("--quantity", type=int, default=1)
    parser.add_argument("--limit-price", type=float, required=True)
    parser.add_argument("--client-order-id", default="order-smoke-1")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--time-in-force", default="GFD")
    parser.add_argument("--live-send", action="store_true")
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    runtime_bridge = stack["runtime_bridge"]

    try:
        result = execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id=args.instrument,
            side=args.side,
            quantity=args.quantity,
            limit_price=args.limit_price,
            client_order_id=args.client_order_id,
            timeout_seconds=args.timeout_seconds,
            dry_run=not args.live_send,
            time_in_force=args.time_in_force,
        )
    except RuntimeError as exc:
        commands = runtime_bridge.drain_submitted_commands()
        events = runtime_bridge.drain_events()
        payload = {
            "baseline": "nautilus-order-lifecycle-smoke-v1",
            "dry_run": not args.live_send,
            "live_send_requested": args.live_send,
            "td_session_identity": None
            if execution_client.td_session_identity is None
            else {
                "front_id": execution_client.td_session_identity.front_id,
                "session_id": execution_client.td_session_identity.session_id,
                "max_order_ref": execution_client.td_session_identity.max_order_ref,
            },
            "error": str(exc),
            "command_kinds": [command.kind.value for command in commands],
            "event_kinds": [event.kind.value for event in events],
            "exec_events": [
                _serialize_exec_event(event)
                for event in events
                if event.kind in {CtpRuntimeEventKind.ORDER, CtpRuntimeEventKind.TRADE}
            ],
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1
    commands = runtime_bridge.drain_submitted_commands()
    events = runtime_bridge.drain_events()

    payload = {
        "baseline": "nautilus-order-lifecycle-smoke-v1",
        "dry_run": result.dry_run,
        "live_send_requested": args.live_send,
        "live_send_armed": result.live_send_armed,
        "bootstrap_ready": result.bootstrap.ready,
        "connect_request_id": result.bootstrap.execution_bootstrap.bootstrap_state.connect_request_id,
        "td_session_identity": None
        if result.bootstrap.td_session_identity is None
        else {
            "front_id": result.bootstrap.td_session_identity.front_id,
            "session_id": result.bootstrap.td_session_identity.session_id,
            "max_order_ref": result.bootstrap.td_session_identity.max_order_ref,
        },
        "mapped_submit_error": None
        if result.mapped_submit.error is None
        else {
            "error_id": result.mapped_submit.error.error_id,
            "error_message": result.mapped_submit.error.error_message,
        },
        "mapped_submit_order_ref": result.mapped_submit.order_ref,
        "matched_exec_count": 0 if not result.matched_execs else len(result.matched_execs),
        "matched_execs": []
        if not result.matched_execs
        else [
            {
                "python_client_order_id": matched.python_client_order_id,
                "native_order_id": matched.native_order_id,
                "native_order_ref": matched.native_order_ref,
                "venue_symbol": matched.venue_symbol,
                "front_id": matched.front_id,
                "session_id": matched.session_id,
                "status": matched.status,
                "is_trade": matched.is_trade,
                "trade_volume": matched.trade_volume,
                "leaves_qty": matched.leaves_qty,
                "match_reason": matched.match_reason,
            }
            for matched in result.matched_execs
        ],
        "command_kinds": [command.kind.value for command in commands],
        "submit_payload": None if result.mapped_submit.command is None else result.mapped_submit.command.payload,
        "event_kinds": [event.kind.value for event in events],
        "exec_events": [
            _serialize_exec_event(event)
            for event in events
            if event.kind in {CtpRuntimeEventKind.ORDER, CtpRuntimeEventKind.TRADE}
        ],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = (
        result.bootstrap.ready
        and result.mapped_submit.error is None
        and result.mapped_submit.command is not None
    )
    if result.dry_run:
        success = success and result.live_send_armed is False
    else:
        success = success and result.live_send_armed and payload["matched_exec_count"] > 0
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
