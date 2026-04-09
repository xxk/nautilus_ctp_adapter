import json
import os
from pathlib import Path
import subprocess
import sys

from nautilus_ctp_adapter import __version__
from nautilus_ctp_adapter.adapters.ctp import (
    CtpAccountQuerySmokeResult,
    CtpAccountQueryBaseline,
    CtpAdapterConfig,
    CtpCancelOrderIntent,
    CtpExecutionBootstrapResult,
    CtpExecutionClient,
    CtpLiveExecutionClientBootstrapResult,
    CtpLiveOpsSnapshot,
    CtpLiveOpsSnapshotAdapter,
    CtpLiveOpsEvidenceMatrix,
    CtpLiveOpsPolicyFinding,
    CtpLiveOpsPolicyResult,
    CtpLiveOpsSnapshotSummary,
    CtpMappedOrderCommand,
    CtpOrderLifecycleSmokeResult,
    CtpProductKind,
    CtpPositionQuerySmokeResult,
    CtpPositionQueryBaseline,
    CtpQueryAdapter,
    CtpQueryAdapterSnapshot,
    CtpReconciliationAdapter,
    CtpReconciliationEvidence,
    CtpReconciliationPolicyFinding,
    CtpReconciliationPolicyResult,
    CtpReconciliationSummary,
    CtpReconciliationSymbolExposure,
    CtpSessionRebuildFinding,
    CtpSessionRebuildPolicyResult,
    CtpStartupTruthAdapter,
    CtpStartupTruthEvidenceMatrix,
    CtpTdMergedEvidenceMatrix,
    CtpTdMergedReconciliationFinding,
    CtpTdMergedReconciliationPolicyResult,
    CtpTdTruthMergeSnapshot,
    CtpTruthMergeAdapter,
    CtpSubmitOrderIntent,
    CtpTdHistoricalCallbackBoundaryFinding,
    CtpTdHistoricalCallbackBoundaryPolicyResult,
    CtpTdBootstrapState,
    CtpTdExecEventPayload,
    CtpTdObservedCallback,
    CtpTdOrderTruthEvidenceMatrix,
    CtpTdOrderTruthBaseline,
    CtpTdSessionIdentity,
    CtpTdSmokeResult,
    CtpTdStartupTruthEvidence,
    normalize_exchange_id,
    normalize_product_kind,
    normalize_symbol,
)
from nautilus_ctp_adapter.adapters.ctp.data_client import (
    CtpMdBootstrapState,
    CtpLiveDataBootstrapResult,
    CtpMarketdataSmokeBaselineResult,
    CtpMdEventBatch,
    CtpMdDisconnectEventPayload,
    CtpMdLoginEventPayload,
    CtpMdRestoreResult,
    CtpMdRestorePolicyFinding,
    CtpMdRestorePolicyResult,
    CtpMdSmokeResult,
    CtpMdStartupTruthEvidence,
    CtpMdTruthEvidenceMatrix,
    CtpMdTickEventPayload,
)
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack
from nautilus_ctp_adapter.native.loader import (
    BOOTSTRAP_MANAGED_DLLS,
    REQUIRED_NATIVE_DLLS,
    candidate_managed_paths,
    candidate_native_paths,
)
from nautilus_ctp_adapter.native.md_ctypes import CtpMdApi
from nautilus_ctp_adapter.native.td_ctypes import CtpTdApi, NativeExecView
from nautilus_ctp_adapter.native.td_ctypes import NativePositionView, NativeTradingAccountView
from nautilus_ctp_adapter.native.manifest import (
    OPTIONAL_COMPAT_DLLS,
    REPO_OWNED_CTP_NATIVE_EXPORTS,
    describe_native_pack,
)
from nautilus_ctp_adapter.runtime import (
    CtpAccountRecord,
    CtpInstrumentRecord,
    CtpMarketRuntime,
    CtpOrderState,
    CtpPositionRecord,
    CtpQueryRuntime,
    CtpRuntimeBridge,
    CtpRuntimeCommand,
    CtpRuntimeCommandKind,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
    CtpSessionRuntime,
    CtpSessionState,
    CtpTradingRuntime,
)


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_factory_builds_minimal_stack() -> None:
    stack = build_ctp_stack(CtpAdapterConfig())
    assert isinstance(stack["runtime_bridge"], CtpRuntimeBridge)
    assert "instrument_provider" in stack
    assert "data_client" in stack
    assert "execution_client" in stack
    assert "query_adapter" in stack
    assert "reconciliation_adapter" in stack
    assert "startup_truth_adapter" in stack
    assert "live_ops_snapshot_adapter" in stack
    assert stack["instrument_provider"].runtime_bridge is stack["runtime_bridge"]
    assert stack["data_client"].runtime_bridge is stack["runtime_bridge"]
    assert stack["execution_client"].runtime_bridge is stack["runtime_bridge"]
    assert stack["query_adapter"].runtime_bridge is stack["runtime_bridge"]
    assert stack["query_adapter"].execution_client is stack["execution_client"]
    assert stack["reconciliation_adapter"].runtime_bridge is stack["runtime_bridge"]
    assert stack["reconciliation_adapter"].query_adapter is stack["query_adapter"]
    assert stack["startup_truth_adapter"].runtime_bridge is stack["runtime_bridge"]
    assert stack["startup_truth_adapter"].execution_client is stack["execution_client"]
    assert stack["live_ops_snapshot_adapter"].runtime_bridge is stack["runtime_bridge"]


def test_runtime_models_are_platform_neutral() -> None:
    command = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.CONNECT)
    event = CtpRuntimeEvent(kind=CtpRuntimeEventKind.CONNECTED)
    bridge = CtpRuntimeBridge()
    bridge.push_event(event)

    assert command.kind is CtpRuntimeCommandKind.CONNECT
    assert bridge.next_event() == event


def test_query_runtime_tracks_instrument_query_lifecycle() -> None:
    query = CtpQueryRuntime()
    request = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.QUERY_INSTRUMENTS,
        request_id="iq-1",
    )
    instrument = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.INSTRUMENT,
        request_id="iq-1",
        venue_symbol="rb2610",
        exchange_id="SHFE",
        payload={
            "product_class": "Futures",
            "instrument_name": "Rebar Oct 2026",
            "price_tick": "1.0",
            "volume_multiple": "10",
        },
    )
    end = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.INSTRUMENT_END,
        request_id="iq-1",
    )

    query.on_command(request)
    assert query.pending_instrument_query_count == 1
    assert query.is_query_pending("iq-1") is True

    query.on_event(instrument)
    records = query.instruments_for_request("iq-1")
    assert records == (
        CtpInstrumentRecord(
            venue_symbol="rb2610",
            exchange_id="SHFE",
            product_class="Futures",
            instrument_name="Rebar Oct 2026",
            price_tick=1.0,
            volume_multiple=10,
        ),
    )

    query.on_event(end)
    assert query.is_query_pending("iq-1") is False
    assert query.is_query_completed("iq-1") is True


def test_query_runtime_tracks_position_query_lifecycle() -> None:
    query = CtpQueryRuntime()
    request = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.QUERY_POSITIONS,
        request_id="pq-1",
    )
    position = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.POSITION,
        request_id="pq-1",
        venue_symbol="c2609",
        exchange_id="DCE",
        payload={
            "direction": "LONG",
            "position_qty": "2",
            "yd_position_qty": "1",
            "td_position_qty": "1",
            "position_cost": "51234.5",
            "snapshot_complete": "true",
        },
    )

    query.on_command(request)
    assert query.pending_position_query_count == 1
    assert query.is_query_pending("pq-1") is True

    query.on_event(position)
    records = query.positions_for_request("pq-1")
    assert records == (
        CtpPositionRecord(
            venue_symbol="c2609",
            exchange_id="DCE",
            direction="LONG",
            position_qty=2,
            yd_position_qty=1,
            td_position_qty=1,
            position_cost=51234.5,
        ),
    )
    assert query.position_count_for_request("pq-1") == 1
    assert query.is_query_pending("pq-1") is False
    assert query.is_query_completed("pq-1") is True


def test_query_runtime_ignores_blank_position_completion_marker() -> None:
    query = CtpQueryRuntime()
    query.on_command(
        CtpRuntimeCommand(
            kind=CtpRuntimeCommandKind.QUERY_POSITIONS,
            request_id="pq-2",
        )
    )

    query.on_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.POSITION,
            request_id="pq-2",
            payload={"snapshot_complete": "true"},
        )
    )

    assert query.position_count_for_request("pq-2") == 0
    assert query.is_query_completed("pq-2") is True


def test_query_runtime_tracks_account_query_lifecycle() -> None:
    query = CtpQueryRuntime()
    request = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.QUERY_ACCOUNT,
        request_id="aq-1",
    )
    account = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.ACCOUNT,
        request_id="aq-1",
        payload={
            "account_id": "025292",
            "balance": "1000000.5",
            "available": "850000.25",
            "margin": "120000.0",
            "commission": "35.5",
            "close_profit": "1200.0",
            "position_profit": "-230.0",
        },
    )

    query.on_command(request)
    assert query.pending_account_query_count == 1
    assert query.is_query_pending("aq-1") is True

    query.on_event(account)
    record = query.account_for_request("aq-1")
    assert record == CtpAccountRecord(
        account_id="025292",
        balance=1000000.5,
        available=850000.25,
        margin=120000.0,
        commission=35.5,
        close_profit=1200.0,
        position_profit=-230.0,
    )
    assert query.pending_account_query_count == 0
    assert query.is_query_pending("aq-1") is False
    assert query.is_query_completed("aq-1") is True


def test_runtime_bridge_submit_and_drain_contract() -> None:
    bridge = CtpRuntimeBridge()
    command_1 = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.CONNECT, request_id="req-1")
    command_2 = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.QUERY_ACCOUNT, request_id="req-2")
    event_1 = CtpRuntimeEvent(kind=CtpRuntimeEventKind.CONNECTED, request_id="req-1")
    event_2 = CtpRuntimeEvent(kind=CtpRuntimeEventKind.ACCOUNT, request_id="req-2")

    bridge.submit_command(command_1)
    bridge.submit_command(command_2)
    bridge.push_event(event_1)
    bridge.push_event(event_2)

    assert bridge.pending_command_count == 2
    assert bridge.pending_event_count == 2
    assert bridge.drain_submitted_commands(limit=1) == [command_1]
    assert bridge.pending_command_count == 1
    assert bridge.drain_events(limit=1) == [event_1]
    assert bridge.pending_event_count == 1
    assert bridge.drain_submitted_commands() == [command_2]
    assert bridge.drain_events() == [event_2]
    assert bridge.pending_command_count == 0
    assert bridge.pending_event_count == 0


def test_session_and_market_runtime_track_minimal_state() -> None:
    session = CtpSessionRuntime()
    market = CtpMarketRuntime()

    connect = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.CONNECT)
    subscribe = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA,
        venue_symbol="rb2512",
        exchange_id="SHFE",
    )
    connected = CtpRuntimeEvent(kind=CtpRuntimeEventKind.CONNECTED)
    logged_in = CtpRuntimeEvent(kind=CtpRuntimeEventKind.LOGIN_SUCCEEDED)

    session.on_command(connect)
    market.on_command(subscribe)
    session.on_event(connected)
    session.on_event(logged_in)

    assert session.state is CtpSessionState.LOGGED_IN
    assert session.is_connected is True
    assert market.subscription_count == 1
    assert market.is_subscribed("rb2512", "SHFE") is True


def test_trading_runtime_tracks_order_state_transitions() -> None:
    trading = CtpTradingRuntime()
    submit = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
        client_order_id="ord-1",
    )
    working = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.ORDER,
        client_order_id="ord-1",
    )
    filled = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.TRADE,
        client_order_id="ord-1",
    )

    trading.on_command(submit)
    assert trading.state_for("ord-1") is CtpOrderState.PENDING_SUBMIT

    trading.on_event(working)
    assert trading.state_for("ord-1") is CtpOrderState.WORKING

    trading.on_event(filled)
    assert trading.state_for("ord-1") is CtpOrderState.FILLED
    assert trading.tracked_order_count == 1


def test_bridge_updates_trading_runtime_automatically() -> None:
    bridge = CtpRuntimeBridge()

    bridge.submit_command(
        CtpRuntimeCommand(
            kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
            client_order_id="ord-2",
        )
    )
    assert bridge.trading.state_for("ord-2") is CtpOrderState.PENDING_SUBMIT

    bridge.push_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.ORDER,
            client_order_id="ord-2",
        )
    )
    assert bridge.trading.state_for("ord-2") is CtpOrderState.WORKING


def test_bridge_updates_query_runtime_automatically() -> None:
    bridge = CtpRuntimeBridge()
    bridge.submit_command(
        CtpRuntimeCommand(
            kind=CtpRuntimeCommandKind.QUERY_INSTRUMENTS,
            request_id="iq-2",
        )
    )
    bridge.push_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.INSTRUMENT,
            request_id="iq-2",
            venue_symbol="c2609",
            exchange_id="DCE",
            payload={
                "product_class": "Futures",
                "instrument_name": "Corn Sep 2026",
                "price_tick": "1.0",
                "volume_multiple": "10",
            },
        )
    )
    bridge.push_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.INSTRUMENT_END,
            request_id="iq-2",
        )
    )

    assert bridge.query.is_query_completed("iq-2") is True
    assert bridge.query.instrument_count_for_request("iq-2") == 1


