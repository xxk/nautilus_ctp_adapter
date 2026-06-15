from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import scripts.ctp_guarded_paper_order_loop as order_loop
from scripts.ctp_guarded_paper_order_loop import (
    build_intent_contract,
    classify_lifecycle_events,
    reconcile_pre_post_snapshots,
    validate_order_command_contract,
    validate_pre_order_snapshot,
)
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpMappedOrderCommand
from nautilus_ctp_adapter.runtime import (
    CtpRuntimeCommand,
    CtpRuntimeCommandKind,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
)


def _snapshot(
    path: Path,
    *,
    success: bool = True,
    profile: str = "openctp-tts-7x24-simulation",
    run_id: str = "run-1",
) -> Path:
    path.write_text(
        json.dumps(
            {
                "success": success,
                "schema": {
                    "run_id": run_id,
                    "account_profile": profile,
                    "evidence_class": "openctp-tts-7x24-simulation",
                    "reconciliation_role": "pre_or_post_order_snapshot",
                },
                "positions": {
                    "position_count": 1,
                    "records": [
                        {
                            "venue_symbol": "c2609",
                            "exchange_id": "DCE",
                            "direction": "SHORT",
                            "position_qty": 3,
                            "yd_position_qty": 2,
                            "td_position_qty": 1,
                        }
                    ],
                },
                "instruments": {
                    "records": [
                        {
                            "venue_symbol": "c2609",
                            "exchange_id": "DCE",
                            "price_tick": 1.0,
                            "volume_multiple": 10,
                            "detail_fields": {
                                "instrument_name": "Iron Ore",
                                "open_date": "20250101",
                                "expire_date": "20260930",
                                "is_trading": None,
                                "min_limit_order_volume": None,
                                "max_limit_order_volume": None,
                                "product_id": "i",
                                "underlying_instr_id": "i2609",
                                "delivery_year": 2026,
                                "delivery_month": 9,
                            },
                        }
                    ]
                },
                "account": {
                    "identity": {
                        "account_id_present": True,
                        "account_id_fingerprint": "redacted-fixture",
                    },
                    "balance_present": True,
                    "available_present": True,
                    "margin_present": True,
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_pre_order_snapshot_accepts_phase2_paper_snapshot(tmp_path: Path) -> None:
    verdict = validate_pre_order_snapshot(_snapshot(tmp_path / "pre.json"))

    assert verdict["accepted"] is True
    assert verdict["issues"] == []


def test_pre_order_snapshot_rejects_missing_or_wrong_profile(tmp_path: Path) -> None:
    missing = validate_pre_order_snapshot(tmp_path / "missing.json")
    assert missing["accepted"] is False
    assert "pre_snapshot_missing" in missing["issues"]

    wrong_profile = validate_pre_order_snapshot(
        _snapshot(tmp_path / "formal.json", profile="formal-trading")
    )
    assert wrong_profile["accepted"] is False
    assert "pre_snapshot_account_profile" in wrong_profile["issues"]


def test_build_intent_contract_captures_order_correctness_fields() -> None:
    contract = build_intent_contract(
        instrument="TEST",
        side="BUY",
        quantity=1,
        limit_price=1.0,
        position_effect="OPEN",
        price_mode="best_level_1",
        client_order_id="paper-1",
    )

    assert contract == {
        "instrument": "TEST",
        "side": "BUY",
        "quantity": 1,
        "limit_price": 1.0,
        "position_effect": "OPEN",
        "order_type": "LIMIT",
        "time_in_force": "GFD",
        "price_mode": "best_level_1",
        "client_order_id": "paper-1",
    }


def test_order_boundary_accepts_tick_aligned_price_from_snapshot_metadata(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))

    verdict = order_loop.validate_order_boundary_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        limit_price=2300.0,
    )

    assert verdict["accepted"] is True
    assert verdict["issues"] == []
    assert verdict["instrument"]["price_tick"] == 1.0


def test_order_boundary_blocks_off_tick_zero_price_and_missing_metadata(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))

    off_tick = order_loop.validate_order_boundary_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        limit_price=2300.5,
    )
    zero_price = order_loop.validate_order_boundary_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        limit_price=0.0,
    )
    missing = order_loop.validate_order_boundary_from_snapshot(
        payload,
        instrument="missing",
        quantity=1,
        limit_price=1.0,
    )

    assert off_tick["accepted"] is False
    assert "off_tick_price" in off_tick["issues"]
    assert zero_price["accepted"] is False
    assert "invalid_limit_price" in zero_price["issues"]
    assert missing["accepted"] is False
    assert "instrument_metadata_missing" in missing["issues"]


def test_order_boundary_blocks_invalid_quantity_before_native_send(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))

    verdict = order_loop.validate_order_boundary_from_snapshot(
        payload,
        instrument="c2609",
        quantity=0,
        limit_price=2300.0,
    )

    assert verdict["accepted"] is False
    assert "invalid_quantity" in verdict["issues"]


def test_order_boundary_blocks_non_tradable_and_min_max_volume_violations(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    payload["instruments"]["records"][0]["detail_fields"]["is_trading"] = False
    payload["instruments"]["records"][0]["detail_fields"]["min_limit_order_volume"] = 2
    payload["instruments"]["records"][0]["detail_fields"]["max_limit_order_volume"] = 3

    verdict = order_loop.validate_order_boundary_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        limit_price=2300.0,
    )

    assert verdict["accepted"] is False
    assert "instrument_not_tradable" in verdict["issues"]
    assert "min_limit_order_volume_violated" in verdict["issues"]


def test_order_boundary_blocks_invalid_lifecycle_dates(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    payload["instruments"]["records"][0]["detail_fields"]["open_date"] = "2025-01-01"
    payload["instruments"]["records"][0]["detail_fields"]["expire_date"] = "2026/09/30"

    verdict = order_loop.validate_order_boundary_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        limit_price=2300.0,
    )

    assert verdict["accepted"] is False
    assert "open_date_invalid" in verdict["issues"]
    assert "expire_date_invalid" in verdict["issues"]


def test_risk_facts_are_loaded_from_redacted_snapshot(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    payload["account"] = {
        "identity": {
            "account_id_present": True,
            "account_id_fingerprint": "redacted-fixture",
        },
        "balance_present": True,
        "available_present": True,
        "margin_present": True,
    }

    facts = order_loop.extract_risk_facts_from_snapshot(payload, instrument="c2609")

    assert facts["account"]["account_id_fingerprint"] == "redacted-fixture"
    assert facts["account"]["balance_present"] is True
    assert facts["account"]["available_present"] is True
    assert facts["account"]["margin_present"] is True
    assert facts["account"]["numeric_values_redacted"] is True
    assert "available" not in facts["account"]
    assert facts["positions"]["short_qty"] == 3
    assert facts["positions"]["net_position"] == -3


def test_risk_preflight_passes_dry_run_with_redacted_account_metrics(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    config = order_loop.CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "u",
            "Password": "p",
            "Pricer": "tcp://md",
            "Host": "tcp://td",
            "Instruments": ["c2609"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 3,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
            },
        }
    )

    verdict = order_loop.build_risk_preflight_from_snapshot(
        payload,
        config=config,
        instrument="c2609",
        side="BUY",
        quantity=1,
        position_effect="OPEN",
        client_order_id="risk-1",
        arm_paper_send=False,
    )

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "risk_preflight_passed"
    assert verdict["projected_net_position"] == -2
    assert verdict["facts"]["account"]["numeric_values_redacted"] is True
    assert verdict["facts"]["instrument"]["detail_fields"]["delivery_year"] == 2026


def test_risk_preflight_blocks_guardrail_failures_before_native_send(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    config = order_loop.CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "u",
            "Password": "p",
            "Pricer": "tcp://md",
            "Host": "tcp://td",
            "Instruments": ["c2609"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 3,
                "MaxSubmitPerMinute": 2,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
            },
        }
    )

    verdict = order_loop.build_risk_preflight_from_snapshot(
        payload,
        config=config,
        instrument="rb2610",
        side="SELL",
        quantity=4,
        position_effect="OPEN",
        client_order_id="dup-1",
        arm_paper_send=True,
        submit_count_last_minute=2,
        session_send_count=5,
        session_send_budget=5,
        seen_client_order_ids=["dup-1"],
    )

    assert verdict["accepted"] is False
    assert verdict["disposition"] == "risk_preflight_failed"
    assert verdict["native_send_allowed"] is False
    assert "kill_switch_closed" in verdict["issues"]
    assert "instrument_not_allowed" in verdict["issues"]
    assert "max_order_qty_exceeded" in verdict["issues"]
    assert "max_net_position_exceeded" in verdict["issues"]
    assert "frequency_cap_exceeded" in verdict["issues"]
    assert "session_send_budget_exceeded" in verdict["issues"]
    assert "duplicate_client_order_id" in verdict["issues"]


def test_risk_preflight_allows_armed_verified_exposure_reduction_only(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    config = order_loop.CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "u",
            "Password": "p",
            "Pricer": "tcp://md",
            "Host": "tcp://td",
            "Instruments": ["c2609"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 3,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
                "AllowExposureReductionOrderSmoke": True,
            },
        }
    )

    verdict = order_loop.build_risk_preflight_from_snapshot(
        payload,
        config=config,
        instrument="c2609",
        side="BUY",
        quantity=1,
        position_effect="CLOSE",
        client_order_id="reduce-1",
        arm_paper_send=True,
    )

    assert verdict["accepted"] is True
    assert verdict["native_send_allowed"] is True
    assert verdict["projected_net_position"] == -2
    assert verdict["verified_exposure_reduction"] is True
    assert verdict["guards"]["kill_switch"]["accepted"] is True
    assert verdict["guards"]["kill_switch"]["exposure_reduction_override"] is True


def test_risk_preflight_does_not_treat_open_as_exposure_reduction(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    config = order_loop.CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "u",
            "Password": "p",
            "Pricer": "tcp://md",
            "Host": "tcp://td",
            "Instruments": ["c2609"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 3,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
                "AllowExposureReductionOrderSmoke": True,
            },
        }
    )

    verdict = order_loop.build_risk_preflight_from_snapshot(
        payload,
        config=config,
        instrument="c2609",
        side="BUY",
        quantity=1,
        position_effect="OPEN",
        client_order_id="open-1",
        arm_paper_send=True,
    )

    assert verdict["accepted"] is False
    assert "kill_switch_closed" in verdict["issues"]
    assert verdict["verified_exposure_reduction"] is False
    assert verdict["guards"]["kill_switch"]["exposure_reduction_override"] is False


