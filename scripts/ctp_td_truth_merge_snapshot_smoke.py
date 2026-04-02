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
    parser = argparse.ArgumentParser(description="Run the TD truth merge snapshot live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    adapter = stack["truth_merge_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    snapshot = adapter.capture_truth_merge_snapshot_mainline(
        timeout_seconds=args.timeout_seconds,
        flow_path=args.flow_path,
        observation_grace_seconds=args.observation_grace_seconds,
        completion_grace_seconds=args.completion_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "td-truth-merge-snapshot-v1",
        "account_id": snapshot.order_truth.account_id,
        "order_truth_disposition": snapshot.order_truth.disposition,
        "observed_callback_count": snapshot.order_truth.observed_callback_count,
        "historical_callback_count": snapshot.order_truth.historical_callback_count,
        "position_count": snapshot.positions.position_count,
        "positions_completed": snapshot.positions.completed,
        "account_query_code": snapshot.account.query_code,
        "account_present": snapshot.account.account is not None,
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = snapshot.order_truth.account_id is not None and snapshot.account.account is not None
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
