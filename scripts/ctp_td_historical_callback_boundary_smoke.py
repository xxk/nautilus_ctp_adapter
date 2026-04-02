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
    parser = argparse.ArgumentParser(description="Run the TD historical callback boundary live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    runtime_bridge = stack["runtime_bridge"]

    result = execution_client.capture_historical_callback_boundary_policy_mainline(
        timeout_seconds=args.timeout_seconds,
        flow_path=args.flow_path,
        observation_grace_seconds=args.observation_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "td-historical-callback-boundary-v1",
        "disposition": result.disposition,
        "observed_callback_count": result.baseline.observed_callback_count,
        "historical_callback_count": result.historical_callback_count,
        "delayed_callback_count": result.delayed_callback_count,
        "current_session_callback_count": result.current_session_callback_count,
        "first_historical_order_id": result.first_historical_order_id,
        "first_current_session_order_id": result.first_current_session_order_id,
        "login_front_id": result.baseline.login_front_id,
        "login_session_id": result.baseline.login_session_id,
        "login_max_order_ref": result.baseline.login_max_order_ref,
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

    return 0 if result.baseline.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
