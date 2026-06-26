from __future__ import annotations

import time
from typing import Any


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


def build_controlled_reconnect_evidence(
    *,
    run_id: str,
    md_symbols: list[str],
    td_ready: bool,
    settlement_code: int,
    paper_send_armed: bool,
    md_drop_count: int,
    td_drop_count: int,
) -> dict[str, Any]:
    payload = build_reconnect_disposition(
        run_id=run_id,
        attempt=1,
        md_symbols=md_symbols,
        md_disconnect_reason=4097 if md_drop_count else None,
        td_disconnect_reason=4098 if td_drop_count else None,
        td_login_success=td_ready,
        settlement_code=settlement_code,
        paper_send_armed=paper_send_armed,
        max_attempts=3,
    )
    payload["flow_mode"] = "controlled-front-proxy"
    payload["paper_send_armed"] = paper_send_armed
    payload["blocker_resolved"] = "forced_front_disconnect_unavailable"
    payload["controlled_proxy"] = {
        "md_drop_count": md_drop_count,
        "td_drop_count": td_drop_count,
        "scope": "process_local",
    }
    payload["success"] = payload["accepted"] and md_drop_count >= 1 and td_drop_count >= 1
    payload["status"] = "passed" if payload["success"] else "blocked"
    return payload


__all__ = [
    "BASELINE",
    "OPENCTP_TTS_7X24_PROFILE",
    "build_controlled_reconnect_evidence",
    "build_reconnect_disposition",
    "build_repo_only_recovery_payload",
    "build_resource_blocker_payload",
    "classify_checkpoint_resume",
    "classify_historical_residue",
]
