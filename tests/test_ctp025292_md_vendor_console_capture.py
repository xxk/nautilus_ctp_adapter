from __future__ import annotations

import argparse
import json
from pathlib import Path

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from scripts.ctp025292_md_vendor_console_capture import (
    _redaction_pairs,
    classify_console_lines,
    redact_text,
)


def test_vendor_console_classifies_native_disconnect_and_spi_prompts() -> None:
    summary = classify_console_lines(
        "\n".join(
            [
                '{"baseline":"md-login-smoke-v1"}',
                "MD OnRspUserLogin called: pRspInfo=PTR, pRspUserLogin=PTR",
                "  ErrorID=0, ErrorMsg=CTP:No Error",
                "CThostFtdcUserApiImplBase::OnSessionDisconnected[PTR][123][ 4097]",
                "TICK rb2610 last=3137 bid=3136 ask=3137",
            ]
        ),
        "Host OnFrontDisconnected nReason: 4097\n",
    )

    assert summary["json_stdout_line_count"] == 1
    assert summary["non_json_console_line_count"] == 5
    assert summary["matched_line_counts"]["native_session_disconnect"] == 1
    assert summary["matched_line_counts"]["front_disconnect"] == 2
    assert summary["matched_line_counts"]["login_response"] == 1
    assert summary["matched_line_counts"]["rsp_error"] == 1
    assert summary["matched_line_counts"]["tick"] == 1


def test_vendor_console_redacts_config_and_cli_values() -> None:
    config = CtpAdapterConfig(
        broker_id="0155",
        user_id="025292",
        password="secret-password",
        auth_code="auth-token",
        app_id="client_app",
        product_info="iQuant",
        md_front="tcp://180.168.159.225:51213",
        td_front="tcp://180.168.159.225:51205",
        instruments=["ag2612"],
    )
    pairs = _redaction_pairs(
        config,
        cli_values=[
            ("md_front", "tcp://10.1.2.3:51213"),
            ("md_protocol_info", "Q7 155"),
        ],
    )

    redacted = redact_text(
        "025292 secret-password tcp://180.168.159.225:51213 tcp://10.1.2.3:51213 Q7 155",
        pairs,
    )

    assert "025292" not in redacted
    assert "secret-password" not in redacted
    assert "180.168.159.225" not in redacted
    assert "10.1.2.3" not in redacted
    assert "Q7 155" not in redacted
    assert "<redacted:user_id:len=6>" in redacted
    assert "<redacted:password:len=15>" in redacted
    assert "<redacted:md_front:tcp_len=27>" in redacted
    assert "<redacted:md_front:tcp_len=20>" in redacted
    assert "<redacted:md_protocol_info:len=6>" in redacted


def test_vendor_console_capture_builds_md_only_redacted_payload(monkeypatch, tmp_path: Path) -> None:
    from scripts import ctp025292_md_vendor_console_capture as module

    config_path = tmp_path / "ctp.json"
    config_path.write_text(
        json.dumps(
            {
                "broker_id": "0155",
                "user_id": "025292",
                "password": "secret-password",
                "md_front": "tcp://180.168.159.225:51213",
                "td_front": "tcp://180.168.159.225:51205",
                "product_info": "iQuant",
                "instruments": ["ag2612"],
            }
        ),
        encoding="utf-8",
    )

    class Completed:
        returncode = 1
        stdout = (
            "MD OnRspUserLogin called: pRspInfo=PTR, pRspUserLogin=PTR\n"
            '{"baseline":"md-login-smoke-v1"}\n'
            "CThostFtdcUserApiImplBase::OnSessionDisconnected[PTR][123][ 4097]\n"
            "user 025292 password secret-password tcp://180.168.159.225:51213\n"
        )
        stderr = ""

    smoke_output = tmp_path / "smoke.json"

    def fake_run(*args, **kwargs):
        smoke_output.write_text(
            json.dumps(
                {
                    "success": False,
                    "failure_reason": "login_failed",
                    "login_success": False,
                    "front_connected_count": 1,
                    "disconnect_count": 1,
                    "first_tick_symbol": None,
                }
            ),
            encoding="utf-8",
        )
        return Completed()

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    payload = module.build_capture(
        argparse.Namespace(
            config=config_path,
            timeout_seconds=1,
            extra_timeout_seconds=1,
            flow_path=tmp_path / "flow",
            output_json=tmp_path / "capture.json",
            smoke_output_json=smoke_output,
            instrument=["ag2612"],
            md_front=None,
            md_user_product_info=None,
            md_interface_product_info=None,
            md_protocol_info=None,
            md_mac_address=None,
            md_client_ip_address=None,
            md_login_remark=None,
            runtime_pack_bin=tmp_path / "runtime-pack" / "bin",
            python_exe="python",
        )
    )

    serialized = json.dumps(payload, ensure_ascii=False)
    assert payload["status"] == "blocked"
    assert payload["command"]["runtime_pack_strict"] is True
    assert payload["negative_assertions"]["did_not_run_td_script"] is True
    assert payload["console_capture"]["summary"]["matched_line_counts"]["login_response"] == 1
    assert payload["console_capture"]["summary"]["matched_line_counts"]["native_session_disconnect"] == 1
    assert "025292" in serialized  # account id may appear only in typed route identity fields.
    assert "secret-password" not in serialized
    assert "180.168.159.225" not in serialized
    assert payload["console_capture"]["raw_secret_values_recorded"] is False
    assert payload["console_capture"]["raw_front_values_recorded"] is False
    assert "effective_config_json" not in payload["artifacts"]
