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

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpCancelOrderIntent
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack
from nautilus_ctp_adapter.native.pyo3_runtime import create_td_live_session
from nautilus_ctp_adapter.devtools.offhours_cli import write_json_payload

from scripts.ctp_guarded_paper_order_loop import (
    OPENCTP_TTS_7X24_EVIDENCE_CLASS,
    OPENCTP_TTS_7X24_PROFILE,
    validate_pre_order_snapshot,
)
from scripts.ctp_paper_session_preflight import paper_config_issues


BASELINE = "ctp-guarded-paper-cancel-loop-v1"
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.openctp.tts.7x24.local.json"


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
        order_ref = str(_event_value(event, "native_order_ref", "") or "")
        front_id = str(_event_value(event, "front_id", "") or "")
        session_id = str(_event_value(event, "session_id", "") or "")
        identity_matches = (
            order_ref == str(cancel_contract["order_ref"])
            and front_id == str(cancel_contract["front_id"])
            and session_id == str(cancel_contract["session_id"])
        )
        if client_order_id != cancel_contract["client_order_id"] and not identity_matches:
            continue
        if venue_symbol and venue_symbol != cancel_contract["instrument"]:
            continue
        kind = str(_event_value(event, "kind", "") or "").lower()
        status = str(_event_value(event, "status", "") or "").lower()
        order_id = str(_event_value(event, "native_order_id", "") or "")
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
        if error_message and status not in {"97", "accepted"}:
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


def run_guarded_paper_cancel(
    *,
    config_path: Path,
    pre_snapshot: Path,
    instrument: str,
    client_order_id: str,
    order_ref: int,
    front_id: int,
    session_id: int,
    exchange_id: str | None,
    arm_cancel_send: bool,
) -> dict[str, Any]:
    pre_snapshot_verdict = validate_pre_order_snapshot(pre_snapshot)
    cancel_contract = build_cancel_contract(
        instrument=instrument,
        client_order_id=client_order_id,
        order_ref=order_ref,
        front_id=front_id,
        session_id=session_id,
        exchange_id=exchange_id,
    )
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "account_profile": OPENCTP_TTS_7X24_PROFILE,
        "evidence_class": OPENCTP_TTS_7X24_EVIDENCE_CLASS,
        "success": False,
        "status": "blocked",
        "failure_reason": None,
        "blocker_type": None,
        "action_mode": "cancel_send" if arm_cancel_send else "dry_run",
        "cancel_send_armed": arm_cancel_send,
        "pre_snapshot": pre_snapshot_verdict,
        "cancel_contract": cancel_contract,
        "mapped_cancel": None,
        "command_contract": None,
        "cancel_lifecycle": None,
        "issues": [],
    }
    if not pre_snapshot_verdict["accepted"]:
        payload["failure_reason"] = "pre_snapshot_rejected"
        payload["blocker_type"] = "paper-safety"
        payload["issues"] = list(pre_snapshot_verdict["issues"])
        return payload

    config = CtpAdapterConfig.from_json_file(config_path)
    config_issues = paper_config_issues(config, allow_live_order_smoke=arm_cancel_send)
    if config_issues:
        payload["failure_reason"] = "config_validation_failed"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = config_issues
        return payload

    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    runtime_bridge = stack["runtime_bridge"]
    mapped_cancel = execution_client.map_cancel_order(
        CtpCancelOrderIntent(
            instrument_id=instrument,
            client_order_id=client_order_id,
            order_ref=order_ref,
            front_id=front_id,
            session_id=session_id,
            exchange_id=exchange_id,
        )
    )
    payload["mapped_cancel"] = {
        "error": None
        if mapped_cancel.error is None
        else {
            "error_id": mapped_cancel.error.error_id,
            "error_message": mapped_cancel.error.error_message,
        },
        "client_order_id": mapped_cancel.client_order_id,
        "order_ref_present": mapped_cancel.order_ref is not None and mapped_cancel.order_ref > 0,
        "front_id_present": mapped_cancel.front_id is not None and mapped_cancel.front_id > 0,
        "session_id_present": mapped_cancel.session_id is not None and mapped_cancel.session_id != 0,
        "command_kind": None if mapped_cancel.command is None else mapped_cancel.command.kind.value,
    }
    payload["command_contract"] = validate_cancel_command_contract(cancel_contract, mapped_cancel.command)
    if mapped_cancel.error is not None or mapped_cancel.command is None:
        payload["failure_reason"] = "cancel_contract_not_ready"
        payload["blocker_type"] = "paper-safety"
        payload["issues"] = [mapped_cancel.error.error_message if mapped_cancel.error else "command_missing"]
        return payload

    if arm_cancel_send:
        native_result = _run_native_cancel_action(
            config=config,
            instrument=instrument,
            order_ref=order_ref,
            front_id=front_id,
            session_id=session_id,
            exchange_id=exchange_id or "",
            timeout_seconds=20,
        )
        payload["native_cancel"] = native_result
        if not native_result["accepted"]:
            payload["failure_reason"] = native_result["failure_reason"]
            payload["blocker_type"] = native_result["blocker_type"]
            payload["issues"] = list(native_result["issues"])
            return payload
        execution_client.submit_mapped_order(mapped_cancel)
    commands = runtime_bridge.drain_submitted_commands()
    events = runtime_bridge.drain_events()
    native_events = (payload.get("native_cancel") or {}).get("events") or []
    lifecycle_events = [*events, *native_events]
    payload["cancel_lifecycle"] = {
        "dry_run": not arm_cancel_send,
        "command_kinds": [command.kind.value for command in commands],
        "event_kinds": [event.kind.value for event in events] + [event.get("kind", "") for event in native_events],
        "verdict": classify_cancel_events(cancel_contract, lifecycle_events),
    }
    if not arm_cancel_send and commands:
        payload["failure_reason"] = "dry_run_submitted_cancel"
        payload["blocker_type"] = "paper-safety"
        payload["issues"] = ["dry_run_submitted_cancel"]
        return payload

    payload["success"] = bool(payload["command_contract"]["accepted"])
    payload["status"] = "passed" if payload["success"] else "blocked"
    payload["failure_reason"] = None if payload["success"] else "cancel_contract_not_ready"
    payload["blocker_type"] = None if payload["success"] else "paper-safety"
    return payload


