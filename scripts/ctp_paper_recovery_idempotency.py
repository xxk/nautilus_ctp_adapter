from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.diagnostics.paper_recovery_idempotency import (
    BASELINE,
    build_reconnect_disposition,
    build_resource_blocker_payload,
    classify_checkpoint_resume,
    classify_historical_residue,
)
from nautilus_ctp_adapter.devtools.offhours_cli import write_json_payload


def write_recovery_attempt(evidence_root: Path, payload: dict[str, Any]) -> Path:
    evidence_root.mkdir(parents=True, exist_ok=True)
    recovery = payload.get("recovery") or {}
    attempt = int(recovery.get("attempt") or 1)
    attempt_path = evidence_root / f"attempt-{attempt:03d}.json"
    write_json_payload(path=attempt_path, payload=payload)

    manifest_path = evidence_root / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"baseline": BASELINE, "attempts": []}
    manifest["attempts"].append(
        {
            "attempt": attempt,
            "path": str(attempt_path),
            "run_id": recovery.get("run_id"),
            "disposition": recovery.get("disposition"),
        }
    )
    write_json_payload(path=manifest_path, payload=manifest)
    return attempt_path

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build deterministic P003 OpenCTP paper recovery/idempotency evidence."
    )
    parser.add_argument("--run-id", default=f"paper-recovery-{int(time.time() * 1000)}")
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--md-symbol", action="append", default=[])
    parser.add_argument("--md-disconnect-reason", type=int, default=4097)
    parser.add_argument("--td-disconnect-reason", type=int, default=4098)
    parser.add_argument("--td-login-failed", action="store_true")
    parser.add_argument("--settlement-code", type=int, default=0)
    parser.add_argument("--paper-send-armed", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--in-flight-client-order-id")
    parser.add_argument("--resource-blocker-code")
    parser.add_argument("--resource-blocker-detail", default="")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    symbols = args.md_symbol or ["rb2610", "rb2610"]
    if args.resource_blocker_code:
        payload = build_resource_blocker_payload(
            run_id=args.run_id,
            attempt=args.attempt,
            code=args.resource_blocker_code,
            detail=args.resource_blocker_detail,
            md_symbols=symbols,
        )
    else:
        reconnect = build_reconnect_disposition(
            run_id=args.run_id,
            attempt=args.attempt,
            md_symbols=symbols,
            md_disconnect_reason=args.md_disconnect_reason,
            td_disconnect_reason=args.td_disconnect_reason,
            td_login_success=not args.td_login_failed,
            settlement_code=args.settlement_code,
            paper_send_armed=args.paper_send_armed,
            max_attempts=args.max_attempts,
            in_flight_client_order_id=args.in_flight_client_order_id,
        )
        idempotency = classify_historical_residue(
            [
                {"identity": "hist-1", "session": "old", "is_trade": True},
                {"identity": "hist-1", "session": "old", "is_trade": True},
                {"identity": "cur-1", "session": "current", "is_trade": True},
            ],
            current_session="current",
        )
        reconnect["recovery"]["idempotency"] = idempotency
        reconnect["success"] = reconnect["accepted"] and idempotency["accepted"]
        reconnect["status"] = "passed" if reconnect["success"] else "blocked"
        reconnect["flow_mode"] = "repo-only"
        reconnect["generated_at_epoch_ms"] = int(time.time() * 1000)
        payload = reconnect
    text = json.dumps(payload, ensure_ascii=False)
    print(text)
    if args.evidence_root is not None:
        write_recovery_attempt(
            args.evidence_root if args.evidence_root.is_absolute() else REPO_ROOT / args.evidence_root,
            payload,
        )
    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        write_json_payload(path=output_path, payload=payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
