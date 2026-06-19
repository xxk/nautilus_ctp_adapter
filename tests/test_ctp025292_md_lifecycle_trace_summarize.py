from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ctp025292_md_lifecycle_trace_summarize import build_summary


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_summary_blocks_when_dispatch_returns_without_login_response(tmp_path: Path) -> None:
    trace = tmp_path / "repo_md_lifecycle_trace.jsonl"
    trace.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts_epoch_us": 900,
                        "event": "md_register_front",
                        "front_present": True,
                        "front_len": 19,
                        "front_tcp_scheme": True,
                        "raw_values_recorded": False,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 950,
                        "event": "md_init_call",
                        "already_initialized": False,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 960,
                        "event": "md_init_return",
                        "call_completed": True,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 1000,
                        "event": "front_connected",
                        "login_requested": True,
                        "login_dispatched": False,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 1100,
                        "event": "md_login_payload_shape",
                        "request_id": 1,
                        "broker_id_present": True,
                        "broker_id_len": 4,
                        "user_id_present": True,
                        "user_id_len": 6,
                        "password_present": True,
                        "password_len": 8,
                        "user_product_info_present": True,
                        "user_product_info_len": 6,
                        "interface_product_info_present": False,
                        "interface_product_info_len": 0,
                        "protocol_info_present": False,
                        "protocol_info_len": 0,
                        "mac_address_present": False,
                        "mac_address_len": 0,
                        "client_ip_address_present": False,
                        "client_ip_address_len": 0,
                        "login_remark_present": False,
                        "login_remark_len": 0,
                        "raw_values_recorded": False,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 1200,
                        "event": "md_login_dispatch_return",
                        "request_id": 1,
                        "return_code": 0,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 2200,
                        "event": "front_disconnected",
                        "reason": 0,
                        "login_requested": True,
                        "login_dispatched_before_disconnect": True,
                        "connected_before_disconnect": True,
                        "pending_login_request_id": 1,
                        "dispatch_to_disconnect_us": 1000,
                        "connected_to_disconnect_us": 1200,
                        "last_login_return_code": 0,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 2300,
                        "event": "md_rsp_error",
                        "request_id": 1,
                        "is_last": True,
                        "error_id": 3,
                        "error_message_present": True,
                        "error_message_len": 12,
                        "raw_values_recorded": False,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 2400,
                        "event": "md_heartbeat_warning",
                        "time_lapse": 9,
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = build_summary(trace)

    assert payload["status"] == "blocked"
    assert payload["blocker_id"] == "ctp025292_marketdata_login_response_missing_after_runtime_lineage"
    assert payload["connected_count"] == 1
    assert payload["dispatch_count"] == 1
    assert payload["payload_shape_count"] == 1
    assert payload["register_front_count"] == 1
    assert payload["init_call_count"] == 1
    assert payload["init_return_count"] == 1
    assert payload["rsp_error_count"] == 1
    assert payload["heartbeat_warning_count"] == 1
    assert payload["disconnect_count"] == 1
    assert payload["login_response_count"] == 0
    assert payload["return_codes"] == [0]
    assert payload["disconnect_reasons"] == [0]
    assert payload["diagnosis"]["response_missing_after_dispatch"] is True
    assert payload["diagnosis"]["all_dispatch_returns_ok"] is True
    assert payload["diagnosis"]["all_disconnect_reasons_zero"] is True
    assert payload["diagnosis"]["payload_shape_trace_available"] is True
    assert payload["diagnosis"]["front_registration_trace_available"] is True
    assert payload["diagnosis"]["init_trace_available"] is True
    assert payload["diagnosis"]["rsp_error_trace_available"] is True
    assert payload["diagnosis"]["heartbeat_warning_trace_available"] is True
    assert payload["diagnosis"]["disconnect_latency_trace_available"] is True
    assert payload["diagnosis"]["disconnect_pending_login_trace_available"] is True
    assert payload["native_close_detail"]["front_shape_summary"] == {
        "event_count": 1,
        "present_counts": {"true": 1, "false": 0, "missing": 0},
        "tcp_scheme_counts": {"true": 1, "false": 0, "missing": 0},
        "lengths": [19],
        "raw_values_recorded": False,
    }
    assert payload["native_close_detail"]["rsp_error_summary"] == {
        "event_count": 1,
        "error_ids": [3],
        "message_present_counts": {"true": 1, "false": 0, "missing": 0},
        "message_lengths": [12],
        "raw_values_recorded": False,
    }
    assert payload["native_close_detail"]["dispatch_to_disconnect_us"] == {
        "count": 1,
        "min": 1000.0,
        "max": 1000.0,
        "avg": 1000.0,
    }
    assert payload["native_close_detail"]["last_login_return_codes"] == [0]
    assert payload["payload_shape_summary"]["raw_values_recorded"] is False
    assert payload["payload_shape_summary"]["fields"]["password"] == {
        "present_counts": {"true": 1, "false": 0, "missing": 0},
        "lengths": [8],
        "raw_values_recorded": False,
    }
    assert payload["payload_shape_summary"]["fields"]["interface_product_info"] == {
        "present_counts": {"true": 0, "false": 1, "missing": 0},
        "lengths": [0],
        "raw_values_recorded": False,
    }
    assert payload["disconnect_state_summary"]["login_dispatched_before_disconnect"] == {
        "true": 1,
        "false": 0,
        "missing": 0,
    }
    assert payload["disconnect_state_summary"]["pending_login_request_ids"] == [1]
    assert payload["negative_assertions"]["did_not_submit_broker_order"] is True


def test_cli_writes_summary_json(tmp_path: Path) -> None:
    trace = tmp_path / "repo_md_lifecycle_trace.jsonl"
    output = tmp_path / "summary.json"
    trace.write_text(
        json.dumps(
            {
                "ts_epoch_us": 1000,
                "event": "md_login_dispatch_return",
                "request_id": 1,
                "return_code": 0,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ctp025292_md_lifecycle_trace_summarize.py"),
            "--trace",
            str(trace),
            "--output-json",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["trace_path"] == str(trace)
    assert payload["dispatch_count"] == 1


def test_summary_preserves_zero_pending_login_request_id_for_diagnostics(tmp_path: Path) -> None:
    trace = tmp_path / "repo_md_lifecycle_trace.jsonl"
    trace.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts_epoch_us": 1000,
                        "event": "md_login_payload_shape",
                        "request_id": 0,
                        "request_id_zero_override": True,
                        "raw_values_recorded": False,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 1100,
                        "event": "md_login_dispatch_return",
                        "request_id": 0,
                        "request_id_zero_override": True,
                        "return_code": 0,
                    }
                ),
                json.dumps(
                    {
                        "ts_epoch_us": 1200,
                        "event": "front_disconnected",
                        "reason": 0,
                        "login_dispatched_before_disconnect": True,
                        "pending_login_request_id": 0,
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = build_summary(trace)

    assert payload["request_id_min"] == 0
    assert payload["request_id_max"] == 0
    assert payload["payload_shape_summary"]["request_ids"] == [0]
    assert payload["disconnect_state_summary"]["pending_login_request_ids"] == [0]
