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


BASELINE = "nautilus-query-adapter-v1"


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
    parser = argparse.ArgumentParser(description="Run the Nautilus-facing query adapter baseline smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        query_adapter = stack["query_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        snapshot = query_adapter.query_snapshot_mainline(
            timeout_seconds=args.timeout_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if snapshot.positions.query_code != 0:
        failure_reason = "positions_query_failed"
    elif snapshot.positions.timed_out:
        failure_reason = "positions_timed_out"
    elif not snapshot.positions.completed:
        failure_reason = "positions_incomplete"
    elif snapshot.account.query_code != 0:
        failure_reason = "account_query_failed"
    elif snapshot.account.timed_out:
        failure_reason = "account_timed_out"
    elif not snapshot.account.completed:
        failure_reason = "account_incomplete"
    elif snapshot.account.account is None:
        failure_reason = "account_missing"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
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
    _emit_payload(payload)
    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