def test_guarded_loop_dry_run_accepts_exposure_reduction_config_flag(tmp_path: Path) -> None:
    pre_snapshot_path = _snapshot(tmp_path / "pre.json")
    payload = json.loads(pre_snapshot_path.read_text(encoding="utf-8"))
    payload["positions"]["records"] = [
        {
            "venue_symbol": "c2609",
            "exchange_id": "DCE",
            "direction": "SHORT",
            "position_qty": 3,
            "yd_position_qty": 2,
            "td_position_qty": 1,
        }
    ]
    pre_snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "BrokerID": "9999",
                "UserID": "u",
                "Password": "p",
                "Pricer": "tcp://trading.openctp.cn:30011",
                "Host": "tcp://trading.openctp.cn:30001",
                "Instruments": ["c2609"],
                "ExecutionGuardrails": {
                    "Enabled": True,
                    "AllowedInstruments": ["c2609"],
                    "MaxOrderQty": 3,
                    "MaxNetPosition": 5,
                    "MaxSubmitPerMinute": 10,
                    "PriceMode": "best_level_1",
                    "AllowLiveOrderSmoke": False,
                    "AllowExposureReductionOrderSmoke": True,
                },
            }
        ),
        encoding="utf-8",
    )

    result = order_loop.run_guarded_paper_order(
        config_path=config_path,
        pre_snapshot=pre_snapshot_path,
        post_snapshot=None,
        instrument="c2609",
        side="BUY",
        quantity=1,
        limit_price=2300.0,
        position_effect="CLOSE",
        client_order_id="dry-run-reduce-1",
        timeout_seconds=1,
        arm_paper_send=False,
        close_from_pre_snapshot=False,
        expected_pre_snapshot_run_id=None,
        close_position_direction="SHORT",
        submit_count_last_minute=0,
        session_send_count=0,
        session_send_budget=1,
        seen_client_order_ids=[],
    )

    assert result["failure_reason"] != "config_validation_failed"
    assert result["paper_send_armed"] is False
    assert result["risk_preflight"]["projected_net_position"] == -2
    assert result["risk_preflight"]["verified_exposure_reduction"] is False
    assert result["order_contract"]["accepted"] is True


def test_guarded_loop_lifecycle_events_preserve_native_diagnostic_fields(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pre_snapshot_path = _snapshot(tmp_path / "pre.json")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "BrokerID": "9999",
                "UserID": "u",
                "Password": "p",
                "Pricer": "tcp://trading.openctp.cn:30011",
                "Host": "tcp://trading.openctp.cn:30001",
                "Instruments": ["c2609"],
                "ExecutionGuardrails": {
                    "Enabled": True,
                    "AllowedInstruments": ["c2609"],
                    "MaxOrderQty": 3,
                    "MaxNetPosition": 5,
                    "MaxSubmitPerMinute": 10,
                    "PriceMode": "best_level_1",
                    "AllowLiveOrderSmoke": False,
                    "AllowExposureReductionOrderSmoke": True,
                },
            }
        ),
        encoding="utf-8",
    )

    class FakeBridge:
        def drain_submitted_commands(self):
            return [
                CtpRuntimeCommand(
                    kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
                    client_order_id="close-diagnostics",
                    venue_symbol="c2609",
                    request_id="submit-42",
                    payload={
                        "instrument": "c2609",
                        "side": "BUY",
                        "quantity": "1",
                        "limit_price": "2300.0",
                        "position_effect": "CLOSE",
                        "native_comb_offset": "1",
                        "order_type": "LIMIT",
                        "time_in_force": "GFD",
                        "order_ref": "7",
                        "submit_request_id": "42",
                        "submit_request_id_source_field": (
                            "CtpRuntimeCommand.request_id -> TdOrderSend.request_id -> "
                            "CTP ReqOrderInsert nRequestID"
                        ),
                    },
                )
            ]

        def drain_events(self):
            return [
                CtpRuntimeEvent(
                    kind=CtpRuntimeEventKind.ORDER,
                    client_order_id="close-diagnostics",
                    venue_symbol="c2609",
                    message="�ֲֲ���",
                    payload={
                        "native_order_id": "7",
                        "native_order_ref": "7",
                        "status": "53",
                        "trade_volume": "0",
                        "trade_price": "0.0",
                        "leaves_qty": "0",
                        "side": "0",
                        "direction": "1",
                        "offset_flag": "1",
                        "response_request_id": "42",
                        "response_is_last": "1",
                        "response_error_id": "31",
                        "hedge_flag": "1",
                        "error_msg": "�ֲֲ���",
                    },
                )
            ]

    class FakeExecutionClient:
        def run_order_lifecycle_smoke_baseline(self, **_kwargs):
            return SimpleNamespace(
                bootstrap=SimpleNamespace(ready=True),
                mapped_submit=CtpMappedOrderCommand(
                    command=FakeBridge().drain_submitted_commands()[0],
                    client_order_id="close-diagnostics",
                    order_ref=7,
                    front_id=1,
                    session_id=2,
                    error=None,
                ),
                dry_run=False,
                live_send_armed=True,
                matched_execs=[
                    SimpleNamespace(
                        python_client_order_id="close-diagnostics",
                        native_order_id="7",
                        native_order_ref="7",
                        venue_symbol="c2609",
                        front_id=1,
                        session_id=2,
                        status=53,
                        callback_source="OnRtnOrder",
                        offset_flag=1,
                        submit_request_offset_flag=1,
                        submit_request_offset_source=(
                            "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
                        ),
                        submit_request_id=42,
                        submit_request_id_source=(
                            "CtpRuntimeCommand.request_id -> TdOrderSend.request_id -> "
                            "CTP ReqOrderInsert nRequestID"
                        ),
                        response_request_id=42,
                        response_is_last=True,
                        response_error_id=31,
                        is_trade=False,
                        trade_volume=0,
                        leaves_qty=0,
                        match_reason="order_ref_echo",
                    )
                ],
            )

    bridge = FakeBridge()
    monkeypatch.setattr(
        order_loop,
        "build_ctp_stack",
        lambda _config: {"execution_client": FakeExecutionClient(), "runtime_bridge": bridge},
    )

    result = order_loop.run_guarded_paper_order(
        config_path=config_path,
        pre_snapshot=pre_snapshot_path,
        post_snapshot=None,
        instrument="c2609",
        side="BUY",
        quantity=1,
        limit_price=2300.0,
        position_effect="CLOSE",
        client_order_id="close-diagnostics",
        timeout_seconds=1,
        arm_paper_send=True,
        close_from_pre_snapshot=False,
        expected_pre_snapshot_run_id=None,
        close_position_direction="SHORT",
        submit_count_last_minute=0,
        session_send_count=0,
        session_send_budget=1,
        seen_client_order_ids=[],
    )

    event = result["order_lifecycle"]["lifecycle_events"][0]
    matched_exec = result["order_lifecycle"]["matched_execs"][0]
    assert result["order_lifecycle"]["matched_exec_count"] == 1
    assert matched_exec["python_client_order_id"] == "close-diagnostics"
    assert matched_exec["native_order_ref"] == "7"
    assert matched_exec["match_reason"] == "order_ref_echo"
    assert matched_exec["callback_source"] == "OnRtnOrder"
    assert matched_exec["offset_flag"] == 1
    assert matched_exec["submit_request_offset_flag"] == 1
    assert (
        matched_exec["submit_request_offset_source"]
        == "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
    )
    assert matched_exec["response_request_id"] == 42
    assert matched_exec["response_is_last"] is True
    assert matched_exec["response_error_id"] == 31
    assert event["side"] == "0"
    assert event["direction"] == "1"
    assert event["offset_flag"] == "1"
    assert event["response_request_id"] == "42"
    assert event["response_is_last"] == "1"
    assert event["response_error_id"] == "31"
    assert event["hedge_flag"] == "1"
    assert result["mapped_submit"]["command_payload"]["native_comb_offset"] == "1"
    assert event["submit_request_id"] == result["mapped_submit"]["command_payload"]["submit_request_id"]
    assert (
        event["submit_request_id_source"]
        == result["mapped_submit"]["command_payload"]["submit_request_id_source_field"]
    )
    assert matched_exec["submit_request_id"] == 42
    assert (
        matched_exec["submit_request_id_source"]
        == "CtpRuntimeCommand.request_id -> TdOrderSend.request_id -> CTP ReqOrderInsert nRequestID"
    )
    assert (
        result["native_offset_semantics"]["disposition"]
        == "callback_offset_matches_submit_native_comb_offset"
    )
    assert event["error_text_contains_replacement_char"] is True
    assert result["order_lifecycle"]["verdict"]["disposition"] == "cancelled"
    diagnostics = result["order_lifecycle"]["verdict"]["native_status_diagnostics"]
    assert diagnostics["observed_statuses"] == ["53"]
    assert (
        diagnostics["ctp_status_meanings"]["53"]
        == "ascii_code_53_for_ctp_order_status_char_5_cancelled"
    )
    assert diagnostics["disposition"] == "ctp_cancelled_status_without_fill"
    assert diagnostics["semantic_reason"] == "undetermined_from_status_only"
    assert diagnostics["error_text_contains_replacement_char"] is True
    assert diagnostics["broker_semantic_reason_inferred"] is False


