from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.diagnostics.paper_session_preflight import paper_config_issues


REPO_ROOT = Path(__file__).resolve().parents[3]
BASELINE = "ctp-paper-readonly-snapshot-v1"
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.openctp.tts.7x24.local.json"
OPENCTP_TTS_7X24_PROFILE = "openctp-tts-7x24-simulation"
C1_DETAIL_FIELD_NAMES = (
    "instrument_name",
    "open_date",
    "expire_date",
    "start_deliv_date",
    "end_deliv_date",
    "is_trading",
    "long_margin_ratio",
    "short_margin_ratio",
    "max_market_order_volume",
    "min_market_order_volume",
    "max_limit_order_volume",
    "min_limit_order_volume",
    "product_id",
    "underlying_instr_id",
    "delivery_year",
    "delivery_month",
)


def paper_readonly_snapshot_config_issues(config: CtpAdapterConfig) -> list[str]:
    return paper_config_issues(config, allow_exposure_reduction_order_smoke=True)


def _fingerprint(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _path_text(path: Path | None) -> str | None:
    return None if path is None else str(path)


def snapshot_schema_metadata(*, run_id: str, flow_path: Path | None, session_label: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "flow_path": _path_text(flow_path),
        "session_label": session_label,
        "account_profile": OPENCTP_TTS_7X24_PROFILE,
        "evidence_class": "openctp-tts-7x24-simulation",
        "reconciliation_role": "pre_or_post_order_snapshot",
        "schema_version": BASELINE,
    }


def redacted_account_identity(account_id: str | None) -> dict[str, Any]:
    return {
        "account_id_present": bool(account_id),
        "account_id_fingerprint": _fingerprint(account_id),
    }


def classify_positions_disposition(
    *, query_code: int, completed: bool, timed_out: bool, no_positions: bool
) -> dict[str, Any]:
    if query_code != 0:
        return {
            "status": "blocked",
            "disposition": "query_failed",
            "failure_reason": "positions_query_failed",
        }
    if timed_out:
        return {
            "status": "blocked",
            "disposition": "timeout",
            "failure_reason": "positions_timed_out",
        }
    if not completed:
        return {
            "status": "blocked",
            "disposition": "incomplete",
            "failure_reason": "positions_incomplete",
        }
    if no_positions:
        return {
            "status": "passed",
            "disposition": "valid_empty",
            "failure_reason": None,
        }
    return {
        "status": "passed",
        "disposition": "positions_present",
        "failure_reason": None,
    }


def classify_account_disposition(
    *, query_code: int, completed: bool, timed_out: bool, account_present: bool
) -> dict[str, Any]:
    if query_code != 0:
        return {
            "status": "blocked",
            "disposition": "query_failed",
            "failure_reason": "account_query_failed",
        }
    if timed_out:
        return {
            "status": "blocked",
            "disposition": "timeout",
            "failure_reason": "account_timed_out",
        }
    if not completed:
        return {
            "status": "blocked",
            "disposition": "incomplete",
            "failure_reason": "account_incomplete",
        }
    if not account_present:
        return {
            "status": "blocked",
            "disposition": "missing",
            "failure_reason": "account_missing",
        }
    return {
        "status": "passed",
        "disposition": "account_present",
        "failure_reason": None,
    }


def position_contract_issues(position: Any) -> list[str]:
    issues: list[str] = []
    if str(position.direction or "").strip().lower() not in {"long", "short", "buy", "sell", "2", "3"}:
        issues.append("direction")
    for field_name in ("position_qty", "yd_position_qty", "td_position_qty"):
        value = getattr(position, field_name)
        if value is None or value < 0:
            issues.append(field_name)
    return issues


def instrument_contract_issues(instrument: Any) -> list[str]:
    issues: list[str] = []
    if not getattr(instrument, "display_symbol", ""):
        issues.append("display_symbol")
    if not getattr(instrument, "venue_symbol", ""):
        issues.append("venue_symbol")
    if not getattr(instrument, "exchange_id", ""):
        issues.append("exchange_id")
    if getattr(instrument, "price_tick", None) in {None, 0}:
        issues.append("price_tick")
    if getattr(instrument, "volume_multiple", None) in {None, 0}:
        issues.append("volume_multiple")
    return issues


def instrument_detail_contract_issues(instrument: Any) -> list[str]:
    issues: list[str] = []
    product_kind = getattr(instrument, "product_kind", None)
    if product_kind is not None and getattr(product_kind, "value", product_kind) == "unknown":
        issues.append("unknown_product_kind")
    open_date = _normalized_text(getattr(instrument, "open_date", None))
    expire_date = _normalized_text(getattr(instrument, "expire_date", None))
    if open_date and not _looks_like_yyyymmdd(open_date):
        issues.append("open_date_invalid")
    if expire_date and not _looks_like_yyyymmdd(expire_date):
        issues.append("expire_date_invalid")
    contract_month = _normalized_text(getattr(instrument, "contract_month", None))
    if contract_month and len(contract_month) != 4:
        issues.append("delivery_month_ambiguous")
    return issues


def build_instrument_detail_payload(instrument: Any) -> dict[str, Any]:
    contract_month = _normalized_text(getattr(instrument, "contract_month", None))
    delivery_year, delivery_month = _parse_delivery_year_month(contract_month)
    detail_fields = {
        "instrument_name": _normalized_text(getattr(instrument, "instrument_name", None)) or None,
        "open_date": _normalized_text(getattr(instrument, "open_date", None)) or None,
        "expire_date": _normalized_text(getattr(instrument, "expire_date", None)) or None,
        "start_deliv_date": None,
        "end_deliv_date": None,
        "is_trading": None,
        "long_margin_ratio": None,
        "short_margin_ratio": None,
        "max_market_order_volume": None,
        "min_market_order_volume": None,
        "max_limit_order_volume": None,
        "min_limit_order_volume": None,
        "product_id": _normalized_text(getattr(instrument, "product_id", None)) or None,
        "underlying_instr_id": _normalized_text(getattr(instrument, "underlying_instr_id", None)) or None,
        "delivery_year": delivery_year,
        "delivery_month": delivery_month,
    }
    missing_fields = [name for name, value in detail_fields.items() if value in {None, ""}]
    issue_codes = instrument_detail_contract_issues(instrument)
    return {
        "detail_fields": detail_fields,
        "raw_detail": dict(detail_fields),
        "missing_fields": missing_fields,
        "contract_issues": issue_codes,
        "correctness_status": "failed" if issue_codes else "passed",
        "completeness_status": "covered" if not missing_fields else "partial",
    }


def build_instrument_correctness_summary(records: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "total": len(records),
        "passed": 0,
        "failed": 0,
        "partial": 0,
        "out_of_scope_current": 0,
    }
    out_of_scope_names = {
        "start_deliv_date",
        "end_deliv_date",
        "is_trading",
        "long_margin_ratio",
        "short_margin_ratio",
        "max_market_order_volume",
        "min_market_order_volume",
        "max_limit_order_volume",
        "min_limit_order_volume",
    }
    for record in records:
        if record.get("contract_issues"):
            summary["failed"] += 1
        elif record.get("missing_fields"):
            summary["partial"] += 1
        else:
            summary["passed"] += 1
        summary["out_of_scope_current"] += len(
            [name for name in (record.get("missing_fields") or []) if name in out_of_scope_names]
        )
    return summary


def build_config_only_snapshot(
    *,
    config: CtpAdapterConfig,
    config_path: Path,
    run_id: str,
    flow_path: Path | None,
    session_label: str,
) -> dict[str, Any]:
    issues = paper_readonly_snapshot_config_issues(config)
    return {
        "baseline": BASELINE,
        "success": not issues,
        "status": "passed" if not issues else "blocked",
        "failure_reason": None if not issues else "config_validation_failed",
        "blocker_type": None if not issues else "paper-resource",
        "action_mode": "request_only",
        "connect_requested": False,
        "schema": snapshot_schema_metadata(
            run_id=run_id,
            flow_path=flow_path,
            session_label=session_label,
        ),
        "config_path": str(config_path),
        "issues": issues,
        "account": {
            "identity": redacted_account_identity(config.user_id),
            "disposition": {
                "status": "not_run",
                "disposition": "request_only",
                "failure_reason": None,
            },
        },
        "positions": {
            "disposition": {
                "status": "not_run",
                "disposition": "request_only",
                "failure_reason": None,
            },
            "position_count": None,
            "no_positions": None,
            "records": [],
        },
        "instruments": {
            "requested_symbols": list(config.instruments),
            "loaded": None,
            "instrument_count": None,
            "records": [],
            "contract_issues": [],
        },
        "order_trade": {
            "disposition": "not_run",
            "observed_order_event_count": None,
            "observed_trade_event_count": None,
        },
    }


def populate_connected_snapshot_payload(
    *,
    payload: dict[str, Any],
    config: CtpAdapterConfig,
    snapshot: Any,
    instrument_result: Any,
    order_trade: Any,
    commands: list[Any],
    events: list[Any],
) -> dict[str, Any]:
    positions_disposition = classify_positions_disposition(
        query_code=snapshot.positions.query_code,
        completed=snapshot.positions.completed,
        timed_out=snapshot.positions.timed_out,
        no_positions=snapshot.positions.no_positions,
    )
    account_present = snapshot.account.account is not None
    account_disposition = classify_account_disposition(
        query_code=snapshot.account.query_code,
        completed=snapshot.account.completed,
        timed_out=snapshot.account.timed_out,
        account_present=account_present,
    )

    position_contract_findings = [
        {"venue_symbol": position.venue_symbol, "issues": position_contract_issues(position)}
        for position in snapshot.positions.positions
        if position_contract_issues(position)
    ]
    instrument_records: list[dict[str, Any]] = []
    instrument_contract_findings: list[dict[str, Any]] = []
    if instrument_result is not None:
        for instrument in instrument_result.instruments:
            instrument_records.append(
                {
                    "venue_symbol": instrument.venue_symbol,
                    "display_symbol": instrument.display_symbol,
                    "exchange_id": instrument.exchange_id,
                    "product_kind": instrument.product_kind.value,
                    "price_tick": instrument.price_tick,
                    "volume_multiple": instrument.volume_multiple,
                    **build_instrument_detail_payload(instrument),
                }
            )
            issues = instrument_contract_issues(instrument)
            detail_issues = instrument_detail_contract_issues(instrument)
            if issues or detail_issues:
                instrument_contract_findings.append(
                    {"display_symbol": instrument.display_symbol, "issues": sorted(set([*issues, *detail_issues]))}
                )

    payload["account"] = {
        "identity": redacted_account_identity(
            None if snapshot.account.account is None else snapshot.account.account.account_id
        ),
        "disposition": account_disposition,
        "request_id": snapshot.account.request_id,
        "query_code": snapshot.account.query_code,
        "completed": snapshot.account.completed,
        "timed_out": snapshot.account.timed_out,
        "balance_present": bool(snapshot.account.account and snapshot.account.account.balance is not None),
        "available_present": bool(snapshot.account.account and snapshot.account.account.available is not None),
        "margin_present": bool(snapshot.account.account and snapshot.account.account.margin is not None),
    }
    payload["positions"] = {
        "disposition": positions_disposition,
        "request_id": snapshot.positions.request_id,
        "query_code": snapshot.positions.query_code,
        "completed": snapshot.positions.completed,
        "timed_out": snapshot.positions.timed_out,
        "no_positions": snapshot.positions.no_positions,
        "position_count": snapshot.positions.position_count,
        "contract_issues": position_contract_findings,
        "records": [
            {
                "venue_symbol": position.venue_symbol,
                "exchange_id": position.exchange_id,
                "direction": position.direction,
                "hedge_flag": position.hedge_flag,
                "date_type": position.date_type,
                "position_qty": position.position_qty,
                "yd_position_qty": position.yd_position_qty,
                "td_position_qty": position.td_position_qty,
                "position_cost": position.position_cost,
            }
            for position in snapshot.positions.positions
        ],
    }
    payload["instruments"] = {
        "requested_symbols": list(config.instruments),
        "loaded": None if instrument_result is None else instrument_result.loaded,
        "instrument_count": None if instrument_result is None else instrument_result.instrument_count,
        "records": instrument_records,
        "contract_issues": instrument_contract_findings,
        "detail_fields": list(C1_DETAIL_FIELD_NAMES),
        "correctness_summary": build_instrument_correctness_summary(instrument_records),
    }
    payload["order_trade"] = {
        "disposition": order_trade.disposition,
        "observed_order_event_count": order_trade.observed_order_event_count,
        "observed_trade_event_count": order_trade.observed_trade_event_count,
        "no_order_events": order_trade.no_order_events,
        "no_trade_events": order_trade.no_trade_events,
        "historical_order_count": order_trade.historical_order_count,
        "historical_trade_count": order_trade.historical_trade_count,
        "current_session_order_count": order_trade.current_session_order_count,
        "current_session_trade_count": order_trade.current_session_trade_count,
        "manual_review_codes": [
            finding.code for finding in order_trade.findings if finding.action == "manual_review_required"
        ],
        "boundary_codes": [
            finding.code for finding in order_trade.findings if finding.action == "boundary_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in order_trade.findings if finding.action == "evidence_only"
        ],
    }
    payload["bridge_command_kinds"] = [command.kind.value for command in commands]
    payload["bridge_event_kinds"] = [event.kind.value for event in events]

    failure_reasons = [
        item["failure_reason"]
        for item in (positions_disposition, account_disposition)
        if item["failure_reason"]
    ]
    if position_contract_findings:
        failure_reasons.append("position_contract_issues")
    if instrument_contract_findings:
        failure_reasons.append("instrument_contract_issues")
    if instrument_result is not None and not instrument_result.loaded:
        failure_reasons.append("instrument_query_incomplete")

    payload["success"] = not failure_reasons
    payload["status"] = "passed" if not failure_reasons else "blocked"
    payload["failure_reason"] = None if not failure_reasons else failure_reasons[0]
    payload["blocker_type"] = None if not failure_reasons else "paper-resource"
    payload["issues"] = failure_reasons
    return payload


def build_connect_process_blocker_snapshot(
    *,
    config: CtpAdapterConfig,
    config_path: Path,
    run_id: str,
    flow_path: Path | None,
    session_label: str,
    process_timeout_seconds: float,
    failure_reason: str,
    error_stage: str = "paper_connect",
    error_type: str | None = None,
    process_exitcode: int | None = None,
) -> dict[str, Any]:
    payload = build_config_only_snapshot(
        config=config,
        config_path=config_path,
        run_id=run_id,
        flow_path=flow_path,
        session_label=session_label,
    )
    payload.update(
        {
            "success": False,
            "status": "blocked",
            "failure_reason": failure_reason,
            "blocker_type": "paper-resource",
            "action_mode": "paper_connect",
            "connect_requested": True,
            "snapshot_complete": False,
            "process_timeout_seconds": process_timeout_seconds,
            "process_exitcode": process_exitcode,
            "error_stage": error_stage,
            "error_type": error_type,
            "issues": [failure_reason],
            "completion": {
                "status": "blocked",
                "disposition": failure_reason,
                "failure_reason": failure_reason,
            },
        }
    )
    return payload


def build_exception_payload(*, stage: str, exc: Exception) -> dict[str, Any]:
    return {
        "baseline": BASELINE,
        "success": False,
        "status": "blocked",
        "failure_reason": "exception",
        "blocker_type": "paper-resource",
        "error_stage": stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }


def _normalized_text(value: str | None) -> str:
    return str(value or "").strip()


def _looks_like_yyyymmdd(value: str) -> bool:
    return len(value) == 8 and value.isdigit()


def _parse_delivery_year_month(contract_month: str) -> tuple[int | None, int | None]:
    if len(contract_month) != 4 or not contract_month.isdigit():
        return (None, None)
    year = 2000 + int(contract_month[:2])
    month = int(contract_month[2:])
    if month < 1 or month > 12:
        return (None, None)
    return (year, month)


__all__ = [
    "BASELINE",
    "DEFAULT_CONFIG",
    "OPENCTP_TTS_7X24_PROFILE",
    "build_config_only_snapshot",
    "build_connect_process_blocker_snapshot",
    "build_exception_payload",
    "paper_readonly_snapshot_config_issues",
    "populate_connected_snapshot_payload",
]