def test_ctp_config_loads_repo_example(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "cfgs" / "ctp.live.example.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["Password"] = "secret"
    local_path = tmp_path / "ctp.live.local.json"
    local_path.write_text(json.dumps(payload), encoding="utf-8")

    config = CtpAdapterConfig.from_json_file(local_path)

    assert config.user_id == "025292"
    assert config.md_front == "tcp://md-front.example:51213"
    assert config.td_front == "tcp://td-front.example:51205"
    assert config.instruments == ["rb2610"]
    assert config.execution_guardrails.enabled is True
    assert config.execution_guardrails.allowed_instruments == ["c2609"]
    assert config.execution_guardrails.max_order_qty == 1
    assert config.execution_guardrails.max_net_position == 5
    assert config.execution_guardrails.max_submit_per_minute == 10
    assert config.execution_guardrails.price_mode == "best_level_1"
    assert config.execution_guardrails.allow_live_order_smoke is False
    assert config.validate() == []


def test_ctp_config_accepts_myvnpy_connect_ctp_shape() -> None:
    payload = {
        "用户名": "025292",
        "密码": "secret",
        "经纪商代码": "0155",
        "交易服务器": "106.75.173.28:51205",
        "行情服务器": "106.75.173.28:51213",
        "产品名称": "client_iq_3.6.2",
        "授权编码": "RFLEXUGHCKIKWGPC",
        "柜台环境": "实盘",
        "service": "iQuant",
        "instruments": ["rb2610"],
    }

    config = CtpAdapterConfig.from_dict(payload)

    assert config.user_id == "025292"
    assert config.broker_id == "0155"
    assert config.auth_code == "RFLEXUGHCKIKWGPC"
    assert config.app_id == "client_iq_3.6.2"
    assert config.product_info == "iQuant"
    assert config.md_front == "tcp://106.75.173.28:51213"
    assert config.td_front == "tcp://106.75.173.28:51205"
    assert config.validate() == []


def test_exchange_normalization_supports_aliases() -> None:
    assert normalize_exchange_id("SHF") == "SHFE"
    assert normalize_exchange_id("zce") == "CZCE"
    assert normalize_exchange_id("CFE") == "CFFEX"
    assert normalize_exchange_id("XINE") == "INE"
    assert normalize_exchange_id("GFEX") == "GFEX"


def test_symbol_normalization_follows_exchange_case_rules() -> None:
    assert normalize_symbol("RB2610", "SHFE") == "rb2610"
    assert normalize_symbol("m2609", "DCE") == "m2609"
    assert normalize_symbol("LC2609", "GFEX") == "lc2609"
    assert normalize_symbol("if2606", "CFFEX") == "IF2606"
    assert normalize_symbol("ta2609", "CZCE") == "TA2609"


def test_product_kind_normalization_maps_ctp_values() -> None:
    assert normalize_product_kind("1") is CtpProductKind.FUTURES
    assert normalize_product_kind("49") is CtpProductKind.FUTURES
    assert normalize_product_kind("2") is CtpProductKind.OPTION
    assert normalize_product_kind("50") is CtpProductKind.OPTION
    assert normalize_product_kind("Futures") is CtpProductKind.FUTURES
    assert normalize_product_kind("Options") is CtpProductKind.OPTION
    assert normalize_product_kind("7") is CtpProductKind.TAS
    assert normalize_product_kind("mystery") is CtpProductKind.UNKNOWN


def test_execution_precheck_enforces_real_account_guardrails() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "UserID": "025292",
            "BrokerID": "0155",
            "Password": "secret",
            "Pricer": "tcp://md-front.example:51213",
            "Host": "tcp://td-front.example:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    client = CtpExecutionClient(config)

    rejected = client.precheck_debug_order(
        instrument_id="rb2610",
        side="BUY",
        quantity=2,
        projected_net_position=6,
        submit_count_last_minute=10,
        best_bid=3200.0,
        best_ask=3201.0,
    )

    assert rejected.allowed is False
    assert any("instrument rb2610" in item for item in rejected.violations)
    assert any("quantity 2" in item for item in rejected.violations)
    assert any("projected_net_position 6" in item for item in rejected.violations)
    assert any("submit_count_last_minute 10" in item for item in rejected.violations)


def test_execution_precheck_uses_best_level_1_price() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "UserID": "025292",
            "BrokerID": "0155",
            "Password": "secret",
            "Pricer": "tcp://md-front.example:51213",
            "Host": "tcp://td-front.example:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    client = CtpExecutionClient(config)

    buy = client.precheck_debug_order(
        instrument_id="c2609",
        side="BUY",
        quantity=1,
        projected_net_position=5,
        submit_count_last_minute=9,
        best_bid=1820.0,
        best_ask=1821.0,
    )
    sell = client.precheck_debug_order(
        instrument_id="c2609",
        side="SELL",
        quantity=1,
        projected_net_position=4,
        submit_count_last_minute=9,
        best_bid=1819.0,
        best_ask=1820.0,
    )

    assert buy.allowed is True
    assert buy.selected_price == 1821.0
    assert sell.allowed is True
    assert sell.selected_price == 1819.0


def test_instrument_provider_bootstrap_submits_query_contract() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    bridge = stack["runtime_bridge"]

    state = provider.bootstrap_instrument_query_mainline()
    commands = bridge.drain_submitted_commands()

    assert state.started is True
    assert state.request_id == "instrument-query-1"
    assert len(commands) == 1
    assert commands[0].kind is CtpRuntimeCommandKind.QUERY_INSTRUMENTS
    assert commands[0].payload["channel"] == "td"
    assert commands[0].payload["query_scope"] == "instruments"
    assert provider.latest_load_result is None


def test_instrument_provider_load_all_returns_pending_result_shape() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    bridge = stack["runtime_bridge"]

    result = provider.load_all_instruments_mainline()
    commands = bridge.drain_submitted_commands()

    assert result.request_id == "instrument-query-1"
    assert result.loaded is False
    assert result.instrument_count == 0
    assert result.instruments == ()
    assert len(commands) == 1


def test_instrument_provider_callbacks_push_query_events() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    bridge = stack["runtime_bridge"]

    state = provider.bootstrap_instrument_query_mainline()
    bridge.drain_submitted_commands()
    provider.push_instrument_snapshot(
        request_id=state.request_id or "",
        venue_symbol="rb2610",
        exchange_id="SHFE",
        product_class="Futures",
        instrument_name="Rebar Oct 2026",
        price_tick=1.0,
        volume_multiple=10,
    )
    provider.complete_instrument_query(request_id=state.request_id or "", instrument_count=1)
    events = bridge.drain_events()

    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.INSTRUMENT,
        CtpRuntimeEventKind.INSTRUMENT_END,
    ]
    assert provider.loaded is True
    assert bridge.query.is_query_completed(state.request_id or "") is True
    assert bridge.query.instrument_count_for_request(state.request_id or "") == 1
    assert provider.latest_load_result is not None
    assert provider.latest_load_result.loaded is True
    assert provider.latest_load_result.instrument_count == 1


def test_instrument_provider_normalizes_query_results() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]

    state = provider.bootstrap_instrument_query_mainline()
    provider.runtime_bridge.drain_submitted_commands()
    provider.push_instrument_snapshot(
        request_id=state.request_id or "",
        venue_symbol="RB2610",
        exchange_id="SHF",
        product_class="1",
        instrument_name="Rebar Oct 2026",
        price_tick=1.0,
        volume_multiple=10,
    )
    provider.complete_instrument_query(request_id=state.request_id or "", instrument_count=1)
    normalized = provider.normalized_instruments_for_request(state.request_id or "")

    assert len(normalized) == 1
    assert normalized[0].exchange_id == "SHFE"
    assert normalized[0].venue_symbol == "rb2610"
    assert normalized[0].display_symbol == "rb2610.SHFE"
    assert normalized[0].underlying == "rb"
    assert normalized[0].contract_month == "2610"
    assert normalized[0].product_kind is CtpProductKind.FUTURES


def test_instrument_provider_load_result_for_request_exposes_stable_shape() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]

    state = provider.bootstrap_instrument_query_mainline()
    provider.runtime_bridge.drain_submitted_commands()
    provider.push_instrument_snapshot(
        request_id=state.request_id or "",
        venue_symbol="IF2606",
        exchange_id="CFE",
        product_class="1",
        instrument_name="CSI 300 Jun 2026",
        price_tick=0.2,
        volume_multiple=300,
    )
    provider.complete_instrument_query(request_id=state.request_id or "", instrument_count=1)

    result = provider.load_result_for_request(state.request_id or "")

    assert result.loaded is True
    assert result.instrument_count == 1
    assert result.instruments[0].exchange_id == "CFFEX"
    assert result.instruments[0].venue_symbol == "IF2606"
    assert result.instruments[0].display_symbol == "IF2606.CFFEX"


def test_native_loader_candidates_cover_repo_owned_pack() -> None:
    root = Path(__file__).resolve().parents[1]
    native_paths = candidate_native_paths(root)
    managed_paths = candidate_managed_paths(root)

    assert root / "vendor" / "ctp" / "bin" in native_paths
    assert root / "vendor" / "ctp" / "bin" in managed_paths
    assert "ctp_native.dll" in REQUIRED_NATIVE_DLLS
    assert "CTPProviderSwig.dll" in BOOTSTRAP_MANAGED_DLLS


def test_native_manifest_tracks_repo_owned_abi_and_pack_layout() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = describe_native_pack(root)
    export_symbols = [item.symbol for item in REPO_OWNED_CTP_NATIVE_EXPORTS]

    assert manifest["vendor_dir"] == root / "vendor" / "ctp"
    assert manifest["bin_dir"] == root / "vendor" / "ctp" / "bin"
    assert "ctp_native.dll" in manifest["required_native_dlls"]
    assert "thosttraderapi.dll" in manifest["optional_compat_dlls"]
    assert "MdCreate" in export_symbols
    assert "TdOrderSend" in export_symbols
    assert "MdSetLoginCallback" in manifest["repo_owned_exports"]
    assert OPTIONAL_COMPAT_DLLS == ("thostmduserapi.dll", "thosttraderapi.dll")


def test_ctypes_md_api_loads_repo_owned_md_exports() -> None:
    root = Path(__file__).resolve().parents[1]
    api = CtpMdApi.load(root)
    flow_path = root / "var" / "test_md_api_flow"
    flow_path.mkdir(parents=True, exist_ok=True)
    handle = api.create(flow_path)
    try:
        assert handle > 0
    finally:
        api.dispose(handle)


def test_ctypes_td_api_loads_repo_owned_td_exports() -> None:
    root = Path(__file__).resolve().parents[1]
    api = CtpTdApi.load(root)
    flow_path = root / "var" / "test_td_api_flow"
    flow_path.mkdir(parents=True, exist_ok=True)
    handle = api.create(flow_path)
    try:
        assert handle > 0
    finally:
        api.dispose(handle)


def test_data_client_bootstrap_submits_md_connect_and_subscribe_commands() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    bridge = stack["runtime_bridge"]

    state = data_client.bootstrap_market_data_mainline()
    commands = bridge.drain_submitted_commands()

    assert state.started is True
    assert state.connect_request_id == "md-connect-1"
    assert state.subscribe_request_ids == ["md-subscribe-2"]
    assert len(commands) == 2
    assert commands[0].kind is CtpRuntimeCommandKind.CONNECT
    assert commands[0].payload["channel"] == "md"
    assert commands[0].payload["front"] == "tcp://106.75.173.28:51213"
    assert commands[1].kind is CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA
    assert commands[1].venue_symbol == "rb2610"


def test_data_client_can_bootstrap_from_instrument_provider_result() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    data_client = stack["data_client"]
    bridge = stack["runtime_bridge"]

    query_state = provider.bootstrap_instrument_query_mainline()
    bridge.drain_submitted_commands()
    provider.push_instrument_snapshot(
        request_id=query_state.request_id or "",
        venue_symbol="RB2610",
        exchange_id="SHF",
        product_class="49",
        instrument_name="Rebar Oct 2026",
        price_tick=1.0,
        volume_multiple=10,
    )
    provider.complete_instrument_query(request_id=query_state.request_id or "", instrument_count=1)
    load_result = provider.load_result_for_request(query_state.request_id or "")

    bootstrap = data_client.bootstrap_live_data_client_mainline(load_result)
    commands = bridge.drain_submitted_commands()

    assert isinstance(bootstrap, CtpLiveDataBootstrapResult)
    assert bootstrap.instrument_request_id == "instrument-query-1"
    assert bootstrap.instrument_loaded is True
    assert bootstrap.source_instrument_count == 1
    assert bootstrap.selected_symbols == ("rb2610",)
    assert bootstrap.bootstrap_state.started is True
    assert bootstrap.bootstrap_state.connect_request_id == "md-connect-1"
    assert bootstrap.bootstrap_state.subscribe_request_ids == ["md-subscribe-2"]
    assert commands[-1].kind is CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA
    assert commands[-1].venue_symbol == "rb2610"


def test_data_client_selects_configured_symbols_from_provider_result() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    data_client = stack["data_client"]

    query_state = provider.bootstrap_instrument_query_mainline()
    provider.runtime_bridge.drain_submitted_commands()
    provider.push_instrument_snapshot(
        request_id=query_state.request_id or "",
        venue_symbol="RB2610",
        exchange_id="SHF",
        product_class="49",
        instrument_name="Rebar Oct 2026",
        price_tick=1.0,
        volume_multiple=10,
    )
    provider.push_instrument_snapshot(
        request_id=query_state.request_id or "",
        venue_symbol="RB2610C3200",
        exchange_id="SHF",
        product_class="50",
        instrument_name="Rebar Call 3200",
        price_tick=0.5,
        volume_multiple=10,
    )
    provider.push_instrument_snapshot(
        request_id=query_state.request_id or "",
        venue_symbol="RB2610P3200",
        exchange_id="SHF",
        product_class="50",
        instrument_name="Rebar Put 3200",
        price_tick=0.5,
        volume_multiple=10,
    )
    provider.complete_instrument_query(request_id=query_state.request_id or "", instrument_count=3)
    load_result = provider.load_result_for_request(query_state.request_id or "")

    selected = data_client.select_subscription_symbols(load_result)

    assert selected == ("rb2610",)


def test_data_client_live_callbacks_push_bridge_events() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    bridge = stack["runtime_bridge"]
    state: dict[str, object] = {}

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 1
        session_id = 2
        max_order_ref = 3

    class Tick:
        symbol = "rb2610"
        last = 3127.0
        bid = 3126.0
        ask = 3127.0
        ts_epoch_us = 1775094554636325

    data_client._on_md_login_callback(LoginResponse(), state)
    data_client._on_md_tick_callback(Tick(), state)
    events = bridge.drain_events()

    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        CtpRuntimeEventKind.TICK,
    ]
    assert events[1].venue_symbol == "rb2610"
    assert events[1].payload["last"] == "3127.0"


def test_data_client_drains_marketdata_events_with_stable_order() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    state: dict[str, object] = {}

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 7
        session_id = 8
        max_order_ref = 9

    class Tick:
        symbol = "rb2610"
        last = 3133.0
        bid = 3132.0
        ask = 3133.0
        ts_epoch_us = 1775096000000000

    data_client._on_md_login_callback(LoginResponse(), state)
    data_client._on_md_tick_callback(Tick(), state)
    data_client._emit_marketdata_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.DISCONNECTED,
            message="md_disconnected:4097",
            payload={"channel": "md", "reason": "4097"},
        )
    )

    events = data_client.drain_marketdata_events()

    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        CtpRuntimeEventKind.TICK,
        CtpRuntimeEventKind.DISCONNECTED,
    ]


def test_data_client_drain_batch_marks_restore_needed_on_disconnect() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]

    data_client.bootstrap_market_data_mainline()
    data_client._emit_marketdata_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.TICK,
            venue_symbol="rb2610",
            payload={"channel": "md", "last": "3130", "bid": "3129", "ask": "3130", "ts_epoch_us": "1"},
        )
    )
    data_client._emit_marketdata_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.DISCONNECTED,
            payload={"channel": "md", "reason": "4097"},
        )
    )

    batch = data_client.drain_marketdata_event_batch()

    assert isinstance(batch, CtpMdEventBatch)
    assert [event.kind for event in batch.events] == [
        CtpRuntimeEventKind.TICK,
        CtpRuntimeEventKind.DISCONNECTED,
    ]
    assert batch.contains_disconnect is True
    assert batch.should_restore is True


def test_data_client_restore_resubmits_active_subscriptions() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    bridge = stack["runtime_bridge"]

    data_client.bootstrap_market_data_mainline()
    bridge.drain_submitted_commands()

    restored = data_client.restore_market_data_subscriptions()
    commands = bridge.drain_submitted_commands()

    assert isinstance(restored, CtpMdRestoreResult)
    assert restored.triggered is True
    assert restored.restored_symbols == ("rb2610",)
    assert restored.bootstrap_state is not None
    assert restored.bootstrap_state.connect_request_id == "md-connect-3"
    assert restored.bootstrap_state.subscribe_request_ids == ["md-subscribe-4"]
    assert [command.kind for command in commands] == [
        CtpRuntimeCommandKind.CONNECT,
        CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA,
    ]


def test_data_client_restore_is_noop_without_active_subscriptions() -> None:
    data_client = build_ctp_stack(CtpAdapterConfig())["data_client"]

    restored = data_client.restore_market_data_subscriptions()

    assert restored.triggered is False
    assert restored.restored_symbols == ()
    assert restored.bootstrap_state is None


