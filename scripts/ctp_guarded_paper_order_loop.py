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
from nautilus_ctp_adapter.diagnostics.guarded_paper_order import (
    build_callback_source_observability,
    finalize_order_lifecycle_payload,
)
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


def build_position_detail_semantics(
    snapshot_payload: dict[str, Any],
    *,
    instrument: str,
    direction: str | None = None,
) -> dict[str, Any]:
    records = ((snapshot_payload.get("positions") or {}).get("records") or [])
    instrument_records = ((snapshot_payload.get("instruments") or {}).get("records") or [])
    instrument_exchange = next(
        (
            record.get("exchange_id")
            for record in instrument_records
            if str(record.get("venue_symbol", "")).strip() == instrument
        ),
        None,
    )
    normalized_direction = "" if direction is None else direction.strip().upper()
    matching_records = [
        record
        for record in records
        if str(record.get("venue_symbol", "")).strip() == instrument
        and (
            not normalized_direction
            or str(record.get("direction", "")).strip().upper() == normalized_direction
        )
    ]
    issues: list[str] = []
    if not matching_records:
        issues.append("no_matching_position")
    if matching_records and not any(record.get("exchange_id") for record in matching_records):
        issues.append("position_exchange_id_missing")
    if matching_records and not any("date_type" in record or "position_date" in record for record in matching_records):
        issues.append("raw_position_date_type_missing")
    if matching_records and not any("hedge_flag" in record for record in matching_records):
        issues.append("raw_position_hedge_flag_missing")
    if instrument_exchange is None:
        issues.append("instrument_exchange_id_missing")

    return {
        "instrument": instrument,
        "direction_filter": normalized_direction or None,
        "matching_position_count": len(matching_records),
        "position_exchange_ids": sorted(
            {
                str(record.get("exchange_id")).strip()
                for record in matching_records
                if record.get("exchange_id")
            }
        ),
        "instrument_exchange_id": instrument_exchange,
        "position_buckets": [
            {
                "direction": record.get("direction"),
                "position_qty": record.get("position_qty"),
                "td_position_qty": record.get("td_position_qty"),
                "yd_position_qty": record.get("yd_position_qty"),
            }
            for record in matching_records
        ],
        "issues": issues,
        "disposition": (
            "position_detail_gap_requires_owner_resolution"
            if issues
            else "position_detail_sufficient_for_current_close_diagnostic"
        ),
        "acceptance_implication": "diagnostic_only_not_position_or_fill_truth",
        "fill_producing_acceptance_satisfied": False,
        "requires_owner_resolution_before_retry": bool(issues),
        "writes_truth": False,
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
    detail_fields = instrument_record.get("detail_fields") or {}
    if price_tick in {None, 0}:
        issues.append("price_tick_missing")
    if volume_multiple in {None, 0}:
        issues.append("volume_multiple_missing")
    if detail_fields.get("is_trading") is False:
        issues.append("instrument_not_tradable")
    open_date = detail_fields.get("open_date")
    expire_date = detail_fields.get("expire_date")
    if open_date and not _looks_like_yyyymmdd(str(open_date)):
        issues.append("open_date_invalid")
    if expire_date and not _looks_like_yyyymmdd(str(expire_date)):
        issues.append("expire_date_invalid")
    min_limit_order_volume = _optional_int(detail_fields.get("min_limit_order_volume"))
    max_limit_order_volume = _optional_int(detail_fields.get("max_limit_order_volume"))
    if min_limit_order_volume is not None and quantity < min_limit_order_volume:
        issues.append("min_limit_order_volume_violated")
    if max_limit_order_volume is not None and quantity > max_limit_order_volume:
        issues.append("max_limit_order_volume_violated")
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
            "detail_fields": detail_fields,
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

    instrument_record = _instrument_record_from_snapshot(snapshot_payload, instrument)
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
        "instrument": {
            "venue_symbol": instrument,
            "detail_fields": {} if instrument_record is None else dict(instrument_record.get("detail_fields") or {}),
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
    current_net_position = facts["positions"]["net_position"]
    projected_net_position = facts["positions"]["net_position"] + _net_delta(
        side=normalized_side,
        position_effect=normalized_effect,
        quantity=quantity,
    )
    exposure_reduces_net_position = _is_exposure_reduction(
        current_net_position=current_net_position,
        projected_net_position=projected_net_position,
        position_effect=normalized_effect,
    )
    exposure_reduction_override = (
        arm_paper_send
        and not guardrails.allow_live_order_smoke
        and guardrails.allow_exposure_reduction_order_smoke
        and exposure_reduces_net_position
    )
    seen_ids = {str(item) for item in (seen_client_order_ids or [])}
    issues: list[str] = []
    guards: dict[str, dict[str, Any]] = {}

    def _record_guard(name: str, accepted: bool, issue: str | None = None, **extra: Any) -> None:
        if issue and not accepted:
            issues.append(issue)
        guards[name] = {"accepted": accepted, **extra}

    account = facts["account"]
    instrument_facts = facts["instrument"].get("detail_fields") or {}
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
        "instrument_trading_status",
        instrument_facts.get("is_trading") is not False,
        "instrument_not_tradable",
        is_trading=instrument_facts.get("is_trading"),
    )
    _record_guard(
        "kill_switch",
        not (
            arm_paper_send
            and not guardrails.allow_live_order_smoke
            and not exposure_reduction_override
        ),
        "kill_switch_closed",
        armed=arm_paper_send,
        allow_live_order_smoke=guardrails.allow_live_order_smoke,
        allow_exposure_reduction_order_smoke=(
            guardrails.allow_exposure_reduction_order_smoke
        ),
        exposure_reduction_override=exposure_reduction_override,
        exposure_reduces_net_position=exposure_reduces_net_position,
        current_net_position=current_net_position,
        projected_net_position=projected_net_position,
        position_effect=normalized_effect,
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
        "verified_exposure_reduction": exposure_reduction_override,
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


def _is_exposure_reduction(
    *,
    current_net_position: int,
    projected_net_position: int,
    position_effect: str,
) -> bool:
    return (
        position_effect in {"CLOSE", "CLOSETODAY", "CLOSEYESTERDAY"}
        and current_net_position != 0
        and abs(projected_net_position) < abs(current_net_position)
    )


def _instrument_record_from_snapshot(snapshot_payload: dict[str, Any], instrument: str) -> dict[str, Any] | None:
    for record in ((snapshot_payload.get("instruments") or {}).get("records") or []):
        if str(record.get("venue_symbol", "")).strip() == instrument:
            return record
    return None


def _optional_int(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    return int(value)


def _looks_like_yyyymmdd(value: str) -> bool:
    text = str(value or "").strip()
    return len(text) == 8 and text.isdigit()


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


def build_native_offset_semantics(
    *,
    intent_contract: dict[str, Any],
    command_payload: dict[str, Any],
    lifecycle_events: list[dict[str, Any]],
) -> dict[str, Any]:
    callback_sources = sorted(
        {
            str(event.get("callback_source", "")).strip()
            for event in lifecycle_events
            if str(event.get("callback_source", "")).strip()
        }
    )
    callback_offset_flags = [
        str(event.get("offset_flag", "")).strip()
        for event in lifecycle_events
        if str(event.get("offset_flag", "")).strip()
    ]
    submit_boundary_offset_flags = [
        str(event.get("submit_request_offset_flag", "")).strip()
        for event in lifecycle_events
        if str(event.get("submit_request_offset_flag", "")).strip()
        and str(event.get("submit_request_offset_flag", "")).strip() != "-1"
    ]
    submit_boundary_offset_sources = sorted(
        {
            str(event.get("submit_request_offset_source", "")).strip()
            for event in lifecycle_events
            if str(event.get("submit_request_offset_source", "")).strip()
        }
    )
    native_comb_offset = str(command_payload.get("native_comb_offset", "")).strip()
    callback_unique = sorted(set(callback_offset_flags))
    submit_boundary_unique = sorted(set(submit_boundary_offset_flags))
    comparison_possible = bool(native_comb_offset and callback_unique)
    submit_boundary_matches_command = (
        all(flag == native_comb_offset for flag in submit_boundary_offset_flags)
        if native_comb_offset and submit_boundary_offset_flags
        else None
    )
    callback_matches_submit = (
        all(flag == native_comb_offset for flag in callback_offset_flags)
        if comparison_possible
        else None
    )
    disposition = (
        "callback_offset_matches_submit_native_comb_offset"
        if comparison_possible and callback_matches_submit
        else "order_insert_response_offset_differs_from_submit_native_comb_offset"
        if comparison_possible
        and not callback_matches_submit
        and "OnRspOrderInsert" in callback_sources
        else "callback_offset_differs_from_submit_native_comb_offset"
        if comparison_possible
        else "insufficient_native_offset_observation"
    )
    order_insert_response_offset_mismatch = (
        disposition
        == "order_insert_response_offset_differs_from_submit_native_comb_offset"
    )
    callback_offset_authority = (
        "front_response_diagnostic"
        if "OnRspOrderInsert" in callback_sources
        else "order_status_diagnostic"
        if "OnRtnOrder" in callback_sources
        else "trade_fill_diagnostic"
        if "OnRtnTrade" in callback_sources
        else None
    )
    return {
        "position_effect": intent_contract["position_effect"],
        "submit_native_comb_offset": native_comb_offset or None,
        "submit_offset_authority": "submit_request_provenance"
        if native_comb_offset
        else None,
        "submit_native_offset_source_field": (
            "CtpExecutionClient._native_comb_offset_value(position_effect)"
            " -> TdOrderSend.comb_offset"
            " -> CThostFtdcInputOrderField.CombOffsetFlag[0]"
            if native_comb_offset
            else None
        ),
        "submit_native_offset_expected_from_position_effect": {
            "OPEN": "0",
            "CLOSE": "1",
            "CLOSETODAY": "3",
            "CLOSEYESTERDAY": "4",
        }.get(str(intent_contract["position_effect"]).strip().upper()),
        "native_submit_boundary_offset_flags": submit_boundary_unique,
        "native_submit_boundary_offset_source": (
            submit_boundary_offset_sources[0]
            if len(submit_boundary_offset_sources) == 1
            else submit_boundary_offset_sources
            if submit_boundary_offset_sources
            else None
        ),
        "native_submit_boundary_matches_command_payload": submit_boundary_matches_command,
        "callback_offset_flags": callback_unique,
        "callback_sources": callback_sources,
        "callback_offset_source_field": (
            "CThostFtdcInputOrderField.CombOffsetFlag[0]"
            if "OnRspOrderInsert" in callback_sources
            else "CThostFtdcOrderField.CombOffsetFlag[0]"
            if "OnRtnOrder" in callback_sources
            else "CThostFtdcTradeField.OffsetFlag"
            if "OnRtnTrade" in callback_sources
            else None
        ),
        "callback_offset_authority": callback_offset_authority,
        "callback_offset_rewrites_submit_truth": False,
        "order_insert_response_offset_mismatch": order_insert_response_offset_mismatch,
        "callback_matches_submit_native_comb_offset": callback_matches_submit,
        "disposition": disposition,
        "acceptance_implication": "diagnostic_only_not_fill_or_closeout_truth",
        "fill_producing_acceptance_satisfied": False,
        "requires_owner_resolution_before_retry": disposition
        != "callback_offset_matches_submit_native_comb_offset",
        "writes_truth": False,
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
    observed_statuses: set[str] = set()
    error_text_seen = False
    error_text_contains_replacement_char = False

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
        fallback_error_message = str(_event_value(event, "error_message", "") or "")
        combined_error_text = f"{error_message}{fallback_error_message}"
        if combined_error_text:
            error_text_seen = True
        if "\ufffd" in combined_error_text:
            error_text_contains_replacement_char = True
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
        if combined_error_text:
            rejected = True
        status = str(_event_value(event, "status", "") or "").lower()
        if status:
            observed_statuses.add(status)
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
        "native_status_diagnostics": build_native_status_diagnostics(
            observed_statuses=observed_statuses,
            fill_volume=fill_volume,
            cancelled=cancelled,
            error_text_seen=error_text_seen,
            error_text_contains_replacement_char=error_text_contains_replacement_char,
        ),
        "issues": sorted(set(issues)),
    }


def build_native_status_diagnostics(
    *,
    observed_statuses: set[str],
    fill_volume: int,
    cancelled: bool,
    error_text_seen: bool,
    error_text_contains_replacement_char: bool,
) -> dict[str, Any]:
    normalized = sorted(str(status).strip().lower() for status in observed_statuses if str(status).strip())
    ctp_meanings: dict[str, str] = {}
    for status in normalized:
        if status == "53":
            ctp_meanings[status] = "ascii_code_53_for_ctp_order_status_char_5_cancelled"
        elif status == "5":
            ctp_meanings[status] = "ctp_order_status_char_5_cancelled"
        elif status in {"cancelled", "canceled"}:
            ctp_meanings[status] = "normalized_cancelled_text"
        else:
            ctp_meanings[status] = "unmapped_status"

    if cancelled and fill_volume == 0:
        disposition = "ctp_cancelled_status_without_fill"
    elif cancelled:
        disposition = "ctp_cancelled_status_with_fill_observed"
    elif normalized:
        disposition = "ctp_status_observed_not_cancelled"
    else:
        disposition = "no_native_status_observed"

    return {
        "observed_statuses": normalized,
        "ctp_status_meanings": ctp_meanings,
        "disposition": disposition,
        "semantic_reason": "undetermined_from_status_only",
        "error_text_seen": error_text_seen,
        "error_text_contains_replacement_char": error_text_contains_replacement_char,
        "broker_semantic_reason_inferred": False,
    }


def build_broker_rejection_semantics(
    *,
    intent_contract: dict[str, Any],
    lifecycle_events: list[dict[str, Any]],
    lifecycle_verdict: dict[str, Any],
    native_offset_semantics: dict[str, Any],
) -> dict[str, Any]:
    error_texts = [
        text
        for event in lifecycle_events
        for text in (
            str(event.get("payload_error_msg", "") or ""),
            str(event.get("error_message", "") or ""),
        )
        if text
    ]
    decoded_error_texts = [text for text in error_texts if "\ufffd" not in text]
    callback_sources = sorted(
        {
            str(event.get("callback_source", "") or "").strip()
            for event in lifecycle_events
            if str(event.get("callback_source", "") or "").strip()
        }
    )
    order_insert_response_identity = [
        {
            "response_request_id": str(event.get("response_request_id", "") or "").strip(),
            "response_is_last": str(event.get("response_is_last", "") or "").strip(),
            "response_error_id": str(event.get("response_error_id", "") or "").strip(),
        }
        for event in lifecycle_events
        if str(event.get("callback_source", "") or "").strip() == "OnRspOrderInsert"
    ]
    order_insert_response_identity_observed = any(
        item["response_request_id"] or item["response_is_last"] or item["response_error_id"]
        for item in order_insert_response_identity
    )
    order_insert_response_identity_authority = (
        "front_response_identity_fields"
        if order_insert_response_identity_observed
        else None
    )
    order_insert_submit_boundary_identity = [
        {
            "submit_request_id": str(event.get("submit_request_id", "") or "").strip(),
            "submit_request_id_source": str(event.get("submit_request_id_source", "") or "").strip(),
        }
        for event in lifecycle_events
        if str(event.get("callback_source", "") or "").strip() == "OnRspOrderInsert"
    ]
    order_insert_submit_boundary_identity_observed = any(
        item["submit_request_id"] and item["submit_request_id_source"]
        for item in order_insert_submit_boundary_identity
    )
    correlated_request_ids = [
        {
            "submit_request_id": submit_identity["submit_request_id"],
            "response_request_id": response_identity["response_request_id"],
        }
        for submit_identity, response_identity in zip(
            order_insert_submit_boundary_identity, order_insert_response_identity
        )
        if submit_identity["submit_request_id"]
        and response_identity["response_request_id"]
        and submit_identity["submit_request_id"] == response_identity["response_request_id"]
    ]
    order_insert_submit_boundary_correlation_observed = bool(correlated_request_ids)
    order_insert_submit_boundary_correlation_rule = (
        "submit_request_id_equals_onrsp_order_insert_response_request_id"
        if order_insert_submit_boundary_correlation_observed
        else None
    )
    insufficient_position = any("持仓不足" in text for text in decoded_error_texts)
    close_intent = intent_contract["position_effect"] in {
        "CLOSE",
        "CLOSETODAY",
        "CLOSEYESTERDAY",
    }
    zero_fill_rejection = (
        lifecycle_verdict.get("disposition") in {"cancelled", "rejected"}
        and int(lifecycle_verdict.get("fill_volume", 0) or 0) == 0
    )
    typed_blocker = close_intent and zero_fill_rejection and insufficient_position
    order_insert_rejection_source = "OnRspOrderInsert" in callback_sources
    if typed_blocker and order_insert_rejection_source:
        disposition = "source_bearing_order_insert_insufficient_position_close_rejection"
    elif typed_blocker:
        disposition = "decoded_broker_insufficient_position_close_rejection"
    else:
        disposition = "no_decoded_broker_close_position_rejection"
    next_adapter_native_semantic_repair_evidence: list[str] = []
    if order_insert_rejection_source and order_insert_response_identity_observed and typed_blocker:
        if order_insert_submit_boundary_correlation_observed:
            next_adapter_native_semantic_repair_evidence = [
                "primary_or_official_broker_front_close_rejection_rule_source",
                "new_formal_bounded_authorization_before_future_send",
            ]
        else:
            next_adapter_native_semantic_repair_evidence = [
                "submit_boundary_request_identity_field",
                "order_insert_response_identity_field",
                "submit_response_identity_correlation_rule",
            ]
    return {
        "disposition": disposition,
        "blocker_type": (
            "broker-or-adapter-close-position-semantics" if typed_blocker else None
        ),
        "decoded_error_texts": decoded_error_texts,
        "callback_sources": callback_sources,
        "order_insert_rejection_source": order_insert_rejection_source,
        "order_insert_response_identity": order_insert_response_identity,
        "order_insert_response_identity_observed": order_insert_response_identity_observed,
        "order_insert_response_identity_authority": order_insert_response_identity_authority,
        "order_insert_submit_boundary_identity": order_insert_submit_boundary_identity,
        "order_insert_submit_boundary_identity_observed": order_insert_submit_boundary_identity_observed,
        "order_insert_submit_boundary_correlation_observed": order_insert_submit_boundary_correlation_observed,
        "order_insert_submit_boundary_correlation_rule": order_insert_submit_boundary_correlation_rule,
        "order_insert_submit_boundary_correlated_request_ids": correlated_request_ids,
        "order_insert_submit_boundary_correlation_required": (
            order_insert_rejection_source
            and order_insert_response_identity_observed
            and typed_blocker
            and not order_insert_submit_boundary_correlation_observed
        ),
        "insufficient_position_text_observed": insufficient_position,
        "close_intent": close_intent,
        "zero_fill_rejection": zero_fill_rejection,
        "native_offset_disposition": native_offset_semantics.get("disposition"),
        "semantic_scope": (
            "order_insert_rejection_before_fill_not_trade_or_closeout_truth"
            if order_insert_rejection_source
            else "decoded_rejection_without_callback_source_scope"
            if typed_blocker
            else "no_close_rejection_scope"
        ),
        "acceptance_implication": "typed_blocker_only_not_fill_or_closeout_truth",
        "stronger_adapter_native_semantic_repair_candidate": (
            order_insert_rejection_source
            and order_insert_response_identity_observed
            and order_insert_submit_boundary_correlation_observed
            and typed_blocker
        ),
        "next_adapter_native_semantic_repair_evidence": next_adapter_native_semantic_repair_evidence,
        "fill_producing_acceptance_satisfied": False,
        "requires_owner_resolution_before_retry": typed_blocker,
        "writes_truth": False,
    }


def build_close_rejection_diagnostic_semantics(
    *,
    intent_contract: dict[str, Any],
    position_detail_semantics: dict[str, Any],
    native_offset_semantics: dict[str, Any],
    broker_rejection_semantics: dict[str, Any],
) -> dict[str, Any]:
    """Narrow a decoded close rejection after native position details are present."""
    position_detail_sufficient = (
        position_detail_semantics.get("disposition")
        == "position_detail_sufficient_for_current_close_diagnostic"
    )
    decoded_insufficient_position_close = (
        broker_rejection_semantics.get("disposition")
        == "decoded_broker_insufficient_position_close_rejection"
    )
    source_bearing_order_insert_close = (
        broker_rejection_semantics.get("disposition")
        == "source_bearing_order_insert_insufficient_position_close_rejection"
    )
    close_today_intent = str(intent_contract.get("position_effect", "")).upper() == "CLOSETODAY"
    native_offset_mismatch = (
        native_offset_semantics.get("disposition")
        in {
            "callback_offset_differs_from_submit_native_comb_offset",
            "order_insert_response_offset_differs_from_submit_native_comb_offset",
        }
    )
    typed_blocker = (
        position_detail_sufficient
        and (decoded_insufficient_position_close or source_bearing_order_insert_close)
        and close_today_intent
    )
    if typed_blocker and source_bearing_order_insert_close and native_offset_mismatch:
        disposition = (
            "sufficient_position_detail_but_order_insert_rejected_close_with_callback_offset_mismatch"
        )
    elif typed_blocker and source_bearing_order_insert_close:
        disposition = "sufficient_position_detail_but_order_insert_rejected_close"
    elif typed_blocker and native_offset_mismatch:
        disposition = "sufficient_position_detail_but_callback_offset_mismatch_and_broker_rejected_close"
    elif typed_blocker:
        disposition = "sufficient_position_detail_but_broker_rejected_close"
    else:
        disposition = "close_rejection_semantics_not_narrowed"

    return {
        "disposition": disposition,
        "blocker_type": (
            "broker-or-adapter-close-position-semantics" if typed_blocker else None
        ),
        "position_detail_sufficient": position_detail_sufficient,
        "decoded_insufficient_position_close_rejection": decoded_insufficient_position_close,
        "source_bearing_order_insert_close_rejection": source_bearing_order_insert_close,
        "close_today_intent": close_today_intent,
        "native_offset_disposition": native_offset_semantics.get("disposition"),
        "diagnostic_conclusion": (
            "order_insert_rejection_source_observed_close_semantics_still_unresolved"
            if typed_blocker and source_bearing_order_insert_close
            else
            "position_detail_gap_ruled_out_close_semantics_still_unresolved"
            if typed_blocker
            else "insufficient_evidence_to_rule_out_position_detail_gap"
        ),
        "ruled_out_gaps": (
            [
                "position_exchange_id_missing",
                "raw_position_date_type_missing",
                "raw_position_hedge_flag_missing",
                "td_bucket_missing",
            ]
            if position_detail_sufficient
            else []
        ),
        "next_required_evidence": (
            [
                "broker_or_exchange_close_offset_rule_tied_to_OnRspOrderInsert_fields",
                "primary_broker_front_close_rejection_rule_source",
                "adapter_offset_or_position_rule_repair_for_source_bearing_close_rejection",
                "adapter_native_repair_beyond_local_diagnostics",
                "new_formal_retry_authorization_before_any_future_send",
            ]
            if typed_blocker and source_bearing_order_insert_close
            else
            [
                "native_callback_source_or_order_insert_rejection_source",
                "broker_or_exchange_close_offset_rule_tied_to_callback_fields",
                "primary_broker_front_close_rejection_rule_source",
                "new_formal_retry_authorization_before_any_future_send",
            ]
            if typed_blocker
            else ["fresh_position_detail_and_decoded_lifecycle_callback"]
        ),
        "primary_rule_source_required": typed_blocker,
        "local_diagnostics_sufficient_to_close": False,
        "acceptance_implication": "typed_blocker_only_not_fill_or_closeout_truth",
        "fill_producing_acceptance_satisfied": False,
        "requires_owner_resolution_before_retry": typed_blocker,
        "writes_truth": False,
    }


def build_close_offset_owner_rule_semantics(
    *,
    intent_contract: dict[str, Any],
    position_detail_semantics: dict[str, Any],
    native_offset_semantics: dict[str, Any],
    broker_rejection_semantics: dict[str, Any],
) -> dict[str, Any]:
    """Lock the owner rule for source-bearing close-offset rejection diagnostics."""
    position_effect = str(intent_contract.get("position_effect", "")).strip().upper()
    submit_offset = native_offset_semantics.get("submit_native_comb_offset")
    expected_offset = native_offset_semantics.get(
        "submit_native_offset_expected_from_position_effect"
    )
    callback_offsets = list(native_offset_semantics.get("callback_offset_flags") or [])
    callback_sources = list(native_offset_semantics.get("callback_sources") or [])
    submit_boundary_matches = (
        native_offset_semantics.get("native_submit_boundary_matches_command_payload")
        is True
    )
    order_insert_response_mismatch = (
        native_offset_semantics.get("order_insert_response_offset_mismatch") is True
    )
    source_bearing_rejection = (
        broker_rejection_semantics.get("disposition")
        == "source_bearing_order_insert_insufficient_position_close_rejection"
    )
    response_identity_observed = (
        broker_rejection_semantics.get("order_insert_response_identity_observed") is True
    )
    position_detail_sufficient = (
        position_detail_semantics.get("disposition")
        == "position_detail_sufficient_for_current_close_diagnostic"
    )
    close_offset_submit_observed = submit_boundary_matches and (
        (
            position_effect == "CLOSETODAY"
            and expected_offset == "3"
            and submit_offset == "3"
        )
        or (
            position_effect == "CLOSEYESTERDAY"
            and expected_offset == "4"
            and submit_offset == "4"
        )
    )
    callback_is_rejection_diagnostic_only = (
        close_offset_submit_observed
        and order_insert_response_mismatch
        and source_bearing_rejection
        and "OnRspOrderInsert" in callback_sources
    )
    blocks_auto_downgrade = (
        callback_is_rejection_diagnostic_only and position_detail_sufficient
    )
    return {
        "disposition": (
            "owner_rule_blocks_callback_offset_as_submit_truth"
            if blocks_auto_downgrade
            else "owner_rule_not_applicable"
        ),
        "blocker_type": (
            "broker-or-adapter-close-position-semantics"
            if blocks_auto_downgrade
            else None
        ),
        "position_effect": position_effect,
        "expected_submit_offset_from_position_effect": expected_offset,
        "observed_submit_boundary_offset": submit_offset,
        "callback_offset_flags": callback_offsets,
        "callback_sources": callback_sources,
        "order_insert_response_identity_observed": response_identity_observed,
        "order_insert_response_identity": broker_rejection_semantics.get(
            "order_insert_response_identity", []
        ),
        "position_detail_sufficient": position_detail_sufficient,
        "submit_boundary_matches_command_payload": submit_boundary_matches,
        "callback_is_rejection_diagnostic_only": callback_is_rejection_diagnostic_only,
        "auto_downgrade_to_generic_close_allowed": False,
        "rule": (
            "OnRspOrderInsert offset fields on a zero-fill insufficient-position "
            "close rejection are diagnostic response fields only. They must not "
            "rewrite close-offset submit-boundary provenance or silently change "
            "a future CLOSETODAY or CLOSEYESTERDAY request into CLOSE."
        ),
        "next_required_evidence": (
            [
                "broker_or_exchange_close_offset_rule_independent_of_rejected_callback_echo",
                "primary_broker_front_close_rejection_rule_source",
                "adapter_native_repair_beyond_local_diagnostics",
                "primary_broker_front_close_rejection_rule_source_or_stronger_adapter_native_semantic_repair",
                "new_formal_retry_authorization_before_any_future_send",
            ]
            if blocks_auto_downgrade
            else []
        ),
        "primary_rule_source_required": blocks_auto_downgrade,
        "local_diagnostics_sufficient_to_close": False,
        "acceptance_implication": "typed_blocker_only_not_fill_or_closeout_truth",
        "fill_producing_acceptance_satisfied": False,
        "requires_owner_resolution_before_retry": blocks_auto_downgrade,
        "writes_truth": False,
    }


def build_source_exhaustion_semantics(
    *,
    broker_rejection_semantics: dict[str, Any],
    close_offset_owner_rule_semantics: dict[str, Any],
) -> dict[str, Any]:
    """Make local-source exhaustion an explicit guarded verdict."""
    close_rule_blocked = (
        close_offset_owner_rule_semantics.get("requires_owner_resolution_before_retry")
        is True
    )
    primary_rule_required = (
        close_offset_owner_rule_semantics.get("primary_rule_source_required") is True
    )
    local_diagnostics_sufficient = (
        close_offset_owner_rule_semantics.get("local_diagnostics_sufficient_to_close")
        is True
    )
    response_identity_observed = (
        broker_rejection_semantics.get("order_insert_response_identity_observed") is True
    )
    source_bearing_rejection = (
        broker_rejection_semantics.get("disposition")
        == "source_bearing_order_insert_insufficient_position_close_rejection"
    )
    typed_blocker = (
        close_rule_blocked
        and primary_rule_required
        and not local_diagnostics_sufficient
        and source_bearing_rejection
    )
    stronger_repair_present = (
        broker_rejection_semantics.get("stronger_adapter_native_semantic_repair_candidate")
        is True
    )
    return {
        "disposition": (
            "adapter_native_repair_observed_formal_authorization_required"
            if typed_blocker and stronger_repair_present
            else
            "local_owner_sources_exhausted_primary_rule_or_stronger_repair_required"
            if typed_blocker
            else "source_exhaustion_semantics_not_applicable"
        ),
        "blocker_type": (
            "formal-bounded-paper-authorization-missing-after-adapter-native-repair"
            if typed_blocker and stronger_repair_present
            else
            "primary-broker-front-close-rejection-rule-source-or-stronger-adapter-native-semantic-repair-missing"
            if typed_blocker
            else None
        ),
        "local_source_classes_evaluated": [
            "owner_code",
            "focused_tests",
            "prior_typed_artifacts",
            "local_vendor_constants",
            "native_response_identity_fields",
        ],
        "external_source_candidate_classes_evaluated": [
            "ctp_api_documentation_mirror",
            "ctp_client_development_guide_primary_candidate",
            "cffex_trader_api_pdf_candidate",
            "futures_broker_ctp_error_help_candidate",
        ],
        "external_source_candidate_evidence": (
            [
                {
                    "class": "ctp_api_documentation_mirror",
                    "authority": "documentation_mirror",
                    "confirms": [
                        "OnRspOrderInsert_callback_shape",
                        "input_order_and_rsp_info_fields",
                    ],
                    "closure_sufficient": False,
                    "insufficiency_reason": (
                        "does_not_explain_observed_response_offset_after_submitted_close_today"
                    ),
                },
                {
                    "class": "ctp_client_development_guide_primary_candidate",
                    "authority": "primary_candidate_documentation",
                    "confirms": [
                        "ctp_callback_model_context",
                        "shfe_today_yesterday_position_model_context",
                    ],
                    "closure_sufficient": False,
                    "insufficiency_reason": (
                        "does_not_tie_broker_front_rejection_offset_to_submit_boundary"
                    ),
                },
                {
                    "class": "cffex_trader_api_pdf_candidate",
                    "authority": "exchange_hosted_api_pdf",
                    "confirms": [
                        "trader_api_callback_context",
                        "OnRspOrderInsert_callback_presence",
                    ],
                    "closure_sufficient": False,
                    "insufficiency_reason": (
                        "does_not_explain_close_today_response_offset_semantics"
                    ),
                },
                {
                    "class": "futures_broker_ctp_error_help_candidate",
                    "authority": "broker_help_page",
                    "confirms": [
                        "ctp_close_position_insufficient_error_category",
                        "pending_close_orders_may_reduce_closable_quantity",
                    ],
                    "closure_sufficient": False,
                    "insufficiency_reason": (
                        "does_not_explain_api_response_offset_or_callback_authority"
                    ),
                },
            ]
            if typed_blocker
            else []
        ),
        "missing_source_class": (
            "primary_or_official_broker_front_close_rejection_rule_source"
            if typed_blocker
            else None
        ),
        "adapter_native_repair_beyond_local_diagnostics_present": stronger_repair_present,
        "external_source_candidates_sufficient_to_close": False,
        "partial_source_context_authorizes_retry": False,
        "source_closure_requirement": (
            "source_candidate_context_must_explain_observed_response_offset_or_adapter_native_semantics"
            if typed_blocker
            else None
        ),
        "order_insert_response_identity_observed": response_identity_observed,
        "source_bearing_rejection_observed": source_bearing_rejection,
        "local_diagnostics_sufficient_to_close": False,
        "next_required_evidence": (
            [
                "new_formal_retry_authorization_before_any_future_send",
                "fresh_same_slice_market_account_preflight_before_any_future_send",
            ]
            if typed_blocker and stronger_repair_present
            else
            [
                "primary_broker_front_close_rejection_rule_source",
                "adapter_native_repair_beyond_local_diagnostics",
                "new_formal_retry_authorization_before_any_future_send",
            ]
            if typed_blocker
            else []
        ),
        "acceptance_implication": "typed_blocker_only_not_fill_or_closeout_truth",
        "fill_producing_acceptance_satisfied": False,
        "requires_owner_resolution_before_retry": typed_blocker,
        "writes_truth": False,
    }


def build_source_closure_authority_guardrail(
    source_exhaustion_semantics: dict[str, Any],
) -> dict[str, Any]:
    """State whether source context can authorize retry or semantic closure."""
    requires_owner_resolution = (
        source_exhaustion_semantics.get("requires_owner_resolution_before_retry") is True
    )
    source_candidates_sufficient = (
        source_exhaustion_semantics.get("external_source_candidates_sufficient_to_close")
        is True
    )
    partial_context_authorizes_retry = (
        source_exhaustion_semantics.get("partial_source_context_authorizes_retry")
        is True
    )
    stronger_repair_present = (
        source_exhaustion_semantics.get(
            "adapter_native_repair_beyond_local_diagnostics_present"
        )
        is True
    )
    blocks_retry_from_partial_sources = (
        requires_owner_resolution
        and not source_candidates_sufficient
        and not partial_context_authorizes_retry
        and not stronger_repair_present
    )
    stronger_repair_requires_formal_authorization = (
        requires_owner_resolution
        and stronger_repair_present
        and not partial_context_authorizes_retry
    )
    return {
        "disposition": (
            "blocks_retry_authorization_from_partial_source_context"
            if blocks_retry_from_partial_sources
            else "blocks_retry_authorization_after_adapter_native_repair_until_formal_authorization"
            if stronger_repair_requires_formal_authorization
            else "source_closure_authority_guardrail_not_applicable"
        ),
        "missing_source_class": (
            source_exhaustion_semantics.get("missing_source_class")
            if blocks_retry_from_partial_sources
            else None
        ),
        "source_closure_requirement": (
            source_exhaustion_semantics.get("source_closure_requirement")
            if blocks_retry_from_partial_sources
            else None
        ),
        "external_source_candidate_classes_evaluated": (
            list(
                source_exhaustion_semantics.get(
                    "external_source_candidate_classes_evaluated", []
                )
            )
            if blocks_retry_from_partial_sources
            else []
        ),
        "external_source_candidate_evidence": (
            list(source_exhaustion_semantics.get("external_source_candidate_evidence", []))
            if blocks_retry_from_partial_sources
            else []
        ),
        "source_candidates_sufficient_to_close": source_candidates_sufficient,
        "partial_source_context_authorizes_retry": partial_context_authorizes_retry,
        "adapter_native_repair_beyond_local_diagnostics_present": stronger_repair_present,
        "retry_authorization_allowed_by_source_context": False,
        "semantic_closure_allowed_by_source_context": False,
        "requires_new_formal_authorization_before_send": (
            blocks_retry_from_partial_sources
            or stronger_repair_requires_formal_authorization
        ),
        "next_required_evidence": (
            [
                "primary_or_official_broker_front_close_rejection_rule_source_that_explains_observed_response_offset",
                "adapter_native_semantic_repair_beyond_local_diagnostics",
                "new_formal_retry_authorization_before_any_future_send",
            ]
            if blocks_retry_from_partial_sources
            else [
                "new_formal_retry_authorization_before_any_future_send",
                "fresh_same_slice_market_account_preflight_before_any_future_send",
            ]
            if stronger_repair_requires_formal_authorization
            else []
        ),
        "acceptance_implication": "typed_blocker_only_not_retry_or_closeout_truth",
        "fill_producing_acceptance_satisfied": False,
        "runtime_truth_created": False,
        "account_console_truth_created": False,
        "writes_truth": False,
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
        "position_detail_semantics": None
        if pre_payload is None
        else build_position_detail_semantics(
            pre_payload,
            instrument=instrument,
            direction=close_position_direction,
        ),
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
        "native_offset_semantics": None,
        "callback_source_observability": None,
        "broker_rejection_semantics": None,
        "close_offset_owner_rule_semantics": None,
        "source_exhaustion_semantics": None,
        "source_closure_authority_guardrail": None,
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
    risk_preflight: dict[str, Any] | None = None
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

    verified_exposure_reduction = bool(
        (risk_preflight or {}).get("verified_exposure_reduction")
    )
    exposure_reduction_preflight = bool(
        ((risk_preflight or {}).get("guards") or {})
        .get("kill_switch", {})
        .get("exposure_reduces_net_position")
    )
    config_issues = paper_config_issues(
        config,
        allow_live_order_smoke=arm_paper_send,
        allow_exposure_reduction_order_smoke=(
            verified_exposure_reduction or exposure_reduction_preflight
        ),
    )
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
            verified_exposure_reduction=verified_exposure_reduction,
        )
        commands = runtime_bridge.drain_submitted_commands()
        events = runtime_bridge.drain_events()
    except Exception as exc:
        payload["failure_reason"] = "paper_order_exception"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = [type(exc).__name__]
        payload["exception"] = {"type": type(exc).__name__, "message": str(exc)}
        return payload

    command_payload = {}
    if result.mapped_submit.command is not None:
        command_payload = dict(getattr(result.mapped_submit.command, "payload", {}) or {})
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
        "command_payload": command_payload,
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
            "side": event.payload.get("side", ""),
            "direction": event.payload.get("direction", ""),
            "offset_flag": event.payload.get("offset_flag", ""),
            "submit_request_offset_flag": event.payload.get("submit_request_offset_flag", ""),
            "submit_request_offset_source": event.payload.get("submit_request_offset_source", ""),
            "submit_request_id": command_payload.get("submit_request_id", ""),
            "submit_request_id_source": command_payload.get("submit_request_id_source_field", ""),
            "response_request_id": event.payload.get("response_request_id", ""),
            "response_is_last": event.payload.get("response_is_last", ""),
            "response_error_id": event.payload.get("response_error_id", ""),
            "hedge_flag": event.payload.get("hedge_flag", ""),
            "callback_source": event.payload.get("callback_source", ""),
            "payload_error_msg": event.payload.get("error_msg", ""),
            "error_message": event.message or "",
            "error_text_contains_replacement_char": "\ufffd"
            in f"{event.payload.get('error_msg', '')}{event.message or ''}",
        }
        for event in events
        if event.kind.value in {"order", "trade"}
    ]
    lifecycle_verdict = classify_lifecycle_events(payload["intent_contract"], lifecycle_events)
    payload["native_offset_semantics"] = build_native_offset_semantics(
        intent_contract=payload["intent_contract"],
        command_payload=command_payload,
        lifecycle_events=lifecycle_events,
    )
    payload["callback_source_observability"] = build_callback_source_observability(
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        paper_send_armed=arm_paper_send,
    )
    payload["broker_rejection_semantics"] = build_broker_rejection_semantics(
        intent_contract=payload["intent_contract"],
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=payload["native_offset_semantics"],
    )
    payload["close_offset_owner_rule_semantics"] = (
        build_close_offset_owner_rule_semantics(
            intent_contract=payload["intent_contract"],
            position_detail_semantics=payload["position_detail_semantics"] or {},
            native_offset_semantics=payload["native_offset_semantics"],
            broker_rejection_semantics=payload["broker_rejection_semantics"],
        )
    )
    payload["source_exhaustion_semantics"] = build_source_exhaustion_semantics(
        broker_rejection_semantics=payload["broker_rejection_semantics"],
        close_offset_owner_rule_semantics=payload["close_offset_owner_rule_semantics"],
    )
    payload["source_closure_authority_guardrail"] = (
        build_source_closure_authority_guardrail(
            payload["source_exhaustion_semantics"]
        )
    )
    if not arm_paper_send and lifecycle_verdict["disposition"] == "timeout":
        lifecycle_verdict = {
            **lifecycle_verdict,
            "accepted": True,
            "disposition": "dry_run_preflight",
        }
    matched_execs = [
        {
            "python_client_order_id": getattr(event, "python_client_order_id", ""),
            "native_order_id": getattr(event, "native_order_id", ""),
            "native_order_ref": getattr(event, "native_order_ref", ""),
            "venue_symbol": getattr(event, "venue_symbol", ""),
            "front_id": getattr(event, "front_id", None),
            "session_id": getattr(event, "session_id", None),
            "status": getattr(event, "status", None),
            "callback_source": getattr(event, "callback_source", ""),
            "offset_flag": getattr(event, "offset_flag", None),
            "submit_request_offset_flag": getattr(event, "submit_request_offset_flag", None),
            "submit_request_offset_source": getattr(event, "submit_request_offset_source", ""),
            "submit_request_id": getattr(event, "submit_request_id", None),
            "submit_request_id_source": getattr(event, "submit_request_id_source", ""),
            "response_request_id": getattr(event, "response_request_id", None),
            "response_is_last": getattr(event, "response_is_last", False),
            "response_error_id": getattr(event, "response_error_id", None),
            "is_trade": getattr(event, "is_trade", False),
            "trade_volume": getattr(event, "trade_volume", 0),
            "leaves_qty": getattr(event, "leaves_qty", 0),
            "match_reason": getattr(event, "match_reason", ""),
        }
        for event in (result.matched_execs or [])
    ]
    payload["order_lifecycle"] = {
        "dry_run": result.dry_run,
        "live_send_armed": result.live_send_armed,
        "bootstrap_ready": result.bootstrap.ready,
        "matched_exec_count": len(matched_execs),
        "matched_execs": matched_execs,
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
    return finalize_order_lifecycle_payload(
        payload=payload,
        bootstrap_ready=result.bootstrap.ready,
        mapped_error=result.mapped_submit.error,
        mapped_command=result.mapped_submit.command,
        order_contract=payload["order_contract"],
        lifecycle_verdict=lifecycle_verdict,
        reconciliation=payload["reconciliation"],
        arm_paper_send=arm_paper_send,
        dry_run=result.dry_run,
        live_send_armed=result.live_send_armed,
    )


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
