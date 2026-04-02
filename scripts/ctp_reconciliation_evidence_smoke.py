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
    parser = argparse.ArgumentParser(description="Run the automated reconciliation evidence smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    adapter = stack["reconciliation_adapter"]
    runtime_bridge = stack["runtime_bridge"]

    evidence = adapter.capture_evidence_mainline(
        timeout_seconds=args.timeout_seconds,
        completion_grace_seconds=args.completion_grace_seconds,
    )
    events = runtime_bridge.drain_events()
    commands = runtime_bridge.drain_submitted_commands()

    payload = {
        "evidence_version": evidence.evidence_version,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "disposition": evidence.disposition,
        "requires_manual_review": evidence.requires_manual_review,
        "finding_count": evidence.finding_count,
        "manual_review_codes": list(evidence.manual_review_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "position_line_count": evidence.position_line_count,
        "symbol_count": evidence.symbol_count,
        "gross_position_qty": evidence.gross_position_qty,
        "available_ratio": evidence.available_ratio,
        "margin_ratio": evidence.margin_ratio,
        "dominant_exposure_symbol": evidence.dominant_exposure_symbol,
        "dominant_exposure_abs_net_qty": evidence.dominant_exposure_abs_net_qty,
        "top_exposures": [
            {
                "venue_symbol": exposure.venue_symbol,
                "exchange_id": exposure.exchange_id,
                "long_qty": exposure.long_qty,
                "short_qty": exposure.short_qty,
                "gross_qty": exposure.gross_qty,
                "net_qty": exposure.net_qty,
                "abs_net_qty": exposure.abs_net_qty,
                "position_cost": exposure.position_cost,
            }
            for exposure in evidence.top_exposures
        ],
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    print(json.dumps(payload, ensure_ascii=False))

    success = evidence.account_id is not None and evidence.finding_count > 0
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