def test_data_client_marketdata_smoke_baseline_result_shape() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    data_client = stack["data_client"]

    query_state = provider.bootstrap_instrument_query_mainline()
    provider.runtime_bridge.drain_submitted_commands()
    provider.push_instrument_snapshot(
        request_id=query_state.request_id or "",
        venue_symbol="RB2610",
        exchange_id="SHF",
        product_class="49",
        instrument_name="Rebar Oct 2026",
        price_tick=1.0,
        volume_multiple=10,
    )
    provider.complete_instrument_query(request_id=query_state.request_id or "", instrument_count=1)
    load_result = provider.load_result_for_request(query_state.request_id or "")

    def fake_run_live_md_smoke(*, timeout_seconds: int = 20, flow_path=None) -> CtpMdSmokeResult:
        data_client._emit_marketdata_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.LOGIN_SUCCEEDED,
                payload={"channel": "md", "front_id": "1", "session_id": "2", "max_order_ref": "3", "error_id": "0"},
            )
        )
        data_client._emit_marketdata_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.TICK,
                venue_symbol="rb2610",
                payload={"channel": "md", "last": "3132", "bid": "3131", "ask": "3132", "ts_epoch_us": "10"},
            )
        )
        return CtpMdSmokeResult(
            init_code=0,
            login_request_code=0,
            subscribe_code=0,
            login_success=True,
            login_error_id=0,
            login_error_message="",
            first_tick_symbol="rb2610",
            first_tick_last=3132.0,
            first_tick_bid=3131.0,
            first_tick_ask=3132.0,
            first_tick_ts_epoch_us=10,
        )

    data_client.run_live_md_smoke = fake_run_live_md_smoke  # type: ignore[method-assign]
    result = data_client.run_marketdata_smoke_baseline(load_result)

    assert isinstance(result, CtpMarketdataSmokeBaselineResult)
    assert result.instrument_loaded is True
    assert result.selected_symbols == ("rb2610",)
    assert result.md_smoke.first_tick_symbol == "rb2610"
    assert [event.kind for event in result.event_batch.events] == [
        CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        CtpRuntimeEventKind.TICK,
    ]


def test_marketdata_payload_parsers_freeze_contract_shape() -> None:
    login_event = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        message="",
        payload={
            "channel": "md",
            "front_id": "11",
            "session_id": "22",
            "max_order_ref": "33",
            "error_id": "0",
        },
    )
    tick_event = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.TICK,
        venue_symbol="rb2610",
        payload={
            "channel": "md",
            "last": "3131.0",
            "bid": "3130.0",
            "ask": "3131.0",
            "ts_epoch_us": "1775095574458788",
        },
    )
    disconnect_event = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.DISCONNECTED,
        payload={
            "channel": "md",
            "reason": "4097",
        },
    )

    login = CtpMdLoginEventPayload.from_runtime_event(login_event)
    tick = CtpMdTickEventPayload.from_runtime_event(tick_event)
    disconnect = CtpMdDisconnectEventPayload.from_runtime_event(disconnect_event)

    assert login.channel == "md"
    assert login.success is True
    assert login.front_id == 11
    assert tick.venue_symbol == "rb2610"
    assert tick.last == 3131.0
    assert disconnect.reason == 4097


def test_execution_client_live_callbacks_push_bridge_events() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]
    state: dict[str, object] = {"disconnects": []}

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 11
        session_id = 22
        max_order_ref = 1

    execution_client._on_td_login_callback(LoginResponse(), state)
    execution_client._on_td_disconnect(4097, state)
    events = bridge.drain_events()

    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        CtpRuntimeEventKind.DISCONNECTED,
    ]
    assert events[0].payload["channel"] == "td"
    assert events[1].message == "td_disconnected:4097"


def test_execution_client_bootstrap_submits_td_connect_command() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    bootstrap = execution_client.bootstrap_execution_mainline()
    commands = bridge.drain_submitted_commands()

    assert isinstance(bootstrap, CtpTdBootstrapState)
    assert bootstrap.started is True
    assert bootstrap.connect_request_id == "td-connect-1"
    assert len(commands) == 1
    assert commands[0].kind is CtpRuntimeCommandKind.CONNECT
    assert commands[0].payload["channel"] == "td"
    assert commands[0].payload["front"] == "tcp://106.75.173.28:51205"


def test_execution_client_mainline_login_result_shape() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    execution_client = build_ctp_stack(config)["execution_client"]

    def fake_td_readiness_smoke(*, timeout_seconds: int = 20, flow_path=None) -> CtpTdSmokeResult:
        return CtpTdSmokeResult(
            init_code=0,
            authenticate_code=0,
            login_code=0,
            settlement_code=0,
            login_success=True,
            login_error_id=0,
            login_error_message="",
            front_id=1,
            session_id=2,
            max_order_ref=3,
            disconnects=[],
        )

    execution_client.run_live_td_readiness_smoke = fake_td_readiness_smoke  # type: ignore[method-assign]
    result = execution_client.run_td_mainline_login_bootstrap()

    assert isinstance(result, CtpExecutionBootstrapResult)
    assert result.bootstrap_state.started is True
    assert result.bootstrap_state.connect_request_id == "td-connect-1"
    assert result.td_smoke.login_success is True
    assert result.td_smoke.settlement_code == 0


def test_execution_client_maps_submit_order_with_td_identity() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    state: dict[str, object] = {"disconnects": []}

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 11
        session_id = 22
        max_order_ref = 100

    execution_client._on_td_login_callback(LoginResponse(), state)
    mapped = execution_client.map_submit_order(
        CtpSubmitOrderIntent(
            instrument_id="c2609",
            side="BUY",
            quantity=1,
            limit_price=2245.0,
            client_order_id="client-1",
        )
    )
    submitted = execution_client.submit_mapped_order(mapped)
    commands = bridge.drain_submitted_commands()

    assert execution_client.td_session_identity == CtpTdSessionIdentity(front_id=11, session_id=22, max_order_ref=100)
    assert isinstance(submitted, CtpMappedOrderCommand)
    assert submitted.error is None
    assert submitted.order_ref == 101
    assert submitted.front_id == 11
    assert submitted.session_id == 22
    assert submitted.command is not None
    assert submitted.command.kind is CtpRuntimeCommandKind.SUBMIT_ORDER
    assert submitted.command.payload["order_ref"] == "101"
    assert submitted.command.payload["front_id"] == "11"
    assert submitted.command.payload["session_id"] == "22"
    assert commands[-1].kind is CtpRuntimeCommandKind.SUBMIT_ORDER


def test_execution_client_rejects_submit_mapping_when_guardrails_fail() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    execution_client = build_ctp_stack(config)["execution_client"]

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 11
        session_id = 22
        max_order_ref = 100

    execution_client._on_td_login_callback(LoginResponse(), {"disconnects": []})
    mapped = execution_client.map_submit_order(
        CtpSubmitOrderIntent(
            instrument_id="rb2610",
            side="BUY",
            quantity=2,
            limit_price=3132.0,
            client_order_id="client-2",
        )
    )

    assert mapped.command is None
    assert mapped.error is not None
    assert mapped.error.error_id == 9001
    assert "instrument rb2610" in mapped.error.error_message
    assert "quantity 2" in mapped.error.error_message


def test_execution_client_maps_cancel_order_with_stable_identity_fields() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    mapped = execution_client.map_cancel_order(
        CtpCancelOrderIntent(
            instrument_id="c2609",
            client_order_id="client-3",
            order_ref=105,
            front_id=11,
            session_id=22,
            exchange_id="DCE",
        )
    )
    execution_client.submit_mapped_order(mapped)
    commands = bridge.drain_submitted_commands()

    assert mapped.error is None
    assert mapped.command is not None
    assert mapped.command.kind is CtpRuntimeCommandKind.CANCEL_ORDER
    assert mapped.command.exchange_id == "DCE"
    assert mapped.command.payload["order_ref"] == "105"
    assert mapped.command.payload["front_id"] == "11"
    assert mapped.command.payload["session_id"] == "22"
    assert commands[-1].kind is CtpRuntimeCommandKind.CANCEL_ORDER


def test_live_execution_client_bootstrap_result_shape() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    execution_client = build_ctp_stack(config)["execution_client"]

    def fake_td_readiness_smoke(*, timeout_seconds: int = 20, flow_path=None) -> CtpTdSmokeResult:
        return CtpTdSmokeResult(
            init_code=0,
            authenticate_code=0,
            login_code=0,
            settlement_code=0,
            login_success=True,
            login_error_id=0,
            login_error_message="",
            front_id=31,
            session_id=41,
            max_order_ref=51,
            disconnects=[],
        )

    execution_client.run_live_td_readiness_smoke = fake_td_readiness_smoke  # type: ignore[method-assign]
    result = execution_client.bootstrap_live_execution_client_mainline()

    assert isinstance(result, CtpLiveExecutionClientBootstrapResult)
    assert result.ready is True
    assert result.execution_bootstrap.bootstrap_state.connect_request_id == "td-connect-1"
    assert result.td_session_identity == CtpTdSessionIdentity(front_id=31, session_id=41, max_order_ref=51)


def test_live_execution_client_debug_submit_uses_bootstrap_identity() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    def fake_td_readiness_smoke(*, timeout_seconds: int = 20, flow_path=None) -> CtpTdSmokeResult:
        return CtpTdSmokeResult(
            init_code=0,
            authenticate_code=0,
            login_code=0,
            settlement_code=0,
            login_success=True,
            login_error_id=0,
            login_error_message="",
            front_id=11,
            session_id=22,
            max_order_ref=7,
            disconnects=[],
        )

    execution_client.run_live_td_readiness_smoke = fake_td_readiness_smoke  # type: ignore[method-assign]
    bootstrap = execution_client.bootstrap_live_execution_client_mainline()
    bridge.drain_submitted_commands()

    mapped = execution_client.submit_debug_order_mainline(
        CtpSubmitOrderIntent(
            instrument_id="c2609",
            side="SELL",
            quantity=1,
            limit_price=2238.0,
            client_order_id="client-4",
        )
    )
    commands = bridge.drain_submitted_commands()

    assert bootstrap.ready is True
    assert mapped.error is None
    assert mapped.order_ref == 8
    assert commands[-1].kind is CtpRuntimeCommandKind.SUBMIT_ORDER
    assert commands[-1].payload["front_id"] == "11"
    assert commands[-1].payload["session_id"] == "22"


def test_position_query_smoke_collects_runtime_positions_with_fake_native() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    class FakeTdApi:
        def __init__(self) -> None:
            self._login_callback = None
            self._disconnect_callback = None
            self._position_callback = None

        def create(self, flow_path: Path) -> int:
            self.flow_path = flow_path
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_position_callback(self, handle: int, callback):
            self._position_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            assert self._login_callback is not None
            self._login_callback(LoginResponse())
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

        def qry_position(self, handle: int) -> int:
            assert self._position_callback is not None
            self._position_callback(
                NativePositionView(
                    symbol="c2609",
                    broker_id="0155",
                    investor_id="025292",
                    pos_direction=2,
                    hedge_flag=1,
                    date_type=1,
                    position=3,
                    yd_position=1,
                    today_position=2,
                    position_cost=61234.5,
                    open_cost=60000.0,
                    exchange_margin=12000.0,
                    use_margin=11000.0,
                    position_profit=345.0,
                    ts_epoch_us=123456789,
                )
            )
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        result = execution_client.run_live_position_query_smoke(
            timeout_seconds=2,
            completion_grace_seconds=0.0,
        )
    finally:
        setattr(CtpTdApi, "load", original_load)

    events = bridge.drain_events()
    commands = bridge.drain_submitted_commands()

    assert isinstance(result, CtpPositionQuerySmokeResult)
    assert result.bootstrap.ready is True
    assert result.query_code == 0
    assert result.completed is True
    assert result.timed_out is False
    assert result.no_positions is False
    assert result.position_count == 1
    assert result.positions == (
        CtpPositionRecord(
            venue_symbol="c2609",
            exchange_id=None,
            direction="LONG",
            position_qty=3,
            yd_position_qty=1,
            td_position_qty=2,
            position_cost=61234.5,
        ),
    )
    assert [command.kind for command in commands][-1] is CtpRuntimeCommandKind.QUERY_POSITIONS
    assert any(event.kind is CtpRuntimeEventKind.POSITION for event in events)


def test_account_query_smoke_collects_runtime_account_with_fake_native() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    class FakeTdApi:
        def __init__(self) -> None:
            self._login_callback = None
            self._disconnect_callback = None
            self._account_callback = None

        def create(self, flow_path: Path) -> int:
            self.flow_path = flow_path
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_account_callback(self, handle: int, callback):
            self._account_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            assert self._login_callback is not None
            self._login_callback(LoginResponse())
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

        def qry_account(self, handle: int) -> int:
            assert self._account_callback is not None
            self._account_callback(
                NativeTradingAccountView(
                    broker_id="0155",
                    account_id="025292",
                    balance=1000000.5,
                    available=850000.25,
                    withdraw_quota=800000.0,
                    curr_margin=120000.0,
                    frozen_margin=5000.0,
                    commission=35.5,
                    frozen_commission=5.0,
                    position_profit=-230.0,
                    close_profit=1200.0,
                    currency_id="CNY",
                    ts_epoch_us=123456790,
                )
            )
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        result = execution_client.run_live_account_query_smoke(timeout_seconds=2)
    finally:
        setattr(CtpTdApi, "load", original_load)

    events = bridge.drain_events()
    commands = bridge.drain_submitted_commands()

    assert isinstance(result, CtpAccountQuerySmokeResult)
    assert result.bootstrap.ready is True
    assert result.query_code == 0
    assert result.completed is True
    assert result.timed_out is False
    assert result.account == CtpAccountRecord(
        account_id="025292",
        balance=1000000.5,
        available=850000.25,
        margin=120000.0,
        commission=35.5,
        close_profit=1200.0,
        position_profit=-230.0,
    )
    assert [command.kind for command in commands][-1] is CtpRuntimeCommandKind.QUERY_ACCOUNT
    assert any(event.kind is CtpRuntimeEventKind.ACCOUNT for event in events)