def test_guarded_loop_payload_blocks_partial_source_context_retry_authority(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pre_snapshot_path = _snapshot(tmp_path / "pre.json")
    pre_payload = json.loads(pre_snapshot_path.read_text(encoding="utf-8"))
    pre_payload["positions"]["records"] = [
        {
            "venue_symbol": "rb2610",
            "exchange_id": "SHFE",
            "direction": "LONG",
            "position_qty": 5,
            "yd_position_qty": 0,
            "td_position_qty": 5,
            "date_type": 1,
            "hedge_flag": 1,
        }
    ]
    pre_payload["instruments"]["records"] = [
        {
            "venue_symbol": "rb2610",
            "exchange_id": "SHFE",
            "price_tick": 1.0,
            "volume_multiple": 10,
            "detail_fields": {
                "instrument_name": "Rebar",
                "open_date": "20250101",
                "expire_date": "20261031",
                "is_trading": True,
                "min_limit_order_volume": 1,
                "max_limit_order_volume": 10,
                "product_id": "rb",
                "underlying_instr_id": "rb2610",
                "delivery_year": 2026,
                "delivery_month": 10,
            },
        }
    ]
    pre_snapshot_path.write_text(json.dumps(pre_payload), encoding="utf-8")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "BrokerID": "9999",
                "UserID": "u",
                "Password": "p",
                "Pricer": "tcp://trading.openctp.cn:30011",
                "Host": "tcp://trading.openctp.cn:30001",
                "Instruments": ["rb2610"],
                "ExecutionGuardrails": {
                    "Enabled": True,
                    "AllowedInstruments": ["rb2610"],
                    "MaxOrderQty": 3,
                    "MaxNetPosition": 5,
                    "MaxSubmitPerMinute": 10,
                    "PriceMode": "best_level_1",
                    "AllowLiveOrderSmoke": False,
                    "AllowExposureReductionOrderSmoke": True,
                },
            }
        ),
        encoding="utf-8",
    )

    class FakeBridge:
        def drain_submitted_commands(self):
            return [
                CtpRuntimeCommand(
                    kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
                    client_order_id="source-closure-payload",
                    venue_symbol="rb2610",
                    payload={
                        "instrument": "rb2610",
                        "side": "SELL",
                        "quantity": "1",
                        "limit_price": "3180.0",
                        "position_effect": "CLOSETODAY",
                        "native_side": "1",
                        "native_comb_offset": "3",
                        "native_comb_hedge": "1",
                        "order_type": "LIMIT",
                        "time_in_force": "GFD",
                        "order_ref": "71",
                    },
                )
            ]

        def drain_events(self):
            return [
                CtpRuntimeEvent(
                    kind=CtpRuntimeEventKind.ORDER,
                    client_order_id="source-closure-payload",
                    venue_symbol="rb2610",
                    message="持仓不足",
                    payload={
                        "native_order_id": "71",
                        "native_order_ref": "71",
                        "status": "53",
                        "trade_volume": "0",
                        "trade_price": "0.0",
                        "leaves_qty": "0",
                        "side": "1",
                        "direction": "1",
                        "offset_flag": "1",
                        "submit_request_offset_flag": "3",
                        "submit_request_offset_source": (
                            "repo_ctp_td_order_send."
                            "CThostFtdcInputOrderField.CombOffsetFlag[0]"
                        ),
                        "response_request_id": "42",
                        "response_is_last": "1",
                        "response_error_id": "31",
                        "hedge_flag": "1",
                        "callback_source": "OnRspOrderInsert",
                        "error_msg": "持仓不足",
                    },
                )
            ]

    class FakeExecutionClient:
        def run_order_lifecycle_smoke_baseline(self, **_kwargs):
            return SimpleNamespace(
                bootstrap=SimpleNamespace(ready=True),
                mapped_submit=CtpMappedOrderCommand(
                    command=FakeBridge().drain_submitted_commands()[0],
                    client_order_id="source-closure-payload",
                    order_ref=71,
                    front_id=1,
                    session_id=2,
                    error=None,
                ),
                dry_run=False,
                live_send_armed=True,
                matched_execs=[
                    SimpleNamespace(
                        python_client_order_id="source-closure-payload",
                        native_order_id="71",
                        native_order_ref="71",
                        venue_symbol="rb2610",
                        front_id=1,
                        session_id=2,
                        status=53,
                        callback_source="OnRspOrderInsert",
                        offset_flag=1,
                        submit_request_offset_flag=3,
                        submit_request_offset_source=(
                            "repo_ctp_td_order_send."
                            "CThostFtdcInputOrderField.CombOffsetFlag[0]"
                        ),
                        response_request_id=42,
                        response_is_last=True,
                        response_error_id=31,
                        is_trade=False,
                        trade_volume=0,
                        leaves_qty=0,
                        match_reason="order_ref_echo",
                    )
                ],
            )

    bridge = FakeBridge()
    monkeypatch.setattr(
        order_loop,
        "build_ctp_stack",
        lambda _config: {"execution_client": FakeExecutionClient(), "runtime_bridge": bridge},
    )

    result = order_loop.run_guarded_paper_order(
        config_path=config_path,
        pre_snapshot=pre_snapshot_path,
        post_snapshot=None,
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3180.0,
        position_effect="CLOSETODAY",
        client_order_id="source-closure-payload",
        timeout_seconds=1,
        arm_paper_send=True,
        close_from_pre_snapshot=True,
        expected_pre_snapshot_run_id="run-1",
        close_position_direction="LONG",
        submit_count_last_minute=0,
        session_send_count=0,
        session_send_budget=1,
        seen_client_order_ids=[],
    )

    assert (
        result["source_exhaustion_semantics"]["disposition"]
        == "local_owner_sources_exhausted_primary_rule_or_stronger_repair_required"
    )
    guardrail = result["source_closure_authority_guardrail"]
    assert guardrail["disposition"] == "blocks_retry_authorization_from_partial_source_context"
    assert (
        guardrail["missing_source_class"]
        == "primary_or_official_broker_front_close_rejection_rule_source"
    )
    assert (
        guardrail["source_closure_requirement"]
        == "source_candidate_context_must_explain_observed_response_offset_or_adapter_native_semantics"
    )
    assert (
        guardrail["external_source_candidate_classes_evaluated"]
        == result["source_exhaustion_semantics"][
            "external_source_candidate_classes_evaluated"
        ]
    )
    assert [
        candidate["class"]
        for candidate in guardrail["external_source_candidate_evidence"]
    ] == guardrail["external_source_candidate_classes_evaluated"]
    assert all(
        candidate["closure_sufficient"] is False
        for candidate in guardrail["external_source_candidate_evidence"]
    )
    assert all(
        candidate["insufficiency_reason"]
        for candidate in guardrail["external_source_candidate_evidence"]
    )
    assert guardrail["retry_authorization_allowed_by_source_context"] is False
    assert guardrail["semantic_closure_allowed_by_source_context"] is False
    assert guardrail["runtime_truth_created"] is False
    assert guardrail["account_console_truth_created"] is False
    assert guardrail["writes_truth"] is False
    assert guardrail["requires_new_formal_authorization_before_send"] is True
    assert "new_formal_retry_authorization_before_any_future_send" in guardrail["next_required_evidence"]
    assert (
        result["close_offset_owner_rule_semantics"]["disposition"]
        == "owner_rule_blocks_callback_offset_as_submit_truth"
    )
    assert (
        result["broker_rejection_semantics"]["disposition"]
        == "source_bearing_order_insert_insufficient_position_close_rejection"
    )
    assert result["paper_send_armed"] is True
    assert result["order_lifecycle"]["live_send_armed"] is True


def test_native_offset_semantics_flags_close_today_submit_callback_mismatch() -> None:
    verdict = order_loop.build_native_offset_semantics(
        intent_contract=build_intent_contract(
            instrument="rb2610",
            side="SELL",
            quantity=1,
            limit_price=3162.0,
            position_effect="CLOSETODAY",
            price_mode="best_level_1",
            client_order_id="close-today-mismatch",
        ),
        command_payload={
            "native_side": "1",
            "native_comb_offset": "3",
            "native_comb_hedge": "1",
        },
        lifecycle_events=[
            {
                "kind": "order",
                "client_order_id": "close-today-mismatch",
                "venue_symbol": "rb2610",
                "status": "53",
                "offset_flag": "1",
                "error_message": "持仓不足",
            }
        ],
    )

    assert verdict["position_effect"] == "CLOSETODAY"
    assert verdict["submit_native_comb_offset"] == "3"
    assert verdict["callback_offset_flags"] == ["1"]
    assert verdict["callback_sources"] == []
    assert verdict["callback_offset_source_field"] is None
    assert verdict["callback_matches_submit_native_comb_offset"] is False
    assert verdict["disposition"] == "callback_offset_differs_from_submit_native_comb_offset"
    assert verdict["acceptance_implication"] == "diagnostic_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_native_offset_semantics_scopes_order_insert_response_offset_mismatch() -> None:
    verdict = order_loop.build_native_offset_semantics(
        intent_contract=build_intent_contract(
            instrument="rb2610",
            side="SELL",
            quantity=1,
            limit_price=3162.0,
            position_effect="CLOSETODAY",
            price_mode="best_level_1",
            client_order_id="source-bearing-offset-mismatch",
        ),
        command_payload={
            "native_side": "1",
            "native_comb_offset": "3",
            "native_comb_hedge": "1",
        },
        lifecycle_events=[
            {
                "kind": "order",
                "client_order_id": "source-bearing-offset-mismatch",
                "venue_symbol": "rb2610",
                "status": "53",
                "offset_flag": "1",
                "submit_request_offset_flag": "3",
                "submit_request_offset_source": (
                    "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
                ),
                "callback_source": "OnRspOrderInsert",
                "error_message": "持仓不足",
            }
        ],
    )

    assert verdict["position_effect"] == "CLOSETODAY"
    assert verdict["submit_native_comb_offset"] == "3"
    assert (
        verdict["submit_native_offset_source_field"]
        == "CtpExecutionClient._native_comb_offset_value(position_effect)"
        " -> TdOrderSend.comb_offset"
        " -> CThostFtdcInputOrderField.CombOffsetFlag[0]"
    )
    assert verdict["submit_native_offset_expected_from_position_effect"] == "3"
    assert verdict["native_submit_boundary_offset_flags"] == ["3"]
    assert (
        verdict["native_submit_boundary_offset_source"]
        == "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
    )
    assert verdict["native_submit_boundary_matches_command_payload"] is True
    assert verdict["callback_offset_flags"] == ["1"]
    assert verdict["callback_sources"] == ["OnRspOrderInsert"]
    assert (
        verdict["callback_offset_source_field"]
        == "CThostFtdcInputOrderField.CombOffsetFlag[0]"
    )
    assert verdict["submit_offset_authority"] == "submit_request_provenance"
    assert verdict["callback_offset_authority"] == "front_response_diagnostic"
    assert verdict["callback_offset_rewrites_submit_truth"] is False
    assert verdict["order_insert_response_offset_mismatch"] is True
    assert verdict["callback_matches_submit_native_comb_offset"] is False
    assert (
        verdict["disposition"]
        == "order_insert_response_offset_differs_from_submit_native_comb_offset"
    )
    assert verdict["acceptance_implication"] == "diagnostic_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_callback_source_observability_blocks_zero_fill_rejection_without_source() -> None:
    lifecycle_verdict = {
        "disposition": "cancelled",
        "fill_volume": 0,
    }

    verdict = order_loop.build_callback_source_observability(
        lifecycle_events=[
            {
                "kind": "order",
                "status": "53",
                "callback_source": "",
            }
        ],
        lifecycle_verdict=lifecycle_verdict,
    )

    assert verdict["accepted"] is False
    assert verdict["disposition"] == "missing_callback_source_for_zero_fill_rejection"
    assert verdict["callback_sources"] == []
    assert verdict["zero_fill_rejection"] is True
    assert verdict["acceptance_implication"] == "diagnostic_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_callback_source_observability_records_source_without_accepting_fill() -> None:
    lifecycle_verdict = {
        "disposition": "cancelled",
        "fill_volume": 0,
    }

    verdict = order_loop.build_callback_source_observability(
        lifecycle_events=[
            {
                "kind": "order",
                "status": "53",
                "callback_source": "OnRtnOrder",
            }
        ],
        lifecycle_verdict=lifecycle_verdict,
    )

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "callback_source_observed"
    assert verdict["callback_sources"] == ["OnRtnOrder"]
    assert verdict["zero_fill_rejection"] is True
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is False
    assert verdict["writes_truth"] is False


