from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpExecutionClient
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack
from nautilus_ctp_adapter.devtools.offhours_cli import write_json_payload

from scripts.ctp_paper_session_preflight import paper_config_issues


BASELINE = "ctp-guarded-paper-order-loop-v1"
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.openctp.tts.7x24.local.json"
OPENCTP_TTS_7X24_PROFILE = "openctp-tts-7x24-simulation"
OPENCTP_TTS_7X24_PROFILE_ALIASES = {OPENCTP_TTS_7X24_PROFILE, "openctp-paper"}
OPENCTP_TTS_7X24_EVIDENCE_CLASS = "openctp-tts-7x24-simulation"
OPENCTP_TTS_7X24_EVIDENCE_ALIASES = {OPENCTP_TTS_7X24_EVIDENCE_CLASS, "paper-simulation"}


def json_stdout_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")


def emit_json_stdout(payload: dict[str, Any]) -> None:
    data = json_stdout_bytes(payload)
    stdout_buffer = getattr(sys.stdout, "buffer", None)
    if stdout_buffer is not None:
        stdout_buffer.write(data)
        stdout_buffer.flush()
        return
    sys.stdout.write(data.decode(sys.stdout.encoding or "utf-8", errors="backslashreplace"))
    sys.stdout.flush()


def validate_pre_order_snapshot(path: Path) -> dict[str, Any]:
    issues: list[str] = []
    if not path.exists():
        return {"accepted": False, "issues": ["pre_snapshot_missing"]}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"accepted": False, "issues": ["pre_snapshot_invalid_json"]}
    schema = payload.get("schema") if isinstance(payload, dict) else {}
    if not payload.get("success"):
        issues.append("pre_snapshot_not_success")
    if schema.get("account_profile") not in OPENCTP_TTS_7X24_PROFILE_ALIASES:
        issues.append("pre_snapshot_account_profile")
    if schema.get("evidence_class") not in OPENCTP_TTS_7X24_EVIDENCE_ALIASES:
        issues.append("pre_snapshot_evidence_class")
    if schema.get("reconciliation_role") != "pre_or_post_order_snapshot":
        issues.append("pre_snapshot_reconciliation_role")
    if payload.get("snapshot_complete") is False:
        issues.append("pre_snapshot_partial")
    completion = payload.get("completion")
    if isinstance(completion, dict) and completion.get("status") in {"partial", "incomplete"}:
        issues.append("pre_snapshot_partial")
    return {"accepted": not issues, "issues": issues}


def select_close_candidate_from_snapshot(
    snapshot_payload: dict[str, Any],
    *,
    instrument: str,
    quantity: int,
    expected_run_id: str | None = None,
    direction: str | None = None,
) -> dict[str, Any]:
    issues: list[str] = []
    schema = snapshot_payload.get("schema") if isinstance(snapshot_payload, dict) else {}
    if expected_run_id and schema.get("run_id") != expected_run_id:
        issues.append("pre_snapshot_run_id_mismatch")
    if not snapshot_payload.get("success"):
        issues.append("pre_snapshot_not_success")
    if schema.get("account_profile") not in OPENCTP_TTS_7X24_PROFILE_ALIASES:
        issues.append("pre_snapshot_account_profile")
    if schema.get("evidence_class") not in OPENCTP_TTS_7X24_EVIDENCE_ALIASES:
        issues.append("pre_snapshot_evidence_class")
    if quantity <= 0:
        issues.append("invalid_close_quantity")
    if issues:
        return {
            "accepted": False,
            "disposition": "close_candidate_failed",
            "issues": issues,
            "candidate": None,
        }

    records = ((snapshot_payload.get("positions") or {}).get("records") or [])
    instrument_records = ((snapshot_payload.get("instruments") or {}).get("records") or [])
    exchange_by_symbol = {
        str(record.get("venue_symbol", "")).strip(): record.get("exchange_id")
        for record in instrument_records
        if record.get("venue_symbol")
    }
    normalized_direction = "" if direction is None else direction.strip().upper()
    matching_records = []
    for record in records:
        if str(record.get("venue_symbol", "")).strip() != instrument:
            continue
        if normalized_direction and str(record.get("direction", "")).strip().upper() != normalized_direction:
            continue
        matching_records.append(record)
    if not matching_records:
        return {
            "accepted": False,
            "disposition": "close_candidate_failed",
            "issues": ["no_matching_position"],
            "candidate": None,
        }

    def _int_value(record: dict[str, Any], key: str) -> int:
        return max(int(record.get(key) or 0), 0)

    for record in matching_records:
        position_qty = _int_value(record, "position_qty")
        td_position_qty = _int_value(record, "td_position_qty")
        yd_position_qty = _int_value(record, "yd_position_qty")
        closable_quantity = position_qty if position_qty > 0 else td_position_qty + yd_position_qty
        if closable_quantity <= 0:
            continue
        return {
            "accepted": True,
            "disposition": "close_candidate_selected",
            "issues": [],
            "candidate": {
                "venue_symbol": record.get("venue_symbol"),
                "exchange_id": record.get("exchange_id") or exchange_by_symbol.get(instrument),
                "direction": record.get("direction"),
                "position_qty": position_qty,
                "td_position_qty": td_position_qty,
                "yd_position_qty": yd_position_qty,
                "closable_quantity": closable_quantity,
            },
        }

    return {
        "accepted": False,
        "disposition": "close_candidate_failed",
        "issues": ["no_closable_position"],
        "candidate": None,
    }


