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
    parser = argparse.ArgumentParser(description="Run the reconciliation mismatch policy smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    adapter = stack["reconciliation_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    result = adapter.capture_policy_result_mainline(
        timeout_seconds=args.timeout_seconds,
        completion_grace_seconds=args.completion_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "reconciliation-policy-v1",
        "disposition": result.disposition,
        "requires_manual_review": result.requires_manual_review,
        "account_id": result.summary.account_id,
        "position_line_count": result.summary.position_line_count,
        "gross_position_qty": result.summary.gross_position_qty,
        "available_ratio": result.summary.available_ratio,
        "margin_ratio": result.summary.margin_ratio,
        "dominant_exposure_symbol": result.summary.dominant_exposure_symbol,
        "dominant_exposure_abs_net_qty": result.summary.dominant_exposure_abs_net_qty,
        "findings": [
            {
                "code": finding.code,
                "severity": finding.severity,
                "action": finding.action,
                "metric": finding.metric,
                "metric_value": finding.metric_value,
                "threshold": finding.threshold,
                "message": finding.message,
            }
            for finding in result.findings
        ],
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = result.summary.account_id is not None and len(result.findings) > 0
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