def test_callback_source_observability_blocks_armed_timeout_without_source() -> None:
    lifecycle_verdict = {
        "disposition": "timeout",
        "fill_volume": 0,
    }

    armed = order_loop.build_callback_source_observability(
        lifecycle_events=[],
        lifecycle_verdict=lifecycle_verdict,
        paper_send_armed=True,
    )
    dry_run = order_loop.build_callback_source_observability(
        lifecycle_events=[],
        lifecycle_verdict=lifecycle_verdict,
        paper_send_armed=False,
    )

    assert armed["accepted"] is False
    assert armed["disposition"] == "missing_callback_source_for_armed_lifecycle_timeout"
    assert armed["armed_lifecycle_timeout"] is True
    assert armed["requires_owner_resolution_before_retry"] is True
    assert armed["fill_producing_acceptance_satisfied"] is False
    assert armed["writes_truth"] is False

    assert dry_run["accepted"] is True
    assert dry_run["disposition"] == "callback_source_not_required_for_non_rejection"
    assert dry_run["armed_lifecycle_timeout"] is False


def test_decoded_insufficient_position_close_rejection_is_typed_blocker_only() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3162.0,
        position_effect="CLOSETODAY",
        price_mode="best_level_1",
        client_order_id="decoded-insufficient-position",
    )
    lifecycle_events = [
        {
            "kind": "order",
            "client_order_id": "decoded-insufficient-position",
            "venue_symbol": "rb2610",
            "status": "53",
            "trade_volume": 0,
            "leaves_qty": 0,
            "offset_flag": "1",
            "payload_error_msg": "持仓不足",
            "error_message": "持仓不足",
        }
    ]
    lifecycle_verdict = classify_lifecycle_events(intent, lifecycle_events)
    offset_semantics = order_loop.build_native_offset_semantics(
        intent_contract=intent,
        command_payload={"native_comb_offset": "3"},
        lifecycle_events=lifecycle_events,
    )

    verdict = order_loop.build_broker_rejection_semantics(
        intent_contract=intent,
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=offset_semantics,
    )

    assert verdict["disposition"] == "decoded_broker_insufficient_position_close_rejection"
    assert verdict["blocker_type"] == "broker-or-adapter-close-position-semantics"
    assert verdict["callback_sources"] == []
    assert verdict["order_insert_rejection_source"] is False
    assert verdict["semantic_scope"] == "decoded_rejection_without_callback_source_scope"
    assert verdict["insufficient_position_text_observed"] is True
    assert verdict["close_intent"] is True
    assert verdict["zero_fill_rejection"] is True
    assert verdict["native_offset_disposition"] == "callback_offset_differs_from_submit_native_comb_offset"
    assert verdict["acceptance_implication"] == "typed_blocker_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_source_bearing_order_insert_rejection_is_scoped_blocker_only() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3162.0,
        position_effect="CLOSETODAY",
        price_mode="best_level_1",
        client_order_id="source-bearing-insufficient-position",
    )
    lifecycle_events = [
        {
            "kind": "order",
            "client_order_id": "source-bearing-insufficient-position",
            "venue_symbol": "rb2610",
            "status": "53",
            "trade_volume": 0,
            "leaves_qty": 0,
            "offset_flag": "1",
            "callback_source": "OnRspOrderInsert",
            "response_request_id": "42",
            "response_is_last": "1",
            "response_error_id": "31",
            "payload_error_msg": "持仓不足",
            "error_message": "持仓不足",
        }
    ]
    lifecycle_verdict = classify_lifecycle_events(intent, lifecycle_events)
    offset_semantics = order_loop.build_native_offset_semantics(
        intent_contract=intent,
        command_payload={"native_comb_offset": "3"},
        lifecycle_events=lifecycle_events,
    )

    verdict = order_loop.build_broker_rejection_semantics(
        intent_contract=intent,
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=offset_semantics,
    )

    assert (
        verdict["disposition"]
        == "source_bearing_order_insert_insufficient_position_close_rejection"
    )
    assert verdict["blocker_type"] == "broker-or-adapter-close-position-semantics"
    assert verdict["callback_sources"] == ["OnRspOrderInsert"]
    assert verdict["order_insert_rejection_source"] is True
    assert verdict["order_insert_response_identity_observed"] is True
    assert verdict["order_insert_response_identity"] == [
        {
            "response_request_id": "42",
            "response_is_last": "1",
            "response_error_id": "31",
        }
    ]
    assert verdict["order_insert_response_identity_authority"] == "front_response_identity_fields"
    assert verdict["order_insert_submit_boundary_identity_observed"] is False
    assert verdict["order_insert_submit_boundary_correlation_observed"] is False
    assert verdict["order_insert_submit_boundary_correlation_rule"] is None
    assert verdict["order_insert_submit_boundary_correlation_required"] is True
    assert verdict["stronger_adapter_native_semantic_repair_candidate"] is False
    assert verdict["next_adapter_native_semantic_repair_evidence"] == [
        "submit_boundary_request_identity_field",
        "order_insert_response_identity_field",
        "submit_response_identity_correlation_rule",
    ]
    assert (
        verdict["semantic_scope"]
        == "order_insert_rejection_before_fill_not_trade_or_closeout_truth"
    )
    assert (
        verdict["native_offset_disposition"]
        == "order_insert_response_offset_differs_from_submit_native_comb_offset"
    )
    assert verdict["acceptance_implication"] == "typed_blocker_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_order_insert_rejection_records_submit_response_identity_correlation_without_accepting_fill() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3162.0,
        position_effect="CLOSETODAY",
        price_mode="best_level_1",
        client_order_id="source-bearing-correlated-insufficient-position",
    )
    lifecycle_events = [
        {
            "kind": "order",
            "client_order_id": "source-bearing-correlated-insufficient-position",
            "venue_symbol": "rb2610",
            "status": "53",
            "trade_volume": 0,
            "leaves_qty": 0,
            "offset_flag": "1",
            "callback_source": "OnRspOrderInsert",
            "submit_request_id": "42",
            "submit_request_id_source": (
                "CtpRuntimeCommand.request_id -> TdOrderSend.request_id -> "
                "CTP ReqOrderInsert nRequestID"
            ),
            "response_request_id": "42",
            "response_is_last": "1",
            "response_error_id": "31",
            "payload_error_msg": "持仓不足",
            "error_message": "持仓不足",
        }
    ]
    lifecycle_verdict = classify_lifecycle_events(intent, lifecycle_events)
    offset_semantics = order_loop.build_native_offset_semantics(
        intent_contract=intent,
        command_payload={"native_comb_offset": "3"},
        lifecycle_events=lifecycle_events,
    )

    verdict = order_loop.build_broker_rejection_semantics(
        intent_contract=intent,
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=offset_semantics,
    )

    assert (
        verdict["disposition"]
        == "source_bearing_order_insert_insufficient_position_close_rejection"
    )
    assert verdict["order_insert_submit_boundary_identity_observed"] is True
    assert verdict["order_insert_submit_boundary_identity"] == [
        {
            "submit_request_id": "42",
            "submit_request_id_source": (
                "CtpRuntimeCommand.request_id -> TdOrderSend.request_id -> "
                "CTP ReqOrderInsert nRequestID"
            ),
        }
    ]
    assert verdict["order_insert_submit_boundary_correlation_observed"] is True
    assert (
        verdict["order_insert_submit_boundary_correlation_rule"]
        == "submit_request_id_equals_onrsp_order_insert_response_request_id"
    )
    assert verdict["order_insert_submit_boundary_correlated_request_ids"] == [
        {"submit_request_id": "42", "response_request_id": "42"}
    ]
    assert verdict["order_insert_submit_boundary_correlation_required"] is False
    assert verdict["stronger_adapter_native_semantic_repair_candidate"] is True
    assert verdict["next_adapter_native_semantic_repair_evidence"] == [
        "primary_or_official_broker_front_close_rejection_rule_source",
        "new_formal_bounded_authorization_before_future_send",
    ]
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_source_exhaustion_consumes_submit_response_correlation_as_repair_not_retry_authority() -> None:
    broker_rejection_semantics = {
        "disposition": "source_bearing_order_insert_insufficient_position_close_rejection",
        "order_insert_response_identity_observed": True,
        "stronger_adapter_native_semantic_repair_candidate": True,
    }
    close_offset_semantics = {
        "requires_owner_resolution_before_retry": True,
        "primary_rule_source_required": True,
        "local_diagnostics_sufficient_to_close": False,
    }

    verdict = order_loop.build_source_exhaustion_semantics(
        broker_rejection_semantics=broker_rejection_semantics,
        close_offset_owner_rule_semantics=close_offset_semantics,
    )

    assert (
        verdict["disposition"]
        == "adapter_native_repair_observed_formal_authorization_required"
    )
    assert (
        verdict["blocker_type"]
        == "formal-bounded-paper-authorization-missing-after-adapter-native-repair"
    )
    assert verdict["adapter_native_repair_beyond_local_diagnostics_present"] is True
    assert verdict["external_source_candidates_sufficient_to_close"] is False
    assert verdict["partial_source_context_authorizes_retry"] is False
    assert verdict["next_required_evidence"] == [
        "new_formal_retry_authorization_before_any_future_send",
        "fresh_same_slice_market_account_preflight_before_any_future_send",
    ]
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_close_rejection_diagnostic_rules_out_position_detail_gap_only() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3162.0,
        position_effect="CLOSETODAY",
        price_mode="best_level_1",
        client_order_id="decoded-insufficient-position",
    )
    lifecycle_events = [
        {
            "kind": "order",
            "client_order_id": "decoded-insufficient-position",
            "venue_symbol": "rb2610",
            "status": "53",
            "trade_volume": 0,
            "leaves_qty": 0,
            "offset_flag": "1",
            "payload_error_msg": "持仓不足",
            "error_message": "持仓不足",
        }
    ]
    lifecycle_verdict = classify_lifecycle_events(intent, lifecycle_events)
    offset_semantics = order_loop.build_native_offset_semantics(
        intent_contract=intent,
        command_payload={"native_comb_offset": "3"},
        lifecycle_events=lifecycle_events,
    )
    rejection_semantics = order_loop.build_broker_rejection_semantics(
        intent_contract=intent,
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=offset_semantics,
    )
    position_detail_semantics = {
        "disposition": "position_detail_sufficient_for_current_close_diagnostic",
        "position_exchange_ids": ["SHFE"],
        "position_buckets": [
            {
                "direction": "LONG",
                "position_qty": 5,
                "td_position_qty": 5,
                "yd_position_qty": 0,
            }
        ],
    }

    verdict = order_loop.build_close_rejection_diagnostic_semantics(
        intent_contract=intent,
        position_detail_semantics=position_detail_semantics,
        native_offset_semantics=offset_semantics,
        broker_rejection_semantics=rejection_semantics,
    )

    assert (
        verdict["disposition"]
        == "sufficient_position_detail_but_callback_offset_mismatch_and_broker_rejected_close"
    )
    assert verdict["blocker_type"] == "broker-or-adapter-close-position-semantics"
    assert verdict["position_detail_sufficient"] is True
    assert verdict["decoded_insufficient_position_close_rejection"] is True
    assert verdict["close_today_intent"] is True
    assert (
        verdict["diagnostic_conclusion"]
        == "position_detail_gap_ruled_out_close_semantics_still_unresolved"
    )
    assert "position_exchange_id_missing" in verdict["ruled_out_gaps"]
    assert "native_callback_source_or_order_insert_rejection_source" in verdict["next_required_evidence"]
    assert "primary_broker_front_close_rejection_rule_source" in verdict["next_required_evidence"]
    assert verdict["primary_rule_source_required"] is True
    assert verdict["local_diagnostics_sufficient_to_close"] is False
    assert verdict["acceptance_implication"] == "typed_blocker_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_close_rejection_diagnostic_consumes_order_insert_source_without_accepting_fill() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3162.0,
        position_effect="CLOSETODAY",
        price_mode="best_level_1",
        client_order_id="source-bearing-insufficient-position",
    )
    lifecycle_events = [
        {
            "kind": "order",
            "client_order_id": "source-bearing-insufficient-position",
            "venue_symbol": "rb2610",
            "status": "53",
            "trade_volume": 0,
            "leaves_qty": 0,
            "offset_flag": "1",
            "callback_source": "OnRspOrderInsert",
            "response_request_id": "42",
            "response_is_last": "1",
            "response_error_id": "31",
            "payload_error_msg": "持仓不足",
            "error_message": "持仓不足",
        }
    ]
    lifecycle_verdict = classify_lifecycle_events(intent, lifecycle_events)
    offset_semantics = order_loop.build_native_offset_semantics(
        intent_contract=intent,
        command_payload={"native_comb_offset": "3"},
        lifecycle_events=lifecycle_events,
    )
    rejection_semantics = order_loop.build_broker_rejection_semantics(
        intent_contract=intent,
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=offset_semantics,
    )
    position_detail_semantics = {
        "disposition": "position_detail_sufficient_for_current_close_diagnostic",
        "position_exchange_ids": ["SHFE"],
        "position_buckets": [
            {
                "direction": "LONG",
                "position_qty": 5,
                "td_position_qty": 5,
                "yd_position_qty": 0,
            }
        ],
    }

    verdict = order_loop.build_close_rejection_diagnostic_semantics(
        intent_contract=intent,
        position_detail_semantics=position_detail_semantics,
        native_offset_semantics=offset_semantics,
        broker_rejection_semantics=rejection_semantics,
    )

    assert (
        verdict["disposition"]
        == "sufficient_position_detail_but_order_insert_rejected_close_with_callback_offset_mismatch"
    )
    assert verdict["blocker_type"] == "broker-or-adapter-close-position-semantics"
    assert verdict["position_detail_sufficient"] is True
    assert verdict["decoded_insufficient_position_close_rejection"] is False
    assert verdict["source_bearing_order_insert_close_rejection"] is True
    assert (
        verdict["diagnostic_conclusion"]
        == "order_insert_rejection_source_observed_close_semantics_still_unresolved"
    )
    assert "native_callback_source_or_order_insert_rejection_source" not in verdict["next_required_evidence"]
    assert "broker_or_exchange_close_offset_rule_tied_to_OnRspOrderInsert_fields" in verdict["next_required_evidence"]
    assert "primary_broker_front_close_rejection_rule_source" in verdict["next_required_evidence"]
    assert "adapter_native_repair_beyond_local_diagnostics" in verdict["next_required_evidence"]
    assert verdict["primary_rule_source_required"] is True
    assert verdict["local_diagnostics_sufficient_to_close"] is False
    assert verdict["acceptance_implication"] == "typed_blocker_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_close_offset_owner_rule_blocks_callback_offset_as_submit_truth() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3178.0,
        position_effect="CLOSETODAY",
        price_mode="snapshot_close",
        client_order_id="source-bearing-insufficient-position",
    )
    lifecycle_events = [
        {
            "kind": "order",
            "client_order_id": "source-bearing-insufficient-position",
            "venue_symbol": "rb2610",
            "status": "53",
            "trade_volume": 0,
            "leaves_qty": 0,
            "offset_flag": "1",
            "submit_request_offset_flag": "3",
            "submit_request_offset_source": (
                "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
            ),
            "callback_source": "OnRspOrderInsert",
            "response_request_id": "42",
            "response_is_last": "1",
            "response_error_id": "31",
            "payload_error_msg": "持仓不足",
            "error_message": "持仓不足",
        }
    ]
    lifecycle_verdict = classify_lifecycle_events(intent, lifecycle_events)
    offset_semantics = order_loop.build_native_offset_semantics(
        intent_contract=intent,
        command_payload={"native_comb_offset": "3"},
        lifecycle_events=lifecycle_events,
    )
    rejection_semantics = order_loop.build_broker_rejection_semantics(
        intent_contract=intent,
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=offset_semantics,
    )
    position_detail_semantics = {
        "disposition": "position_detail_sufficient_for_current_close_diagnostic",
        "position_exchange_ids": ["SHFE"],
        "instrument_exchange_id": "SHFE",
        "position_buckets": [
            {
                "direction": "LONG",
                "position_qty": 5,
                "td_position_qty": 5,
                "yd_position_qty": 0,
            }
        ],
    }

    verdict = order_loop.build_close_offset_owner_rule_semantics(
        intent_contract=intent,
        position_detail_semantics=position_detail_semantics,
        native_offset_semantics=offset_semantics,
        broker_rejection_semantics=rejection_semantics,
    )

    assert verdict["disposition"] == "owner_rule_blocks_callback_offset_as_submit_truth"
    assert verdict["blocker_type"] == "broker-or-adapter-close-position-semantics"
    assert verdict["expected_submit_offset_from_position_effect"] == "3"
    assert verdict["observed_submit_boundary_offset"] == "3"
    assert verdict["callback_offset_flags"] == ["1"]
    assert verdict["callback_sources"] == ["OnRspOrderInsert"]
    assert verdict["order_insert_response_identity_observed"] is True
    assert verdict["order_insert_response_identity"] == [
        {
            "response_request_id": "42",
            "response_is_last": "1",
            "response_error_id": "31",
        }
    ]
    assert verdict["submit_boundary_matches_command_payload"] is True
    assert verdict["callback_is_rejection_diagnostic_only"] is True
    assert verdict["auto_downgrade_to_generic_close_allowed"] is False
    assert "primary_broker_front_close_rejection_rule_source" in verdict["next_required_evidence"]
    assert "adapter_native_repair_beyond_local_diagnostics" in verdict["next_required_evidence"]
    assert (
        "primary_broker_front_close_rejection_rule_source_or_stronger_adapter_native_semantic_repair"
        in verdict["next_required_evidence"]
    )
    assert "new_formal_retry_authorization_before_any_future_send" in verdict["next_required_evidence"]
    assert verdict["primary_rule_source_required"] is True
    assert verdict["local_diagnostics_sufficient_to_close"] is False
    assert verdict["acceptance_implication"] == "typed_blocker_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_source_exhaustion_semantics_requires_primary_rule_or_stronger_repair() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="SELL",
        quantity=1,
        limit_price=3180.0,
        position_effect="CLOSETODAY",
        price_mode="snapshot_close",
        client_order_id="source-exhaustion-insufficient-position",
    )
    lifecycle_events = [
        {
            "kind": "order",
            "client_order_id": "source-exhaustion-insufficient-position",
            "venue_symbol": "rb2610",
            "status": "53",
            "trade_volume": 0,
            "leaves_qty": 0,
            "offset_flag": "1",
            "submit_request_offset_flag": "3",
            "callback_source": "OnRspOrderInsert",
            "response_request_id": "42",
            "response_is_last": "1",
            "response_error_id": "31",
            "payload_error_msg": "持仓不足",
            "error_message": "持仓不足",
        }
    ]
    lifecycle_verdict = classify_lifecycle_events(intent, lifecycle_events)
    offset_semantics = order_loop.build_native_offset_semantics(
        intent_contract=intent,
        command_payload={"native_comb_offset": "3"},
        lifecycle_events=lifecycle_events,
    )
    rejection_semantics = order_loop.build_broker_rejection_semantics(
        intent_contract=intent,
        lifecycle_events=lifecycle_events,
        lifecycle_verdict=lifecycle_verdict,
        native_offset_semantics=offset_semantics,
    )
    position_detail_semantics = {
        "disposition": "position_detail_sufficient_for_current_close_diagnostic",
        "position_exchange_ids": ["SHFE"],
        "instrument_exchange_id": "SHFE",
        "position_buckets": [
            {
                "direction": "LONG",
                "position_qty": 5,
                "td_position_qty": 5,
                "yd_position_qty": 0,
            }
        ],
    }
    close_offset_semantics = order_loop.build_close_offset_owner_rule_semantics(
        intent_contract=intent,
        position_detail_semantics=position_detail_semantics,
        native_offset_semantics=offset_semantics,
        broker_rejection_semantics=rejection_semantics,
    )

    verdict = order_loop.build_source_exhaustion_semantics(
        broker_rejection_semantics=rejection_semantics,
        close_offset_owner_rule_semantics=close_offset_semantics,
    )

    assert (
        verdict["disposition"]
        == "local_owner_sources_exhausted_primary_rule_or_stronger_repair_required"
    )
    assert (
        verdict["blocker_type"]
        == "primary-broker-front-close-rejection-rule-source-or-stronger-adapter-native-semantic-repair-missing"
    )
    assert verdict["local_source_classes_evaluated"] == [
        "owner_code",
        "focused_tests",
        "prior_typed_artifacts",
        "local_vendor_constants",
        "native_response_identity_fields",
    ]
    assert verdict["external_source_candidate_classes_evaluated"] == [
        "ctp_api_documentation_mirror",
        "ctp_client_development_guide_primary_candidate",
        "cffex_trader_api_pdf_candidate",
        "futures_broker_ctp_error_help_candidate",
    ]
    assert [
        candidate["class"]
        for candidate in verdict["external_source_candidate_evidence"]
    ] == verdict["external_source_candidate_classes_evaluated"]
    assert {
        candidate["authority"]
        for candidate in verdict["external_source_candidate_evidence"]
    } == {
        "documentation_mirror",
        "primary_candidate_documentation",
        "exchange_hosted_api_pdf",
        "broker_help_page",
    }
    assert all(
        candidate["closure_sufficient"] is False
        for candidate in verdict["external_source_candidate_evidence"]
    )
    assert all(
        candidate["insufficiency_reason"]
        for candidate in verdict["external_source_candidate_evidence"]
    )
    assert (
        verdict["missing_source_class"]
        == "primary_or_official_broker_front_close_rejection_rule_source"
    )
    assert verdict["adapter_native_repair_beyond_local_diagnostics_present"] is False
    assert verdict["external_source_candidates_sufficient_to_close"] is False
    assert verdict["partial_source_context_authorizes_retry"] is False
    assert (
        verdict["source_closure_requirement"]
        == "source_candidate_context_must_explain_observed_response_offset_or_adapter_native_semantics"
    )
    assert verdict["order_insert_response_identity_observed"] is True
    assert verdict["source_bearing_rejection_observed"] is True
    assert verdict["local_diagnostics_sufficient_to_close"] is False
    assert "primary_broker_front_close_rejection_rule_source" in verdict["next_required_evidence"]
    assert "adapter_native_repair_beyond_local_diagnostics" in verdict["next_required_evidence"]
    assert "new_formal_retry_authorization_before_any_future_send" in verdict["next_required_evidence"]
    assert verdict["acceptance_implication"] == "typed_blocker_only_not_fill_or_closeout_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_source_exhaustion_semantics_does_not_overblock_non_source_rejection() -> None:
    rejection_semantics = {
        "disposition": "decoded_broker_insufficient_position_close_rejection",
        "order_insert_response_identity_observed": False,
    }
    close_offset_semantics = {
        "requires_owner_resolution_before_retry": True,
        "primary_rule_source_required": True,
        "local_diagnostics_sufficient_to_close": False,
    }

    verdict = order_loop.build_source_exhaustion_semantics(
        broker_rejection_semantics=rejection_semantics,
        close_offset_owner_rule_semantics=close_offset_semantics,
    )

    assert verdict["disposition"] == "source_exhaustion_semantics_not_applicable"
    assert verdict["blocker_type"] is None
    assert verdict["external_source_candidates_sufficient_to_close"] is False
    assert verdict["partial_source_context_authorizes_retry"] is False
    assert verdict["source_closure_requirement"] is None
    assert verdict["external_source_candidate_evidence"] == []
    assert verdict["source_bearing_rejection_observed"] is False
    assert verdict["order_insert_response_identity_observed"] is False
    assert verdict["next_required_evidence"] == []
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is False
    assert verdict["writes_truth"] is False


