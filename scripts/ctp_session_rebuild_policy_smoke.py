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
    parser = argparse.ArgumentParser(description="Run the TD session rebuild policy live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--shared-flow-path", type=Path, default=None)
    parser.add_argument("--isolated-flow-path", type=Path, default=None)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    adapter = stack["startup_truth_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    result = adapter.capture_session_rebuild_policy_mainline(
        timeout_seconds=args.timeout_seconds,
        shared_flow_path=args.shared_flow_path,
        isolated_flow_path=args.isolated_flow_path,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "td-session-rebuild-policy-v1",
        "disposition": result.disposition,
        "shared_flow_reuse_allowed": result.shared_flow_reuse_allowed,
        "session_rotated": result.session_rotated,
        "max_order_ref_reset": result.max_order_ref_reset,
        "shared_truth": {
            "flow_path": result.shared_truth.flow_path,
            "flow_mode": result.shared_truth.flow_mode,
            "ready": result.shared_truth.ready,
            "login_success": result.shared_truth.login_success,
            "settlement_code": result.shared_truth.settlement_code,
            "front_id": result.shared_truth.front_id,
            "session_id": result.shared_truth.session_id,
            "max_order_ref": result.shared_truth.max_order_ref,
            "disconnect_count": result.shared_truth.disconnect_count,
        },
        "isolated_truth": {
            "flow_path": result.isolated_truth.flow_path,
            "flow_mode": result.isolated_truth.flow_mode,
            "ready": result.isolated_truth.ready,
            "login_success": result.isolated_truth.login_success,
            "settlement_code": result.isolated_truth.settlement_code,
            "front_id": result.isolated_truth.front_id,
            "session_id": result.isolated_truth.session_id,
            "max_order_ref": result.isolated_truth.max_order_ref,
            "disconnect_count": result.isolated_truth.disconnect_count,
        },
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

    success = result.shared_truth.ready and result.isolated_truth.ready and len(result.findings) > 0
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
