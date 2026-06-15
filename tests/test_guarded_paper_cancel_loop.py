from __future__ import annotations

import json
from pathlib import Path

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig, CtpExecutionGuardrails
from nautilus_ctp_adapter.adapters.ctp.execution_client import (
    CtpCancelOrderIntent,
    CtpExecutionClient,
)

from scripts.ctp_guarded_paper_cancel_loop import (
    classify_cancel_events,
    run_guarded_paper_cancel,
    validate_cancel_command_contract,
)


def _config() -> CtpAdapterConfig:
    return CtpAdapterConfig(
        broker_id="9999",
        user_id="u",
        password="p",
        md_front="tcp://trading.openctp.cn:30011",
        td_front="tcp://trading.openctp.cn:30001",
        app_id="client_test",
        auth_code="auth",
        product_info="prod",
        instruments=["rb2610"],
        execution_guardrails=CtpExecutionGuardrails(
            enabled=True,
            allowed_instruments=["rb2610"],
            max_order_qty=3,
            max_net_position=3,
            max_submit_per_minute=5,
            allow_live_order_smoke=False,
        ),
    )


def _snapshot(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "success": True,
                "snapshot_complete": True,
                "schema": {
                    "account_profile": "openctp-tts-7x24-simulation",
                    "evidence_class": "openctp-tts-7x24-simulation",
                    "reconciliation_role": "pre_or_post_order_snapshot",
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_map_cancel_order_rejects_missing_native_identity() -> None:
    client = CtpExecutionClient(_config())

    mapped = client.map_cancel_order(
        CtpCancelOrderIntent(
            instrument_id="rb2610",
            client_order_id="cancel-1",
            order_ref=0,
            front_id=0,
            session_id=0,
        )
    )

    assert mapped.command is None
    assert mapped.error is not None
    assert mapped.error.error_id == 9003
    assert "cancel_contract_failed" in mapped.error.error_message
    assert "order_ref_missing" in mapped.error.error_message
    assert "front_id_missing" in mapped.error.error_message
    assert "session_id_missing" in mapped.error.error_message


def test_validate_cancel_command_contract_accepts_mapped_cancel() -> None:
    client = CtpExecutionClient(_config())
    mapped = client.map_cancel_order(
        CtpCancelOrderIntent(
            instrument_id="rb2610",
            client_order_id="cancel-1",
            order_ref=42,
            front_id=7,
            session_id=8,
            exchange_id="SHFE",
        )
    )

    verdict = validate_cancel_command_contract(
        {
            "instrument": "rb2610",
            "client_order_id": "cancel-1",
            "order_ref": 42,
            "front_id": 7,
            "session_id": 8,
            "exchange_id": "SHFE",
        },
        mapped.command,
    )

    assert verdict == {
        "accepted": True,
        "disposition": "cancel_contract_passed",
        "issues": [],
    }


def test_validate_cancel_command_contract_accepts_negative_ctp_session_id() -> None:
    client = CtpExecutionClient(_config())
    mapped = client.map_cancel_order(
        CtpCancelOrderIntent(
            instrument_id="rb2610",
            client_order_id="cancel-negative-session",
            order_ref=42,
            front_id=7,
            session_id=-1169162043,
            exchange_id="SHFE",
        )
    )

    verdict = validate_cancel_command_contract(
        {
            "instrument": "rb2610",
            "client_order_id": "cancel-negative-session",
            "order_ref": 42,
            "front_id": 7,
            "session_id": -1169162043,
            "exchange_id": "SHFE",
        },
        mapped.command,
    )

    assert mapped.error is None
    assert verdict["accepted"] is True


def test_run_guarded_paper_cancel_dry_run_does_not_submit_command(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "BrokerID": "9999",
                "UserID": "u",
                "Password": "p",
                "Pricer": "tcp://trading.openctp.cn:30011",
                "Host": "tcp://trading.openctp.cn:30001",
                "AppID": "client_test",
                "AuthCode": "auth",
                "ProductInfo": "prod",
                "Instruments": ["rb2610"],
                "ExecutionGuardrails": {
                    "Enabled": True,
                    "AllowedInstruments": ["rb2610"],
                    "MaxOrderQty": 3,
                    "MaxNetPosition": 3,
                    "MaxSubmitPerMinute": 5,
                    "AllowLiveOrderSmoke": False,
                },
            }
        ),
        encoding="utf-8",
    )

    payload = run_guarded_paper_cancel(
        config_path=config_path,
        pre_snapshot=_snapshot(tmp_path / "snapshot.json"),
        instrument="rb2610",
        client_order_id="cancel-1",
        order_ref=42,
        front_id=7,
        session_id=8,
        exchange_id="SHFE",
        arm_cancel_send=False,
    )

    assert payload["success"] is True
    assert payload["action_mode"] == "dry_run"
    assert payload["command_contract"]["accepted"] is True
    assert payload["cancel_lifecycle"]["command_kinds"] == []


def test_classify_cancel_events_deduplicates_cancel_callbacks() -> None:
    events = [
        {
            "kind": "order",
            "client_order_id": "cancel-1",
            "venue_symbol": "rb2610",
            "native_order_id": "SYS-1",
            "native_order_ref": "42",
            "status": "cancelled",
        },
        {
            "kind": "order",
            "client_order_id": "cancel-1",
            "venue_symbol": "rb2610",
            "native_order_id": "SYS-1",
            "native_order_ref": "42",
            "status": "cancelled",
        },
    ]

    verdict = classify_cancel_events(
        {
            "instrument": "rb2610",
            "client_order_id": "cancel-1",
            "order_ref": 42,
            "front_id": 7,
            "session_id": 8,
            "exchange_id": "SHFE",
        },
        events,
    )

    assert verdict["disposition"] == "cancelled"
    assert verdict["matched_event_count"] == 1
    assert verdict["duplicate_event_count"] == 1
