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
    parser = argparse.ArgumentParser(description="Run the real-account read-only account query smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    runtime_bridge = stack["runtime_bridge"]

    result = execution_client.run_live_account_query_smoke(timeout_seconds=args.timeout_seconds)
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "account-query-smoke-v1",
        "query_request_id": result.query_request_id,
        "query_code": result.query_code,
        "completed": result.completed,
        "timed_out": result.timed_out,
        "account": None
        if result.account is None
        else {
            "account_id": result.account.account_id,
            "balance": result.account.balance,
            "available": result.account.available,
            "margin": result.account.margin,
            "commission": result.account.commission,
            "close_profit": result.account.close_profit,
            "position_profit": result.account.position_profit,
        },
        "bootstrap_ready": result.bootstrap.ready,
        "td_login_success": result.bootstrap.execution_bootstrap.td_smoke.login_success,
        "td_settlement_code": result.bootstrap.execution_bootstrap.td_smoke.settlement_code,
        "disconnects": result.disconnects,
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = (
        result.bootstrap.ready
        and result.query_code == 0
        and result.completed
        and not result.timed_out
        and result.account is not None
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
