from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_SOURCE = REPO_ROOT / "rust" / "ctp_runtime_core" / "native" / "ctp_vendor_bridge.cpp"


def test_md_native_lifecycle_trace_records_payload_shape_without_raw_values() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    assert '"md_login_payload_shape"' in source
    assert '"request_id_zero_override"' in source
    assert 'text_shape_fields("password", request.password)' in source
    assert 'text_shape_fields("broker_id", request.broker_id)' in source
    assert 'text_shape_fields("client_ip_address", request.client_ip_address)' in source
    assert '\\"raw_values_recorded\\":false' in source

    payload_trace_start = source.index('"md_login_payload_shape"')
    payload_trace_end = source.index("const std::int32_t return_code", payload_trace_start)
    payload_trace_block = source[payload_trace_start:payload_trace_end]

    assert "request.password" in payload_trace_block
    assert 'json_escape(request.password)' not in payload_trace_block
    assert 'request.password + ' not in payload_trace_block
    assert 'request.client_ip_address + ' not in payload_trace_block


def test_md_native_request_id_zero_override_is_explicit_md_diagnostic_only() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    assert "NAUTILUS_CTP_MD_LOGIN_REQUEST_ID_ZERO" in source
    assert "env_flag_enabled(" in source
    assert "const bool request_id_zero_override" in source
    assert "const std::int32_t request_id = request_id_zero_override ? 0 : session->next_request_id++;" in source
    assert "session->last_login_request_id = request_id;" in source


def test_md_native_empty_flow_override_is_explicit_md_diagnostic_only() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    assert "NAUTILUS_CTP_MD_CREATE_EMPTY_FLOW" in source
    assert "const bool create_empty_flow_override" in source
    assert 'const char* api_flow_path = create_empty_flow_override ? "" : session->flow_path.c_str();' in source
    assert "CThostFtdcMdApi::CreateFtdcMdApi(api_flow_path, false, false)" in source
    assert '"api_flow_path_empty_override"' in source
    assert '"api_flow_path_present"' in source


def test_md_native_disconnect_trace_records_pending_login_state() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    assert '"login_requested"' in source
    assert '"login_dispatched_before_disconnect"' in source
    assert '"connected_before_disconnect"' in source
    assert '"pending_login_request_id"' in source
    assert '"dispatch_to_disconnect_us"' in source
    assert '"connected_to_disconnect_us"' in source
    assert '"last_login_return_code"' in source
    assert "pending_login_request_id = session_ptr->login_dispatched ? session_ptr->last_login_request_id : 0;" in source


def test_md_native_close_reason_trace_records_front_init_and_spi_errors_without_raw_values() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    assert '"md_api_created"' in source
    assert '"md_register_spi"' in source
    assert '"md_register_front"' in source
    assert '"md_init_call"' in source
    assert '"md_init_return"' in source
    assert '"md_rsp_error"' in source
    assert '"md_heartbeat_warning"' in source
    assert "front_shape_fields(session->front)" in source
    assert 'text_shape_fields("error_message", error_message)' in source

    front_trace_start = source.index('"md_register_front"')
    front_trace_end = source.index("session->api->RegisterFront", front_trace_start)
    front_trace_block = source[front_trace_start:front_trace_end]
    assert "session->front" in front_trace_block
    assert "json_escape(session->front)" not in front_trace_block

    rsp_error_start = source.index('"md_rsp_error"')
    rsp_error_end = source.index("void MdSpiImpl::OnHeartBeatWarning", rsp_error_start)
    rsp_error_block = source[rsp_error_start:rsp_error_end]
    assert "error_message" in rsp_error_block
    assert "json_escape(error_message)" not in rsp_error_block
    assert '\\"raw_values_recorded\\":false' in source