def test_query_adapter_snapshot_delegates_to_execution_client() -> None:
    bridge = CtpRuntimeBridge()

    class FakeExecutionClient:
        def __init__(self) -> None:
            self.position_calls: list[dict[str, object]] = []
            self.account_calls: list[dict[str, object]] = []

        def run_live_position_query_smoke(
            self,
            *,
            timeout_seconds: int = 20,
            flow_path=None,
            completion_grace_seconds: float = 1.0,
        ) -> CtpPositionQuerySmokeResult:
            self.position_calls.append(
                {
                    "timeout_seconds": timeout_seconds,
                    "flow_path": flow_path,
                    "completion_grace_seconds": completion_grace_seconds,
                }
            )
            return CtpPositionQuerySmokeResult(
                bootstrap=CtpLiveExecutionClientBootstrapResult(
                    execution_bootstrap=CtpExecutionBootstrapResult(
                        bootstrap_state=CtpTdBootstrapState(
                            started=True,
                            connect_request_id="td-connect-1",
                        ),
                        td_smoke=CtpTdSmokeResult(
                            init_code=0,
                            authenticate_code=0,
                            login_code=0,
                            settlement_code=0,
                            login_success=True,
                            login_error_id=0,
                            login_error_message="",
                            front_id=1,
                            session_id=2,
                            max_order_ref=3,
                            disconnects=[],
                        ),
                    ),
                    ready=True,
                    td_session_identity=CtpTdSessionIdentity(front_id=1, session_id=2, max_order_ref=3),
                ),
                query_request_id="position-query-1",
                query_code=0,
                completed=True,
                timed_out=False,
                no_positions=False,
                position_count=1,
                positions=(
                    CtpPositionRecord(
                        venue_symbol="c2609",
                        exchange_id="DCE",
                        direction="LONG",
                        position_qty=2,
                        yd_position_qty=1,
                        td_position_qty=1,
                        position_cost=51234.5,
                    ),
                ),
                disconnects=(),
            )

        def run_live_account_query_smoke(
            self,
            *,
            timeout_seconds: int = 20,
            flow_path=None,
        ) -> CtpAccountQuerySmokeResult:
            self.account_calls.append(
                {
                    "timeout_seconds": timeout_seconds,
                    "flow_path": flow_path,
                }
            )
            return CtpAccountQuerySmokeResult(
                bootstrap=CtpLiveExecutionClientBootstrapResult(
                    execution_bootstrap=CtpExecutionBootstrapResult(
                        bootstrap_state=CtpTdBootstrapState(
                            started=True,
                            connect_request_id="td-connect-1",
                        ),
                        td_smoke=CtpTdSmokeResult(
                            init_code=0,
                            authenticate_code=0,
                            login_code=0,
                            settlement_code=0,
                            login_success=True,
                            login_error_id=0,
                            login_error_message="",
                            front_id=1,
                            session_id=2,
                            max_order_ref=3,
                            disconnects=[],
                        ),
                    ),
                    ready=True,
                    td_session_identity=CtpTdSessionIdentity(front_id=1, session_id=2, max_order_ref=3),
                ),
                query_request_id="account-query-1",
                query_code=0,
                completed=True,
                timed_out=False,
                account=CtpAccountRecord(
                    account_id="025292",
                    balance=1000000.5,
                    available=850000.25,
                    margin=120000.0,
                    commission=35.5,
                    close_profit=1200.0,
                    position_profit=-230.0,
                ),
                disconnects=(),
            )

    execution_client = FakeExecutionClient()
    query_adapter = CtpQueryAdapter(
        config=CtpAdapterConfig(),
        runtime_bridge=bridge,
        execution_client=execution_client,  # type: ignore[arg-type]
    )

    snapshot = query_adapter.query_snapshot_mainline(
        timeout_seconds=7,
        flow_path=Path("D:/tmp/ctp-query"),
        completion_grace_seconds=0.25,
    )

    assert isinstance(snapshot, CtpQueryAdapterSnapshot)
    assert snapshot.positions == CtpPositionQueryBaseline(
        request_id="position-query-1",
        query_code=0,
        completed=True,
        timed_out=False,
        no_positions=False,
        position_count=1,
        positions=(
            CtpPositionRecord(
                venue_symbol="c2609",
                exchange_id="DCE",
                direction="LONG",
                position_qty=2,
                yd_position_qty=1,
                td_position_qty=1,
                position_cost=51234.5,
            ),
        ),
    )
    assert snapshot.account == CtpAccountQueryBaseline(
        request_id="account-query-1",
        query_code=0,
        completed=True,
        timed_out=False,
        account=CtpAccountRecord(
            account_id="025292",
            balance=1000000.5,
            available=850000.25,
            margin=120000.0,
            commission=35.5,
            close_profit=1200.0,
            position_profit=-230.0,
        ),
    )
    assert execution_client.position_calls == [
        {
            "timeout_seconds": 7,
            "flow_path": Path("D:/tmp/ctp-query"),
            "completion_grace_seconds": 0.25,
        }
    ]
    assert execution_client.account_calls == [
        {
            "timeout_seconds": 7,
            "flow_path": Path("D:/tmp/ctp-query"),
        }
    ]


def test_reconciliation_adapter_summarizes_query_snapshot() -> None:
    bridge = CtpRuntimeBridge()

    class FakeQueryAdapter:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def query_snapshot_mainline(
            self,
            *,
            timeout_seconds: int = 20,
            flow_path=None,
            completion_grace_seconds: float = 1.0,
        ) -> CtpQueryAdapterSnapshot:
            self.calls.append(
                {
                    "timeout_seconds": timeout_seconds,
                    "flow_path": flow_path,
                    "completion_grace_seconds": completion_grace_seconds,
                }
            )
            return CtpQueryAdapterSnapshot(
                positions=CtpPositionQueryBaseline(
                    request_id="position-query-1",
                    query_code=0,
                    completed=True,
                    timed_out=False,
                    no_positions=False,
                    position_count=3,
                    positions=(
                        CtpPositionRecord(
                            venue_symbol="c2609",
                            exchange_id="DCE",
                            direction="LONG",
                            position_qty=3,
                            yd_position_qty=1,
                            td_position_qty=2,
                            position_cost=61234.5,
                        ),
                        CtpPositionRecord(
                            venue_symbol="c2609",
                            exchange_id="DCE",
                            direction="SHORT",
                            position_qty=1,
                            yd_position_qty=1,
                            td_position_qty=0,
                            position_cost=10200.0,
                        ),
                        CtpPositionRecord(
                            venue_symbol="rb2610",
                            exchange_id="SHFE",
                            direction="LONG",
                            position_qty=2,
                            yd_position_qty=0,
                            td_position_qty=2,
                            position_cost=82000.0,
                        ),
                    ),
                ),
                account=CtpAccountQueryBaseline(
                    request_id="account-query-2",
                    query_code=0,
                    completed=True,
                    timed_out=False,
                    account=CtpAccountRecord(
                        account_id="025292",
                        balance=1000000.0,
                        available=600000.0,
                        margin=250000.0,
                        commission=35.5,
                        close_profit=1200.0,
                        position_profit=-230.0,
                    ),
                ),
            )

    query_adapter = FakeQueryAdapter()
    reconciliation_adapter = CtpReconciliationAdapter(
        config=CtpAdapterConfig(),
        runtime_bridge=bridge,
        query_adapter=query_adapter,  # type: ignore[arg-type]
    )

    summary = reconciliation_adapter.capture_summary_mainline(
        timeout_seconds=9,
        flow_path=Path("D:/tmp/ctp-reconcile"),
        completion_grace_seconds=0.5,
    )

    assert isinstance(summary, CtpReconciliationSummary)
    assert summary.position_request_id == "position-query-1"
    assert summary.account_request_id == "account-query-2"
    assert summary.account_id == "025292"
    assert summary.position_line_count == 3
    assert summary.symbol_count == 2
    assert summary.total_long_qty == 5
    assert summary.total_short_qty == 1
    assert summary.gross_position_qty == 6
    assert summary.total_position_cost == 153434.5
    assert summary.account_balance == 1000000.0
    assert summary.account_available == 600000.0
    assert summary.account_margin == 250000.0
    assert summary.available_ratio == 0.6
    assert summary.margin_ratio == 0.25
    assert summary.dominant_exposure_symbol == "c2609"
    assert summary.dominant_exposure_exchange == "DCE"
    assert summary.dominant_exposure_abs_net_qty == 2
    assert summary.exposures == (
        CtpReconciliationSymbolExposure(
            venue_symbol="c2609",
            exchange_id="DCE",
            long_qty=3,
            short_qty=1,
            gross_qty=4,
            net_qty=2,
            abs_net_qty=2,
            position_cost=71434.5,
        ),
        CtpReconciliationSymbolExposure(
            venue_symbol="rb2610",
            exchange_id="SHFE",
            long_qty=2,
            short_qty=0,
            gross_qty=2,
            net_qty=2,
            abs_net_qty=2,
            position_cost=82000.0,
        ),
    )
    assert query_adapter.calls == [
        {
            "timeout_seconds": 9,
            "flow_path": Path("D:/tmp/ctp-reconcile"),
            "completion_grace_seconds": 0.5,
        }
    ]


def test_reconciliation_policy_flags_manual_review_and_evidence_only() -> None:
    adapter = CtpReconciliationAdapter(config=CtpAdapterConfig(), runtime_bridge=CtpRuntimeBridge())
    summary = CtpReconciliationSummary(
        position_request_id="position-query-1",
        account_request_id="account-query-1",
        account_id="025292",
        position_line_count=3,
        symbol_count=2,
        total_long_qty=5,
        total_short_qty=12,
        gross_position_qty=17,
        total_position_cost=153434.5,
        account_balance=1000000.0,
        account_available=210000.0,
        account_margin=780000.0,
        available_ratio=0.21,
        margin_ratio=0.78,
        dominant_exposure_symbol="m2605-P-3000",
        dominant_exposure_exchange=None,
        dominant_exposure_abs_net_qty=10,
        exposures=(
            CtpReconciliationSymbolExposure(
                venue_symbol="m2605-P-3000",
                exchange_id=None,
                long_qty=0,
                short_qty=10,
                gross_qty=10,
                net_qty=-10,
                abs_net_qty=10,
                position_cost=11900.0,
            ),
        ),
    )

    result = adapter.evaluate_summary(summary)

    assert isinstance(result, CtpReconciliationPolicyResult)
    assert result.disposition == "manual_review_required"
    assert result.requires_manual_review is True
    assert result.findings == (
        CtpReconciliationPolicyFinding(
            code="available_ratio_warn",
            severity="warn",
            action="manual_review_required",
            metric="available_ratio",
            metric_value=0.21,
            threshold=0.25,
            message="Available ratio is below the baseline comfort threshold.",
        ),
        CtpReconciliationPolicyFinding(
            code="margin_ratio_warn",
            severity="warn",
            action="manual_review_required",
            metric="margin_ratio",
            metric_value=0.78,
            threshold=0.75,
            message="Margin ratio is above the baseline comfort threshold.",
        ),
        CtpReconciliationPolicyFinding(
            code="dominant_exposure_watch",
            severity="info",
            action="evidence_only",
            metric="dominant_exposure_abs_net_qty",
            metric_value=10,
            threshold=10,
            message="Dominant single-symbol exposure is large enough to keep in live evidence.",
        ),
    )


def test_reconciliation_evidence_rolls_up_policy_result() -> None:
    adapter = CtpReconciliationAdapter(config=CtpAdapterConfig(), runtime_bridge=CtpRuntimeBridge())
    result = CtpReconciliationPolicyResult(
        summary=CtpReconciliationSummary(
            position_request_id="position-query-1",
            account_request_id="account-query-1",
            account_id="025292",
            position_line_count=3,
            symbol_count=2,
            total_long_qty=5,
            total_short_qty=12,
            gross_position_qty=17,
            total_position_cost=153434.5,
            account_balance=1000000.0,
            account_available=210000.0,
            account_margin=780000.0,
            available_ratio=0.21,
            margin_ratio=0.78,
            dominant_exposure_symbol="m2605-P-3000",
            dominant_exposure_exchange=None,
            dominant_exposure_abs_net_qty=10,
            exposures=(
                CtpReconciliationSymbolExposure(
                    venue_symbol="m2605-P-3000",
                    exchange_id=None,
                    long_qty=0,
                    short_qty=10,
                    gross_qty=10,
                    net_qty=-10,
                    abs_net_qty=10,
                    position_cost=11900.0,
                ),
                CtpReconciliationSymbolExposure(
                    venue_symbol="PK605",
                    exchange_id=None,
                    long_qty=6,
                    short_qty=0,
                    gross_qty=6,
                    net_qty=6,
                    abs_net_qty=6,
                    position_cost=241620.0,
                ),
            ),
        ),
        disposition="manual_review_required",
        requires_manual_review=True,
        findings=(
            CtpReconciliationPolicyFinding(
                code="available_ratio_warn",
                severity="warn",
                action="manual_review_required",
                metric="available_ratio",
                metric_value=0.21,
                threshold=0.25,
                message="Available ratio is below the baseline comfort threshold.",
            ),
            CtpReconciliationPolicyFinding(
                code="dominant_exposure_watch",
                severity="info",
                action="evidence_only",
                metric="dominant_exposure_abs_net_qty",
                metric_value=10,
                threshold=10,
                message="Dominant single-symbol exposure is large enough to keep in live evidence.",
            ),
        ),
    )

    evidence = adapter.build_evidence(result)

    assert isinstance(evidence, CtpReconciliationEvidence)
    assert evidence.evidence_version == "reconciliation-evidence-v1"
    assert evidence.account_id == "025292"
    assert evidence.disposition == "manual_review_required"
    assert evidence.requires_manual_review is True
    assert evidence.finding_count == 2
    assert evidence.manual_review_codes == ("available_ratio_warn",)
    assert evidence.evidence_only_codes == ("dominant_exposure_watch",)
    assert evidence.position_line_count == 3
    assert evidence.symbol_count == 2
    assert evidence.gross_position_qty == 17
    assert evidence.available_ratio == 0.21
    assert evidence.margin_ratio == 0.78
    assert evidence.dominant_exposure_symbol == "m2605-P-3000"
    assert evidence.dominant_exposure_abs_net_qty == 10
    assert evidence.top_exposures == result.summary.exposures
    assert evidence.captured_at_utc.endswith("Z")


def test_startup_truth_adapter_captures_td_bootstrap_evidence() -> None:
    bridge = CtpRuntimeBridge()

    class FakeExecutionClient:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def resolve_td_flow_path(self, flow_path=None) -> Path:
            return Path(flow_path) if flow_path else Path("D:/repo/var/td_flow_smoke")

        def bootstrap_live_execution_client_mainline(
            self,
            *,
            timeout_seconds: int = 20,
            flow_path=None,
        ) -> CtpLiveExecutionClientBootstrapResult:
            self.calls.append(
                {
                    "timeout_seconds": timeout_seconds,
                    "flow_path": flow_path,
                }
            )
            return CtpLiveExecutionClientBootstrapResult(
                execution_bootstrap=CtpExecutionBootstrapResult(
                    bootstrap_state=CtpTdBootstrapState(
                        started=True,
                        connect_request_id="td-connect-1",
                    ),
                    td_smoke=CtpTdSmokeResult(
                        init_code=0,
                        authenticate_code=0,
                        login_code=0,
                        settlement_code=0,
                        login_success=True,
                        login_error_id=0,
                        login_error_message="",
                        front_id=11,
                        session_id=22,
                        max_order_ref=13,
                        disconnects=[4097],
                    ),
                ),
                ready=True,
                td_session_identity=CtpTdSessionIdentity(
                    front_id=11,
                    session_id=22,
                    max_order_ref=13,
                ),
            )

    execution_client = FakeExecutionClient()
    adapter = CtpStartupTruthAdapter(
        config=CtpAdapterConfig(),
        runtime_bridge=bridge,
        execution_client=execution_client,  # type: ignore[arg-type]
    )

    evidence = adapter.capture_td_startup_truth_mainline(
        timeout_seconds=8,
        flow_path=Path("D:/tmp/td-flow"),
    )

    assert isinstance(evidence, CtpTdStartupTruthEvidence)
    assert evidence == CtpTdStartupTruthEvidence(
        flow_path="D:\\tmp\\td-flow",
        flow_mode="explicit_override",
        ready=True,
        login_success=True,
        settlement_code=0,
        front_id=11,
        session_id=22,
        max_order_ref=13,
        disconnect_count=1,
        disconnect_reasons=(4097,),
    )
    assert execution_client.calls == [
        {
            "timeout_seconds": 8,
            "flow_path": Path("D:/tmp/td-flow"),
        }
    ]


