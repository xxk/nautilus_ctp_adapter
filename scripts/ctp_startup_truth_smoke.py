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
    parser = argparse.ArgumentParser(description="Run the TD startup truth live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    adapter = stack["startup_truth_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    evidence = adapter.capture_td_startup_truth_mainline(
        timeout_seconds=args.timeout_seconds,
        flow_path=args.flow_path,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "baseline": "td-startup-truth-v1",
        "flow_path": evidence.flow_path,
        "flow_mode": evidence.flow_mode,
        "ready": evidence.ready,
        "login_success": evidence.login_success,
        "settlement_code": evidence.settlement_code,
        "front_id": evidence.front_id,
        "session_id": evidence.session_id,
        "max_order_ref": evidence.max_order_ref,
        "disconnect_count": evidence.disconnect_count,
        "disconnect_reasons": list(evidence.disconnect_reasons),
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = evidence.ready and evidence.login_success is True and evidence.settlement_code == 0
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