def test_source_closure_authority_guardrail_blocks_partial_source_retry() -> None:
    source_exhaustion_semantics = {
        "requires_owner_resolution_before_retry": True,
        "missing_source_class": "primary_or_official_broker_front_close_rejection_rule_source",
        "source_closure_requirement": "source_candidate_context_must_explain_observed_response_offset_or_adapter_native_semantics",
        "external_source_candidate_classes_evaluated": [
            "ctp_api_documentation_mirror",
            "futures_broker_ctp_error_help_candidate",
        ],
        "external_source_candidate_evidence": [
            {
                "class": "ctp_api_documentation_mirror",
                "closure_sufficient": False,
                "insufficiency_reason": "does_not_explain_observed_response_offset_after_submitted_close_today",
            },
            {
                "class": "futures_broker_ctp_error_help_candidate",
                "closure_sufficient": False,
                "insufficiency_reason": "does_not_explain_api_response_offset_or_callback_authority",
            },
        ],
        "external_source_candidates_sufficient_to_close": False,
        "partial_source_context_authorizes_retry": False,
        "adapter_native_repair_beyond_local_diagnostics_present": False,
    }

    verdict = order_loop.build_source_closure_authority_guardrail(
        source_exhaustion_semantics
    )

    assert (
        verdict["disposition"]
        == "blocks_retry_authorization_from_partial_source_context"
    )
    assert (
        verdict["missing_source_class"]
        == "primary_or_official_broker_front_close_rejection_rule_source"
    )
    assert (
        verdict["source_closure_requirement"]
        == "source_candidate_context_must_explain_observed_response_offset_or_adapter_native_semantics"
    )
    assert verdict["external_source_candidate_classes_evaluated"] == [
        "ctp_api_documentation_mirror",
        "futures_broker_ctp_error_help_candidate",
    ]
    assert [
        candidate["class"]
        for candidate in verdict["external_source_candidate_evidence"]
    ] == [
        "ctp_api_documentation_mirror",
        "futures_broker_ctp_error_help_candidate",
    ]
    assert all(
        candidate["closure_sufficient"] is False
        for candidate in verdict["external_source_candidate_evidence"]
    )
    assert all(
        candidate["insufficiency_reason"]
        for candidate in verdict["external_source_candidate_evidence"]
    )
    assert verdict["source_candidates_sufficient_to_close"] is False
    assert verdict["partial_source_context_authorizes_retry"] is False
    assert verdict["adapter_native_repair_beyond_local_diagnostics_present"] is False
    assert verdict["retry_authorization_allowed_by_source_context"] is False
    assert verdict["semantic_closure_allowed_by_source_context"] is False
    assert verdict["requires_new_formal_authorization_before_send"] is True
    assert (
        "primary_or_official_broker_front_close_rejection_rule_source_that_explains_observed_response_offset"
        in verdict["next_required_evidence"]
    )
    assert "adapter_native_semantic_repair_beyond_local_diagnostics" in verdict[
        "next_required_evidence"
    ]
    assert "new_formal_retry_authorization_before_any_future_send" in verdict[
        "next_required_evidence"
    ]
    assert (
        verdict["acceptance_implication"]
        == "typed_blocker_only_not_retry_or_closeout_truth"
    )
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["runtime_truth_created"] is False
    assert verdict["account_console_truth_created"] is False
    assert verdict["writes_truth"] is False


