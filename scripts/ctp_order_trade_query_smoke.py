from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKTREE_ROOT = REPO_ROOT.parents[0]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.native.loader import add_windows_dll_directories, preload_runtime_vendor_dlls
from nautilus_ctp_adapter.native.td_ctypes import CtpTdApi, NativeExecView, NativeTdLoginResponseView


BASELINE = "account-console.openctp-order-trade-query.v1"
DEFAULT_CONFIG = Path("D:/Nautilus/nautilus_ctp_adapter/cfgs/local/ctp.openctp.tts.7x24.local.json")
DEFAULT_VENDOR_BIN = Path("D:/Nautilus/nautilus_ctp_adapter/vendor/ctp/bin")
DEFAULT_NATIVE_DLL = REPO_ROOT / "rust" / "target" / "release" / "ctp_native.dll"
DEFAULT_OUTPUT = (
    WORKTREE_ROOT
    / "nautilus_account_console"
    / "output"
    / "account_capability"
    / "ctp-paper-19053"
    / "current-openctp-login"
    / "order_trade_query.json"
)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, default=_json_default))


def _exec_record(view: NativeExecView) -> dict[str, Any]:
    return asdict(view)


def _wait_for_login(state: dict[str, Any], deadline: float) -> NativeTdLoginResponseView | None:
    while time.time() < deadline:
        login = state.get("login")
        if login is not None:
            return login
        time.sleep(0.05)
    return None


def _wait_for_query(
    rows: list[dict[str, Any]],
    *,
    source: str,
    min_started_at: float,
    deadline: float,
    quiet_seconds: float,
) -> tuple[bool, bool]:
    saw_source = False
    last_count = -1
    last_changed = time.time()
    while time.time() < deadline:
        matching = [row for row in rows if row.get("callback_source") == source]
        if matching:
            saw_source = True
        if len(matching) != last_count:
            last_count = len(matching)
            last_changed = time.time()
        if any(row.get("response_is_last") is True for row in matching):
            return True, saw_source
        if saw_source and time.time() - last_changed >= quiet_seconds and time.time() >= min_started_at + quiet_seconds:
            return False, saw_source
        time.sleep(0.05)
    return False, saw_source