def test_startup_truth_adapter_evaluates_session_rebuild_policy() -> None:
    adapter = CtpStartupTruthAdapter(config=CtpAdapterConfig(), runtime_bridge=CtpRuntimeBridge())
    shared_truth = CtpTdStartupTruthEvidence(
        flow_path="D:\\repo\\var\\td_flow_smoke",
        flow_mode="default_shared_flow",
        ready=True,
        login_success=True,
        settlement_code=0,
        front_id=11,
        session_id=100,
        max_order_ref=8,
        disconnect_count=0,
        disconnect_reasons=(),
    )
    isolated_truth = CtpTdStartupTruthEvidence(
        flow_path="D:\\repo\\output\\debug\\session_rebuild_truth_1",
        flow_mode="explicit_override",
        ready=True,
        login_success=True,
        settlement_code=0,
        front_id=11,
        session_id=101,
        max_order_ref=1,
        disconnect_count=0,
        disconnect_reasons=(),
    )

    result = adapter.evaluate_session_rebuild_policy(shared_truth, isolated_truth)

    assert isinstance(result, CtpSessionRebuildPolicyResult)
    assert result.disposition == "rebuild_required"
    assert result.shared_flow_reuse_allowed is False
    assert result.session_rotated is True
    assert result.max_order_ref_reset is True
    assert result.findings == (
        CtpSessionRebuildFinding(
            code="shared_flow_requires_isolated_rebuild",
            severity="warn",
            action="rebuild_required",
            metric="shared_flow_mode",
            metric_value="default_shared_flow",
            threshold="explicit_override",
            message="Shared default TD flow must not be treated as rebuild-safe truth for session-sensitive checks.",
        ),
        CtpSessionRebuildFinding(
            code="isolated_flow_verified",
            severity="info",
            action="evidence_only",
            metric="isolated_flow_mode",
            metric_value="explicit_override",
            threshold="explicit_override",
            message="Isolated override flow was used and can serve as rebuild-safe session truth.",
        ),
        CtpSessionRebuildFinding(
            code="fresh_session_identity_observed",
            severity="info",
            action="evidence_only",
            metric="session_id",
            metric_value=101,
            threshold="!= shared_session_id",
            message="A fresh session identity was observed after isolated rebuild bootstrap.",
        ),
        CtpSessionRebuildFinding(
            code="max_order_ref_reinitialized",
            severity="info",
            action="evidence_only",
            metric="max_order_ref",
            metric_value=1,
            threshold="<= shared_max_order_ref",
            message="Isolated rebuild bootstrap reinitialized max_order_ref, so old order-ref chains must not be inherited.",
        ),
    )


def test_startup_truth_adapter_builds_evidence_matrix() -> None:
    adapter = CtpStartupTruthAdapter(
        config=CtpAdapterConfig.from_dict({"UserID": "025292"}),
        runtime_bridge=CtpRuntimeBridge(),
    )
    result = CtpSessionRebuildPolicyResult(
        shared_truth=CtpTdStartupTruthEvidence(
            flow_path="D:\\repo\\var\\td_flow_smoke",
            flow_mode="default_shared_flow",
            ready=True,
            login_success=True,
            settlement_code=0,
            front_id=11,
            session_id=100,
            max_order_ref=8,
            disconnect_count=1,
            disconnect_reasons=(4097,),
        ),
        isolated_truth=CtpTdStartupTruthEvidence(
            flow_path="D:\\repo\\output\\debug\\session_rebuild_truth_1",
            flow_mode="explicit_override",
            ready=True,
            login_success=True,
            settlement_code=0,
            front_id=11,
            session_id=101,
            max_order_ref=1,
            disconnect_count=0,
            disconnect_reasons=(),
        ),
        disposition="rebuild_required",
        shared_flow_reuse_allowed=False,
        session_rotated=True,
        max_order_ref_reset=True,
        findings=(
            CtpSessionRebuildFinding(
                code="shared_flow_requires_isolated_rebuild",
                severity="warn",
                action="rebuild_required",
                metric="shared_flow_mode",
                metric_value="default_shared_flow",
                threshold="explicit_override",
                message="Shared default TD flow must not be treated as rebuild-safe truth for session-sensitive checks.",
            ),
            CtpSessionRebuildFinding(
                code="isolated_flow_verified",
                severity="info",
                action="evidence_only",
                metric="isolated_flow_mode",
                metric_value="explicit_override",
                threshold="explicit_override",
                message="Isolated override flow was used and can serve as rebuild-safe session truth.",
            ),
        ),
    )

    evidence = adapter.build_evidence_matrix(result)

    assert isinstance(evidence, CtpStartupTruthEvidenceMatrix)
    assert evidence.evidence_version == "startup-truth-evidence-v1"
    assert evidence.account_id == "025292"
    assert evidence.disposition == "rebuild_required"
    assert evidence.shared_flow_reuse_allowed is False
    assert evidence.session_rotated is True
    assert evidence.max_order_ref_reset is True
    assert evidence.shared_flow_path == "D:\\repo\\var\\td_flow_smoke"
    assert evidence.isolated_flow_path == "D:\\repo\\output\\debug\\session_rebuild_truth_1"
    assert evidence.shared_session_id == 100
    assert evidence.isolated_session_id == 101
    assert evidence.shared_max_order_ref == 8
    assert evidence.isolated_max_order_ref == 1
    assert evidence.shared_disconnect_count == 1
    assert evidence.isolated_disconnect_count == 0
    assert evidence.manual_review_codes == ()
    assert evidence.rebuild_required_codes == ("shared_flow_requires_isolated_rebuild",)
    assert evidence.evidence_only_codes == ("isolated_flow_verified",)
    assert evidence.captured_at_utc.endswith("Z")


def test_data_client_captures_md_startup_truth() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    client = CtpExecutionClient(config)
    data_client = build_ctp_stack(config)["data_client"]

    fake_smoke = CtpMdSmokeResult(
        init_code=0,
        login_request_code=0,
        subscribe_code=0,
        login_success=True,
        login_error_id=0,
        login_error_message="",
        first_tick_symbol="rb2610",
        first_tick_last=3137.0,
        first_tick_bid=3136.0,
        first_tick_ask=3137.0,
        first_tick_ts_epoch_us=1775052501781380,
    )
    data_client.run_live_md_smoke = lambda **kwargs: fake_smoke  # type: ignore[method-assign]
    data_client._emit_marketdata_event(  # type: ignore[attr-defined]
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.DISCONNECTED,
            payload={"channel": "md", "reason": "4097"},
        )
    )

    evidence = data_client.capture_md_startup_truth_mainline(timeout_seconds=8, flow_path=Path("D:/tmp/md-flow"))

    assert isinstance(evidence, CtpMdStartupTruthEvidence)
    assert evidence == CtpMdStartupTruthEvidence(
        flow_path="D:\\tmp\\md-flow",
        flow_mode="explicit_override",
        selected_symbols=("rb2610",),
        ready=True,
        login_success=True,
        login_error_id=0,
        subscribe_code=0,
        first_tick_symbol="rb2610",
        first_tick_last=3137.0,
        first_tick_bid=3136.0,
        first_tick_ask=3137.0,
        first_tick_ts_epoch_us=1775052501781380,
        disconnect_count=1,
        disconnect_reasons=(4097,),
    )


def test_data_client_evaluates_md_restore_policy() -> None:
    data_client = build_ctp_stack(CtpAdapterConfig.from_dict({"UserID": "025292"}))["data_client"]
    startup_truth = CtpMdStartupTruthEvidence(
        flow_path="D:\\repo\\var\\md_flow_smoke",
        flow_mode="default_shared_flow",
        selected_symbols=("rb2610",),
        ready=True,
        login_success=True,
        login_error_id=0,
        subscribe_code=0,
        first_tick_symbol="rb2610",
        first_tick_last=3137.0,
        first_tick_bid=3136.0,
        first_tick_ask=3138.0,
        first_tick_ts_epoch_us=100,
        disconnect_count=1,
        disconnect_reasons=(4097,),
    )
    restore_result = CtpMdRestoreResult(
        triggered=True,
        restored_symbols=("rb2610",),
        bootstrap_state=CtpMdBootstrapState(started=True, connect_request_id="md-connect-3", subscribe_request_ids=["md-subscribe-4"]),
    )
    restored_truth = CtpMdStartupTruthEvidence(
        flow_path="D:\\repo\\var\\md_flow_smoke",
        flow_mode="default_shared_flow",
        selected_symbols=("rb2610",),
        ready=True,
        login_success=True,
        login_error_id=0,
        subscribe_code=0,
        first_tick_symbol="rb2610",
        first_tick_last=3138.0,
        first_tick_bid=3137.0,
        first_tick_ask=3138.0,
        first_tick_ts_epoch_us=200,
        disconnect_count=0,
        disconnect_reasons=(),
    )

    result = data_client.evaluate_md_restore_policy(startup_truth, restore_result, restored_truth)

    assert isinstance(result, CtpMdRestorePolicyResult)
    assert result.disposition == "evidence_only"
    assert result.restore_succeeded is True
    assert result.findings == (
        CtpMdRestorePolicyFinding(
            code="restore_resubscribe_triggered",
            severity="info",
            action="evidence_only",
            metric="restored_symbols",
            metric_value="rb2610",
            threshold="non-empty",
            message="MD restore re-submitted the tracked symbols.",
        ),
    )


def test_data_client_builds_md_truth_evidence_matrix() -> None:
    data_client = build_ctp_stack(CtpAdapterConfig.from_dict({"UserID": "025292"}))["data_client"]
    result = CtpMdRestorePolicyResult(
        startup_truth=CtpMdStartupTruthEvidence(
            flow_path="D:\\repo\\var\\md_flow_smoke",
            flow_mode="default_shared_flow",
            selected_symbols=("rb2610",),
            ready=True,
            login_success=True,
            login_error_id=0,
            subscribe_code=0,
            first_tick_symbol="rb2610",
            first_tick_last=3137.0,
            first_tick_bid=3136.0,
            first_tick_ask=3138.0,
            first_tick_ts_epoch_us=100,
            disconnect_count=1,
            disconnect_reasons=(4097,),
        ),
        restored_truth=CtpMdStartupTruthEvidence(
            flow_path="D:\\repo\\var\\md_flow_smoke",
            flow_mode="default_shared_flow",
            selected_symbols=("rb2610",),
            ready=True,
            login_success=True,
            login_error_id=0,
            subscribe_code=0,
            first_tick_symbol="rb2610",
            first_tick_last=3138.0,
            first_tick_bid=3137.0,
            first_tick_ask=3138.0,
            first_tick_ts_epoch_us=200,
            disconnect_count=0,
            disconnect_reasons=(),
        ),
        restore_result=CtpMdRestoreResult(
            triggered=True,
            restored_symbols=("rb2610",),
            bootstrap_state=CtpMdBootstrapState(started=True, connect_request_id="md-connect-3", subscribe_request_ids=["md-subscribe-4"]),
        ),
        disposition="evidence_only",
        restore_succeeded=True,
        findings=(
            CtpMdRestorePolicyFinding(
                code="restore_resubscribe_triggered",
                severity="info",
                action="evidence_only",
                metric="restored_symbols",
                metric_value="rb2610",
                threshold="non-empty",
                message="MD restore re-submitted the tracked symbols.",
            ),
        ),
    )

    evidence = data_client.build_md_truth_evidence_matrix(result)

    assert isinstance(evidence, CtpMdTruthEvidenceMatrix)
    assert evidence.evidence_version == "md-truth-evidence-v1"
    assert evidence.account_id == "025292"
    assert evidence.symbol == "rb2610"
    assert evidence.disposition == "evidence_only"
    assert evidence.startup_ready is True
    assert evidence.restore_triggered is True
    assert evidence.restore_succeeded is True
    assert evidence.startup_flow_path == "D:\\repo\\var\\md_flow_smoke"
    assert evidence.restored_flow_path == "D:\\repo\\var\\md_flow_smoke"
    assert evidence.startup_first_tick_ts_epoch_us == 100
    assert evidence.restored_first_tick_ts_epoch_us == 200
    assert evidence.manual_review_codes == ()
    assert evidence.restore_required_codes == ()
    assert evidence.evidence_only_codes == ("restore_resubscribe_triggered",)
    assert evidence.captured_at_utc.endswith("Z")


