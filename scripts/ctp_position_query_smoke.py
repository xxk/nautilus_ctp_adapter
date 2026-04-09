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


BASELINE = "position-query-smoke-v1"


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
    parser = argparse.ArgumentParser(description="Run the real-account read-only position query smoke.")
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
        execution_client = stack["execution_client"]
        runtime_bridge = stack["runtime_bridge"]

        result = execution_client.run_live_position_query_smoke(
            timeout_seconds=args.timeout_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if not result.bootstrap.ready:
        failure_reason = "bootstrap_not_ready"
    elif result.query_code != 0:
        failure_reason = "position_query_failed"
    elif result.timed_out:
        failure_reason = "position_query_timed_out"
    elif not result.completed:
        failure_reason = "position_snapshot_incomplete"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "query_request_id": result.query_request_id,
        "query_code": result.query_code,
        "completed": result.completed,
        "timed_out": result.timed_out,
        "no_positions": result.no_positions,
        "position_count": result.position_count,
        "positions": [
            {
                "venue_symbol": position.venue_symbol,
                "exchange_id": position.exchange_id,
                "direction": position.direction,
                "position_qty": position.position_qty,
                "yd_position_qty": position.yd_position_qty,
                "td_position_qty": position.td_position_qty,
                "position_cost": position.position_cost,
            }
            for position in result.positions
        ],
        "bootstrap_ready": result.bootstrap.ready,
        "td_login_success": result.bootstrap.execution_bootstrap.td_smoke.login_success,
        "td_settlement_code": result.bootstrap.execution_bootstrap.td_smoke.settlement_code,
        "disconnects": result.disconnects,
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    _emit_payload(payload)
    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
