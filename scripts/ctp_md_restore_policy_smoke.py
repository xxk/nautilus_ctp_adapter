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
    parser = argparse.ArgumentParser(description="Run the MD restore policy live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    runtime_bridge = stack["runtime_bridge"]

    result = data_client.capture_md_restore_policy_mainline(
        timeout_seconds=args.timeout_seconds,
        flow_path=args.flow_path,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "md-restore-policy-v1",
        "disposition": result.disposition,
        "restore_triggered": result.restore_result.triggered,
        "restore_succeeded": result.restore_succeeded,
        "startup_truth": {
            "flow_path": result.startup_truth.flow_path,
            "flow_mode": result.startup_truth.flow_mode,
            "selected_symbols": list(result.startup_truth.selected_symbols),
            "ready": result.startup_truth.ready,
            "first_tick_symbol": result.startup_truth.first_tick_symbol,
            "first_tick_ts_epoch_us": result.startup_truth.first_tick_ts_epoch_us,
        },
        "restored_truth": {
            "flow_path": result.restored_truth.flow_path,
            "flow_mode": result.restored_truth.flow_mode,
            "selected_symbols": list(result.restored_truth.selected_symbols),
            "ready": result.restored_truth.ready,
            "first_tick_symbol": result.restored_truth.first_tick_symbol,
            "first_tick_ts_epoch_us": result.restored_truth.first_tick_ts_epoch_us,
        },
        "restored_symbols": list(result.restore_result.restored_symbols),
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

    return 0 if result.restore_succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