def build_close_intent_from_snapshot(
    snapshot_payload: dict[str, Any],
    *,
    instrument: str,
    quantity: int,
    requested_position_effect: str,
    limit_price: float,
    client_order_id: str,
    expected_run_id: str | None = None,
    direction: str | None = None,
) -> dict[str, Any]:
    candidate_verdict = select_close_candidate_from_snapshot(
        snapshot_payload,
        instrument=instrument,
        quantity=quantity,
        expected_run_id=expected_run_id,
        direction=direction,
    )
    payload: dict[str, Any] = {
        "accepted": False,
        "disposition": "close_intent_failed",
        "candidate": candidate_verdict.get("candidate"),
        "selected_bucket": None,
        "submit_intent": None,
        "issues": list(candidate_verdict.get("issues") or []),
    }
    if not candidate_verdict["accepted"]:
        return payload

    candidate = candidate_verdict["candidate"] or {}
    close_plan = CtpExecutionClient().build_close_position_intent(
        instrument_id=instrument,
        exchange_id=candidate.get("exchange_id"),
        direction=str(candidate.get("direction") or ""),
        position_qty=candidate.get("position_qty"),
        td_position_qty=candidate.get("td_position_qty"),
        yd_position_qty=candidate.get("yd_position_qty"),
        close_quantity=quantity,
        requested_position_effect=requested_position_effect,
        limit_price=limit_price,
        client_order_id=client_order_id,
    )
    if close_plan.error is not None or close_plan.submit_intent is None:
        payload["issues"].append(
            "close_intent_error"
            if close_plan.error is None
            else close_plan.error.error_message
        )
        return payload

    submit_intent = close_plan.submit_intent
    payload.update(
        {
            "accepted": True,
            "disposition": "close_intent_ready",
            "selected_bucket": close_plan.selected_bucket,
            "submit_intent": build_intent_contract(
                instrument=submit_intent.instrument_id,
                side=submit_intent.side,
                quantity=submit_intent.quantity,
                limit_price=submit_intent.limit_price,
                position_effect=submit_intent.position_effect,
                price_mode="snapshot_close",
                client_order_id=submit_intent.client_order_id or client_order_id,
            ),
            "issues": [],
        }
    )
    return payload


def validate_order_boundary_from_snapshot(
    snapshot_payload: dict[str, Any],
    *,
    instrument: str,
    quantity: int,
    limit_price: float,
) -> dict[str, Any]:
    issues: list[str] = []
    instrument_record = _instrument_record_from_snapshot(snapshot_payload, instrument)
    if quantity <= 0:
        issues.append("invalid_quantity")
    if limit_price <= 0:
        issues.append("invalid_limit_price")
    if instrument_record is None:
        issues.append("instrument_metadata_missing")
        return {
            "accepted": False,
            "disposition": "order_boundary_failed",
            "issues": issues,
            "instrument": None,
            "limit_boundary": {"source": "not_available", "status": "unknown"},
        }

    price_tick = instrument_record.get("price_tick")
    volume_multiple = instrument_record.get("volume_multiple")
    if price_tick in {None, 0}:
        issues.append("price_tick_missing")
    if volume_multiple in {None, 0}:
        issues.append("volume_multiple_missing")
    if price_tick not in {None, 0} and limit_price > 0 and not _is_price_tick_aligned(limit_price, price_tick):
        issues.append("off_tick_price")
    return {
        "accepted": not issues,
        "disposition": "order_boundary_passed" if not issues else "order_boundary_failed",
        "issues": issues,
        "instrument": {
            "venue_symbol": instrument_record.get("venue_symbol"),
            "exchange_id": instrument_record.get("exchange_id"),
            "price_tick": price_tick,
            "volume_multiple": volume_multiple,
        },
        "limit_boundary": {"source": "not_available", "status": "unknown"},
    }