def test_source_closure_authority_guardrail_ignores_non_blocking_context() -> None:
    source_exhaustion_semantics = {
        "requires_owner_resolution_before_retry": False,
        "external_source_candidates_sufficient_to_close": False,
        "partial_source_context_authorizes_retry": False,
        "adapter_native_repair_beyond_local_diagnostics_present": False,
    }

    verdict = order_loop.build_source_closure_authority_guardrail(
        source_exhaustion_semantics
    )

    assert verdict["disposition"] == "source_closure_authority_guardrail_not_applicable"
    assert verdict["missing_source_class"] is None
    assert verdict["source_closure_requirement"] is None
    assert verdict["external_source_candidate_classes_evaluated"] == []
    assert verdict["external_source_candidate_evidence"] == []
    assert verdict["requires_new_formal_authorization_before_send"] is False
    assert verdict["next_required_evidence"] == []
    assert verdict["retry_authorization_allowed_by_source_context"] is False
    assert verdict["semantic_closure_allowed_by_source_context"] is False
    assert verdict["writes_truth"] is False


def test_source_closure_authority_guardrail_requires_authorization_after_stronger_repair() -> None:
    source_exhaustion_semantics = {
        "requires_owner_resolution_before_retry": True,
        "missing_source_class": "primary_or_official_broker_front_close_rejection_rule_source",
        "source_closure_requirement": "source_candidate_context_must_explain_observed_response_offset_or_adapter_native_semantics",
        "external_source_candidate_classes_evaluated": [
            "ctp_api_documentation_mirror",
        ],
        "external_source_candidate_evidence": [
            {
                "class": "ctp_api_documentation_mirror",
                "closure_sufficient": False,
                "insufficiency_reason": "does_not_explain_observed_response_offset_after_submitted_close_today",
            },
        ],
        "external_source_candidates_sufficient_to_close": False,
        "partial_source_context_authorizes_retry": False,
        "adapter_native_repair_beyond_local_diagnostics_present": True,
    }

    verdict = order_loop.build_source_closure_authority_guardrail(
        source_exhaustion_semantics
    )

    assert (
        verdict["disposition"]
        == "blocks_retry_authorization_after_adapter_native_repair_until_formal_authorization"
    )
    assert verdict["adapter_native_repair_beyond_local_diagnostics_present"] is True
    assert verdict["requires_new_formal_authorization_before_send"] is True
    assert verdict["next_required_evidence"] == [
        "new_formal_retry_authorization_before_any_future_send",
        "fresh_same_slice_market_account_preflight_before_any_future_send",
    ]
    assert verdict["retry_authorization_allowed_by_source_context"] is False
    assert verdict["semantic_closure_allowed_by_source_context"] is False
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["runtime_truth_created"] is False
    assert verdict["account_console_truth_created"] is False
    assert verdict["writes_truth"] is False


