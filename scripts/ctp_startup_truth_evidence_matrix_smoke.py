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
    parser = argparse.ArgumentParser(description="Run the startup truth evidence matrix live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--shared-flow-path", type=Path, default=None)
    parser.add_argument("--isolated-flow-path", type=Path, default=None)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    adapter = stack["startup_truth_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    evidence = adapter.capture_evidence_matrix_mainline(
        timeout_seconds=args.timeout_seconds,
        shared_flow_path=args.shared_flow_path,
        isolated_flow_path=args.isolated_flow_path,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "evidence_version": evidence.evidence_version,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "disposition": evidence.disposition,
        "shared_flow_reuse_allowed": evidence.shared_flow_reuse_allowed,
        "session_rotated": evidence.session_rotated,
        "max_order_ref_reset": evidence.max_order_ref_reset,
        "shared_flow_path": evidence.shared_flow_path,
        "isolated_flow_path": evidence.isolated_flow_path,
        "shared_session_id": evidence.shared_session_id,
        "isolated_session_id": evidence.isolated_session_id,
        "shared_max_order_ref": evidence.shared_max_order_ref,
        "isolated_max_order_ref": evidence.isolated_max_order_ref,
        "shared_disconnect_count": evidence.shared_disconnect_count,
        "isolated_disconnect_count": evidence.isolated_disconnect_count,
        "manual_review_codes": list(evidence.manual_review_codes),
        "rebuild_required_codes": list(evidence.rebuild_required_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = evidence.account_id is not None and (
        len(evidence.rebuild_required_codes) > 0 or len(evidence.manual_review_codes) > 0
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
