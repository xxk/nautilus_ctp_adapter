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
    NAUTILUS_LIVE_SMOKE_BASELINE,
    build_nautilus_live_smoke_payload,
)


BASELINE = NAUTILUS_LIVE_SMOKE_BASELINE


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

    payload = build_nautilus_live_smoke_payload(
        bootstrap=bootstrap,
        md_result=md_result,
        td_result=td_result,
        configured_instruments=config.instruments,
        bridge_events=events,
    )
    _emit_payload(payload)

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
