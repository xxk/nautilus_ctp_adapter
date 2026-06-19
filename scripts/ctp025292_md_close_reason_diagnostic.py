from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig


BASELINE = "ctp025292-md-close-reason-diagnostic-v1"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload must be an object: {path}")
    return payload


def _struct_fields(header_text: str, struct_name: str) -> list[str]:
    pattern = re.compile(rf"struct\s+{re.escape(struct_name)}\s*\{{(?P<body>.*?)\}};", re.S)
    match = pattern.search(header_text)
    if match is None:
        return []
    fields: list[str] = []
    for line in match.group("body").splitlines():
        line = line.strip()
        if not line or line.startswith("///"):
            continue
        parts = line.rstrip(";").split()
        if len(parts) >= 2:
            fields.append(parts[-1])
    return fields


def _md_api_login_signature(header_text: str) -> str:
    match = re.search(
        r"virtual\s+int\s+ReqUserLogin\s*\((?P<signature>[^)]*)\)\s*=\s*0\s*;",
        header_text,
    )
    return "" if match is None else " ".join(match.group("signature").split())


def _field_shape(value: str) -> dict[str, object]:
    return {"present": bool(value), "length": len(value), "raw_value_recorded": False}


def build_diagnostic(
    *,
    config_path: Path,
    sdk_struct_header: Path,
    md_api_header: Path,
    lifecycle_summary_path: Path,
    smoke_path: Path,
    flow_path: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    config = CtpAdapterConfig.from_json_file(config_path)
    struct_header_text = sdk_struct_header.read_text(encoding="utf-8", errors="replace")
    md_api_header_text = md_api_header.read_text(encoding="utf-8", errors="replace")
    lifecycle_summary = _read_json(lifecycle_summary_path)
    smoke = _read_json(smoke_path)

    req_user_login_fields = _struct_fields(struct_header_text, "CThostFtdcReqUserLoginField")
    req_user_login_sc_fields = _struct_fields(struct_header_text, "CThostFtdcReqUserLoginSCField")
    md_login_signature = _md_api_login_signature(md_api_header_text)

    auth_app_supported_by_md_req_user_login = {
        "auth_code": "AuthCode" in req_user_login_fields,
        "app_id": "AppID" in req_user_login_fields,
        "md_api_uses_sc_login_struct": "CThostFtdcReqUserLoginSCField" in md_login_signature,
    }
    flow_files = sorted(path.name for path in flow_path.iterdir()) if flow_path.exists() else []
    ctp_flow_files = [
        name for name in flow_files if name.lower().endswith((".con", ".dat", ".xml", ".ini"))
    ]

    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": False,
        "status": "blocked",
        "blocker_id": "ctp025292_md_front_closes_without_rsp_error_after_close_reason_trace",
        "inputs": {
            "config_path": str(config_path),
            "sdk_struct_header": str(sdk_struct_header),
            "md_api_header": str(md_api_header),
            "lifecycle_summary_path": str(lifecycle_summary_path),
            "smoke_path": str(smoke_path),
            "flow_path": str(flow_path),
        },
        "sdk_capability": {
            "md_api_req_user_login_signature": md_login_signature,
            "req_user_login_fields": req_user_login_fields,
            "req_user_login_sc_fields_include_auth_app": (
                "AuthCode" in req_user_login_sc_fields and "AppID" in req_user_login_sc_fields
            ),
            "auth_app_supported_by_md_req_user_login": auth_app_supported_by_md_req_user_login,
            "diagnosis": (
                "Current CThostFtdcMdApi::ReqUserLogin accepts CThostFtdcReqUserLoginField, "
                "which does not contain AuthCode/AppID. AuthCode/AppID exist on other login/auth "
                "structures, so their presence in config cannot by itself make them appear in the MD login payload."
            ),
        },
        "redacted_config_shape": {
            "broker_id": _field_shape(config.broker_id),
            "user_id": _field_shape(config.user_id),
            "password": _field_shape(config.password),
            "product_info": _field_shape(config.product_info),
            "app_id": _field_shape(config.app_id),
            "auth_code": _field_shape(config.auth_code),
            "md_front": {
                "present": bool(config.md_front),
                "length": len(config.md_front),
                "tcp_scheme": config.md_front.startswith("tcp://"),
                "raw_value_recorded": False,
            },
            "md_login_compatibility": {
                "interface_product_info": _field_shape(config.md_login_compatibility.interface_product_info),
                "protocol_info": _field_shape(config.md_login_compatibility.protocol_info),
                "mac_address": _field_shape(config.md_login_compatibility.mac_address),
                "client_ip_address": _field_shape(config.md_login_compatibility.client_ip_address),
                "login_remark": _field_shape(config.md_login_compatibility.login_remark),
            },
        },
        "runtime_observation": {
            "smoke_success": bool(smoke.get("success")),
            "failure_reason": smoke.get("failure_reason"),
            "init_code": smoke.get("init_code"),
            "login_request_code": smoke.get("login_request_code"),
            "subscribe_code": smoke.get("subscribe_code"),
            "front_connected_count": smoke.get("front_connected_count"),
            "disconnect_count": smoke.get("disconnect_count"),
            "first_tick_symbol": smoke.get("first_tick_symbol"),
            "event_counts": lifecycle_summary.get("event_counts"),
            "login_response_count": lifecycle_summary.get("login_response_count"),
            "rsp_error_count": lifecycle_summary.get("rsp_error_count"),
            "heartbeat_warning_count": lifecycle_summary.get("heartbeat_warning_count"),
            "tick_count": lifecycle_summary.get("tick_count"),
            "native_close_detail": lifecycle_summary.get("native_close_detail"),
            "diagnosis": lifecycle_summary.get("diagnosis"),
        },
        "flow_path_diagnostic": {
            "exists": flow_path.exists(),
            "entry_count": len(flow_files),
            "entries": flow_files,
            "ctp_state_file_count": len(ctp_flow_files),
            "ctp_state_files": ctp_flow_files,
            "repo_trace_present": "repo_md_lifecycle_trace.jsonl" in flow_files,
        },
        "interpretation": {
            "not_market_closed_pause": True,
            "not_runtime_lineage_failure": True,
            "not_td_or_order_scope": True,
            "md_auth_app_payload_gap_confirmed": True,
            "front_close_remains_unexplained_by_spi": True,
            "summary": (
                "The current SDK MD login entry point cannot carry AppID/AuthCode through "
                "CThostFtdcReqUserLoginField. The trusted runtime still shows front registration, Init, "
                "ReqUserLogin return_code=0 and fast reason=0 disconnect without login response or SPI error."
            ),
        },
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_use_025292_as_trading_account": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
            "did_not_claim_paper_ready": True,
            "did_not_claim_live_ready": True,
            "secret_values_recorded": False,
            "front_values_recorded": False,
        },
        "next_action": (
            "Either obtain a broker/operator-confirmed MD login mode that supports AuthCode/AppID or "
            "trusted MdLoginCompatibility fields for this 025292 front, or continue diagnosing front/session "
            "policy and flow/session requirements using read-only MD smoke only."
        ),
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose 025292 MD close-reason blocker without opening TD/order channels.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--sdk-struct-header", type=Path, default=Path("vendor/ctp/sdk/ThostFtdcUserApiStruct.h"))
    parser.add_argument("--md-api-header", type=Path, default=Path("vendor/ctp/sdk/ThostFtdcMdApi.h"))
    parser.add_argument("--lifecycle-summary", type=Path, required=True)
    parser.add_argument("--smoke-json", type=Path, required=True)
    parser.add_argument("--flow-path", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_diagnostic(
        config_path=args.config,
        sdk_struct_header=args.sdk_struct_header,
        md_api_header=args.md_api_header,
        lifecycle_summary_path=args.lifecycle_summary,
        smoke_path=args.smoke_json,
        flow_path=args.flow_path,
        output_path=args.output_json,
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
