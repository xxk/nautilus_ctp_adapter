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
    parser = argparse.ArgumentParser(description="Run the Nautilus-facing query adapter baseline smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    query_adapter = stack["query_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    snapshot = query_adapter.query_snapshot_mainline(
        timeout_seconds=args.timeout_seconds,
        completion_grace_seconds=args.completion_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "nautilus-query-adapter-v1",
        "positions": {
            "request_id": snapshot.positions.request_id,
            "query_code": snapshot.positions.query_code,
            "completed": snapshot.positions.completed,
            "timed_out": snapshot.positions.timed_out,
            "no_positions": snapshot.positions.no_positions,
            "position_count": snapshot.positions.position_count,
        },
        "account": {
            "request_id": snapshot.account.request_id,
            "query_code": snapshot.account.query_code,
            "completed": snapshot.account.completed,
            "timed_out": snapshot.account.timed_out,
            "account_id": None if snapshot.account.account is None else snapshot.account.account.account_id,
            "balance": None if snapshot.account.account is None else snapshot.account.account.balance,
            "available": None if snapshot.account.account is None else snapshot.account.account.available,
        },
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = (
        snapshot.positions.query_code == 0
        and snapshot.positions.completed
        and not snapshot.positions.timed_out
        and snapshot.account.query_code == 0
        and snapshot.account.completed
        and not snapshot.account.timed_out
        and snapshot.account.account is not None
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