def test_execution_client_captures_td_order_truth_baseline() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    execution_client = build_ctp_stack(config)["execution_client"]

    class FakeTdApi:
        def __init__(self) -> None:
            self._login_callback = None
            self._disconnect_callback = None
            self._exec_callback = None

        def create(self, flow_path: Path) -> int:
            self.flow_path = flow_path
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_exec_callback(self, handle: int, callback):
            self._exec_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            self._login_callback(LoginResponse())
            self._exec_callback(
                NativeExecView(
                    order_id="hist-order-1",
                    symbol="c2609",
                    price=2241.0,
                    qty=1,
                    side=0,
                    status=3,
                    ts_epoch_us=10,
                    order_ref="77",
                    front_id=11,
                    session_id=22,
                    direction=0,
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            self._exec_callback(
                NativeExecView(
                    order_id="hist-trade-1",
                    symbol="c2609",
                    price=2241.0,
                    qty=1,
                    side=0,
                    status=4,
                    ts_epoch_us=11,
                    order_ref="77",
                    front_id=11,
                    session_id=22,
                    direction=0,
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=True,
                    trade_price=2241.0,
                    trade_volume=1,
                    error_msg="",
                    leaves_qty=0,
                )
            )
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        result = execution_client.capture_td_order_truth_baseline_mainline(
            timeout_seconds=5,
            flow_path=Path("D:/tmp/td-order-truth"),
            observation_grace_seconds=0.01,
        )
    finally:
        setattr(CtpTdApi, "load", original_load)

    assert isinstance(result, CtpTdOrderTruthBaseline)
    assert result == CtpTdOrderTruthBaseline(
        flow_path="D:\\tmp\\td-order-truth",
        flow_mode="explicit_override",
        ready=True,
        login_success=True,
        settlement_code=0,
        login_front_id=11,
        login_session_id=22,
        login_max_order_ref=100,
        disconnect_count=0,
        disconnect_reasons=(),
        observed_callback_count=2,
        observed_order_event_count=1,
        observed_trade_event_count=1,
        no_callbacks_observed=False,
        first_order_id="hist-order-1",
        first_order_ref="77",
        first_session_id=22,
        first_front_id=11,
        first_is_trade=False,
        observed_callbacks=(
            CtpTdObservedCallback(
                order_id="hist-order-1",
                order_ref="77",
                front_id=11,
                session_id=22,
                is_trade=False,
                ts_epoch_us=10,
                status=3,
            ),
            CtpTdObservedCallback(
                order_id="hist-trade-1",
                order_ref="77",
                front_id=11,
                session_id=22,
                is_trade=True,
                ts_epoch_us=11,
                status=4,
            ),
        ),
    )


def test_execution_client_evaluates_historical_callback_boundary_policy() -> None:
    execution_client = build_ctp_stack(CtpAdapterConfig.from_dict({"UserID": "025292"}))["execution_client"]
    baseline = CtpTdOrderTruthBaseline(
        flow_path="D:\\repo\\var\\td_flow_smoke",
        flow_mode="default_shared_flow",
        ready=True,
        login_success=True,
        settlement_code=0,
        login_front_id=11,
        login_session_id=22,
        login_max_order_ref=100,
        disconnect_count=0,
        disconnect_reasons=(),
        observed_callback_count=3,
        observed_order_event_count=2,
        observed_trade_event_count=1,
        no_callbacks_observed=False,
        first_order_id="hist-order-1",
        first_order_ref="77",
        first_session_id=0,
        first_front_id=0,
        first_is_trade=False,
        observed_callbacks=(
            CtpTdObservedCallback(
                order_id="hist-order-1",
                order_ref="77",
                front_id=0,
                session_id=0,
                is_trade=False,
                ts_epoch_us=10,
                status=3,
            ),
            CtpTdObservedCallback(
                order_id="delay-order-1",
                order_ref="88",
                front_id=11,
                session_id=22,
                is_trade=False,
                ts_epoch_us=11,
                status=3,
            ),
            CtpTdObservedCallback(
                order_id="current-order-1",
                order_ref="101",
                front_id=11,
                session_id=22,
                is_trade=True,
                ts_epoch_us=12,
                status=4,
            ),
        ),
    )

    result = execution_client.evaluate_historical_callback_boundary_policy(baseline)

    assert isinstance(result, CtpTdHistoricalCallbackBoundaryPolicyResult)
    assert result.disposition == "boundary_required"
    assert result.historical_callback_count == 1
    assert result.delayed_callback_count == 1
    assert result.current_session_callback_count == 1
    assert result.first_historical_order_id == "hist-order-1"
    assert result.first_current_session_order_id == "current-order-1"
    assert result.findings == (
        CtpTdHistoricalCallbackBoundaryFinding(
            code="historical_callbacks_present",
            severity="warn",
            action="boundary_required",
            metric="historical_callback_count",
            metric_value=1,
            threshold=0,
            message="Observed callbacks whose front/session identity does not match the current login truth.",
        ),
        CtpTdHistoricalCallbackBoundaryFinding(
            code="delayed_callbacks_present",
            severity="warn",
            action="boundary_required",
            metric="delayed_callback_count",
            metric_value=1,
            threshold=0,
            message="Observed callbacks that match the current session but use order refs at or below the login baseline.",
        ),
        CtpTdHistoricalCallbackBoundaryFinding(
            code="current_session_callbacks_present",
            severity="info",
            action="evidence_only",
            metric="current_session_callback_count",
            metric_value=1,
            threshold=0,
            message="Observed callbacks that belong to the current TD session identity.",
        ),
    )


def test_execution_client_builds_td_order_truth_evidence_matrix() -> None:
    execution_client = build_ctp_stack(CtpAdapterConfig.from_dict({"UserID": "025292"}))["execution_client"]
    result = CtpTdHistoricalCallbackBoundaryPolicyResult(
        baseline=CtpTdOrderTruthBaseline(
            flow_path="D:\\repo\\var\\td_flow_smoke",
            flow_mode="default_shared_flow",
            ready=True,
            login_success=True,
            settlement_code=0,
            login_front_id=11,
            login_session_id=22,
            login_max_order_ref=100,
            disconnect_count=0,
            disconnect_reasons=(),
            observed_callback_count=3,
            observed_order_event_count=2,
            observed_trade_event_count=1,
            no_callbacks_observed=False,
            first_order_id="hist-order-1",
            first_order_ref="77",
            first_session_id=0,
            first_front_id=0,
            first_is_trade=False,
            observed_callbacks=(),
        ),
        disposition="boundary_required",
        historical_callback_count=1,
        delayed_callback_count=1,
        current_session_callback_count=1,
        first_historical_order_id="hist-order-1",
        first_current_session_order_id="current-order-1",
        findings=(
            CtpTdHistoricalCallbackBoundaryFinding(
                code="historical_callbacks_present",
                severity="warn",
                action="boundary_required",
                metric="historical_callback_count",
                metric_value=1,
                threshold=0,
                message="Observed callbacks whose front/session identity does not match the current login truth.",
            ),
            CtpTdHistoricalCallbackBoundaryFinding(
                code="current_session_callbacks_present",
                severity="info",
                action="evidence_only",
                metric="current_session_callback_count",
                metric_value=1,
                threshold=0,
                message="Observed callbacks that belong to the current TD session identity.",
            ),
        ),
    )

    evidence = execution_client.build_td_order_truth_evidence_matrix(result)

    assert isinstance(evidence, CtpTdOrderTruthEvidenceMatrix)
    assert evidence.evidence_version == "td-order-truth-evidence-v1"
    assert evidence.account_id == "025292"
    assert evidence.disposition == "boundary_required"
    assert evidence.observed_callback_count == 3
    assert evidence.historical_callback_count == 1
    assert evidence.delayed_callback_count == 1
    assert evidence.current_session_callback_count == 1
    assert evidence.first_historical_order_id == "hist-order-1"
    assert evidence.first_current_session_order_id == "current-order-1"
    assert evidence.manual_review_codes == ()
    assert evidence.boundary_codes == ("historical_callbacks_present",)
    assert evidence.evidence_only_codes == ("current_session_callbacks_present",)


def test_truth_merge_adapter_captures_snapshot() -> None:
    config = CtpAdapterConfig.from_dict({"UserID": "025292"})

    class FakeExecutionClient:
        def capture_td_order_truth_evidence_matrix_mainline(self, **kwargs) -> CtpTdOrderTruthEvidenceMatrix:
            return CtpTdOrderTruthEvidenceMatrix(
                evidence_version="td-order-truth-evidence-v1",
                captured_at_utc="2026-04-02T08:10:00Z",
                account_id="025292",
                disposition="boundary_required",
                observed_callback_count=9,
                historical_callback_count=9,
                delayed_callback_count=0,
                current_session_callback_count=0,
                first_historical_order_id="49456082",
                first_current_session_order_id=None,
                manual_review_codes=(),
                boundary_codes=("historical_callbacks_present",),
                evidence_only_codes=(),
            )

    class FakeQueryAdapter:
        def query_positions_mainline(self, **kwargs) -> CtpPositionQueryBaseline:
            return CtpPositionQueryBaseline(
                request_id="query-positions-1",
                query_code=0,
                completed=True,
                timed_out=False,
                no_positions=False,
                position_count=73,
                positions=(),
            )

        def query_account_mainline(self, **kwargs) -> CtpAccountQueryBaseline:
            return CtpAccountQueryBaseline(
                request_id="query-account-1",
                query_code=0,
                completed=True,
                timed_out=False,
                account=CtpAccountRecord(
                    account_id="025292",
                    balance=1000000.0,
                    available=214000.0,
                    margin=780000.0,
                    commission=35.0,
                    close_profit=1200.0,
                    position_profit=-230.0,
                ),
            )

    adapter = CtpTruthMergeAdapter(
        config=config,
        runtime_bridge=CtpRuntimeBridge(),
        execution_client=FakeExecutionClient(),  # type: ignore[arg-type]
        query_adapter=FakeQueryAdapter(),  # type: ignore[arg-type]
    )

    snapshot = adapter.capture_truth_merge_snapshot_mainline()

    assert isinstance(snapshot, CtpTdTruthMergeSnapshot)
    assert snapshot.order_truth.account_id == "025292"
    assert snapshot.positions.position_count == 73
    assert snapshot.account.account is not None
    assert snapshot.account.account.account_id == "025292"


def test_truth_merge_adapter_evaluates_merged_reconciliation_policy() -> None:
    adapter = CtpTruthMergeAdapter(config=CtpAdapterConfig.from_dict({"UserID": "025292"}))
    snapshot = CtpTdTruthMergeSnapshot(
        order_truth=CtpTdOrderTruthEvidenceMatrix(
            evidence_version="td-order-truth-evidence-v1",
            captured_at_utc="2026-04-02T08:10:00Z",
            account_id="025292",
            disposition="boundary_required",
            observed_callback_count=9,
            historical_callback_count=9,
            delayed_callback_count=0,
            current_session_callback_count=0,
            first_historical_order_id="49456082",
            first_current_session_order_id=None,
            manual_review_codes=(),
            boundary_codes=("historical_callbacks_present",),
            evidence_only_codes=(),
        ),
        positions=CtpPositionQueryBaseline(
            request_id="query-positions-1",
            query_code=0,
            completed=True,
            timed_out=False,
            no_positions=False,
            position_count=73,
            positions=(),
        ),
        account=CtpAccountQueryBaseline(
            request_id="query-account-1",
            query_code=0,
            completed=True,
            timed_out=False,
            account=CtpAccountRecord(
                account_id="025292",
                balance=1000000.0,
                available=214000.0,
                margin=780000.0,
                commission=35.0,
                close_profit=1200.0,
                position_profit=-230.0,
            ),
        ),
    )

    result = adapter.evaluate_merged_reconciliation_policy(snapshot)

    assert isinstance(result, CtpTdMergedReconciliationPolicyResult)
    assert result.disposition == "manual_review_required"
    assert result.available_ratio == 0.214
    assert result.margin_ratio == 0.78
    assert result.findings == (
        CtpTdMergedReconciliationFinding(
            code="historical_callbacks_present",
            severity="warn",
            action="boundary_required",
            metric="historical_callback_count",
            metric_value=9,
            threshold=0,
            message="Merged snapshot still contains historical callback residue and must preserve that boundary.",
        ),
        CtpTdMergedReconciliationFinding(
            code="available_ratio_warn",
            severity="warn",
            action="manual_review_required",
            metric="available_ratio",
            metric_value=0.214,
            threshold=0.25,
            message="Available ratio is below the merged truth comfort threshold.",
        ),
        CtpTdMergedReconciliationFinding(
            code="margin_ratio_warn",
            severity="warn",
            action="manual_review_required",
            metric="margin_ratio",
            metric_value=0.78,
            threshold=0.75,
            message="Margin ratio is above the merged truth comfort threshold.",
        ),
        CtpTdMergedReconciliationFinding(
            code="no_current_session_callbacks",
            severity="info",
            action="evidence_only",
            metric="current_session_callback_count",
            metric_value=0,
            threshold="> 0 optional",
            message="No callbacks were classified as belonging to the current TD session truth.",
        ),
    )


def test_truth_merge_adapter_builds_merged_evidence_matrix() -> None:
    adapter = CtpTruthMergeAdapter(config=CtpAdapterConfig.from_dict({"UserID": "025292"}))
    result = CtpTdMergedReconciliationPolicyResult(
        snapshot=CtpTdTruthMergeSnapshot(
            order_truth=CtpTdOrderTruthEvidenceMatrix(
                evidence_version="td-order-truth-evidence-v1",
                captured_at_utc="2026-04-02T08:10:00Z",
                account_id="025292",
                disposition="boundary_required",
                observed_callback_count=9,
                historical_callback_count=9,
                delayed_callback_count=0,
                current_session_callback_count=0,
                first_historical_order_id="49456082",
                first_current_session_order_id=None,
                manual_review_codes=(),
                boundary_codes=("historical_callbacks_present",),
                evidence_only_codes=(),
            ),
            positions=CtpPositionQueryBaseline(
                request_id="query-positions-1",
                query_code=0,
                completed=True,
                timed_out=False,
                no_positions=False,
                position_count=73,
                positions=(),
            ),
            account=CtpAccountQueryBaseline(
                request_id="query-account-1",
                query_code=0,
                completed=True,
                timed_out=False,
                account=CtpAccountRecord(
                    account_id="025292",
                    balance=1000000.0,
                    available=214000.0,
                    margin=780000.0,
                    commission=35.0,
                    close_profit=1200.0,
                    position_profit=-230.0,
                ),
            ),
        ),
        disposition="manual_review_required",
        available_ratio=0.214,
        margin_ratio=0.78,
        findings=(
            CtpTdMergedReconciliationFinding(
                code="historical_callbacks_present",
                severity="warn",
                action="boundary_required",
                metric="historical_callback_count",
                metric_value=9,
                threshold=0,
                message="Merged snapshot still contains historical callback residue and must preserve that boundary.",
            ),
            CtpTdMergedReconciliationFinding(
                code="available_ratio_warn",
                severity="warn",
                action="manual_review_required",
                metric="available_ratio",
                metric_value=0.214,
                threshold=0.25,
                message="Available ratio is below the merged truth comfort threshold.",
            ),
            CtpTdMergedReconciliationFinding(
                code="no_current_session_callbacks",
                severity="info",
                action="evidence_only",
                metric="current_session_callback_count",
                metric_value=0,
                threshold="> 0 optional",
                message="No callbacks were classified as belonging to the current TD session truth.",
            ),
        ),
    )

    evidence = adapter.build_merged_evidence_matrix(result)

    assert isinstance(evidence, CtpTdMergedEvidenceMatrix)
    assert evidence.evidence_version == "td-merged-evidence-v1"
    assert evidence.account_id == "025292"
    assert evidence.disposition == "manual_review_required"
    assert evidence.position_count == 73
    assert evidence.observed_callback_count == 9
    assert evidence.historical_callback_count == 9
    assert evidence.current_session_callback_count == 0
    assert evidence.available_ratio == 0.214
    assert evidence.margin_ratio == 0.78
    assert evidence.manual_review_codes == ("available_ratio_warn",)
    assert evidence.boundary_codes == ("historical_callbacks_present",)
    assert evidence.evidence_only_codes == ("no_current_session_callbacks",)
    assert evidence.captured_at_utc.endswith("Z")


def test_live_ops_snapshot_adapter_captures_snapshot() -> None:
    bridge = CtpRuntimeBridge()

    class FakeStartupTruthAdapter:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def capture_evidence_matrix_mainline(self, **kwargs) -> CtpStartupTruthEvidenceMatrix:
            self.calls.append(kwargs)
            return CtpStartupTruthEvidenceMatrix(
                evidence_version="startup-truth-evidence-v1",
                captured_at_utc="2026-04-02T08:00:00Z",
                account_id="025292",
                disposition="rebuild_required",
                shared_flow_reuse_allowed=False,
                session_rotated=True,
                max_order_ref_reset=True,
                shared_flow_path="D:\\repo\\var\\td_flow_smoke",
                isolated_flow_path="D:\\repo\\output\\debug\\td_flow_isolated",
                shared_session_id=100,
                isolated_session_id=101,
                shared_max_order_ref=8,
                isolated_max_order_ref=1,
                shared_disconnect_count=1,
                isolated_disconnect_count=0,
                manual_review_codes=(),
                rebuild_required_codes=("shared_flow_requires_isolated_rebuild",),
                evidence_only_codes=("fresh_session_identity_observed",),
            )

    class FakeDataClient:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def capture_md_truth_evidence_matrix_mainline(self, **kwargs) -> CtpMdTruthEvidenceMatrix:
            self.calls.append(kwargs)
            return CtpMdTruthEvidenceMatrix(
                evidence_version="md-truth-evidence-v1",
                captured_at_utc="2026-04-02T08:01:00Z",
                account_id="025292",
                symbol="rb2610",
                disposition="evidence_only",
                startup_ready=True,
                restore_triggered=True,
                restore_succeeded=True,
                startup_flow_path="D:\\repo\\var\\md_flow_smoke",
                restored_flow_path="D:\\repo\\var\\md_flow_smoke",
                startup_first_tick_ts_epoch_us=1000,
                restored_first_tick_ts_epoch_us=2000,
                manual_review_codes=(),
                restore_required_codes=(),
                evidence_only_codes=("restore_resubscribe_triggered",),
            )

    class FakeTruthMergeAdapter:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def capture_merged_evidence_matrix_mainline(self, **kwargs) -> CtpTdMergedEvidenceMatrix:
            self.calls.append(kwargs)
            return CtpTdMergedEvidenceMatrix(
                evidence_version="td-merged-evidence-v1",
                captured_at_utc="2026-04-02T08:02:00Z",
                account_id="025292",
                disposition="manual_review_required",
                position_count=73,
                observed_callback_count=9,
                historical_callback_count=9,
                current_session_callback_count=0,
                available_ratio=0.213352,
                margin_ratio=0.781532,
                manual_review_codes=("available_ratio_warn", "margin_ratio_warn"),
                boundary_codes=("historical_callbacks_present",),
                evidence_only_codes=("no_current_session_callbacks",),
            )

    class FakeReconciliationAdapter:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def capture_evidence_mainline(self, **kwargs) -> CtpReconciliationEvidence:
            self.calls.append(kwargs)
            return CtpReconciliationEvidence(
                evidence_version="reconciliation-evidence-v1",
                captured_at_utc="2026-04-02T08:03:00Z",
                account_id="025292",
                disposition="manual_review_required",
                requires_manual_review=True,
                finding_count=3,
                manual_review_codes=("available_ratio_warn", "margin_ratio_warn"),
                evidence_only_codes=("dominant_exposure_watch",),
                position_line_count=73,
                symbol_count=41,
                gross_position_qty=183,
                available_ratio=0.213352,
                margin_ratio=0.781532,
                dominant_exposure_symbol="m2605-P-3000",
                dominant_exposure_abs_net_qty=10,
                top_exposures=(),
            )

    startup_truth_adapter = FakeStartupTruthAdapter()
    data_client = FakeDataClient()
    truth_merge_adapter = FakeTruthMergeAdapter()
    reconciliation_adapter = FakeReconciliationAdapter()

    adapter = CtpLiveOpsSnapshotAdapter(
        config=CtpAdapterConfig.from_dict({"UserID": "025292"}),
        runtime_bridge=bridge,
        startup_truth_adapter=startup_truth_adapter,  # type: ignore[arg-type]
        data_client=data_client,  # type: ignore[arg-type]
        truth_merge_adapter=truth_merge_adapter,  # type: ignore[arg-type]
        reconciliation_adapter=reconciliation_adapter,  # type: ignore[arg-type]
    )

    snapshot = adapter.capture_live_ops_snapshot_mainline(
        timeout_seconds=9,
        td_shared_flow_path=Path("D:/tmp/td-shared"),
        td_isolated_flow_path=Path("D:/tmp/td-isolated"),
        md_flow_path=Path("D:/tmp/md-flow"),
        td_flow_path=Path("D:/tmp/td-flow"),
        query_flow_path=Path("D:/tmp/query-flow"),
        observation_grace_seconds=0.75,
        completion_grace_seconds=0.5,
    )

    assert isinstance(snapshot, CtpLiveOpsSnapshot)
    assert snapshot.startup_truth.account_id == "025292"
    assert snapshot.md_truth.symbol == "rb2610"
    assert snapshot.td_truth.position_count == 73
    assert snapshot.reconciliation.gross_position_qty == 183
    assert startup_truth_adapter.calls == [
        {
            "timeout_seconds": 9,
            "shared_flow_path": Path("D:/tmp/td-shared"),
            "isolated_flow_path": Path("D:/tmp/td-isolated"),
        }
    ]
    assert data_client.calls == [
        {
            "timeout_seconds": 9,
            "flow_path": Path("D:/tmp/md-flow"),
        }
    ]
    assert truth_merge_adapter.calls == [
        {
            "timeout_seconds": 9,
            "flow_path": Path("D:/tmp/td-flow"),
            "observation_grace_seconds": 0.75,
            "completion_grace_seconds": 0.5,
        }
    ]
    assert reconciliation_adapter.calls == [
        {
            "timeout_seconds": 9,
            "flow_path": Path("D:/tmp/query-flow"),
            "completion_grace_seconds": 0.5,
        }
    ]


def test_live_ops_snapshot_adapter_summarizes_snapshot() -> None:
    adapter = CtpLiveOpsSnapshotAdapter(
        config=CtpAdapterConfig.from_dict({"UserID": "025292"}),
        runtime_bridge=CtpRuntimeBridge(),
    )
    snapshot = CtpLiveOpsSnapshot(
        startup_truth=CtpStartupTruthEvidenceMatrix(
            evidence_version="startup-truth-evidence-v1",
            captured_at_utc="2026-04-02T08:00:00Z",
            account_id="025292",
            disposition="rebuild_required",
            shared_flow_reuse_allowed=False,
            session_rotated=True,
            max_order_ref_reset=True,
            shared_flow_path="D:\\repo\\var\\td_flow_smoke",
            isolated_flow_path="D:\\repo\\output\\debug\\td_flow_isolated",
            shared_session_id=100,
            isolated_session_id=101,
            shared_max_order_ref=8,
            isolated_max_order_ref=1,
            shared_disconnect_count=1,
            isolated_disconnect_count=0,
            manual_review_codes=(),
            rebuild_required_codes=("shared_flow_requires_isolated_rebuild",),
            evidence_only_codes=("fresh_session_identity_observed",),
        ),
        md_truth=CtpMdTruthEvidenceMatrix(
            evidence_version="md-truth-evidence-v1",
            captured_at_utc="2026-04-02T08:01:00Z",
            account_id="025292",
            symbol="rb2610",
            disposition="evidence_only",
            startup_ready=True,
            restore_triggered=True,
            restore_succeeded=True,
            startup_flow_path="D:\\repo\\var\\md_flow_smoke",
            restored_flow_path="D:\\repo\\var\\md_flow_smoke",
            startup_first_tick_ts_epoch_us=1000,
            restored_first_tick_ts_epoch_us=2000,
            manual_review_codes=(),
            restore_required_codes=(),
            evidence_only_codes=("restore_resubscribe_triggered",),
        ),
        td_truth=CtpTdMergedEvidenceMatrix(
            evidence_version="td-merged-evidence-v1",
            captured_at_utc="2026-04-02T08:02:00Z",
            account_id="025292",
            disposition="manual_review_required",
            position_count=73,
            observed_callback_count=9,
            historical_callback_count=9,
            current_session_callback_count=0,
            available_ratio=0.213352,
            margin_ratio=0.781532,
            manual_review_codes=("available_ratio_warn", "margin_ratio_warn"),
            boundary_codes=("historical_callbacks_present",),
            evidence_only_codes=("no_current_session_callbacks",),
        ),
        reconciliation=CtpReconciliationEvidence(
            evidence_version="reconciliation-evidence-v1",
            captured_at_utc="2026-04-02T08:03:00Z",
            account_id="025292",
            disposition="manual_review_required",
            requires_manual_review=True,
            finding_count=3,
            manual_review_codes=("available_ratio_warn", "margin_ratio_warn"),
            evidence_only_codes=("dominant_exposure_watch",),
            position_line_count=73,
            symbol_count=41,
            gross_position_qty=183,
            available_ratio=0.213352,
            margin_ratio=0.781532,
            dominant_exposure_symbol="m2605-P-3000",
            dominant_exposure_abs_net_qty=10,
            top_exposures=(),
        ),
    )

    summary = adapter.summarize_live_ops_snapshot(snapshot)

    assert isinstance(summary, CtpLiveOpsSnapshotSummary)
    assert summary.baseline == "live-ops-snapshot-v1"
    assert summary.account_id == "025292"
    assert summary.symbol == "rb2610"
    assert summary.startup_disposition == "rebuild_required"
    assert summary.md_disposition == "evidence_only"
    assert summary.td_disposition == "manual_review_required"
    assert summary.reconciliation_disposition == "manual_review_required"
    assert summary.startup_shared_flow_reuse_allowed is False
    assert summary.startup_session_rotated is True
    assert summary.md_restore_succeeded is True
    assert summary.position_count == 73
    assert summary.observed_callback_count == 9
    assert summary.historical_callback_count == 9
    assert summary.current_session_callback_count == 0
    assert summary.available_ratio == 0.213352
    assert summary.margin_ratio == 0.781532
    assert summary.manual_review_codes == ("available_ratio_warn", "margin_ratio_warn")
    assert summary.rebuild_required_codes == ("shared_flow_requires_isolated_rebuild",)
    assert summary.restore_required_codes == ()
    assert summary.boundary_codes == ("historical_callbacks_present",)
    assert summary.evidence_only_codes == (
        "fresh_session_identity_observed",
        "restore_resubscribe_triggered",
        "no_current_session_callbacks",
        "dominant_exposure_watch",
    )


def test_live_ops_snapshot_adapter_evaluates_policy_priority() -> None:
    adapter = CtpLiveOpsSnapshotAdapter(
        config=CtpAdapterConfig.from_dict({"UserID": "025292"}),
        runtime_bridge=CtpRuntimeBridge(),
    )
    summary = CtpLiveOpsSnapshotSummary(
        baseline="live-ops-snapshot-v1",
        account_id="025292",
        symbol="rb2610",
        startup_disposition="rebuild_required",
        md_disposition="evidence_only",
        td_disposition="manual_review_required",
        reconciliation_disposition="manual_review_required",
        startup_shared_flow_reuse_allowed=False,
        startup_session_rotated=True,
        md_restore_succeeded=True,
        position_count=73,
        observed_callback_count=9,
        historical_callback_count=9,
        current_session_callback_count=0,
        available_ratio=0.213352,
        margin_ratio=0.781532,
        manual_review_codes=("available_ratio_warn", "margin_ratio_warn"),
        rebuild_required_codes=("shared_flow_requires_isolated_rebuild",),
        restore_required_codes=(),
        boundary_codes=("historical_callbacks_present",),
        evidence_only_codes=("dominant_exposure_watch",),
    )

    result = adapter.evaluate_live_ops_policy(summary)

    assert isinstance(result, CtpLiveOpsPolicyResult)
    assert result.disposition == "manual_review_required"
    assert [finding.code for finding in result.findings] == [
        "manual_review_codes_present",
        "startup_rebuild_required",
        "td_boundary_required",
        "evidence_only_signals_present",
    ]
    assert [finding.action for finding in result.findings] == [
        "manual_review_required",
        "rebuild_required",
        "boundary_required",
        "evidence_only",
    ]


def test_live_ops_snapshot_adapter_builds_evidence_matrix() -> None:
    adapter = CtpLiveOpsSnapshotAdapter(
        config=CtpAdapterConfig.from_dict({"UserID": "025292"}),
        runtime_bridge=CtpRuntimeBridge(),
    )
    result = CtpLiveOpsPolicyResult(
        summary=CtpLiveOpsSnapshotSummary(
            baseline="live-ops-snapshot-v1",
            account_id="025292",
            symbol="rb2610",
            startup_disposition="rebuild_required",
            md_disposition="evidence_only",
            td_disposition="manual_review_required",
            reconciliation_disposition="manual_review_required",
            startup_shared_flow_reuse_allowed=False,
            startup_session_rotated=True,
            md_restore_succeeded=True,
            position_count=73,
            observed_callback_count=9,
            historical_callback_count=9,
            current_session_callback_count=0,
            available_ratio=0.213352,
            margin_ratio=0.781532,
            manual_review_codes=("available_ratio_warn", "margin_ratio_warn"),
            rebuild_required_codes=("shared_flow_requires_isolated_rebuild",),
            restore_required_codes=(),
            boundary_codes=("historical_callbacks_present",),
            evidence_only_codes=("dominant_exposure_watch",),
        ),
        disposition="manual_review_required",
        findings=(
            CtpLiveOpsPolicyFinding(
                code="manual_review_codes_present",
                severity="warn",
                action="manual_review_required",
                metric="manual_review_codes",
                metric_value="available_ratio_warn,margin_ratio_warn",
                threshold="empty",
                message="Underlying truth layers raised manual review findings, so live ops disposition must stay manual_review_required.",
            ),
            CtpLiveOpsPolicyFinding(
                code="startup_rebuild_required",
                severity="warn",
                action="rebuild_required",
                metric="startup_shared_flow_reuse_allowed",
                metric_value=False,
                threshold=True,
                message="TD startup truth still requires isolated rebuild-safe flow handling.",
            ),
        ),
    )

    evidence = adapter.build_live_ops_evidence_matrix(result)

    assert isinstance(evidence, CtpLiveOpsEvidenceMatrix)
    assert evidence.evidence_version == "live-ops-evidence-v1"
    assert evidence.account_id == "025292"
    assert evidence.symbol == "rb2610"
    assert evidence.disposition == "manual_review_required"
    assert evidence.startup_disposition == "rebuild_required"
    assert evidence.md_disposition == "evidence_only"
    assert evidence.td_disposition == "manual_review_required"
    assert evidence.reconciliation_disposition == "manual_review_required"
    assert evidence.startup_shared_flow_reuse_allowed is False
    assert evidence.startup_session_rotated is True
    assert evidence.md_restore_succeeded is True
    assert evidence.position_count == 73
    assert evidence.observed_callback_count == 9
    assert evidence.historical_callback_count == 9
    assert evidence.current_session_callback_count == 0
    assert evidence.available_ratio == 0.213352
    assert evidence.margin_ratio == 0.781532
    assert evidence.manual_review_codes == ("available_ratio_warn", "margin_ratio_warn")
    assert evidence.rebuild_required_codes == ("shared_flow_requires_isolated_rebuild",)
    assert evidence.restore_required_codes == ()
    assert evidence.boundary_codes == ("historical_callbacks_present",)
    assert evidence.evidence_only_codes == ("dominant_exposure_watch",)


def test_order_lifecycle_smoke_baseline_is_dry_run_and_submits_runtime_command() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    def fake_td_readiness_smoke(*, timeout_seconds: int = 20, flow_path=None) -> CtpTdSmokeResult:
        return CtpTdSmokeResult(
            init_code=0,
            authenticate_code=0,
            login_code=0,
            settlement_code=0,
            login_success=True,
            login_error_id=0,
            login_error_message="",
            front_id=11,
            session_id=22,
            max_order_ref=13,
            disconnects=[],
        )

    execution_client.run_live_td_readiness_smoke = fake_td_readiness_smoke  # type: ignore[method-assign]
    result = execution_client.run_order_lifecycle_smoke_baseline(
        instrument_id="c2609",
        side="BUY",
        quantity=1,
        limit_price=2241.0,
        client_order_id="order-smoke-1",
        dry_run=True,
    )
    commands = bridge.drain_submitted_commands()

    assert isinstance(result, CtpOrderLifecycleSmokeResult)
    assert result.dry_run is True
    assert result.live_send_armed is False
    assert result.bootstrap.ready is True
    assert result.mapped_submit.error is None
    assert result.mapped_submit.order_ref == 14
    assert [command.kind for command in commands] == [
        CtpRuntimeCommandKind.CONNECT,
        CtpRuntimeCommandKind.SUBMIT_ORDER,
    ]


def test_order_lifecycle_live_send_requires_config_arm() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": False,
            },
        }
    )
    execution_client = build_ctp_stack(config)["execution_client"]

    def fake_td_readiness_smoke(*, timeout_seconds: int = 20, flow_path=None) -> CtpTdSmokeResult:
        return CtpTdSmokeResult(
            init_code=0,
            authenticate_code=0,
            login_code=0,
            settlement_code=0,
            login_success=True,
            login_error_id=0,
            login_error_message="",
            front_id=11,
            session_id=22,
            max_order_ref=13,
            disconnects=[],
        )

    execution_client.run_live_td_readiness_smoke = fake_td_readiness_smoke  # type: ignore[method-assign]

    try:
        execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id="c2609",
            side="BUY",
            quantity=1,
            limit_price=2241.0,
            dry_run=False,
        )
        assert False, "expected live-send gate to reject when config is not armed"
    except RuntimeError as exc:
        assert "AllowLiveOrderSmoke=true" in str(exc)