def extract_risk_facts_from_snapshot(snapshot_payload: dict[str, Any], *, instrument: str) -> dict[str, Any]:
    account = snapshot_payload.get("account") or {}
    identity = account.get("identity") or {}
    positions = snapshot_payload.get("positions") or {}
    records = positions.get("records") or []
    long_qty = 0
    short_qty = 0
    considered = 0
    for record in records:
        if str(record.get("venue_symbol") or "").strip() != instrument:
            continue
        considered += 1
        qty = max(int(record.get("position_qty") or 0), 0)
        direction = str(record.get("direction") or "").strip().upper()
        if direction == "LONG":
            long_qty += qty
        elif direction == "SHORT":
            short_qty += qty

    return {
        "account": {
            "account_id_present": bool(identity.get("account_id_present")),
            "account_id_fingerprint": str(identity.get("account_id_fingerprint") or ""),
            "balance_present": _metric_present(account, "balance"),
            "available_present": _metric_present(account, "available"),
            "margin_present": _metric_present(account, "margin"),
            "numeric_values_redacted": True,
        },
        "positions": {
            "position_count": int(positions.get("position_count") or len(records)),
            "query_disposition": str((positions.get("completion") or {}).get("disposition") or ""),
            "instrument": instrument,
            "records_considered": considered,
            "long_qty": long_qty,
            "short_qty": short_qty,
            "net_position": long_qty - short_qty,
            "gross_position": long_qty + short_qty,
        },
    }


def build_risk_preflight_from_snapshot(
    snapshot_payload: dict[str, Any],
    *,
    config: CtpAdapterConfig,
    instrument: str,
    side: str,
    quantity: int,
    position_effect: str,
    client_order_id: str,
    arm_paper_send: bool,
    submit_count_last_minute: int = 0,
    session_send_count: int = 0,
    session_send_budget: int = 0,
    seen_client_order_ids: list[str] | None = None,
) -> dict[str, Any]:
    facts = extract_risk_facts_from_snapshot(snapshot_payload, instrument=instrument)
    guardrails = config.execution_guardrails
    normalized_side = side.strip().upper()
    normalized_effect = position_effect.strip().upper()
    projected_net_position = facts["positions"]["net_position"] + _net_delta(
        side=normalized_side,
        position_effect=normalized_effect,
        quantity=quantity,
    )
    seen_ids = {str(item) for item in (seen_client_order_ids or [])}
    issues: list[str] = []
    guards: dict[str, dict[str, Any]] = {}

    def _record_guard(name: str, accepted: bool, issue: str | None = None, **extra: Any) -> None:
        if issue and not accepted:
            issues.append(issue)
        guards[name] = {"accepted": accepted, **extra}

    account = facts["account"]
    _record_guard(
        "account_identity",
        bool(account["account_id_present"]),
        "account_identity_unavailable",
    )
    _record_guard(
        "available_metric",
        bool(account["available_present"]),
        "account_available_metric_unavailable",
        basis="presence_only_redacted",
    )
    _record_guard(
        "margin_metric",
        bool(account["margin_present"]),
        "account_margin_metric_unavailable",
        basis="presence_only_redacted",
    )
    _record_guard(
        "kill_switch",
        not (arm_paper_send and not guardrails.allow_live_order_smoke),
        "kill_switch_closed",
        armed=arm_paper_send,
        allow_live_order_smoke=guardrails.allow_live_order_smoke,
    )

    if guardrails.enabled:
        _record_guard(
            "instrument_allowlist",
            not guardrails.allowed_instruments or instrument in guardrails.allowed_instruments,
            "instrument_not_allowed",
            allowed_instruments=list(guardrails.allowed_instruments),
        )
        _record_guard(
            "max_order_qty",
            quantity > 0 and (not guardrails.max_order_qty or quantity <= guardrails.max_order_qty),
            "max_order_qty_exceeded",
            max_order_qty=guardrails.max_order_qty,
            quantity=quantity,
        )
        _record_guard(
            "max_net_position",
            not guardrails.max_net_position
            or abs(projected_net_position) <= guardrails.max_net_position,
            "max_net_position_exceeded",
            max_net_position=guardrails.max_net_position,
            projected_net_position=projected_net_position,
        )
        _record_guard(
            "frequency_cap",
            not guardrails.max_submit_per_minute
            or submit_count_last_minute < guardrails.max_submit_per_minute,
            "frequency_cap_exceeded",
            submit_count_last_minute=submit_count_last_minute,
            max_submit_per_minute=guardrails.max_submit_per_minute,
        )

    _record_guard(
        "session_send_budget",
        not session_send_budget or session_send_count < session_send_budget,
        "session_send_budget_exceeded",
        session_send_count=session_send_count,
        session_send_budget=session_send_budget,
    )
    _record_guard(
        "client_order_id_idempotency",
        client_order_id not in seen_ids,
        "duplicate_client_order_id",
        client_order_id=client_order_id,
    )

    unique_issues = sorted(set(issues))
    return {
        "accepted": not unique_issues,
        "disposition": "risk_preflight_passed" if not unique_issues else "risk_preflight_failed",
        "issues": unique_issues,
        "facts": facts,
        "guards": guards,
        "projected_net_position": projected_net_position,
        "native_send_allowed": not unique_issues,
    }


def _metric_present(account: dict[str, Any], name: str) -> bool:
    present_key = f"{name}_present"
    if present_key in account:
        return bool(account[present_key])
    return account.get(name) is not None


def _net_delta(*, side: str, position_effect: str, quantity: int) -> int:
    if position_effect in {"OPEN", "CLOSE", "CLOSETODAY", "CLOSEYESTERDAY"}:
        if side == "BUY":
            return quantity
        if side == "SELL":
            return -quantity
    return 0


