from __future__ import annotations

import json
from pathlib import Path

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig

import scripts.ctp_paper_readonly_snapshot as snapshot_script
from scripts.ctp_paper_readonly_snapshot import (
    build_instrument_detail_payload,
    build_connected_snapshot_with_watchdog,
    build_config_only_snapshot,
    classify_account_disposition,
    classify_positions_disposition,
    instrument_contract_issues,
    instrument_detail_contract_issues,
    paper_readonly_snapshot_config_issues,
    position_contract_issues,
    redacted_account_identity,
    snapshot_schema_metadata,
)


def _paper_config() -> CtpAdapterConfig:
    return CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "PAPER_USER_TEST",
            "Password": "secret",
            "Pricer": "tcp://trading.openctp.cn:30011",
            "Host": "tcp://trading.openctp.cn:30001",
            "Instruments": ["TEST"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["TEST"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
            },
        }
    )


def test_snapshot_schema_metadata_includes_phase3_reconciliation_fields() -> None:
    metadata = snapshot_schema_metadata(
        run_id="run-1",
        flow_path=Path("output/flow"),
        session_label="paper-dev",
    )

    assert metadata["run_id"] == "run-1"
    assert metadata["flow_path"] == "output\\flow"
    assert metadata["session_label"] == "paper-dev"
    assert metadata["account_profile"] == "openctp-tts-7x24-simulation"
    assert metadata["evidence_class"] == "openctp-tts-7x24-simulation"
    assert metadata["reconciliation_role"] == "pre_or_post_order_snapshot"


def test_redacted_account_identity_omits_raw_account_id() -> None:
    identity = redacted_account_identity("PAPER_USER_TEST")
    serialized = json.dumps(identity, ensure_ascii=False)

    assert identity["account_id_present"] is True
    assert identity["account_id_fingerprint"]
    assert "PAPER_USER_TEST" not in serialized


def test_dispositions_distinguish_valid_empty_from_timeout_and_failure() -> None:
    assert classify_positions_disposition(query_code=0, completed=True, timed_out=False, no_positions=True) == {
        "status": "passed",
        "disposition": "valid_empty",
        "failure_reason": None,
    }
    assert classify_positions_disposition(query_code=0, completed=False, timed_out=True, no_positions=False)[
        "failure_reason"
    ] == "positions_timed_out"
    assert classify_account_disposition(query_code=0, completed=True, timed_out=False, account_present=False)[
        "failure_reason"
    ] == "account_missing"


def test_config_only_snapshot_is_redacted_and_request_only(tmp_path: Path) -> None:
    config_path = tmp_path / "paper.json"
    config = _paper_config()

    snapshot = build_config_only_snapshot(
        config=config,
        config_path=config_path,
        run_id="run-2",
        flow_path=Path("output/paper-flow"),
        session_label="paper-session",
    )
    serialized = json.dumps(snapshot, ensure_ascii=False)

    assert snapshot["success"] is True
    assert snapshot["action_mode"] == "request_only"
    assert snapshot["schema"]["account_profile"] == "openctp-tts-7x24-simulation"
    assert snapshot["account"]["identity"]["account_id_present"] is True
    assert "PAPER_USER_TEST" not in serialized
    assert "secret" not in serialized


def test_readonly_snapshot_allows_exposure_reduction_smoke_flag_without_live_send() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "PAPER_USER_TEST",
            "Password": "secret",
            "Pricer": "tcp://trading.openctp.cn:30011",
            "Host": "tcp://trading.openctp.cn:30001",
            "Instruments": ["TEST"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["TEST"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
                "AllowExposureReductionOrderSmoke": True,
            },
        }
    )

    assert paper_readonly_snapshot_config_issues(config) == []


def test_readonly_snapshot_still_rejects_general_live_order_smoke() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "PAPER_USER_TEST",
            "Password": "secret",
            "Pricer": "tcp://trading.openctp.cn:30011",
            "Host": "tcp://trading.openctp.cn:30001",
            "Instruments": ["TEST"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["TEST"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": True,
                "AllowExposureReductionOrderSmoke": True,
            },
        }
    )

    assert "execution_guardrails.allow_live_order_smoke_must_be_false" in (
        paper_readonly_snapshot_config_issues(config)
    )


def test_connected_snapshot_watchdog_returns_typed_timeout_blocker(tmp_path: Path) -> None:
    config = _paper_config()
    payload = build_connected_snapshot_with_watchdog(
        config=config,
        config_path=tmp_path / "paper.json",
        run_id="run-timeout",
        flow_path=tmp_path / "flow",
        session_label="paper-timeout",
        timeout_seconds=20,
        completion_grace_seconds=1,
        observation_grace_seconds=1,
        process_timeout_seconds=0,
    )

    assert payload["success"] is False
    assert payload["status"] == "blocked"
    assert payload["blocker_type"] == "paper-resource"
    assert payload["failure_reason"] == "connect_process_timeout"
    assert payload["snapshot_complete"] is False
    assert payload["schema"]["account_profile"] == "openctp-tts-7x24-simulation"