def test_risk_preflight_blocks_missing_external_account_metrics(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    payload["account"] = {
        "identity": {"account_id_present": False, "account_id_fingerprint": ""},
        "balance_present": False,
        "available_present": False,
        "margin_present": False,
    }
    config = order_loop.CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "u",
            "Password": "p",
            "Pricer": "tcp://md",
            "Host": "tcp://td",
            "Instruments": ["c2609"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 3,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
            },
        }
    )

    verdict = order_loop.build_risk_preflight_from_snapshot(
        payload,
        config=config,
        instrument="c2609",
        side="BUY",
        quantity=1,
        position_effect="OPEN",
        client_order_id="risk-missing",
        arm_paper_send=False,
    )

    assert verdict["accepted"] is False
    assert "account_identity_unavailable" in verdict["issues"]
    assert "account_available_metric_unavailable" in verdict["issues"]
    assert "account_margin_metric_unavailable" in verdict["issues"]


def test_risk_preflight_blocks_non_tradable_instrument_from_snapshot(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    payload["instruments"]["records"][0]["detail_fields"]["is_trading"] = False
    config = order_loop.CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "u",
            "Password": "p",
            "Pricer": "tcp://md",
            "Host": "tcp://td",
            "Instruments": ["c2609"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 3,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
            },
        }
    )

    verdict = order_loop.build_risk_preflight_from_snapshot(
        payload,
        config=config,
        instrument="c2609",
        side="BUY",
        quantity=1,
        position_effect="OPEN",
        client_order_id="risk-tradable",
        arm_paper_send=False,
    )

    assert verdict["accepted"] is False
    assert "instrument_not_tradable" in verdict["issues"]


def test_pre_order_snapshot_rejects_partial_snapshot(tmp_path: Path) -> None:
    path = _snapshot(tmp_path / "partial.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["snapshot_complete"] = False
    payload["completion"] = {"status": "partial"}
    path.write_text(json.dumps(payload), encoding="utf-8")

    verdict = validate_pre_order_snapshot(path)

    assert verdict["accepted"] is False
    assert "pre_snapshot_partial" in verdict["issues"]


def test_validate_order_command_contract_blocks_intent_mismatch() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="BUY",
        quantity=1,
        limit_price=3550.0,
        position_effect="OPEN",
        price_mode="best_level_1",
        client_order_id="paper-1",
    )
    command = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
        venue_symbol="rb2610",
        client_order_id="paper-1",
        payload={
            "side": "SELL",
            "quantity": "2",
            "limit_price": "3550.0",
            "position_effect": "OPEN",
            "order_type": "LIMIT",
            "time_in_force": "GFD",
            "order_ref": "101",
            "front_id": "1",
            "session_id": "2",
        },
    )

    verdict = validate_order_command_contract(intent, command)

    assert verdict["accepted"] is False
    assert verdict["disposition"] == "order_contract_failed"
    assert verdict["issues"] == ["side_mismatch", "quantity_mismatch"]


def test_lifecycle_classification_deduplicates_fills_and_rejects_overfill() -> None:
    intent = build_intent_contract(
        instrument="rb2610",
        side="BUY",
        quantity=1,
        limit_price=3550.0,
        position_effect="OPEN",
        price_mode="best_level_1",
        client_order_id="paper-1",
    )

    verdict = classify_lifecycle_events(
        intent,
        [
            {
                "kind": "trade",
                "client_order_id": "paper-1",
                "native_order_id": "SYS-1",
                "native_trade_id": "TRADE-1",
                "venue_symbol": "rb2610",
                "trade_volume": 1,
                "trade_price": 3550.0,
                "leaves_qty": 0,
            },
            {
                "kind": "trade",
                "client_order_id": "paper-1",
                "native_order_id": "SYS-1",
                "native_trade_id": "TRADE-1",
                "venue_symbol": "rb2610",
                "trade_volume": 1,
                "trade_price": 3550.0,
                "leaves_qty": 0,
            },
            {
                "kind": "trade",
                "client_order_id": "paper-1",
                "native_order_id": "SYS-1",
                "native_trade_id": "TRADE-2",
                "venue_symbol": "rb2610",
                "trade_volume": 1,
                "trade_price": 3550.0,
                "leaves_qty": -1,
            },
        ],
    )

    assert verdict["accepted"] is False
    assert verdict["disposition"] == "callback_contract_failed"
    assert verdict["duplicate_fill_count"] == 1
    assert "fill_volume_exceeds_quantity" in verdict["issues"]
    assert "negative_leaves_qty" in verdict["issues"]


def test_lifecycle_classification_treats_ctp_ascii_cancel_status_as_cancelled() -> None:
    intent = build_intent_contract(
        instrument="TEST",
        side="SELL",
        quantity=1,
        limit_price=999999.0,
        position_effect="OPEN",
        price_mode="best_level_1",
        client_order_id="paper-cancelled",
    )

    verdict = classify_lifecycle_events(
        intent,
        [
            {
                "kind": "order",
                "client_order_id": "paper-cancelled",
                "venue_symbol": "TEST",
                "status": "53",
                "trade_volume": 0,
                "leaves_qty": 0,
                "error_message": "instrument status text",
            }
        ],
    )

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "cancelled"
    assert verdict["leaves_qty"] == 0
    diagnostics = verdict["native_status_diagnostics"]
    assert diagnostics["observed_statuses"] == ["53"]
    assert (
        diagnostics["ctp_status_meanings"]["53"]
        == "ascii_code_53_for_ctp_order_status_char_5_cancelled"
    )
    assert diagnostics["disposition"] == "ctp_cancelled_status_without_fill"
    assert diagnostics["semantic_reason"] == "undetermined_from_status_only"
    assert diagnostics["broker_semantic_reason_inferred"] is False


def test_lifecycle_classification_keeps_replacement_text_as_nonsemantic_blocker() -> None:
    intent = build_intent_contract(
        instrument="TEST",
        side="SELL",
        quantity=1,
        limit_price=999999.0,
        position_effect="CLOSETODAY",
        price_mode="best_level_1",
        client_order_id="paper-mojibake",
    )

    verdict = classify_lifecycle_events(
        intent,
        [
            {
                "kind": "order",
                "client_order_id": "paper-mojibake",
                "venue_symbol": "TEST",
                "status": "53",
                "trade_volume": 0,
                "leaves_qty": 0,
                "payload_error_msg": "�ֲֲ���",
                "error_message": "�ֲֲ���",
            }
        ],
    )

    diagnostics = verdict["native_status_diagnostics"]
    assert verdict["disposition"] == "cancelled"
    assert diagnostics["error_text_seen"] is True
    assert diagnostics["error_text_contains_replacement_char"] is True
    assert diagnostics["semantic_reason"] == "undetermined_from_status_only"
    assert diagnostics["broker_semantic_reason_inferred"] is False


def test_reconcile_pre_post_snapshots_requires_same_profile_and_complete_snapshots(tmp_path: Path) -> None:
    pre = json.loads(_snapshot(tmp_path / "pre.json").read_text(encoding="utf-8"))
    post = json.loads(_snapshot(tmp_path / "post.json").read_text(encoding="utf-8"))
    pre["account"]["identity"]["account_id_fingerprint"] = "same"
    post["account"]["identity"]["account_id_fingerprint"] = "same"
    post["schema"]["run_id"] = "run-2"
    post["positions"]["position_count"] = 2

    verdict = reconcile_pre_post_snapshots(pre, post)

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "reconciled"
    assert verdict["position_count_delta"] == 1

    post["schema"]["account_profile"] = "formal-trading"
    verdict = reconcile_pre_post_snapshots(pre, post)

    assert verdict["accepted"] is False
    assert "profile_mismatch" in verdict["issues"]


def _snapshot_payload_with_position(
    *,
    run_id: str,
    account_fingerprint: str = "same",
    direction: str = "SHORT",
    position_qty: int = 3,
) -> dict:
    payload = json.loads(_snapshot(Path("unused.json"), run_id=run_id).read_text(encoding="utf-8")) if False else {
        "success": True,
        "schema": {
            "run_id": run_id,
            "account_profile": "openctp-tts-7x24-simulation",
            "evidence_class": "openctp-tts-7x24-simulation",
            "reconciliation_role": "pre_or_post_order_snapshot",
        },
        "account": {"identity": {"account_id_fingerprint": account_fingerprint}},
        "positions": {
            "position_count": 1,
            "records": [
                {
                    "venue_symbol": "c2609",
                    "direction": direction,
                    "position_qty": position_qty,
                    "td_position_qty": 0,
                    "yd_position_qty": position_qty,
                }
            ],
        },
    }
    return payload