def test_order_lifecycle_live_send_hits_native_order_send_and_collects_exec_events() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": True,
            },
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    class FakeTdApi:
        def __init__(self) -> None:
            self.order_send_calls: list[dict[str, object]] = []
            self._login_callback = None
            self._disconnect_callback = None
            self._exec_callback = None

        def create(self, flow_path: Path) -> int:
            self.flow_path = flow_path
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_exec_callback(self, handle: int, callback):
            self._exec_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            self.init_front = front
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            self.auth_payload = (app_id, auth_code, product_info)
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            assert self._login_callback is not None
            self._login_callback(LoginResponse())
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

        def order_send(self, handle: int, **kwargs) -> int:
            self.order_send_calls.append(kwargs)
            assert self._exec_callback is not None
            self._exec_callback(
                NativeExecView(
                    order_id=str(kwargs["order_id"]),
                    symbol=str(kwargs["symbol"]),
                    price=float(kwargs["price"]),
                    qty=int(kwargs["qty"]),
                    side=int(kwargs["side"]),
                    status=3,
                    ts_epoch_us=10,
                    order_ref="101",
                    front_id=11,
                    session_id=22,
                    direction=int(kwargs["side"]),
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            self._exec_callback(
                NativeExecView(
                    order_id=str(kwargs["order_id"]),
                    symbol=str(kwargs["symbol"]),
                    price=float(kwargs["price"]),
                    qty=int(kwargs["qty"]),
                    side=int(kwargs["side"]),
                    status=4,
                    ts_epoch_us=11,
                    order_ref="101",
                    front_id=11,
                    session_id=22,
                    direction=int(kwargs["side"]),
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=True,
                    trade_price=float(kwargs["price"]),
                    trade_volume=int(kwargs["qty"]),
                    error_msg="",
                    leaves_qty=0,
                )
            )
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        result = execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id="c2609",
            side="BUY",
            quantity=1,
            limit_price=2241.0,
            client_order_id="order-smoke-live-1",
            dry_run=False,
        )
    finally:
        setattr(CtpTdApi, "load", original_load)

    commands = bridge.drain_submitted_commands()
    events = bridge.drain_events()

    assert result.dry_run is False
    assert result.live_send_armed is True  # [CONTRACT-LOCK: config arm plus live path must reach native order send]
    assert result.mapped_submit.error is None
    assert [matched.match_reason for matched in result.matched_execs or []] == [
        "client_order_id_echo",
        "native_alias",
    ]
    assert fake_api.order_send_calls[0]["symbol"] == "c2609"  # [CONTRACT-LOCK: live smoke native send stays locked to c2609]
    assert fake_api.order_send_calls[0]["qty"] == 1
    assert [command.kind for command in commands] == [
        CtpRuntimeCommandKind.CONNECT,
        CtpRuntimeCommandKind.SUBMIT_ORDER,
    ]
    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        CtpRuntimeEventKind.SETTLEMENT_CONFIRMED,
        CtpRuntimeEventKind.ORDER,
        CtpRuntimeEventKind.TRADE,
    ]
    assert [event.client_order_id for event in events[-2:]] == [
        "order-smoke-live-1",
        "order-smoke-live-1",
    ]  # [CONTRACT-LOCK: native ORDER/TRADE callbacks must be rebound to the Python smoke client_order_id after correlation]


