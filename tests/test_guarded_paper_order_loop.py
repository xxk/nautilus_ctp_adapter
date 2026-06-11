from __future__ import annotations

import json
from pathlib import Path

import scripts.ctp_guarded_paper_order_loop as order_loop
from scripts.ctp_guarded_paper_order_loop import (
    build_intent_contract,
    classify_lifecycle_events,
    reconcile_pre_post_snapshots,
    validate_order_command_contract,
    validate_pre_order_snapshot,
)
from nautilus_ctp_adapter.runtime import CtpRuntimeCommand, CtpRuntimeCommandKind


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


def test_json_stdout_bytes_encodes_ctp_replacement_text_as_utf8() -> None:
    payload = {"message": "ctp bad char \ufffd"}

    data = order_loop.json_stdout_bytes(payload)

    assert data.endswith(b"\n")
    assert b"\\ufffd" not in data
    assert "ctp bad char \ufffd".encode("utf-8") in data
