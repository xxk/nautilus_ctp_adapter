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
    parser = argparse.ArgumentParser(description="Run the MD truth evidence matrix live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    runtime_bridge = stack["runtime_bridge"]

    evidence = data_client.capture_md_truth_evidence_matrix_mainline(
        timeout_seconds=args.timeout_seconds,
        flow_path=args.flow_path,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "evidence_version": evidence.evidence_version,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "symbol": evidence.symbol,
        "disposition": evidence.disposition,
        "startup_ready": evidence.startup_ready,
        "restore_triggered": evidence.restore_triggered,
        "restore_succeeded": evidence.restore_succeeded,
        "startup_flow_path": evidence.startup_flow_path,
        "restored_flow_path": evidence.restored_flow_path,
        "startup_first_tick_ts_epoch_us": evidence.startup_first_tick_ts_epoch_us,
        "restored_first_tick_ts_epoch_us": evidence.restored_first_tick_ts_epoch_us,
        "manual_review_codes": list(evidence.manual_review_codes),
        "restore_required_codes": list(evidence.restore_required_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    return 0 if evidence.restore_succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
