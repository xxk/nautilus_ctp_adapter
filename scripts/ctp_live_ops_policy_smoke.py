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
    parser = argparse.ArgumentParser(description="Run the live ops policy baseline smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    parser.add_argument("--td-shared-flow-path", type=Path, default=None)
    parser.add_argument("--td-isolated-flow-path", type=Path, default=None)
    parser.add_argument("--md-flow-path", type=Path, default=None)
    parser.add_argument("--td-flow-path", type=Path, default=None)
    parser.add_argument("--query-flow-path", type=Path, default=None)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    adapter = stack["live_ops_snapshot_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    result = adapter.capture_live_ops_policy_mainline(
        timeout_seconds=args.timeout_seconds,
        td_shared_flow_path=args.td_shared_flow_path,
        td_isolated_flow_path=args.td_isolated_flow_path,
        md_flow_path=args.md_flow_path,
        td_flow_path=args.td_flow_path,
        query_flow_path=args.query_flow_path,
        observation_grace_seconds=args.observation_grace_seconds,
        completion_grace_seconds=args.completion_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "live-ops-policy-v1",
        "account_id": result.summary.account_id,
        "symbol": result.summary.symbol,
        "disposition": result.disposition,
        "startup_disposition": result.summary.startup_disposition,
        "md_disposition": result.summary.md_disposition,
        "td_disposition": result.summary.td_disposition,
        "reconciliation_disposition": result.summary.reconciliation_disposition,
        "manual_review_codes": list(result.summary.manual_review_codes),
        "rebuild_required_codes": list(result.summary.rebuild_required_codes),
        "restore_required_codes": list(result.summary.restore_required_codes),
        "boundary_codes": list(result.summary.boundary_codes),
        "evidence_only_codes": list(result.summary.evidence_only_codes),
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

    return 0 if result.summary.account_id is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())

