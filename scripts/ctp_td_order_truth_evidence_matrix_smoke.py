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
    parser = argparse.ArgumentParser(description="Run the TD order truth evidence matrix live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    runtime_bridge = stack["runtime_bridge"]

    evidence = execution_client.capture_td_order_truth_evidence_matrix_mainline(
        timeout_seconds=args.timeout_seconds,
        flow_path=args.flow_path,
        observation_grace_seconds=args.observation_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "evidence_version": evidence.evidence_version,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "disposition": evidence.disposition,
        "observed_callback_count": evidence.observed_callback_count,
        "historical_callback_count": evidence.historical_callback_count,
        "delayed_callback_count": evidence.delayed_callback_count,
        "current_session_callback_count": evidence.current_session_callback_count,
        "first_historical_order_id": evidence.first_historical_order_id,
        "first_current_session_order_id": evidence.first_current_session_order_id,
        "manual_review_codes": list(evidence.manual_review_codes),
        "boundary_codes": list(evidence.boundary_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    return 0 if evidence.account_id is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