def test_connected_snapshot_watchdog_uses_timed_queue_get_after_process_exit(
    monkeypatch, tmp_path: Path
) -> None:
    class FakeQueue:
        def get(self, *, timeout: float) -> dict:
            assert timeout > 0
            return {
                "kind": "payload",
                "payload": {
                    "success": True,
                    "status": "passed",
                    "sentinel": "queue-get",
                },
            }

    class FakeProcess:
        exitcode = 0

        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

        def start(self) -> None:
            return None

        def join(self, timeout=None) -> None:
            return None

        def is_alive(self) -> bool:
            return False

    class FakeContext:
        def Queue(self, maxsize: int) -> FakeQueue:
            assert maxsize == 1
            return FakeQueue()

        def Process(self, *, target, args) -> FakeProcess:
            return FakeProcess(target=target, args=args)

    monkeypatch.setattr(snapshot_script.mp, "get_context", lambda method: FakeContext())

    payload = build_connected_snapshot_with_watchdog(
        config=_paper_config(),
        config_path=tmp_path / "paper.json",
        run_id="run-queue-get",
        flow_path=tmp_path / "flow",
        session_label="paper-queue-get",
        timeout_seconds=20,
        completion_grace_seconds=1,
        observation_grace_seconds=1,
        process_timeout_seconds=5,
    )

    assert payload["success"] is True
    assert payload["sentinel"] == "queue-get"


def test_connected_snapshot_no_payload_blocker_includes_process_exitcode(monkeypatch, tmp_path: Path) -> None:
    class FakeQueue:
        def get(self, *, timeout: float) -> dict:
            raise snapshot_script.queue_mod.Empty

    class FakeProcess:
        exitcode = 17

        def start(self) -> None:
            return None

        def join(self, timeout=None) -> None:
            return None

        def is_alive(self) -> bool:
            return False

    class FakeContext:
        def Queue(self, maxsize: int) -> FakeQueue:
            return FakeQueue()

        def Process(self, *, target, args) -> FakeProcess:
            return FakeProcess()

    monkeypatch.setattr(snapshot_script.mp, "get_context", lambda method: FakeContext())

    payload = build_connected_snapshot_with_watchdog(
        config=_paper_config(),
        config_path=tmp_path / "paper.json",
        run_id="run-no-payload",
        flow_path=tmp_path / "flow",
        session_label="paper-no-payload",
        timeout_seconds=20,
        completion_grace_seconds=1,
        observation_grace_seconds=1,
        process_timeout_seconds=5,
    )

    assert payload["success"] is False
    assert payload["failure_reason"] == "connect_process_no_payload"
    assert payload["process_exitcode"] == 17


def test_instrument_correctness_requires_provider_cache_fields() -> None:
    class Instrument:
        venue_symbol = "TEST"
        display_symbol = "TEST.TEST"
        exchange_id = "TEST"
        price_tick = 1.0
        volume_multiple = 10

    assert instrument_contract_issues(Instrument()) == []

    Instrument.price_tick = None
    assert "price_tick" in instrument_contract_issues(Instrument())


def test_instrument_detail_payload_preserves_c1_fields_and_missing_list() -> None:
    class ProductKind:
        value = "futures"

    class Instrument:
        venue_symbol = "c2609"
        display_symbol = "c2609.DCE"
        exchange_id = "DCE"
        product_kind = ProductKind()
        instrument_name = "Iron Ore"
        open_date = "20250101"
        expire_date = "20260930"
        contract_month = "2609"
        product_id = "i"
        underlying_instr_id = "i2609"

    payload = build_instrument_detail_payload(Instrument())

    assert payload["detail_fields"]["instrument_name"] == "Iron Ore"
    assert payload["detail_fields"]["delivery_year"] == 2026
    assert payload["detail_fields"]["delivery_month"] == 9
    assert "is_trading" in payload["missing_fields"]
    assert payload["correctness_status"] == "passed"


def test_instrument_detail_contract_issues_flag_unknown_product_and_bad_dates() -> None:
    class ProductKind:
        value = "unknown"

    class Instrument:
        product_kind = ProductKind()
        open_date = "2025-01-01"
        expire_date = "2026/09/30"
        contract_month = "609"

    issues = instrument_detail_contract_issues(Instrument())

    assert "unknown_product_kind" in issues
    assert "open_date_invalid" in issues
    assert "expire_date_invalid" in issues
    assert "delivery_month_ambiguous" in issues


def test_position_correctness_requires_direction_and_qty_split() -> None:
    class Position:
        direction = "LONG"
        position_qty = 4
        yd_position_qty = 0
        td_position_qty = 4

    assert position_contract_issues(Position()) == []

    Position.direction = "INVALID"
    assert "direction" in position_contract_issues(Position())

    Position.direction = "LONG"
    Position.td_position_qty = -1
    assert "td_position_qty" in position_contract_issues(Position())
