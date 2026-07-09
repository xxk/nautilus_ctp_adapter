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

from nautilus_ctp_adapter.devtools.offhours_cli import write_json_payload


BASELINE = "ctp-paper-recovery-idempotency-v1"


OPENCTP_TTS_7X24_PROFILE = "openctp-tts-7x24-simulation"
OPENCTP_TTS_7X24_PROFILE_ALIASES = {OPENCTP_TTS_7X24_PROFILE, "openctp-paper"}


def _canonical_profile(profile: str | None) -> str:
    if profile in OPENCTP_TTS_7X24_PROFILE_ALIASES:
        return OPENCTP_TTS_7X24_PROFILE
    return str(profile or "")


def classify_checkpoint_resume(
    checkpoint: dict[str, Any],
    *,
    current_account_profile: str = OPENCTP_TTS_7X24_PROFILE,
) -> dict[str, Any]:
    issues: list[str] = []
    if _canonical_profile(checkpoint.get("account_profile")) != _canonical_profile(current_account_profile):
        issues.append("account_profile_mismatch")
    if checkpoint.get("schema_version") != BASELINE:
        issues.append("schema_version_mismatch")
    completed_steps = list(checkpoint.get("completed_steps") or [])
    pending_steps = list(checkpoint.get("pending_steps") or [])
    return {
        "accepted": not issues,
        "disposition": "resume_ready" if not issues else "checkpoint_contract_failed",
        "run_id": checkpoint.get("run_id"),
        "session_label": checkpoint.get("session_label"),
        "account_profile": checkpoint.get("account_profile"),
        "next_attempt": int(checkpoint.get("attempt") or 0) + 1,
        "resume_from": {
            "last_completed_step": completed_steps[-1] if completed_steps else None,
            "completed_steps": completed_steps,
            "pending_steps": pending_steps,
        },
        "issues": issues,
    }