def test_order_lifecycle_live_send_uses_unique_default_flow_directory() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": True,
            },
        }
    )
    execution_client = build_ctp_stack(config)["execution_client"]

    class FakeTdApi:
        def __init__(self) -> None:
            self.flow_path: Path | None = None
            self._login_callback = None
            self._disconnect_callback = None
            self._exec_callback = None

        def create(self, flow_path: Path) -> int:
            self.flow_path = flow_path
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_exec_callback(self, handle: int, callback):
            self._exec_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            self._login_callback(LoginResponse())
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

        def order_send(self, handle: int, **kwargs) -> int:
            self._exec_callback(
                NativeExecView(
                    order_id=str(kwargs["order_id"]),
                    symbol=str(kwargs["symbol"]),
                    price=float(kwargs["price"]),
                    qty=int(kwargs["qty"]),
                    side=int(kwargs["side"]),
                    status=3,
                    ts_epoch_us=10,
                    order_ref="101",
                    front_id=11,
                    session_id=22,
                    direction=int(kwargs["side"]),
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id="c2609",
            side="BUY",
            quantity=1,
            limit_price=2241.0,
            client_order_id="order-smoke-live-flow-default",
            dry_run=False,
        )
    finally:
        setattr(CtpTdApi, "load", original_load)

    assert fake_api.flow_path is not None
    assert fake_api.flow_path.parent.name == "debug"
    assert fake_api.flow_path.name.startswith("live_order_smoke_")  # [CONTRACT-LOCK: real order smoke must use a unique default flow directory to avoid reusing stale TD session artifacts]


def test_order_lifecycle_live_send_ignores_unrelated_exec_callbacks_until_matching_symbol_callback_arrives() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": True,
            },
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    class FakeTdApi:
        def __init__(self) -> None:
            self._login_callback = None
            self._disconnect_callback = None
            self._exec_callback = None

        def create(self, flow_path: Path) -> int:
            self.flow_path = flow_path
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_exec_callback(self, handle: int, callback):
            self._exec_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            assert self._login_callback is not None
            self._login_callback(LoginResponse())
            assert self._exec_callback is not None
            self._exec_callback(
                NativeExecView(
                    order_id="historical-order",
                    symbol="c2609",
                    price=2300.0,
                    qty=1,
                    side=0,
                    status=3,
                    ts_epoch_us=9,
                    order_ref="77",
                    front_id=11,
                    session_id=22,
                    direction=0,
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

        def order_send(self, handle: int, **kwargs) -> int:
            assert self._exec_callback is not None
            self._exec_callback(
                NativeExecView(
                    order_id="server-generated-order-id",
                    symbol=str(kwargs["symbol"]),
                    price=float(kwargs["price"]),
                    qty=int(kwargs["qty"]),
                    side=1,
                    status=3,
                    ts_epoch_us=10,
                    order_ref="server-generated-order-ref",
                    front_id=11,
                    session_id=22,
                    direction=int(kwargs["side"]),
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        result = execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id="c2609",
            side="BUY",
            quantity=1,
            limit_price=2241.0,
            client_order_id="order-smoke-live-2",
            dry_run=False,
        )
    finally:
        setattr(CtpTdApi, "load", original_load)

    events = bridge.drain_events()

    assert result.live_send_armed is True
    assert [event.client_order_id for event in events if event.kind is CtpRuntimeEventKind.ORDER] == [
        "historical-order",
        "order-smoke-live-2",
    ]
    assert result.mapped_submit.order_ref == 101
    assert result.mapped_submit.client_order_id == "order-smoke-live-2"
    assert [matched.match_reason for matched in result.matched_execs or []] == [
        "post_send_symbol_qty",
    ]  # [CONTRACT-LOCK: when native ids drift, the first post-send same-symbol/same-qty callback becomes the alias anchor for the smoke order even if callback side semantics differ]
    assert result.matched_execs[0].native_order_id == "server-generated-order-id"
    assert bridge.trading.state_for("order-smoke-live-2") is CtpOrderState.WORKING
    assert any(
        event.kind is CtpRuntimeEventKind.ORDER and event.venue_symbol == "c2609"
        for event in events
    )  # [CONTRACT-LOCK: live smoke must ignore historical callbacks and accept the first post-send c2609 callback even if native order ids differ]


def test_order_lifecycle_live_send_ignores_delayed_historical_same_symbol_callbacks_before_native_boundary_match() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": True,
            },
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    class FakeTdApi:
        def __init__(self) -> None:
            self._login_callback = None
            self._disconnect_callback = None
            self._exec_callback = None

        def create(self, flow_path: Path) -> int:
            self.flow_path = flow_path
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_exec_callback(self, handle: int, callback):
            self._exec_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            assert self._login_callback is not None
            self._login_callback(LoginResponse())
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

        def order_send(self, handle: int, **kwargs) -> int:
            assert self._exec_callback is not None
            self._exec_callback(
                NativeExecView(
                    order_id="99",
                    symbol=str(kwargs["symbol"]),
                    price=float(kwargs["price"]),
                    qty=int(kwargs["qty"]),
                    side=1,
                    status=3,
                    ts_epoch_us=10,
                    order_ref="77",
                    front_id=11,
                    session_id=22,
                    direction=int(kwargs["side"]),
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            self._exec_callback(
                NativeExecView(
                    order_id="101",
                    symbol=str(kwargs["symbol"]),
                    price=float(kwargs["price"]),
                    qty=int(kwargs["qty"]),
                    side=1,
                    status=3,
                    ts_epoch_us=11,
                    order_ref="24332",
                    front_id=11,
                    session_id=22,
                    direction=int(kwargs["side"]),
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        result = execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id="c2609",
            side="BUY",
            quantity=1,
            limit_price=2241.0,
            client_order_id="order-smoke-live-3",
            dry_run=False,
        )
    finally:
        setattr(CtpTdApi, "load", original_load)

    events = bridge.drain_events()

    assert result.live_send_armed is True
    assert [matched.match_reason for matched in result.matched_execs or []] == [
        "post_send_native_order_id_boundary",
    ]  # [CONTRACT-LOCK: delayed same-symbol historical callbacks must not consume the live smoke alias when their native order_id does not cross the login boundary]
    assert result.matched_execs[0].native_order_id == "101"
    assert [event.client_order_id for event in events if event.kind is CtpRuntimeEventKind.ORDER] == [
        "99",
        "order-smoke-live-3",
    ]


def test_order_lifecycle_live_send_maps_ioc_to_native_time_condition() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
                "AllowLiveOrderSmoke": True,
            },
        }
    )
    execution_client = build_ctp_stack(config)["execution_client"]

    class FakeTdApi:
        def __init__(self) -> None:
            self.order_send_calls: list[dict[str, object]] = []
            self._login_callback = None
            self._disconnect_callback = None
            self._exec_callback = None

        def create(self, flow_path: Path) -> int:
            return 1

        def dispose(self, handle: int) -> None:
            self.disposed_handle = handle

        def set_login_callback(self, handle: int, callback):
            self._login_callback = callback
            return callback

        def set_front_disconnected_callback(self, handle: int, callback):
            self._disconnect_callback = callback
            return callback

        def set_exec_callback(self, handle: int, callback):
            self._exec_callback = callback
            return callback

        def init(self, handle: int, front: str) -> int:
            return 0

        def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
            return 0

        def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 11
                session_id = 22
                max_order_ref = 100

            self._login_callback(LoginResponse())
            return 0

        def confirm_settlement(self, handle: int) -> int:
            return 0

        def order_send(self, handle: int, **kwargs) -> int:
            self.order_send_calls.append(kwargs)
            self._exec_callback(
                NativeExecView(
                    order_id=str(kwargs["order_id"]),
                    symbol=str(kwargs["symbol"]),
                    price=float(kwargs["price"]),
                    qty=int(kwargs["qty"]),
                    side=int(kwargs["side"]),
                    status=3,
                    ts_epoch_us=10,
                    order_ref="101",
                    front_id=11,
                    session_id=22,
                    direction=int(kwargs["side"]),
                    offset_flag=0,
                    hedge_flag=1,
                    is_trade=False,
                    trade_price=0.0,
                    trade_volume=0,
                    error_msg="",
                    leaves_qty=1,
                )
            )
            return 0

    fake_api = FakeTdApi()
    original_load = CtpTdApi.__dict__["load"]
    setattr(CtpTdApi, "load", classmethod(lambda cls, base_dir: fake_api))

    try:
        execution_client.run_order_lifecycle_smoke_baseline(
            instrument_id="c2609",
            side="BUY",
            quantity=1,
            limit_price=2241.0,
            client_order_id="order-smoke-ioc-1",
            dry_run=False,
            time_in_force="IOC",
        )
    finally:
        setattr(CtpTdApi, "load", original_load)

    assert fake_api.order_send_calls[0]["time_condition"] == 1  # [CONTRACT-LOCK: IOC live smoke must map to native IOC time condition]


def test_execution_client_exec_callback_maps_order_and_trade_events() -> None:
    stack = build_ctp_stack(CtpAdapterConfig())
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]

    execution_client._on_td_exec_callback(
        NativeExecView(
            order_id="ord-1",
            symbol="c2609",
            price=2241.0,
            qty=1,
            side=0,
            status=3,
            ts_epoch_us=10,
            order_ref="2",
            front_id=11,
            session_id=22,
            direction=0,
            offset_flag=0,
            hedge_flag=1,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            error_msg="",
            leaves_qty=1,
        )
    )
    execution_client._on_td_exec_callback(
        NativeExecView(
            order_id="ord-1",
            symbol="c2609",
            price=2241.0,
            qty=1,
            side=0,
            status=4,
            ts_epoch_us=11,
            order_ref="2",
            front_id=11,
            session_id=22,
            direction=0,
            offset_flag=0,
            hedge_flag=1,
            is_trade=True,
            trade_price=2241.0,
            trade_volume=1,
            error_msg="",
            leaves_qty=0,
        )
    )
    events = bridge.drain_events()
    order_payload = CtpTdExecEventPayload.from_runtime_event(events[0])
    trade_payload = CtpTdExecEventPayload.from_runtime_event(events[1])

    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.ORDER,
        CtpRuntimeEventKind.TRADE,
    ]
    assert order_payload.order_ref == "2"
    assert order_payload.front_id == 11
    assert trade_payload.is_trade is True
    assert trade_payload.trade_volume == 1


def test_check_rust_gate_reports_missing_cargo_when_toolchain_is_absent(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "check_rust_gate.py"
    env = os.environ.copy()
    env["PATH"] = str(tmp_path)

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
    )

    assert result.returncode == 1
    assert "FAIL rust-gate: cargo-not-found" in result.stdout
    assert "NEXT rust-gate: install Rust toolchain" in result.stdout


def test_check_rust_gate_runs_metadata_and_check_with_fake_cargo(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "check_rust_gate.py"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_cargo_py = fake_bin / "fake_cargo.py"
    fake_cargo_py.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import sys",
                "",
                "command = sys.argv[1] if len(sys.argv) > 1 else ''",
                "if command == 'metadata':",
                "    print('{\"workspace_members\":[\"ctp_runtime_core 0.1.0 (path+file:///D:/Nautilus/nautilus_ctp_adapter/rust/ctp_runtime_core)\"],\"version\":1}')",
                "    raise SystemExit(0)",
                "if command == 'check':",
                "    print('Finished dev [unoptimized + debuginfo] target(s) in 0.01s')",
                "    raise SystemExit(0)",
                "print('unsupported cargo command', file=sys.stderr)",
                "raise SystemExit(1)",
            ]
        ),
        encoding="utf-8",
    )
    fake_cargo = fake_bin / "cargo.cmd"
    fake_cargo.write_text(
        "\n".join(
            [
                "@echo off",
                f'"{sys.executable}" "%~dp0fake_cargo.py" %*',
            ]
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PATH"] = str(fake_bin)

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "PASS rust-gate: cargo-found" in result.stdout
    assert "PASS rust-gate: workspace-members=1" in result.stdout
    assert "PASS rust-gate: cargo-check" in result.stdout


def test_read_only_smokes_report_structured_config_load_failure() -> None:
    root = Path(__file__).resolve().parents[1]
    missing_config = root / "output" / "debug" / "missing-live-config.json"
    cases = {
        "ctp_query_adapter_smoke.py": "nautilus-query-adapter-v1",
        "ctp_position_query_smoke.py": "position-query-smoke-v1",
        "ctp_account_query_smoke.py": "account-query-smoke-v1",
        "ctp_reconciliation_snapshot_smoke.py": "reconciliation-snapshot-v1",
        "ctp_td_truth_merge_snapshot_smoke.py": "td-truth-merge-snapshot-v1",
        "ctp_td_merged_reconciliation_policy_smoke.py": "td-merged-reconciliation-policy-v1",
    }

    for script_name, baseline in cases.items():
        script = root / "scripts" / script_name
        result = subprocess.run(
            [sys.executable, str(script), "--config", str(missing_config)],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        assert result.returncode == 1, script_name
        payload = json.loads(result.stdout)
        assert payload["baseline"] == baseline, script_name
        assert payload["success"] is False, script_name
        assert payload["failure_reason"] == "exception", script_name
        assert payload["error_stage"] == "config_load", script_name
        assert payload["error_type"] == "FileNotFoundError", script_name
        assert "missing-live-config.json" in payload["error_message"], script_name


def test_query_adapter_smoke_rejects_live_send_argument() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "ctp_query_adapter_smoke.py"
    config = root / "cfgs" / "ctp.live.example.json"

    result = subprocess.run(
        [sys.executable, str(script), "--config", str(config), "--live-send"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 2
    assert "unrecognized arguments: --live-send" in result.stderr