def test_reconcile_pre_post_snapshots_matches_close_fill_position_delta() -> None:
    pre = _snapshot_payload_with_position(run_id="pre-run", position_qty=3)
    post = _snapshot_payload_with_position(run_id="post-run", position_qty=2)
    intent = build_intent_contract(
        instrument="c2609",
        side="BUY",
        quantity=1,
        limit_price=2350.0,
        position_effect="CLOSE",
        price_mode="snapshot_close",
        client_order_id="close-fill",
    )
    lifecycle = {"disposition": "filled", "fill_volume": 1, "leaves_qty": 0}

    verdict = reconcile_pre_post_snapshots(pre, post, intent_contract=intent, lifecycle_verdict=lifecycle)

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "filled_reconciled"
    assert verdict["target_position_key"] == {"venue_symbol": "c2609", "direction": "SHORT"}
    assert verdict["target_position_delta"] == -1
    assert verdict["expected_position_delta"] == -1


def test_reconcile_pre_post_snapshots_rejects_stale_post_snapshot_same_run_id() -> None:
    pre = _snapshot_payload_with_position(run_id="same-run", position_qty=3)
    post = _snapshot_payload_with_position(run_id="same-run", position_qty=2)

    verdict = reconcile_pre_post_snapshots(pre, post)

    assert verdict["accepted"] is False
    assert "post_snapshot_stale_same_run_id" in verdict["issues"]


def test_reconcile_pre_post_snapshots_rejects_account_fingerprint_mismatch() -> None:
    pre = _snapshot_payload_with_position(run_id="pre-run", account_fingerprint="pre")
    post = _snapshot_payload_with_position(run_id="post-run", account_fingerprint="post")

    verdict = reconcile_pre_post_snapshots(pre, post)

    assert verdict["accepted"] is False
    assert "account_identity_mismatch" in verdict["issues"]


def test_reconcile_pre_post_snapshots_blocks_fill_delta_mismatch() -> None:
    pre = _snapshot_payload_with_position(run_id="pre-run", position_qty=3)
    post = _snapshot_payload_with_position(run_id="post-run", position_qty=3)
    intent = build_intent_contract(
        instrument="c2609",
        side="BUY",
        quantity=1,
        limit_price=2350.0,
        position_effect="CLOSE",
        price_mode="snapshot_close",
        client_order_id="close-fill",
    )
    lifecycle = {"disposition": "filled", "fill_volume": 1, "leaves_qty": 0}

    verdict = reconcile_pre_post_snapshots(pre, post, intent_contract=intent, lifecycle_verdict=lifecycle)

    assert verdict["accepted"] is False
    assert verdict["disposition"] == "reconciliation_failed"
    assert "position_delta_mismatch" in verdict["issues"]


def test_reconcile_pre_post_snapshots_types_timeout_without_guessing_final_state() -> None:
    pre = _snapshot_payload_with_position(run_id="pre-run", position_qty=3)
    post = _snapshot_payload_with_position(run_id="post-run", position_qty=3)
    intent = build_intent_contract(
        instrument="c2609",
        side="BUY",
        quantity=1,
        limit_price=2350.0,
        position_effect="CLOSE",
        price_mode="snapshot_close",
        client_order_id="close-timeout",
    )
    lifecycle = {"disposition": "timeout", "fill_volume": 0, "leaves_qty": 1}

    verdict = reconcile_pre_post_snapshots(pre, post, intent_contract=intent, lifecycle_verdict=lifecycle)

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "timeout_no_delta"
    assert verdict["requires_followup"] is True


def test_reconcile_pre_post_snapshots_types_accepted_pending_without_final_state() -> None:
    pre = _snapshot_payload_with_position(run_id="pre-run", position_qty=2)
    post = _snapshot_payload_with_position(run_id="post-run", position_qty=2)
    intent = build_intent_contract(
        instrument="c2609",
        side="SELL",
        quantity=1,
        limit_price=999999.0,
        position_effect="OPEN",
        price_mode="best_level_1",
        client_order_id="pending-open",
    )
    lifecycle = {"disposition": "accepted", "fill_volume": 0, "leaves_qty": 1}

    verdict = reconcile_pre_post_snapshots(pre, post, intent_contract=intent, lifecycle_verdict=lifecycle)

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "accepted_pending_no_delta"
    assert verdict["requires_followup"] is True


def test_select_close_candidate_requires_fresh_snapshot_run_id(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))

    verdict = order_loop.select_close_candidate_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        expected_run_id="stale-run",
    )

    assert verdict["accepted"] is False
    assert verdict["disposition"] == "close_candidate_failed"
    assert "pre_snapshot_run_id_mismatch" in verdict["issues"]


def test_select_close_candidate_maps_short_position_to_buy_close_from_snapshot(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))

    verdict = order_loop.select_close_candidate_from_snapshot(
        payload,
        instrument="c2609",
        quantity=2,
        expected_run_id="fresh-run",
    )

    assert verdict["accepted"] is True
    assert verdict["disposition"] == "close_candidate_selected"
    assert verdict["candidate"]["direction"] == "SHORT"
    assert verdict["candidate"]["exchange_id"] == "DCE"
    assert verdict["candidate"]["closable_quantity"] == 3


def test_select_close_candidate_filters_requested_direction_when_both_sides_exist(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))
    payload["positions"]["records"].insert(
        0,
        {
            "venue_symbol": "c2609",
            "exchange_id": "DCE",
            "direction": "LONG",
            "position_qty": 1,
            "yd_position_qty": 0,
            "td_position_qty": 1,
        },
    )

    verdict = order_loop.select_close_candidate_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        expected_run_id="fresh-run",
        direction="SHORT",
    )

    assert verdict["accepted"] is True
    assert verdict["candidate"]["direction"] == "SHORT"


def test_build_close_intent_from_snapshot_blocks_over_close_before_native_send(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))

    verdict = order_loop.build_close_intent_from_snapshot(
        payload,
        instrument="c2609",
        quantity=4,
        requested_position_effect="CLOSE",
        limit_price=2300.0,
        client_order_id="close-1",
        expected_run_id="fresh-run",
    )

    assert verdict["accepted"] is False
    assert verdict["submit_intent"] is None
    assert "insufficient_closable_position" in verdict["issues"]


def test_build_close_intent_from_snapshot_caps_yd_to_current_position_qty(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))
    payload["positions"]["records"][0]["position_qty"] = 2
    payload["positions"]["records"][0]["yd_position_qty"] = 3
    payload["positions"]["records"][0]["td_position_qty"] = 0

    verdict = order_loop.build_close_intent_from_snapshot(
        payload,
        instrument="c2609",
        quantity=3,
        requested_position_effect="CLOSE",
        limit_price=2300.0,
        client_order_id="close-over",
        expected_run_id="fresh-run",
    )

    assert verdict["accepted"] is False
    assert verdict["candidate"]["closable_quantity"] == 2
    assert "insufficient_closable_position" in verdict["issues"]


def test_build_close_intent_from_snapshot_returns_order_contract_for_valid_close(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))

    verdict = order_loop.build_close_intent_from_snapshot(
        payload,
        instrument="c2609",
        quantity=1,
        requested_position_effect="CLOSE",
        limit_price=2300.0,
        client_order_id="close-2",
        expected_run_id="fresh-run",
    )

    assert verdict["accepted"] is True
    assert verdict["submit_intent"] == {
        "instrument": "c2609",
        "side": "BUY",
        "quantity": 1,
        "limit_price": 2300.0,
        "position_effect": "CLOSE",
        "order_type": "LIMIT",
        "time_in_force": "GFD",
        "price_mode": "snapshot_close",
        "client_order_id": "close-2",
    }


def test_build_close_intent_from_snapshot_uses_instrument_exchange_when_position_exchange_missing(
    tmp_path: Path,
) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))
    payload["positions"]["records"][0] = {
        "venue_symbol": "zn2610",
        "exchange_id": None,
        "direction": "LONG",
        "position_qty": 2,
        "yd_position_qty": 2,
        "td_position_qty": 0,
    }
    payload["instruments"]["records"][0] = {
        "venue_symbol": "zn2610",
        "exchange_id": "SHFE",
    }

    verdict = order_loop.build_close_intent_from_snapshot(
        payload,
        instrument="zn2610",
        quantity=1,
        requested_position_effect="CLOSE",
        limit_price=25000.0,
        client_order_id="close-3",
        expected_run_id="fresh-run",
    )

    assert verdict["accepted"] is True
    assert verdict["candidate"]["exchange_id"] == "SHFE"
    assert verdict["selected_bucket"] == "yesterday"
    assert verdict["submit_intent"]["side"] == "SELL"
    assert verdict["submit_intent"]["position_effect"] == "CLOSEYESTERDAY"


def test_position_detail_semantics_flags_missing_raw_owner_fields(tmp_path: Path) -> None:
    payload = json.loads(_snapshot(tmp_path / "pre.json", run_id="fresh-run").read_text(encoding="utf-8"))
    payload["positions"]["records"][0] = {
        "venue_symbol": "rb2610",
        "exchange_id": None,
        "direction": "LONG",
        "position_qty": 5,
        "yd_position_qty": 0,
        "td_position_qty": 5,
    }
    payload["instruments"]["records"][0] = {
        "venue_symbol": "rb2610",
        "exchange_id": "SHFE",
    }

    verdict = order_loop.build_position_detail_semantics(
        payload,
        instrument="rb2610",
        direction="LONG",
    )

    assert verdict["disposition"] == "position_detail_gap_requires_owner_resolution"
    assert verdict["matching_position_count"] == 1
    assert verdict["position_exchange_ids"] == []
    assert verdict["instrument_exchange_id"] == "SHFE"
    assert "position_exchange_id_missing" in verdict["issues"]
    assert "raw_position_date_type_missing" in verdict["issues"]
    assert "raw_position_hedge_flag_missing" in verdict["issues"]
    assert verdict["acceptance_implication"] == "diagnostic_only_not_position_or_fill_truth"
    assert verdict["fill_producing_acceptance_satisfied"] is False
    assert verdict["requires_owner_resolution_before_retry"] is True
    assert verdict["writes_truth"] is False


def test_json_stdout_bytes_encodes_ctp_replacement_text_as_utf8() -> None:
    payload = {"message": "ctp bad char \ufffd"}

    data = order_loop.json_stdout_bytes(payload)

    assert data.endswith(b"\n")
    assert b"\\ufffd" not in data
    assert "ctp bad char \ufffd".encode("utf-8") in data