def _run_native_cancel_action(
    *,
    config: CtpAdapterConfig,
    instrument: str,
    order_ref: int,
    front_id: int,
    session_id: int,
    exchange_id: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    flow_path = REPO_ROOT / "output" / "debug" / f"cancel_action_{time.time_ns()}"
    flow_path.mkdir(parents=True, exist_ok=True)
    state: dict[str, Any] = {"login": None, "disconnects": [], "events": []}
    try:
        session = create_td_live_session(flow_path)
    except Exception as exc:
        return {
            "accepted": False,
            "failure_reason": "native_cancel_unavailable",
            "blocker_type": "paper-resource",
            "issues": [type(exc).__name__],
            "message": str(exc),
            "flow_path": str(flow_path),
        }

    try:
        if not hasattr(session, "order_action"):
            return {
                "accepted": False,
                "failure_reason": "native_cancel_unavailable",
                "blocker_type": "paper-resource",
                "issues": ["order_action_missing"],
                "flow_path": str(flow_path),
            }
        session.set_login_callback(lambda resp: state.__setitem__("login", resp))
        session.set_front_disconnected_callback(lambda reason: state["disconnects"].append(reason))
        session.set_exec_callback(lambda exec_view: state["events"].append(exec_view))

        init_code = session.init(config.td_front)
        auth_code = session.authenticate(config.app_id, config.auth_code, config.product_info)
        login_code = session.login(config.broker_id, config.user_id, config.password)
        deadline = time.time() + timeout_seconds
        while time.time() < deadline and state["login"] is None:
            time.sleep(0.1)
        login = state["login"]
        if login is None or not getattr(login, "success", False):
            return {
                "accepted": False,
                "failure_reason": "native_cancel_login_failed",
                "blocker_type": "paper-resource",
                "issues": ["login_failed_or_timeout"],
                "init_code": init_code,
                "authenticate_code": auth_code,
                "login_code": login_code,
                "login_error_id": None if login is None else getattr(login, "error_id", None),
                "login_error_message": None if login is None else getattr(login, "error_message", None),
                "flow_path": str(flow_path),
            }
        settlement_code = session.confirm_settlement()
        if settlement_code != 0:
            return {
                "accepted": False,
                "failure_reason": "native_cancel_settlement_failed",
                "blocker_type": "paper-resource",
                "issues": ["settlement_failed"],
                "settlement_code": settlement_code,
                "flow_path": str(flow_path),
            }
        native_code = session.order_action(
            config.broker_id,
            config.user_id,
            instrument,
            str(order_ref),
            front_id,
            session_id,
            exchange_id,
            "",
            0,
        )
        observation_deadline = time.time() + max(timeout_seconds / 2, 1)
        while time.time() < observation_deadline and not state["events"]:
            time.sleep(0.1)
        return {
            "accepted": native_code == 0,
            "failure_reason": None if native_code == 0 else "native_cancel_action_failed",
            "blocker_type": None if native_code == 0 else "paper-resource",
            "issues": [] if native_code == 0 else [f"native_code={native_code}"],
            "native_code": native_code,
            "flow_path": str(flow_path),
            "disconnect_count": len(state["disconnects"]),
            "observed_event_count": len(state["events"]),
            "events": [_native_exec_event_payload(event) for event in state["events"]],
        }
    finally:
        session.dispose()


def _native_exec_event_payload(event: Any) -> dict[str, Any]:
    return {
        "kind": "trade" if bool(getattr(event, "is_trade", False)) else "order",
        "client_order_id": "",
        "venue_symbol": getattr(event, "symbol", ""),
        "native_order_id": getattr(event, "order_id", ""),
        "native_order_ref": getattr(event, "order_ref", ""),
        "front_id": getattr(event, "front_id", None),
        "session_id": getattr(event, "session_id", None),
        "status": getattr(event, "status", None),
        "trade_volume": getattr(event, "trade_volume", None),
        "leaves_qty": getattr(event, "leaves_qty", None),
        "error_message": getattr(event, "error_msg", ""),
        "callback_source": getattr(event, "callback_source", ""),
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
    if name in {"front_id", "session_id"}:
        payload = getattr(event, "payload", {}) or {}
        return payload.get(name, getattr(event, name, default))
    return getattr(event, name, default)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run guarded OpenCTP paper cancel preflight/dry-run loop.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--pre-snapshot", type=Path, required=True)
    parser.add_argument("--instrument", required=True)
    parser.add_argument("--client-order-id", required=True)
    parser.add_argument("--order-ref", type=int, required=True)
    parser.add_argument("--front-id", type=int, required=True)
    parser.add_argument("--session-id", type=int, required=True)
    parser.add_argument("--exchange-id", default=None)
    parser.add_argument("--arm-cancel-send", action="store_true")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    payload = run_guarded_paper_cancel(
        config_path=args.config if args.config.is_absolute() else REPO_ROOT / args.config,
        pre_snapshot=args.pre_snapshot if args.pre_snapshot.is_absolute() else REPO_ROOT / args.pre_snapshot,
        instrument=args.instrument,
        client_order_id=args.client_order_id,
        order_ref=args.order_ref,
        front_id=args.front_id,
        session_id=args.session_id,
        exchange_id=args.exchange_id,
        arm_cancel_send=args.arm_cancel_send,
    )
    text = json.dumps(payload, ensure_ascii=False)
    print(text)
    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        write_json_payload(path=output_path, payload=payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
