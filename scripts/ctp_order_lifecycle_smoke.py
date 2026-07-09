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
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    ORDER_LIFECYCLE_SMOKE_BASELINE,
    build_order_lifecycle_exception_payload,
    build_order_lifecycle_payload,
    classify_order_lifecycle_success,
)


BASELINE = ORDER_LIFECYCLE_SMOKE_BASELINE


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
        payload = build_order_lifecycle_exception_payload(
            dry_run=not args.live_send,
            live_send_requested=args.live_send,
            td_session_identity=execution_client.td_session_identity,
            error=str(exc),
            commands=commands,
            events=events,
        )
        print(json.dumps(payload, ensure_ascii=False))
        return 1
    commands = runtime_bridge.drain_submitted_commands()
    events = runtime_bridge.drain_events()

    payload = build_order_lifecycle_payload(
        result=result,
        live_send_requested=args.live_send,
        commands=commands,
        events=events,
    )
    print(json.dumps(payload, ensure_ascii=False))

    success = classify_order_lifecycle_success(
        result,
        matched_exec_count=int(payload["matched_exec_count"]),
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
