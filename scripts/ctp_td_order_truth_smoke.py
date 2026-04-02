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
    parser = argparse.ArgumentParser(description="Run the TD order truth baseline live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    runtime_bridge = stack["runtime_bridge"]

    result = execution_client.capture_td_order_truth_baseline_mainline(
        timeout_seconds=args.timeout_seconds,
        flow_path=args.flow_path,
        observation_grace_seconds=args.observation_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "td-order-truth-v1",
        "flow_path": result.flow_path,
        "flow_mode": result.flow_mode,
        "ready": result.ready,
        "login_success": result.login_success,
        "settlement_code": result.settlement_code,
        "disconnect_count": result.disconnect_count,
        "disconnect_reasons": list(result.disconnect_reasons),
        "observed_callback_count": result.observed_callback_count,
        "observed_order_event_count": result.observed_order_event_count,
        "observed_trade_event_count": result.observed_trade_event_count,
        "no_callbacks_observed": result.no_callbacks_observed,
        "first_order_id": result.first_order_id,
        "first_order_ref": result.first_order_ref,
        "first_session_id": result.first_session_id,
        "first_front_id": result.first_front_id,
        "first_is_trade": result.first_is_trade,
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    return 0 if result.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