def _failure_payload(stage: str, reason: str, **extra: Any) -> dict[str, Any]:
    payload = {
        "schema": BASELINE,
        "success": False,
        "failure_reason": reason,
        "failure_stage": stage,
        "captured_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "raw_secret_values_recorded": False,
        "raw_broker_endpoint_recorded": False,
        "order_send_called": False,
        "order_action_sent": False,
        "cancel_order_sent": False,
        "replace_order_sent": False,
    }
    payload.update(extra)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Read current OpenCTP order and trade query rows without sending orders.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--native-dll", type=Path, default=DEFAULT_NATIVE_DLL)
    parser.add_argument("--vendor-bin", type=Path, default=DEFAULT_VENDOR_BIN)
    parser.add_argument("--flow-path", type=Path, default=DEFAULT_OUTPUT.parent / "td_query_flow")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-seconds", type=float, default=25.0)
    parser.add_argument("--query-timeout-seconds", type=float, default=10.0)
    parser.add_argument("--quiet-seconds", type=float, default=1.0)
    args = parser.parse_args()

    captured_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not args.config.exists():
        payload = _failure_payload("config", "config_missing", config_ref=str(args.config))
        _write_json(args.output_json, payload)
        _emit(payload)
        return 1
    if not args.native_dll.exists():
        payload = _failure_payload("native", "native_dll_missing", native_dll_ref=str(args.native_dll))
        _write_json(args.output_json, payload)
        _emit(payload)
        return 1

    config = CtpAdapterConfig.from_json_file(args.config)
    issues = config.validate()
    if issues:
        payload = _failure_payload("config", "config_invalid", config_ref=str(args.config), missing_fields=issues)
        _write_json(args.output_json, payload)
        _emit(payload)
        return 1

    add_windows_dll_directories(args.native_dll.parent, args.vendor_bin)
    preload_runtime_vendor_dlls(args.vendor_bin, dll_loader=ctypes.CDLL)
    api = CtpTdApi(ctypes.CDLL(str(args.native_dll)))
    args.flow_path.mkdir(parents=True, exist_ok=True)
    handle = api.create(args.flow_path)
    state: dict[str, Any] = {"login": None, "disconnects": [], "exec_rows": []}

    def on_exec(view: NativeExecView) -> None:
        state["exec_rows"].append(_exec_record(view))

    try:
        api.set_login_callback(handle, lambda resp: state.__setitem__("login", resp))
        api.set_front_disconnected_callback(handle, lambda reason: state["disconnects"].append(int(reason)))
        api.set_exec_callback(handle, on_exec)

        init_code = api.init(handle, config.td_front)
        auth_code = api.authenticate(handle, config.app_id, config.auth_code, config.product_info)
        login_code = api.login(handle, config.broker_id, config.user_id, config.password)
        login = _wait_for_login(state, time.time() + args.timeout_seconds)
        settlement_code = -1
        ready = False
        if init_code == 0 and auth_code == 0 and login_code == 0 and login is not None and login.success:
            settlement_code = api.confirm_settlement(handle)
            ready = settlement_code == 0

        query_order_code = -1
        query_trade_code = -1
        order_is_last = False
        trade_is_last = False
        order_callback_observed = False
        trade_callback_observed = False
        if ready:
            order_started = time.time()
            query_order_code = api.qry_order(handle)
            order_is_last, order_callback_observed = _wait_for_query(
                state["exec_rows"],
                source="OnRspQryOrder",
                min_started_at=order_started,
                deadline=time.time() + args.query_timeout_seconds,
                quiet_seconds=args.quiet_seconds,
            )
            time.sleep(1.0)
            trade_started = time.time()
            query_trade_code = api.qry_trade(handle)
            trade_is_last, trade_callback_observed = _wait_for_query(
                state["exec_rows"],
                source="OnRspQryTrade",
                min_started_at=trade_started,
                deadline=time.time() + args.query_timeout_seconds,
                quiet_seconds=args.quiet_seconds,
            )

        rows = list(state["exec_rows"])
        orders = [row for row in rows if row.get("callback_source") == "OnRspQryOrder"]
        trades = [row for row in rows if row.get("callback_source") == "OnRspQryTrade"]
        payload = {
            "schema": BASELINE,
            "success": bool(ready and query_order_code == 0 and query_trade_code == 0),
            "failure_reason": None if ready and query_order_code == 0 and query_trade_code == 0 else "query_not_ready",
            "captured_at_utc": captured_at,
            "account_id": "acct.ctp.paper.19053",
            "display_alias": "19053",
            "source_kind": "ctp_trader_api",
            "query_kind": "order_trade_query",
            "config_ref": "owner://nautilus_ctp_adapter/cfgs/local/ctp.openctp.tts.7x24.local.json",
            "native_dll_ref": str(args.native_dll),
            "native_dll_checksum": _sha256(args.native_dll),
            "flow_path": str(args.flow_path),
            "login_success": None if login is None else bool(login.success),
            "login_error_id": None if login is None else int(login.error_id),
            "settlement_code": settlement_code,
            "ready": ready,
            "init_code": init_code,
            "authenticate_code": auth_code,
            "login_code": login_code,
            "query_order_code": query_order_code,
            "query_trade_code": query_trade_code,
            "order_query_is_last_observed": order_is_last,
            "trade_query_is_last_observed": trade_is_last,
            "order_query_callback_observed": order_callback_observed,
            "trade_query_callback_observed": trade_callback_observed,
            "disconnect_count": len(state["disconnects"]),
            "disconnect_reasons": list(state["disconnects"]),
            "readonly_api_calls": ["ReqQryOrder", "ReqQryTrade"],
            "order_send_called": False,
            "order_action_sent": False,
            "cancel_order_sent": False,
            "replace_order_sent": False,
            "raw_secret_values_recorded": False,
            "raw_broker_endpoint_recorded": False,
            "orders": orders,
            "trades": trades,
            "order_count": len(orders),
            "trade_count": len(trades),
        }
    finally:
        api.dispose(handle)

    _write_json(args.output_json, payload)
    _emit(payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
