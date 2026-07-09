from __future__ import annotations

from pathlib import Path
from typing import Any


BASELINE = "ctp-guarded-paper-cancel-loop-v1"


def build_cancel_contract(
    *,
    instrument: str,
    client_order_id: str,
    order_ref: int,
    front_id: int,
    session_id: int,
    exchange_id: str | None,
) -> dict[str, Any]:
    return {
        "instrument": instrument,
        "client_order_id": client_order_id,
        "order_ref": order_ref,
        "front_id": front_id,
        "session_id": session_id,
        "exchange_id": exchange_id,
    }


def validate_cancel_command_contract(
    cancel_contract: dict[str, Any],
    command: Any | None,
) -> dict[str, Any]:
    issues: list[str] = []
    if command is None:
        return {
            "accepted": False,
            "disposition": "cancel_contract_failed",
            "issues": ["command_missing"],
        }
    if getattr(command, "kind", None) is None or getattr(command, "kind").value != "cancel_order":
        issues.append("command_kind_mismatch")
    if getattr(command, "venue_symbol", None) != cancel_contract["instrument"]:
        issues.append("instrument_mismatch")
    if getattr(command, "client_order_id", None) != cancel_contract["client_order_id"]:
        issues.append("client_order_id_mismatch")
    payload = getattr(command, "payload", {}) or {}
    for field_name in ("order_ref", "front_id", "session_id"):
        if str(payload.get(field_name, "")) != str(cancel_contract[field_name]):
            issues.append(f"{field_name}_mismatch")
    return {
        "accepted": not issues,
        "disposition": "cancel_contract_passed" if not issues else "cancel_contract_failed",
        "issues": issues,
    }


def classify_cancel_events(cancel_contract: dict[str, Any], events: list[Any]) -> dict[str, Any]:
    matched_events: list[Any] = []
    duplicate_count = 0
    seen_keys: set[tuple[str, str, str, str]] = set()
    cancelled = False
    rejected = False
    filled = False

    for event in events:
        client_order_id = str(_event_value(event, "client_order_id", "") or "")
        venue_symbol = str(_event_value(event, "venue_symbol", "") or "")
        if client_order_id != cancel_contract["client_order_id"]:
            continue
        if venue_symbol and venue_symbol != cancel_contract["instrument"]:
            continue
        kind = str(_event_value(event, "kind", "") or "").lower()
        status = str(_event_value(event, "status", "") or "").lower()
        order_id = str(_event_value(event, "native_order_id", "") or "")
        order_ref = str(_event_value(event, "native_order_ref", "") or "")
        error_message = str(_event_value(event, "error_message", "") or "")
        event_key = (kind, order_id, order_ref, status)
        if event_key in seen_keys:
            duplicate_count += 1
            continue
        seen_keys.add(event_key)
        matched_events.append(event)
        if status in {"cancelled", "canceled", "5"}:
            cancelled = True
        if kind == "trade":
            filled = True
        if error_message:
            rejected = True

    if cancelled:
        disposition = "cancelled"
    elif filled:
        disposition = "filled_before_cancel"
    elif rejected:
        disposition = "cancel_rejected"
    elif matched_events:
        disposition = "cancel_accepted"
    else:
        disposition = "timeout"
    return {
        "accepted": True,
        "disposition": disposition,
        "matched_event_count": len(matched_events),
        "duplicate_event_count": duplicate_count,
    }


def build_native_cancel_unavailable_payload(
    *,
    issue: str,
    flow_path: Path,
    message: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "accepted": False,
        "failure_reason": "native_cancel_unavailable",
        "blocker_type": "paper-resource",
        "issues": [issue],
        "flow_path": str(flow_path),
    }
    if message is not None:
        payload["message"] = message
    return payload


def build_native_cancel_login_failed_payload(
    *,
    init_code: int,
    authenticate_code: int,
    login_code: int,
    login: Any | None,
    flow_path: Path,
) -> dict[str, Any]:
    return {
        "accepted": False,
        "failure_reason": "native_cancel_login_failed",
        "blocker_type": "paper-resource",
        "issues": ["login_failed_or_timeout"],
        "init_code": init_code,
        "authenticate_code": authenticate_code,
        "login_code": login_code,
        "login_error_id": None if login is None else getattr(login, "error_id", None),
        "login_error_message": None if login is None else getattr(login, "error_message", None),
        "flow_path": str(flow_path),
    }


def build_native_cancel_settlement_failed_payload(
    *,
    settlement_code: int,
    flow_path: Path,
) -> dict[str, Any]:
    return {
        "accepted": False,
        "failure_reason": "native_cancel_settlement_failed",
        "blocker_type": "paper-resource",
        "issues": ["settlement_failed"],
        "settlement_code": settlement_code,
        "flow_path": str(flow_path),
    }


def build_native_cancel_action_payload(
    *,
    native_code: int,
    flow_path: Path,
    disconnect_count: int,
    observed_event_count: int,
) -> dict[str, Any]:
    return {
        "accepted": native_code == 0,
        "failure_reason": None if native_code == 0 else "native_cancel_action_failed",
        "blocker_type": None if native_code == 0 else "paper-resource",
        "issues": [] if native_code == 0 else [f"native_code={native_code}"],
        "native_code": native_code,
        "flow_path": str(flow_path),
        "disconnect_count": disconnect_count,
        "observed_event_count": observed_event_count,
    }


def _event_value(event: Any, name: str, default: Any = None) -> Any:
    if isinstance(event, dict):
        return event.get(name, default)
    if name == "kind" and hasattr(event, "kind"):
        kind = getattr(event, "kind")
        return getattr(kind, "value", kind)
    if name == "native_order_id":
        payload = getattr(event, "payload", {}) or {}
        return payload.get("native_order_id") or payload.get("order_id") or default
    if name == "native_order_ref":
        payload = getattr(event, "payload", {}) or {}
        return payload.get("native_order_ref") or payload.get("order_ref") or default
    if name == "status":
        payload = getattr(event, "payload", {}) or {}
        return payload.get("status", default)
    return getattr(event, name, default)


__all__ = [
    "BASELINE",
    "build_cancel_contract",
    "build_native_cancel_action_payload",
    "build_native_cancel_login_failed_payload",
    "build_native_cancel_settlement_failed_payload",
    "build_native_cancel_unavailable_payload",
    "classify_cancel_events",
    "validate_cancel_command_contract",
]
