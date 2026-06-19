from __future__ import annotations

import json
from pathlib import Path

from scripts.ctp025292_md_close_reason_diagnostic import build_diagnostic


def test_close_reason_diagnostic_redacts_config_and_locks_md_login_struct_gap(tmp_path: Path) -> None:
    config = tmp_path / "ctp.live.025292.local.json"
    config.write_text(
        json.dumps(
            {
                "BrokerID": "0155",
                "UserID": "025292",
                "Password": "secret-pass",
                "ProductInfo": "iQuant",
                "AppID": "client_iq_3.6.2",
                "AuthCode": "secret-auth",
                "Pricer": "tcp://106.75.173.28:51213",
                "Host": "tcp://106.75.173.28:51205",
                "Instruments": ["ag2612"],
            }
        ),
        encoding="utf-8",
    )
    struct_header = tmp_path / "ThostFtdcUserApiStruct.h"
    struct_header.write_text(
        """
        struct CThostFtdcReqUserLoginField
        {
            TThostFtdcBrokerIDType BrokerID;
            TThostFtdcUserIDType UserID;
            TThostFtdcPasswordType Password;
            TThostFtdcProductInfoType UserProductInfo;
            TThostFtdcProductInfoType InterfaceProductInfo;
            TThostFtdcProtocolInfoType ProtocolInfo;
            TThostFtdcMacAddressType MacAddress;
            TThostFtdcLoginRemarkType LoginRemark;
            TThostFtdcIPAddressType ClientIPAddress;
        };
        struct CThostFtdcReqUserLoginSCField
        {
            TThostFtdcAuthCodeType AuthCode;
            TThostFtdcAppIDType AppID;
        };
        """,
        encoding="utf-8",
    )
    md_header = tmp_path / "ThostFtdcMdApi.h"
    md_header.write_text(
        "virtual int ReqUserLogin(CThostFtdcReqUserLoginField *pReqUserLoginField, int nRequestID) = 0;",
        encoding="utf-8",
    )
    summary = tmp_path / "summary.json"
    summary.write_text(
        json.dumps(
            {
                "event_counts": {
                    "md_register_front": 1,
                    "md_init_call": 1,
                    "md_login_dispatch_return": 156,
                    "front_disconnected": 155,
                },
                "login_response_count": 0,
                "rsp_error_count": 0,
                "heartbeat_warning_count": 0,
                "tick_count": 0,
                "native_close_detail": {
                    "dispatch_to_disconnect_us": {"count": 155, "avg": 97690.013}
                },
                "diagnosis": {"response_missing_after_dispatch": True},
            }
        ),
        encoding="utf-8",
    )
    smoke = tmp_path / "smoke.json"
    smoke.write_text(
        json.dumps(
            {
                "success": False,
                "failure_reason": "login_failed",
                "init_code": 0,
                "login_request_code": 0,
                "subscribe_code": -1,
                "front_connected_count": 156,
                "disconnect_count": 155,
                "first_tick_symbol": None,
            }
        ),
        encoding="utf-8",
    )
    flow = tmp_path / "flow"
    flow.mkdir()
    (flow / "repo_md_lifecycle_trace.jsonl").write_text("{}", encoding="utf-8")

    payload = build_diagnostic(
        config_path=config,
        sdk_struct_header=struct_header,
        md_api_header=md_header,
        lifecycle_summary_path=summary,
        smoke_path=smoke,
        flow_path=flow,
    )

    assert payload["status"] == "blocked"
    assert payload["sdk_capability"]["auth_app_supported_by_md_req_user_login"] == {
        "auth_code": False,
        "app_id": False,
        "md_api_uses_sc_login_struct": False,
    }
    assert payload["sdk_capability"]["req_user_login_sc_fields_include_auth_app"] is True
    assert payload["redacted_config_shape"]["password"] == {
        "present": True,
        "length": 11,
        "raw_value_recorded": False,
    }
    assert payload["redacted_config_shape"]["auth_code"] == {
        "present": True,
        "length": 11,
        "raw_value_recorded": False,
    }
    assert payload["redacted_config_shape"]["md_front"] == {
        "present": True,
        "length": 25,
        "tcp_scheme": True,
        "raw_value_recorded": False,
    }
    assert payload["flow_path_diagnostic"]["repo_trace_present"] is True
    assert payload["interpretation"]["md_auth_app_payload_gap_confirmed"] is True
    assert payload["negative_assertions"]["did_not_submit_broker_order"] is True
    assert payload["negative_assertions"]["secret_values_recorded"] is False