def _instrument_record_from_snapshot(snapshot_payload: dict[str, Any], instrument: str) -> dict[str, Any] | None:
    for record in ((snapshot_payload.get("instruments") or {}).get("records") or []):
        if str(record.get("venue_symbol", "")).strip() == instrument:
            return record
    return None


def _is_price_tick_aligned(limit_price: float, price_tick: float) -> bool:
    try:
        price = Decimal(str(limit_price))
        tick = Decimal(str(price_tick))
    except InvalidOperation:
        return False
    if tick <= 0:
        return False
    return (price / tick) == (price / tick).to_integral_value()


def build_intent_contract(
    *,
    instrument: str,
    side: str,
    quantity: int,
    limit_price: float,
    position_effect: str,
    price_mode: str,
    client_order_id: str,
    order_type: str = "LIMIT",
    time_in_force: str = "GFD",
) -> dict[str, Any]:
    return {
        "instrument": instrument,
        "side": side.strip().upper(),
        "quantity": quantity,
        "limit_price": limit_price,
        "position_effect": position_effect.strip().upper(),
        "order_type": order_type.strip().upper(),
        "time_in_force": time_in_force.strip().upper(),
        "price_mode": price_mode,
        "client_order_id": client_order_id,
    }


def validate_order_command_contract(
    intent_contract: dict[str, Any],
    command: Any | None,
) -> dict[str, Any]:
    issues: list[str] = []
    if command is None:
        return {
            "accepted": False,
            "disposition": "order_contract_failed",
            "issues": ["command_missing"],
        }
    if getattr(command, "kind", None) is None or getattr(command, "kind").value != "submit_order":
        issues.append("command_kind_mismatch")
    if getattr(command, "venue_symbol", None) != intent_contract["instrument"]:
        issues.append("instrument_mismatch")
    if getattr(command, "client_order_id", None) != intent_contract["client_order_id"]:
        issues.append("client_order_id_mismatch")
    payload = getattr(command, "payload", {}) or {}
    if str(payload.get("side", "")).upper() != intent_contract["side"]:
        issues.append("side_mismatch")
    if int(payload.get("quantity", "0") or 0) != int(intent_contract["quantity"]):
        issues.append("quantity_mismatch")
    if float(payload.get("limit_price", "0") or 0) != float(intent_contract["limit_price"]):
        issues.append("limit_price_mismatch")
    if str(payload.get("position_effect", "")).upper() != intent_contract["position_effect"]:
        issues.append("position_effect_mismatch")
    if str(payload.get("order_type", "")).upper() != intent_contract["order_type"]:
        issues.append("order_type_mismatch")
    if str(payload.get("time_in_force", "")).upper() != intent_contract["time_in_force"]:
        issues.append("time_in_force_mismatch")
    for field_name in ("order_ref", "front_id", "session_id"):
        if not payload.get(field_name):
            issues.append(f"{field_name}_missing")
    return {
        "accepted": not issues,
        "disposition": "order_contract_passed" if not issues else "order_contract_failed",
        "issues": issues,
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
    if name == "native_trade_id":
        payload = getattr(event, "payload", {}) or {}
        return payload.get("trade_id") or payload.get("native_trade_id") or payload.get("order_id") or default
    if name == "native_order_ref":
        payload = getattr(event, "payload", {}) or {}
        return payload.get("native_order_ref") or payload.get("order_ref") or default
    if name in {"trade_volume", "trade_price", "leaves_qty"}:
        payload = getattr(event, "payload", {}) or {}
        return payload.get(name, default)
    return getattr(event, name, default)


def classify_lifecycle_events(
    intent_contract: dict[str, Any],
    events: list[Any],
) -> dict[str, Any]:
    issues: list[str] = []
    matched_events: list[Any] = []
    fill_volume = 0
    duplicate_fill_count = 0
    seen_fill_keys: set[tuple[str, str]] = set()
    rejected = False
    cancelled = False
    last_leaves_qty: int | None = None

    for event in events:
        client_order_id = str(_event_value(event, "client_order_id", "") or "")
        venue_symbol = str(_event_value(event, "venue_symbol", "") or "")
        if client_order_id != intent_contract["client_order_id"]:
            continue
        if venue_symbol and venue_symbol != intent_contract["instrument"]:
            issues.append("venue_symbol_mismatch")
            continue
        matched_events.append(event)
        kind = str(_event_value(event, "kind", "") or "").lower()
        error_message = str(_event_value(event, "payload_error_msg", "") or "")
        if kind == "trade":
            order_id = str(_event_value(event, "native_order_id", "") or "")
            trade_id = str(_event_value(event, "native_trade_id", "") or order_id)
            fill_key = (order_id, trade_id)
            if fill_key in seen_fill_keys:
                duplicate_fill_count += 1
                continue
            seen_fill_keys.add(fill_key)
            fill_volume += int(_event_value(event, "trade_volume", 0) or 0)
            if int(_event_value(event, "leaves_qty", 0) or 0) < 0:
                issues.append("negative_leaves_qty")
        if error_message:
            rejected = True
        status = str(_event_value(event, "status", "") or "").lower()
        event_leaves_qty = _event_value(event, "leaves_qty", None)
        if event_leaves_qty is not None:
            last_leaves_qty = int(event_leaves_qty or 0)
        if status in {"cancelled", "canceled", "5", "53"}:
            cancelled = True

    if fill_volume > int(intent_contract["quantity"]):
        issues.append("fill_volume_exceeds_quantity")
    if issues:
        disposition = "callback_contract_failed"
    elif fill_volume == int(intent_contract["quantity"]):
        disposition = "filled"
    elif cancelled:
        disposition = "cancelled"
    elif rejected:
        disposition = "rejected"
    elif matched_events:
        disposition = "accepted"
    else:
        disposition = "timeout"
    return {
        "accepted": not issues,
        "disposition": disposition,
        "matched_event_count": len(matched_events),
        "unique_fill_count": len(seen_fill_keys),
        "duplicate_fill_count": duplicate_fill_count,
        "fill_volume": fill_volume,
        "leaves_qty": last_leaves_qty
        if cancelled and last_leaves_qty is not None
        else max(int(intent_contract["quantity"]) - fill_volume, 0),
        "issues": sorted(set(issues)),
    }


def reconcile_pre_post_snapshots(
    pre_snapshot: dict[str, Any],
    post_snapshot: dict[str, Any],
    *,
    intent_contract: dict[str, Any] | None = None,
    lifecycle_verdict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues: list[str] = []
    pre_schema = pre_snapshot.get("schema") if isinstance(pre_snapshot, dict) else {}
    post_schema = post_snapshot.get("schema") if isinstance(post_snapshot, dict) else {}
    if pre_schema.get("account_profile") != post_schema.get("account_profile"):
        issues.append("profile_mismatch")
    if pre_schema.get("evidence_class") != post_schema.get("evidence_class"):
        issues.append("evidence_class_mismatch")
    if pre_schema.get("run_id") and post_schema.get("run_id") and pre_schema.get("run_id") == post_schema.get("run_id"):
        issues.append("post_snapshot_stale_same_run_id")
    if pre_snapshot.get("snapshot_complete") is False or post_snapshot.get("snapshot_complete") is False:
        issues.append("snapshot_partial")

    pre_identity = ((pre_snapshot.get("account") or {}).get("identity") or {})
    post_identity = ((post_snapshot.get("account") or {}).get("identity") or {})
    pre_account_fp = pre_identity.get("account_id_fingerprint")
    post_account_fp = post_identity.get("account_id_fingerprint")
    if pre_account_fp and post_account_fp and pre_account_fp != post_account_fp:
        issues.append("account_identity_mismatch")

    pre_positions = pre_snapshot.get("positions") or {}
    post_positions = post_snapshot.get("positions") or {}
    pre_count = int(pre_positions.get("position_count") or 0)
    post_count = int(post_positions.get("position_count") or 0)
    target_key = _target_position_key_for_intent(intent_contract)
    target_position_delta: int | None = None
    expected_position_delta: int | None = None
    requires_followup = False
    disposition = "reconciled" if not issues else "reconciliation_failed"

    if target_key is not None:
        pre_target_qty = _position_qty_for_key(pre_positions.get("records") or [], target_key)
        post_target_qty = _position_qty_for_key(post_positions.get("records") or [], target_key)
        target_position_delta = post_target_qty - pre_target_qty
        fill_volume = int((lifecycle_verdict or {}).get("fill_volume") or 0)
        lifecycle_disposition = str((lifecycle_verdict or {}).get("disposition") or "").lower()
        expected_position_delta = _expected_position_delta_for_intent(intent_contract, fill_volume)

        if lifecycle_disposition == "filled":
            if target_position_delta != expected_position_delta:
                issues.append("position_delta_mismatch")
                disposition = "reconciliation_failed"
            elif not issues:
                disposition = "filled_reconciled"
        elif lifecycle_disposition in {"rejected", "cancelled", "canceled", "dry_run_preflight"}:
            if target_position_delta != 0:
                issues.append("unexpected_position_delta")
                disposition = "reconciliation_failed"
            elif not issues:
                disposition = f"{lifecycle_disposition}_reconciled"
        elif lifecycle_disposition == "timeout":
            requires_followup = True
            if target_position_delta == 0 and not issues:
                disposition = "timeout_no_delta"
            elif not issues:
                disposition = "timeout_with_delta"
        elif lifecycle_disposition == "accepted":
            requires_followup = True
            if target_position_delta != expected_position_delta:
                issues.append("position_delta_mismatch")
                disposition = "reconciliation_failed"
            elif target_position_delta == 0 and not issues:
                disposition = "accepted_pending_no_delta"
            elif not issues:
                disposition = "accepted_pending_with_delta"

    return {
        "accepted": not issues,
        "disposition": disposition if not issues else "reconciliation_failed",
        "position_count_before": pre_count,
        "position_count_after": post_count,
        "position_count_delta": post_count - pre_count,
        "target_position_key": None
        if target_key is None
        else {"venue_symbol": target_key[0], "direction": target_key[1]},
        "target_position_delta": target_position_delta,
        "expected_position_delta": expected_position_delta,
        "requires_followup": requires_followup,
        "issues": issues,
    }


def _target_position_key_for_intent(intent_contract: dict[str, Any] | None) -> tuple[str, str] | None:
    if not intent_contract:
        return None
    instrument = str(intent_contract.get("instrument") or "").strip()
    side = str(intent_contract.get("side") or "").strip().upper()
    position_effect = str(intent_contract.get("position_effect") or "").strip().upper()
    if not instrument or not side:
        return None
    if position_effect == "OPEN":
        direction = "LONG" if side == "BUY" else "SHORT" if side == "SELL" else ""
    elif position_effect in {"CLOSE", "CLOSETODAY", "CLOSEYESTERDAY"}:
        direction = "SHORT" if side == "BUY" else "LONG" if side == "SELL" else ""
    else:
        direction = ""
    if not direction:
        return None
    return (instrument, direction)


def _position_qty_for_key(records: list[dict[str, Any]], key: tuple[str, str]) -> int:
    instrument, direction = key
    for record in records:
        if str(record.get("venue_symbol") or "").strip() != instrument:
            continue
        if str(record.get("direction") or "").strip().upper() != direction:
            continue
        return int(record.get("position_qty") or 0)
    return 0


def _expected_position_delta_for_intent(intent_contract: dict[str, Any], fill_volume: int) -> int:
    position_effect = str(intent_contract.get("position_effect") or "").strip().upper()
    if position_effect == "OPEN":
        return fill_volume
    if position_effect in {"CLOSE", "CLOSETODAY", "CLOSEYESTERDAY"}:
        return -fill_volume
    return 0


def run_guarded_paper_order(
    *,
    config_path: Path,
    pre_snapshot: Path,
    instrument: str,
    side: str,
    quantity: int,
    limit_price: float,
    position_effect: str = "OPEN",
    order_type: str = "LIMIT",
    time_in_force: str = "GFD",
    client_order_id: str,
    arm_paper_send: bool,
    timeout_seconds: int,
    post_snapshot: Path | None = None,
    close_from_pre_snapshot: bool = False,
    expected_pre_snapshot_run_id: str | None = None,
    close_position_direction: str | None = None,
    submit_count_last_minute: int = 0,
    session_send_count: int = 0,
    session_send_budget: int = 0,
    seen_client_order_ids: list[str] | None = None,
) -> dict[str, Any]:
    pre_snapshot_verdict = validate_pre_order_snapshot(pre_snapshot)
    close_intent: dict[str, Any] | None = None
    order_boundary: dict[str, Any] | None = None
    pre_payload: dict[str, Any] | None = None
    normalized_side = side.strip().upper()
    normalized_position_effect = position_effect.strip().upper()
    if pre_snapshot_verdict["accepted"]:
        try:
            pre_payload = json.loads(pre_snapshot.read_text(encoding="utf-8"))
        except Exception as exc:
            order_boundary = {
                "accepted": False,
                "disposition": "order_boundary_failed",
                "issues": [type(exc).__name__],
                "instrument": None,
                "limit_boundary": {"source": "not_available", "status": "unknown"},
            }
    if close_from_pre_snapshot and pre_snapshot_verdict["accepted"] and pre_payload is not None:
        try:
            close_intent = build_close_intent_from_snapshot(
                pre_payload,
                instrument=instrument,
                quantity=quantity,
                requested_position_effect=normalized_position_effect,
                limit_price=limit_price,
                client_order_id=client_order_id,
                expected_run_id=expected_pre_snapshot_run_id,
                direction=close_position_direction,
            )
        except Exception as exc:
            close_intent = {
                "accepted": False,
                "disposition": "close_intent_failed",
                "candidate": None,
                "selected_bucket": None,
                "submit_intent": None,
                "issues": [type(exc).__name__],
            }
        if close_intent["accepted"]:
            submit_intent = close_intent["submit_intent"]
            normalized_side = submit_intent["side"]
            normalized_position_effect = submit_intent["position_effect"]
    if pre_snapshot_verdict["accepted"] and order_boundary is None and pre_payload is not None:
        order_boundary = validate_order_boundary_from_snapshot(
            pre_payload,
            instrument=instrument,
            quantity=quantity,
            limit_price=limit_price,
        )
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "account_profile": OPENCTP_TTS_7X24_PROFILE,
        "evidence_class": OPENCTP_TTS_7X24_EVIDENCE_CLASS,
        "success": False,
        "status": "blocked",
        "failure_reason": None,
        "blocker_type": None,
        "action_mode": "paper_send" if arm_paper_send else "dry_run",
        "paper_send_armed": arm_paper_send,
        "pre_snapshot": pre_snapshot_verdict,
        "close_intent": close_intent,
        "order_boundary": order_boundary,
        "risk_preflight": None,
        "intent_contract": build_intent_contract(
            instrument=instrument,
            side=normalized_side,
            quantity=quantity,
            limit_price=limit_price,
            position_effect=normalized_position_effect,
            order_type=order_type,
            time_in_force=time_in_force,
            price_mode="snapshot_close" if close_from_pre_snapshot else "best_level_1",
            client_order_id=client_order_id,
        ),
        "order_contract": None,
        "mapped_submit": None,
        "order_lifecycle": None,
        "post_snapshot": None,
        "reconciliation": None,
        "issues": [],
    }
    if not pre_snapshot_verdict["accepted"]:
        payload["failure_reason"] = "pre_snapshot_rejected"
        payload["blocker_type"] = "paper-safety"
        payload["issues"] = list(pre_snapshot_verdict["issues"])
        return payload
    if close_from_pre_snapshot and (close_intent is None or not close_intent["accepted"]):
        payload["failure_reason"] = "close_intent_rejected"
        payload["blocker_type"] = "paper-safety"
        payload["issues"] = ["close_intent_missing"] if close_intent is None else list(close_intent["issues"])
        return payload
    if order_boundary is not None and not order_boundary["accepted"]:
        payload["failure_reason"] = "order_boundary_rejected"
        payload["blocker_type"] = "paper-safety"
        payload["issues"] = list(order_boundary["issues"])
        return payload

    config = CtpAdapterConfig.from_json_file(config_path)
    if pre_payload is not None:
        risk_preflight = build_risk_preflight_from_snapshot(
            pre_payload,
            config=config,
            instrument=instrument,
            side=normalized_side,
            quantity=quantity,
            position_effect=normalized_position_effect,
            client_order_id=client_order_id,
            arm_paper_send=arm_paper_send,
            submit_count_last_minute=submit_count_last_minute,
            session_send_count=session_send_count,
            session_send_budget=session_send_budget,
            seen_client_order_ids=seen_client_order_ids,
        )
        payload["risk_preflight"] = risk_preflight
        if not risk_preflight["accepted"]:
            payload["failure_reason"] = "risk_preflight_rejected"
            payload["blocker_type"] = "paper-safety"
            payload["issues"] = list(risk_preflight["issues"])
            return payload

    config_issues = paper_config_issues(config, allow_live_order_smoke=arm_paper_send)
    if config_issues:
        payload["failure_reason"] = "config_validation_failed"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = config_issues
        return payload

    try:
        stack = build_ctp_stack(config)
        execution_client = stack["execution_client"]
        runtime_bridge = stack["runtime_bridge"]
        result = execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id=instrument,
            side=normalized_side,
            quantity=quantity,
            limit_price=limit_price,
            position_effect=normalized_position_effect,
            client_order_id=client_order_id,
            timeout_seconds=timeout_seconds,
            dry_run=not arm_paper_send,
            time_in_force=time_in_force,
            order_type=order_type,
        )
        commands = runtime_bridge.drain_submitted_commands()
        events = runtime_bridge.drain_events()
    except Exception as exc:
        payload["failure_reason"] = "paper_order_exception"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = [type(exc).__name__]
        payload["exception"] = {"type": type(exc).__name__, "message": str(exc)}
        return payload

    payload["mapped_submit"] = {
        "error": None
        if result.mapped_submit.error is None
        else {
            "error_id": result.mapped_submit.error.error_id,
            "error_message": result.mapped_submit.error.error_message,
        },
        "client_order_id": result.mapped_submit.client_order_id,
        "order_ref": result.mapped_submit.order_ref,
        "front_id": result.mapped_submit.front_id,
        "session_id": result.mapped_submit.session_id,
        "order_ref_present": result.mapped_submit.order_ref is not None,
        "front_id_present": result.mapped_submit.front_id is not None,
        "session_id_present": result.mapped_submit.session_id is not None,
        "command_kind": None if result.mapped_submit.command is None else result.mapped_submit.command.kind.value,
    }
    payload["order_contract"] = validate_order_command_contract(
        payload["intent_contract"],
        result.mapped_submit.command,
    )
    lifecycle_events = [
        {
            "kind": event.kind.value,
            "client_order_id": event.client_order_id,
            "venue_symbol": event.venue_symbol,
            "native_order_id": event.payload.get("native_order_id") or event.payload.get("order_id"),
            "native_order_ref": event.payload.get("native_order_ref") or event.payload.get("order_ref"),
            "native_trade_id": event.payload.get("trade_id") or event.payload.get("order_id"),
            "trade_volume": event.payload.get("trade_volume", 0),
            "trade_price": event.payload.get("trade_price", 0),
            "leaves_qty": event.payload.get("leaves_qty", 0),
            "status": event.payload.get("status", ""),
            "payload_error_msg": event.payload.get("error_msg", ""),
            "error_message": event.message or "",
        }
        for event in events
        if event.kind.value in {"order", "trade"}
    ]
    lifecycle_verdict = classify_lifecycle_events(payload["intent_contract"], lifecycle_events)
    if not arm_paper_send and lifecycle_verdict["disposition"] == "timeout":
        lifecycle_verdict = {
            **lifecycle_verdict,
            "accepted": True,
            "disposition": "dry_run_preflight",
        }
    payload["order_lifecycle"] = {
        "dry_run": result.dry_run,
        "live_send_armed": result.live_send_armed,
        "bootstrap_ready": result.bootstrap.ready,
        "matched_exec_count": 0 if not result.matched_execs else len(result.matched_execs),
        "command_kinds": [command.kind.value for command in commands],
        "event_kinds": [event.kind.value for event in events],
        "lifecycle_events": lifecycle_events,
        "verdict": lifecycle_verdict,
    }
    if post_snapshot is not None:
        post_snapshot_verdict = validate_pre_order_snapshot(post_snapshot)
        payload["post_snapshot"] = post_snapshot_verdict
        if post_snapshot_verdict["accepted"]:
            try:
                pre_payload = json.loads(pre_snapshot.read_text(encoding="utf-8"))
                post_payload = json.loads(post_snapshot.read_text(encoding="utf-8"))
                payload["reconciliation"] = reconcile_pre_post_snapshots(
                    pre_payload,
                    post_payload,
                    intent_contract=payload["intent_contract"],
                    lifecycle_verdict=lifecycle_verdict,
                )
            except Exception as exc:
                payload["reconciliation"] = {
                    "accepted": False,
                    "disposition": "reconciliation_failed",
                    "issues": [type(exc).__name__],
                }
        else:
            payload["reconciliation"] = {
                "accepted": False,
                "disposition": "post_snapshot_rejected",
                "issues": list(post_snapshot_verdict["issues"]),
            }
    success = (
        result.bootstrap.ready
        and result.mapped_submit.error is None
        and result.mapped_submit.command is not None
        and payload["order_contract"]["accepted"]
        and lifecycle_verdict["accepted"]
    )
    if payload["reconciliation"] is not None:
        success = success and payload["reconciliation"]["accepted"]
    if not arm_paper_send:
        success = success and result.dry_run and result.live_send_armed is False
    else:
        success = success and result.live_send_armed
    payload["success"] = success
    payload["status"] = "passed" if success else "blocked"
    payload["failure_reason"] = None if success else "order_lifecycle_not_ready"
    payload["blocker_type"] = None if success else "paper-resource"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run guarded OpenCTP paper order preflight/dry-run loop.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--pre-snapshot", type=Path, required=True)
    parser.add_argument("--post-snapshot", type=Path)
    parser.add_argument("--instrument", default="TEST")
    parser.add_argument("--side", default="BUY")
    parser.add_argument("--quantity", type=int, default=1)
    parser.add_argument("--limit-price", type=float, required=True)
    parser.add_argument("--position-effect", default="OPEN")
    parser.add_argument("--order-type", default="LIMIT")
    parser.add_argument("--time-in-force", default="GFD")
    parser.add_argument("--client-order-id", default="paper-order-1")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--arm-paper-send", action="store_true")
    parser.add_argument("--close-from-pre-snapshot", action="store_true")
    parser.add_argument("--expected-pre-snapshot-run-id")
    parser.add_argument("--close-position-direction")
    parser.add_argument("--submit-count-last-minute", type=int, default=0)
    parser.add_argument("--session-send-count", type=int, default=0)
    parser.add_argument("--session-send-budget", type=int, default=0)
    parser.add_argument("--seen-client-order-id", action="append", default=[])
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    config_path = args.config if args.config.is_absolute() else REPO_ROOT / args.config
    payload = run_guarded_paper_order(
        config_path=config_path,
        pre_snapshot=args.pre_snapshot if args.pre_snapshot.is_absolute() else REPO_ROOT / args.pre_snapshot,
        instrument=args.instrument,
        side=args.side,
        quantity=args.quantity,
        limit_price=args.limit_price,
        position_effect=args.position_effect,
        order_type=args.order_type,
        time_in_force=args.time_in_force,
        client_order_id=args.client_order_id,
        arm_paper_send=args.arm_paper_send,
        timeout_seconds=args.timeout_seconds,
        close_from_pre_snapshot=args.close_from_pre_snapshot,
        expected_pre_snapshot_run_id=args.expected_pre_snapshot_run_id,
        close_position_direction=args.close_position_direction,
        submit_count_last_minute=args.submit_count_last_minute,
        session_send_count=args.session_send_count,
        session_send_budget=args.session_send_budget,
        seen_client_order_ids=args.seen_client_order_id,
        post_snapshot=None
        if args.post_snapshot is None
        else args.post_snapshot
        if args.post_snapshot.is_absolute()
        else REPO_ROOT / args.post_snapshot,
    )
    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        write_json_payload(path=output_path, payload=payload)
    emit_json_stdout(payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