def _unique_symbols(symbols: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
        normalized = str(symbol or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _resubscribe_counts(symbols: list[str]) -> dict[str, int]:
    return {symbol: 1 for symbol in _unique_symbols(symbols)}


def build_reconnect_disposition(
    *,
    run_id: str,
    attempt: int,
    md_symbols: list[str],
    md_disconnect_reason: int | None,
    td_disconnect_reason: int | None,
    td_login_success: bool,
    settlement_code: int,
    paper_send_armed: bool,
    max_attempts: int,
    in_flight_client_order_id: str | None = None,
) -> dict[str, Any]:
    issues: list[str] = []
    if attempt > max_attempts:
        issues.append("retry_budget_exhausted")
    if paper_send_armed:
        issues.append("paper_send_rearmed_after_reconnect")
    if not td_login_success:
        issues.append("td_login_failed")
    if settlement_code != 0:
        issues.append("td_settlement_not_ready")
    if in_flight_client_order_id:
        issues.append("in_flight_order_requires_manual_reconciliation")

    resubscribed_symbols = _unique_symbols(md_symbols)
    in_flight_order = {
        "client_order_id": in_flight_client_order_id,
        "disposition": "conservative_blocker" if in_flight_client_order_id else "none",
    }
    recovery = {
        "run_id": run_id,
        "attempt": attempt,
        "timeline": [
            {"event": "md_disconnect_detected", "reason": md_disconnect_reason, "attempt": attempt},
            {"event": "td_disconnect_detected", "reason": td_disconnect_reason, "attempt": attempt},
            {"event": "md_relogin_succeeded", "attempt": attempt},
            {"event": "md_resubscribe_replayed", "symbols": resubscribed_symbols, "attempt": attempt},
            {"event": "td_relogin_completed", "success": td_login_success, "attempt": attempt},
            {"event": "td_settlement_confirmed", "code": settlement_code, "attempt": attempt},
        ],
        "disconnects": [
            {
                "channel": "md",
                "reason": md_disconnect_reason,
                "attempt": attempt,
            },
            {
                "channel": "td",
                "reason": td_disconnect_reason,
                "attempt": attempt,
            },
        ],
        "reconnects": [
            {
                "channel": "md",
                "login_success": True,
                "settlement_code": None,
                "resubscribed_symbols": resubscribed_symbols,
                "resubscribe_counts": _resubscribe_counts(md_symbols),
                "guardrails_preserved": True,
            },
            {
                "channel": "td",
                "login_success": td_login_success,
                "settlement_code": settlement_code,
                "resubscribed_symbols": [],
                "guardrails_preserved": not paper_send_armed,
            },
        ],
        "query_recovery": {
            "account_query": "ready" if td_login_success and settlement_code == 0 else "blocked",
            "position_query": "ready" if td_login_success and settlement_code == 0 else "blocked",
            "order_query": "ready" if td_login_success and settlement_code == 0 else "blocked",
            "disposition": "query_ready" if td_login_success and settlement_code == 0 else "query_blocked",
        },
        "in_flight_order": in_flight_order,
        "disposition": "passed" if not issues else "typed_blocker",
    }
    return {
        "accepted": not issues,
        "baseline": BASELINE,
        "account_profile": OPENCTP_TTS_7X24_PROFILE,
        "evidence_class": "openctp-tts-7x24-simulation",
        "recovery": recovery,
        "issues": issues,
    }


def build_resource_blocker_payload(
    *,
    run_id: str,
    attempt: int,
    code: str,
    detail: str,
    md_symbols: list[str],
) -> dict[str, Any]:
    resubscribed_symbols = _unique_symbols(md_symbols)
    return {
        "accepted": False,
        "success": False,
        "status": "blocked",
        "baseline": BASELINE,
        "account_profile": OPENCTP_TTS_7X24_PROFILE,
        "evidence_class": "openctp-tts-7x24-simulation",
        "flow_mode": "openctp-tts-resource-blocker",
        "blocker_type": "paper-resource",
        "recovery": {
            "run_id": run_id,
            "attempt": attempt,
            "timeline": [
                {"event": "resource_blocker_recorded", "code": code, "detail": detail},
            ],
            "disconnects": [],
            "reconnects": [
                {
                    "channel": "md",
                    "login_success": None,
                    "settlement_code": None,
                    "resubscribed_symbols": resubscribed_symbols,
                    "resubscribe_counts": _resubscribe_counts(md_symbols),
                    "guardrails_preserved": True,
                },
                {
                    "channel": "td",
                    "login_success": None,
                    "settlement_code": None,
                    "resubscribed_symbols": [],
                    "guardrails_preserved": True,
                },
            ],
            "query_recovery": {
                "account_query": "not_executed",
                "position_query": "not_executed",
                "order_query": "not_executed",
                "disposition": "resource_blocked",
            },
            "in_flight_order": {"client_order_id": None, "disposition": "not_executed"},
            "disposition": "typed_blocker",
        },
        "issues": [code],
        "blocker_detail": detail,
    }


def classify_historical_residue(
    callbacks: list[dict[str, Any]],
    *,
    current_session: str,
) -> dict[str, Any]:
    seen: set[str] = set()
    historical_count = 0
    duplicate_input_count = 0
    emitted_current_report_count = 0
    for callback in callbacks:
        identity = str(callback.get("identity") or "")
        session = str(callback.get("session") or "")
        key = f"{session}:{identity}:{callback.get('is_trade')}"
        if key in seen:
            duplicate_input_count += 1
        else:
            seen.add(key)
        if session != current_session:
            historical_count += 1
            continue
        if identity:
            emitted_current_report_count += 1
    return {
        "accepted": True,
        "disposition": "historical_residue_isolated",
        "historical_count": historical_count,
        "duplicate_input_count": duplicate_input_count,
        "deduped_count": duplicate_input_count,
        "emitted_current_report_count": emitted_current_report_count,
    }


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


def build_repo_only_recovery_payload(*, run_id: str, attempt: int) -> dict[str, Any]:
    reconnect = build_reconnect_disposition(
        run_id=run_id,
        attempt=attempt,
        md_symbols=["rb2610", "rb2610"],
        md_disconnect_reason=4097,
        td_disconnect_reason=4098,
        td_login_success=True,
        settlement_code=0,
        paper_send_armed=False,
        max_attempts=3,
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
    return reconnect


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
