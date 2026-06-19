from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_SOURCE = REPO_ROOT / "rust" / "ctp_runtime_core" / "native" / "ctp_vendor_bridge.cpp"


def test_td_order_send_records_comb_offset_at_native_submit_boundary_before_req_order_insert() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    function_start = source.index("extern \"C\" std::int32_t repo_ctp_td_order_send")
    function_end = source.index("extern \"C\" std::int32_t repo_ctp_td_order_action", function_start)
    function_body = source[function_start:function_end]

    offset_assignment = "order.CombOffsetFlag[0] = offset_text.empty() ? THOST_FTDC_OF_Open : offset_text[0];"
    remember_call = "remember_td_submit_offset_locked("
    submit_field = "normalize_enum_value(order.CombOffsetFlag[0])"
    req_order_insert = "api->ReqOrderInsert(&order, request_id)"

    assert offset_assignment in function_body
    assert remember_call in function_body
    assert submit_field in function_body
    assert req_order_insert in function_body
    assert function_body.index(offset_assignment) < function_body.index(remember_call)
    assert function_body.index(remember_call) < function_body.index(req_order_insert)


def test_order_insert_callbacks_report_submit_boundary_offset_separately_from_response_offset() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    on_rsp_start = source.index("void TdSpiImpl::OnRspOrderInsert")
    on_rsp_end = source.index("void TdSpiImpl::OnErrRtnOrderInsert", on_rsp_start)
    on_rsp_body = source[on_rsp_start:on_rsp_end]

    assert "resolve_td_submit_offset_locked(*session_ptr, normalized_text(input_order->OrderRef))" in on_rsp_body
    assert "normalize_enum_value(input_order->CombOffsetFlag[0])" in on_rsp_body
    assert "submit_request_offset_flag" in on_rsp_body
    assert "submit_offset_source_for(submit_request_offset_flag)" in on_rsp_body
    assert on_rsp_body.index("resolve_td_submit_offset_locked") < on_rsp_body.index("const NativeExec snapshot")
