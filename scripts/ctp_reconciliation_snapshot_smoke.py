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


BASELINE = "reconciliation-snapshot-v1"


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
    parser = argparse.ArgumentParser(description="Run the reconciliation snapshot smoke.")
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
        adapter = stack["reconciliation_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        summary = adapter.capture_summary_mainline(
            timeout_seconds=args.timeout_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if summary.account_id is None:
        failure_reason = "account_id_missing"
    elif summary.account_balance is None:
        failure_reason = "account_balance_missing"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "position_request_id": summary.position_request_id,
        "account_request_id": summary.account_request_id,
        "account_id": summary.account_id,
        "position_line_count": summary.position_line_count,
        "symbol_count": summary.symbol_count,
        "total_long_qty": summary.total_long_qty,
        "total_short_qty": summary.total_short_qty,
        "gross_position_qty": summary.gross_position_qty,
        "total_position_cost": summary.total_position_cost,
        "account_balance": summary.account_balance,
        "account_available": summary.account_available,
        "account_margin": summary.account_margin,
        "available_ratio": summary.available_ratio,
        "margin_ratio": summary.margin_ratio,
        "dominant_exposure_symbol": summary.dominant_exposure_symbol,
        "dominant_exposure_exchange": summary.dominant_exposure_exchange,
        "dominant_exposure_abs_net_qty": summary.dominant_exposure_abs_net_qty,
        "top_exposures": [
            {
                "venue_symbol": exposure.venue_symbol,
                "exchange_id": exposure.exchange_id,
                "long_qty": exposure.long_qty,
                "short_qty": exposure.short_qty,
                "gross_qty": exposure.gross_qty,
                "net_qty": exposure.net_qty,
                "abs_net_qty": exposure.abs_net_qty,
                "position_cost": exposure.position_cost,
            }
            for exposure in summary.exposures[:10]
        ],
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    _emit_payload(payload)
    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
