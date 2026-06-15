"""Unit tests for Nautilus-compatible CTP data/execution client and config."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.ctp_nautilus_engine_harness as engine_harness

from nautilus_trader.core.uuid import UUID4
from nautilus_trader.config import LiveDataClientConfig, LiveExecClientConfig, InstrumentProviderConfig
from nautilus_trader.execution.messages import (
    GenerateFillReports,
    GenerateOrderStatusReport,
    GenerateOrderStatusReports,
    GeneratePositionStatusReports,
)
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.model.events import AccountState
from nautilus_trader.model.enums import OrderStatus, PositionSide
from nautilus_trader.model.identifiers import InstrumentId, VenueOrderId

from nautilus_ctp_adapter.adapters.ctp.nautilus_config import (
    CtpDataClientConfig,
    CtpExecClientConfig,
    CtpInstrumentProviderConfig,
)
from nautilus_ctp_adapter.adapters.ctp.nautilus_data import CtpLiveDataClient
from nautilus_ctp_adapter.adapters.ctp.nautilus_data import provider_backed_subscription_symbols
from nautilus_ctp_adapter.adapters.ctp.nautilus_data import resolve_ctp_tick_instrument
from nautilus_ctp_adapter.adapters.ctp.nautilus_data import resolve_ctp_tick_instrument_id
from nautilus_ctp_adapter.adapters.ctp.nautilus_execution import CtpLiveExecutionClient
from nautilus_ctp_adapter.adapters.ctp.nautilus_execution import ctp_account_record_to_account_state
from nautilus_ctp_adapter.adapters.ctp.nautilus_execution import ctp_exec_event_to_fill_report
from nautilus_ctp_adapter.adapters.ctp.nautilus_execution import ctp_exec_event_to_order_status_report
from nautilus_ctp_adapter.adapters.ctp.nautilus_execution import ctp_position_record_to_status_report
from nautilus_ctp_adapter.adapters.ctp.nautilus_factories import (
    CtpLiveDataClientFactory,
    CtpLiveExecClientFactory,
    get_ctp_instrument_provider,
    _CTP_PROVIDERS,
)
from nautilus_ctp_adapter.adapters.ctp.nautilus_provider import CtpNautilusInstrumentProvider
from nautilus_ctp_adapter.adapters.ctp.normalization import CtpProductKind, NormalizedCtpInstrument
from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpExecutionClient
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpSubmitOrderIntent
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpTdExecEventPayload
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpTdSessionIdentity
from nautilus_ctp_adapter.native import NativeExecView
from nautilus_ctp_adapter.runtime.query import CtpAccountRecord
from nautilus_ctp_adapter.runtime.query import CtpPositionRecord


# ---------------------------------------------------------------------------
# A1: CtpDataClientConfig inherits LiveDataClientConfig and is frozen
# ---------------------------------------------------------------------------


class TestCtpDataClientConfig:
    def test_isinstance_live_data_client_config(self) -> None:
        cfg = CtpDataClientConfig(
            md_front="tcp://180.168.146.187:10131",
            broker_id="9999",
            user_id="test",
            password="test",
        )
        assert isinstance(cfg, LiveDataClientConfig)

    def test_frozen(self) -> None:
        cfg = CtpDataClientConfig(md_front="tcp://1.2.3.4:10131")
        with pytest.raises(AttributeError):
            cfg.md_front = "tcp://other:10131"  # type: ignore[misc]

    def test_fields_accessible(self) -> None:
        cfg = CtpDataClientConfig(
            md_front="tcp://1.2.3.4:10131",
            broker_id="9999",
            user_id="user1",
            password="pw",
            subscribe_symbols=["rb2610", "ag2612"],
        )
        assert cfg.md_front == "tcp://1.2.3.4:10131"
        assert cfg.broker_id == "9999"
        assert cfg.user_id == "user1"
        assert cfg.password == "pw"
        assert cfg.subscribe_symbols == ["rb2610", "ag2612"]

    def test_default_values(self) -> None:
        cfg = CtpDataClientConfig()
        assert cfg.md_front == ""
        assert cfg.broker_id == ""
        assert cfg.subscribe_symbols == []
        assert isinstance(cfg.instrument_provider, CtpInstrumentProviderConfig)


# ---------------------------------------------------------------------------
# A5: to_adapter_config() correctly maps to CtpAdapterConfig
# ---------------------------------------------------------------------------


class TestToAdapterConfig:
    def test_to_adapter_config_mapping(self) -> None:
        cfg = CtpDataClientConfig(
            md_front="tcp://1.2.3.4:10131",
            broker_id="9999",
            user_id="test_user",
            password="test_pw",
            subscribe_symbols=["rb2610", "ag2612"],
        )
        adapter_cfg = cfg.to_adapter_config()
        assert isinstance(adapter_cfg, CtpAdapterConfig)
        assert adapter_cfg.broker_id == "9999"
        assert adapter_cfg.user_id == "test_user"
        assert adapter_cfg.password == "test_pw"
        assert adapter_cfg.md_front == "tcp://1.2.3.4:10131"
        assert adapter_cfg.instruments == ["rb2610", "ag2612"]

    def test_to_adapter_config_empty(self) -> None:
        cfg = CtpDataClientConfig()
        adapter_cfg = cfg.to_adapter_config()
        assert adapter_cfg.broker_id == ""
        assert adapter_cfg.instruments == []


# ---------------------------------------------------------------------------
# A2: CtpInstrumentProviderConfig inherits InstrumentProviderConfig
# ---------------------------------------------------------------------------


class TestCtpInstrumentProviderConfig:
    def test_isinstance(self) -> None:
        cfg = CtpInstrumentProviderConfig()
        assert isinstance(cfg, InstrumentProviderConfig)

    def test_frozen(self) -> None:
        cfg = CtpInstrumentProviderConfig()
        with pytest.raises(AttributeError):
            cfg.td_front = "changed"  # type: ignore[misc]

    def test_ctp_fields(self) -> None:
        cfg = CtpInstrumentProviderConfig(
            td_front="tcp://1.2.3.4:10130",
            broker_id="9999",
            load_contracts_on_start=False,
            contract_filter=["rb", "ag"],
        )
        assert cfg.td_front == "tcp://1.2.3.4:10130"
        assert cfg.broker_id == "9999"
        assert cfg.load_contracts_on_start is False
        assert cfg.contract_filter == ["rb", "ag"]


# ---------------------------------------------------------------------------
# A1 + A3 + A4: CtpLiveDataClient inherits LiveMarketDataClient,
#               has coroutine _connect/_disconnect,
#               has _subscribe/_unsubscribe_quote_ticks
# ---------------------------------------------------------------------------


class TestCtpLiveDataClient:
    def test_isinstance_live_market_data_client(self) -> None:
        assert issubclass(CtpLiveDataClient, LiveMarketDataClient)

    def test_connect_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveDataClient._connect)

    def test_disconnect_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveDataClient._disconnect)

    def test_subscribe_quote_ticks_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveDataClient._subscribe_quote_ticks)

    def test_unsubscribe_quote_ticks_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveDataClient._unsubscribe_quote_ticks)

    def test_subscribe_instrument_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveDataClient._subscribe_instrument)

    def test_request_instrument_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveDataClient._request_instrument)

    def test_request_instruments_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveDataClient._request_instruments)


# ---------------------------------------------------------------------------
# A6: tick callback uses call_soon_threadsafe (code-level check)
# ---------------------------------------------------------------------------


class TestCallbackBridge:
    def test_on_md_tick_uses_call_soon_threadsafe(self) -> None:
        """Verify _on_md_tick method exists and references call_soon_threadsafe."""
        import inspect

        source = inspect.getsource(CtpLiveDataClient._on_md_tick)
        assert "call_soon_threadsafe" in source

    def test_on_md_login_uses_call_soon_threadsafe(self) -> None:
        import inspect

        source = inspect.getsource(CtpLiveDataClient._on_md_login)
        assert "call_soon_threadsafe" in source

    def test_on_md_disconnect_uses_call_soon_threadsafe(self) -> None:
        import inspect

        source = inspect.getsource(CtpLiveDataClient._on_md_disconnect)
        assert "call_soon_threadsafe" in source


# ===========================================================================
# C3: CtpExecClientConfig + CtpLiveExecutionClient tests
# ===========================================================================


# ---------------------------------------------------------------------------
# B1: CtpExecClientConfig inherits LiveExecClientConfig and is frozen
# ---------------------------------------------------------------------------


class TestCtpExecClientConfig:
    def test_isinstance_live_exec_client_config(self) -> None:
        cfg = CtpExecClientConfig(
            td_front="tcp://180.168.146.187:10130",
            broker_id="9999",
            user_id="test",
            password="test",
        )
        assert isinstance(cfg, LiveExecClientConfig)

    def test_frozen(self) -> None:
        cfg = CtpExecClientConfig(td_front="tcp://1.2.3.4:10130")
        with pytest.raises(AttributeError):
            cfg.td_front = "tcp://other:10130"  # type: ignore[misc]

    def test_fields_accessible(self) -> None:
        cfg = CtpExecClientConfig(
            td_front="tcp://1.2.3.4:10130",
            broker_id="9999",
            user_id="user1",
            password="pw",
            app_id="simnow_client_test",
            auth_code="0000000000000000",
            product_info="test_product",
        )
        assert cfg.td_front == "tcp://1.2.3.4:10130"
        assert cfg.broker_id == "9999"
        assert cfg.user_id == "user1"
        assert cfg.password == "pw"
        assert cfg.app_id == "simnow_client_test"
        assert cfg.auth_code == "0000000000000000"
        assert cfg.product_info == "test_product"

    def test_default_values(self) -> None:
        cfg = CtpExecClientConfig()
        assert cfg.td_front == ""
        assert cfg.broker_id == ""
        assert cfg.app_id == ""
        assert cfg.auth_code == ""
        assert cfg.product_info == ""
        assert isinstance(cfg.instrument_provider, CtpInstrumentProviderConfig)


# ---------------------------------------------------------------------------
# B2: CtpExecClientConfig.to_adapter_config()
# ---------------------------------------------------------------------------


class TestExecConfigToAdapterConfig:
    def test_to_adapter_config_mapping(self) -> None:
        cfg = CtpExecClientConfig(
            td_front="tcp://1.2.3.4:10130",
            broker_id="9999",
            user_id="test_user",
            password="test_pw",
            app_id="simnow_client_test",
            auth_code="0000000000000000",
            product_info="test_product",
        )
        adapter_cfg = cfg.to_adapter_config()
        assert isinstance(adapter_cfg, CtpAdapterConfig)
        assert adapter_cfg.broker_id == "9999"
        assert adapter_cfg.user_id == "test_user"
        assert adapter_cfg.password == "test_pw"
        assert adapter_cfg.td_front == "tcp://1.2.3.4:10130"
        assert adapter_cfg.app_id == "simnow_client_test"
        assert adapter_cfg.auth_code == "0000000000000000"
        assert adapter_cfg.product_info == "test_product"

    def test_to_adapter_config_empty(self) -> None:
        cfg = CtpExecClientConfig()
        adapter_cfg = cfg.to_adapter_config()
        assert adapter_cfg.broker_id == ""
        assert adapter_cfg.td_front == ""


# ---------------------------------------------------------------------------
# B3: CtpLiveExecutionClient inherits LiveExecutionClient
# ---------------------------------------------------------------------------


class TestCtpLiveExecutionClient:
    def test_isinstance_live_execution_client(self) -> None:
        assert issubclass(CtpLiveExecutionClient, LiveExecutionClient)

    def test_connect_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._connect)

    def test_disconnect_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._disconnect)

    def test_submit_order_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._submit_order)

    def test_cancel_order_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._cancel_order)

    def test_cancel_all_orders_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._cancel_all_orders)

    def test_modify_order_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._modify_order)

    def test_submit_order_list_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._submit_order_list)

    def test_batch_cancel_orders_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient._batch_cancel_orders)

    def test_generate_order_status_report_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient.generate_order_status_report)

    def test_generate_order_status_reports_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient.generate_order_status_reports)

    def test_generate_fill_reports_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient.generate_fill_reports)

    def test_generate_position_status_reports_is_coroutine(self) -> None:
        assert asyncio.iscoroutinefunction(CtpLiveExecutionClient.generate_position_status_reports)


# ---------------------------------------------------------------------------
# B4: Execution callback uses call_soon_threadsafe (code-level check)
# ---------------------------------------------------------------------------


class TestExecCallbackBridge:
    def test_on_td_login_uses_call_soon_threadsafe(self) -> None:
        import inspect

        source = inspect.getsource(CtpLiveExecutionClient._on_td_login)
        assert "call_soon_threadsafe" in source

    def test_on_td_exec_event_uses_call_soon_threadsafe(self) -> None:
        import inspect

        source = inspect.getsource(CtpLiveExecutionClient._on_td_exec_event)
        assert "call_soon_threadsafe" in source

    def test_on_td_disconnect_uses_call_soon_threadsafe(self) -> None:
        import inspect

        source = inspect.getsource(CtpLiveExecutionClient._on_td_disconnect)
        assert "call_soon_threadsafe" in source


# ===========================================================================
# C4: Factory + shared InstrumentProvider tests
# ===========================================================================


from nautilus_trader.live.factories import LiveDataClientFactory, LiveExecClientFactory


class TestCtpLiveDataClientFactory:
    def test_isinstance_live_data_client_factory(self) -> None:
        assert issubclass(CtpLiveDataClientFactory, LiveDataClientFactory)

    def test_create_is_static_method(self) -> None:
        assert isinstance(
            CtpLiveDataClientFactory.__dict__["create"],
            staticmethod,
        )


class TestCtpLiveExecClientFactory:
    def test_isinstance_live_exec_client_factory(self) -> None:
        assert issubclass(CtpLiveExecClientFactory, LiveExecClientFactory)

    def test_create_is_static_method(self) -> None:
        assert isinstance(
            CtpLiveExecClientFactory.__dict__["create"],
            staticmethod,
        )


class TestSharedInstrumentProvider:
    def test_same_config_returns_same_provider(self) -> None:
        _CTP_PROVIDERS.clear()
        cfg = CtpInstrumentProviderConfig(
            td_front="tcp://1.2.3.4:10130",
            broker_id="9999",
            user_id="test",
        )
        p1 = get_ctp_instrument_provider(cfg)
        p2 = get_ctp_instrument_provider(cfg)
        assert p1 is p2
        assert isinstance(p1, CtpNautilusInstrumentProvider)

    def test_different_config_returns_different_provider(self) -> None:
        _CTP_PROVIDERS.clear()
        cfg_a = CtpInstrumentProviderConfig(
            td_front="tcp://1.2.3.4:10130",
            broker_id="9999",
            user_id="user_a",
        )
        cfg_b = CtpInstrumentProviderConfig(
            td_front="tcp://1.2.3.4:10130",
            broker_id="9999",
            user_id="user_b",
        )
        p_a = get_ctp_instrument_provider(cfg_a)
        p_b = get_ctp_instrument_provider(cfg_b)
        assert p_a is not p_b

    def test_cache_key_uses_td_front_broker_user(self) -> None:
        _CTP_PROVIDERS.clear()
        cfg = CtpInstrumentProviderConfig(
            td_front="tcp://5.6.7.8:10130",
            broker_id="1234",
            user_id="unique",
        )
        get_ctp_instrument_provider(cfg)
        assert "tcp://5.6.7.8:10130:1234:unique" in _CTP_PROVIDERS

    def test_provider_keeps_ctp_metadata_by_display_symbol(self) -> None:
        provider = CtpNautilusInstrumentProvider()
        instrument = NormalizedCtpInstrument(
            raw_symbol="rb2610",
            raw_exchange_id="SHFE",
            venue_symbol="rb2610",
            exchange_id="SHFE",
            display_symbol="rb2610.SHFE",
            underlying="rb",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="rebar test",
            price_tick=1.0,
            volume_multiple=10,
        )

        provider.add_ctp_metadata(instrument)

        assert provider.ctp_metadata("rb2610.SHFE") == instrument
        assert provider.ctp_metadata("rb2610") == instrument
        assert provider.ctp_metadata("missing.SHFE") is None
        assert provider.count == 0  # metadata staging must not fabricate a Nautilus Instrument

    def test_provider_hydrates_futures_contract_from_ctp_metadata(self) -> None:
        provider = CtpNautilusInstrumentProvider()
        instrument = NormalizedCtpInstrument(
            raw_symbol="rb2610",
            raw_exchange_id="SHFE",
            venue_symbol="rb2610",
            exchange_id="SHFE",
            display_symbol="rb2610.SHFE",
            underlying="rb",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="rebar test",
            price_tick=1.0,
            volume_multiple=10,
        )

        hydrated_ids = provider.hydrate_ctp_metadata((instrument,))

        assert [instrument_id.value for instrument_id in hydrated_ids] == ["rb2610.SHFE"]
        assert provider.count == 1
        loaded = provider.list_all()[0]
        assert loaded.id.value == "rb2610.SHFE"
        assert loaded.raw_symbol.value == "rb2610"
        assert str(loaded.price_increment) == "1"
        assert str(loaded.multiplier) == "10"

    def test_provider_does_not_hydrate_incomplete_ctp_metadata(self) -> None:
        provider = CtpNautilusInstrumentProvider()
        incomplete = NormalizedCtpInstrument(
            raw_symbol="bad2610",
            raw_exchange_id="SHFE",
            venue_symbol="bad2610",
            exchange_id="SHFE",
            display_symbol="bad2610.SHFE",
            underlying="bad",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="bad test",
            price_tick=None,
            volume_multiple=10,
        )

        hydrated_ids = provider.hydrate_ctp_metadata((incomplete,))

        assert hydrated_ids == ()
        assert provider.count == 0
        assert provider.ctp_metadata("bad2610.SHFE") == incomplete

    def test_tick_instrument_id_uses_ctp_provider_metadata(self) -> None:
        provider = CtpNautilusInstrumentProvider()
        instrument = NormalizedCtpInstrument(
            raw_symbol="rb2610",
            raw_exchange_id="SHFE",
            venue_symbol="rb2610",
            exchange_id="SHFE",
            display_symbol="rb2610.SHFE",
            underlying="rb",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="rebar test",
            price_tick=1.0,
            volume_multiple=10,
        )
        provider.hydrate_ctp_metadata((instrument,))

        instrument_id = resolve_ctp_tick_instrument_id(provider, "rb2610")

        assert instrument_id.value == "rb2610.SHFE"

    def test_tick_instrument_id_falls_back_to_ctp_when_metadata_missing(self) -> None:
        provider = CtpNautilusInstrumentProvider()

        instrument_id = resolve_ctp_tick_instrument_id(provider, "rb2610")

        assert instrument_id is None

    def test_tick_resolution_reuses_hydrated_provider_instrument(self) -> None:
        class EmptyCache:
            def instrument(self, instrument_id):
                return None

        provider = CtpNautilusInstrumentProvider()
        instrument = NormalizedCtpInstrument(
            raw_symbol="rb2610",
            raw_exchange_id="SHFE",
            venue_symbol="rb2610",
            exchange_id="SHFE",
            display_symbol="rb2610.SHFE",
            underlying="rb",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="rebar test",
            price_tick=1.0,
            volume_multiple=10,
        )
        provider.hydrate_ctp_metadata((instrument,))

        resolution = resolve_ctp_tick_instrument(
            cache=EmptyCache(),
            instrument_provider=provider,
            symbol="rb2610",
        )

        assert resolution.instrument_id is not None
        assert resolution.instrument_id.value == "rb2610.SHFE"
        assert resolution.instrument is provider.find(resolution.instrument_id)
        assert resolution.diagnostic is None

    def test_tick_resolution_reports_missing_metadata_without_fabricating_ctp_id(self) -> None:
        class EmptyCache:
            def instrument(self, instrument_id):
                raise AssertionError("cache must not be queried without CTP metadata")

        provider = CtpNautilusInstrumentProvider()

        resolution = resolve_ctp_tick_instrument(
            cache=EmptyCache(),
            instrument_provider=provider,
            symbol="rb2610",
        )

        assert resolution.instrument_id is None
        assert resolution.instrument is None
        assert resolution.diagnostic == "ctp_metadata_missing"

    def test_tick_resolution_reports_metadata_not_hydrated(self) -> None:
        class EmptyCache:
            def instrument(self, instrument_id):
                return None

        provider = CtpNautilusInstrumentProvider()
        instrument = NormalizedCtpInstrument(
            raw_symbol="bad2610",
            raw_exchange_id="SHFE",
            venue_symbol="bad2610",
            exchange_id="SHFE",
            display_symbol="bad2610.SHFE",
            underlying="bad",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="bad test",
            price_tick=None,
            volume_multiple=10,
        )
        provider.add_ctp_metadata(instrument)

        resolution = resolve_ctp_tick_instrument(
            cache=EmptyCache(),
            instrument_provider=provider,
            symbol="bad2610",
        )

        assert resolution.instrument_id is not None
        assert resolution.instrument_id.value == "bad2610.SHFE"
        assert resolution.instrument is None
        assert resolution.diagnostic == "instrument_not_hydrated"

    def test_provider_backed_subscription_symbols_filters_unknown_symbols(self) -> None:
        provider = CtpNautilusInstrumentProvider()
        instrument = NormalizedCtpInstrument(
            raw_symbol="rb2610",
            raw_exchange_id="SHFE",
            venue_symbol="rb2610",
            exchange_id="SHFE",
            display_symbol="rb2610.SHFE",
            underlying="rb",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="rebar test",
            price_tick=1.0,
            volume_multiple=10,
        )
        provider.add_ctp_metadata(instrument)

        symbols = provider_backed_subscription_symbols(provider, {"missing", "rb2610"})

        assert symbols == ("rb2610",)


class TestCtpNautilusExecutionReports:
    def _provider_with_rb(self) -> CtpNautilusInstrumentProvider:
        provider = CtpNautilusInstrumentProvider()
        instrument = NormalizedCtpInstrument(
            raw_symbol="rb2610",
            raw_exchange_id="SHFE",
            venue_symbol="rb2610",
            exchange_id="SHFE",
            display_symbol="rb2610.SHFE",
            underlying="rb",
            contract_month="2610",
            product_kind=CtpProductKind.FUTURES,
            instrument_name="rebar test",
            price_tick=1.0,
            volume_multiple=10,
        )
        provider.hydrate_ctp_metadata((instrument,))
        return provider

    def test_order_callback_payload_maps_to_order_status_report(self) -> None:
        payload = CtpTdExecEventPayload(
            order_id="SYS-1",
            venue_symbol="rb2610",
            order_ref="42",
            front_id=1,
            session_id=2,
            status=0,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            leaves_qty=1,
            error_message="",
        )

        report = ctp_exec_event_to_order_status_report(
            payload,
            account_id="CTP-TEST",
            instrument_provider=self._provider_with_rb(),
            ts_init=123,
        )

        assert report is not None
        assert report.instrument_id.value == "rb2610.SHFE"
        assert report.venue_order_id.value == "SYS-1"
        assert report.order_status == OrderStatus.ACCEPTED
        assert str(report.quantity) == "1"
        assert str(report.filled_qty) == "0"

    def test_trade_callback_payload_maps_to_fill_report(self) -> None:
        payload = CtpTdExecEventPayload(
            order_id="TRADE-1",
            venue_symbol="rb2610",
            order_ref="42",
            front_id=1,
            session_id=2,
            status=0,
            is_trade=True,
            trade_price=3550.0,
            trade_volume=2,
            leaves_qty=0,
            error_message="",
        )

        report = ctp_exec_event_to_fill_report(
            payload,
            account_id="CTP-TEST",
            instrument_provider=self._provider_with_rb(),
            ts_init=456,
        )

        assert report is not None
        assert report.instrument_id.value == "rb2610.SHFE"
        assert report.venue_order_id.value == "TRADE-1"
        assert report.trade_id.value == "TRADE-1"
        assert str(report.last_qty) == "2"
        assert str(report.last_px) == "3550.0"

    def test_cancel_callback_payload_maps_to_canceled_order_status_report(self) -> None:
        payload = CtpTdExecEventPayload(
            order_id="SYS-CANCEL",
            venue_symbol="rb2610",
            order_ref="42",
            front_id=1,
            session_id=2,
            status=53,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            leaves_qty=0,
            error_message="",
        )

        report = ctp_exec_event_to_order_status_report(
            payload,
            account_id="CTP-TEST",
            instrument_provider=self._provider_with_rb(),
            ts_init=456,
        )

        assert report is not None
        assert report.order_status == OrderStatus.CANCELED

    def test_position_record_maps_to_position_status_report(self) -> None:
        record = CtpPositionRecord(
            venue_symbol="rb2610",
            exchange_id="SHFE",
            direction="2",
            position_qty=4,
            yd_position_qty=1,
            td_position_qty=3,
            position_cost=125580.0,
        )

        report = ctp_position_record_to_status_report(
            record,
            account_id="CTP-TEST",
            instrument_provider=self._provider_with_rb(),
            ts_init=789,
        )

        assert report is not None
        assert report.instrument_id.value == "rb2610.SHFE"
        assert report.position_side == PositionSide.LONG
        assert str(report.quantity) == "4"

    def test_account_record_maps_to_account_state(self) -> None:
        record = CtpAccountRecord(
            account_id="CTP-TEST",
            balance=10000000.0,
            available=9991206.76,
            margin=8790.6,
            commission=2.64,
            close_profit=0.0,
            position_profit=0.0,
        )

        state = ctp_account_record_to_account_state(record, ts_init=999)

        assert isinstance(state, AccountState)
        assert state.account_id.value == "CTP-TEST"
        assert state.is_reported is True
        assert str(state.balances[0].total) == "10000000.00 CNY"
        assert str(state.balances[0].free) == "9991206.76 CNY"
        assert str(state.margins[0].initial) == "8790.60 CNY"

    def test_report_generation_apis_return_cached_ctp_reports(self) -> None:
        provider = self._provider_with_rb()
        order_payload = CtpTdExecEventPayload(
            order_id="SYS-1",
            venue_symbol="rb2610",
            order_ref="42",
            front_id=1,
            session_id=2,
            status=0,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            leaves_qty=1,
            error_message="",
        )
        trade_payload = CtpTdExecEventPayload(
            order_id="TRADE-1",
            venue_symbol="rb2610",
            order_ref="42",
            front_id=1,
            session_id=2,
            status=0,
            is_trade=True,
            trade_price=3550.0,
            trade_volume=2,
            leaves_qty=0,
            error_message="",
        )
        position_record = CtpPositionRecord(
            venue_symbol="rb2610",
            exchange_id="SHFE",
            direction="2",
            position_qty=4,
            yd_position_qty=1,
            td_position_qty=3,
            position_cost=125580.0,
        )
        order_report = ctp_exec_event_to_order_status_report(
            order_payload,
            account_id="CTP-TEST",
            instrument_provider=provider,
            ts_init=123,
        )
        fill_report = ctp_exec_event_to_fill_report(
            trade_payload,
            account_id="CTP-TEST",
            instrument_provider=provider,
            ts_init=456,
        )
        position_report = ctp_position_record_to_status_report(
            position_record,
            account_id="CTP-TEST",
            instrument_provider=provider,
            ts_init=789,
        )
        fake_client = SimpleNamespace(
            _order_status_reports=[order_report],
            _fill_reports=[fill_report],
            _position_status_reports=[position_report],
        )
        instrument_id = InstrumentId.from_str("rb2610.SHFE")

        one_order = asyncio.run(
            CtpLiveExecutionClient.generate_order_status_report(
                fake_client,
                GenerateOrderStatusReport(
                    instrument_id=instrument_id,
                    client_order_id=None,
                    venue_order_id=VenueOrderId("SYS-1"),
                    command_id=UUID4(),
                    ts_init=1,
                ),
            )
        )
        order_reports = asyncio.run(
            CtpLiveExecutionClient.generate_order_status_reports(
                fake_client,
                GenerateOrderStatusReports(
                    instrument_id=instrument_id,
                    start=None,
                    end=None,
                    open_only=True,
                    command_id=UUID4(),
                    ts_init=1,
                ),
            )
        )
        fill_reports = asyncio.run(
            CtpLiveExecutionClient.generate_fill_reports(
                fake_client,
                GenerateFillReports(
                    instrument_id=instrument_id,
                    venue_order_id=VenueOrderId("TRADE-1"),
                    start=None,
                    end=None,
                    command_id=UUID4(),
                    ts_init=1,
                ),
            )
        )
        position_reports = asyncio.run(
            CtpLiveExecutionClient.generate_position_status_reports(
                fake_client,
                GeneratePositionStatusReports(
                    instrument_id=instrument_id,
                    start=None,
                    end=None,
                    command_id=UUID4(),
                    ts_init=1,
                ),
            )
        )

        assert one_order is order_report
        assert order_reports == [order_report]
        assert fill_reports == [fill_report]
        assert position_reports == [position_report]

    def test_duplicate_order_callback_is_idempotent(self) -> None:
        payload = CtpTdExecEventPayload(
            order_id="SYS-1",
            venue_symbol="rb2610",
            order_ref="42",
            front_id=1,
            session_id=2,
            status=5,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            leaves_qty=0,
            error_message="",
        )
        fake_client = SimpleNamespace(
            _clock=SimpleNamespace(timestamp_ns=lambda: 123),
            _order_status_reports=[],
            _fill_reports=[],
            _seen_exec_report_keys=set(),
            _log=SimpleNamespace(debug=lambda *_args, **_kwargs: None),
            instrument_provider=self._provider_with_rb(),
            _report_account_id=lambda: "CTP-TEST",
            _coerce_exec_payload=CtpLiveExecutionClient._coerce_exec_payload,
            _exec_report_key=CtpLiveExecutionClient._exec_report_key,
        )

        CtpLiveExecutionClient._handle_td_exec_event(fake_client, payload)
        CtpLiveExecutionClient._handle_td_exec_event(fake_client, payload)

        assert len(fake_client._order_status_reports) == 1
        assert not fake_client._fill_reports

    def test_minimal_engine_harness_uses_provider_entrypoint_and_reports(self) -> None:
        payload = engine_harness.build_engine_harness_payload(run_id="test-engine-harness")

        assert payload["success"] is True
        assert payload["provider_entrypoint"] == "CtpLiveExecutionClient"
        assert payload["script_only_smoke"] is False
        assert payload["paper_send_armed"] is False
        assert payload["instrument_provider"]["loaded"] is True
        assert payload["reports"]["accepted_count"] == 1
        assert payload["reports"]["canceled_count"] == 1
        assert payload["reports"]["rejected_count"] == 1
        assert payload["reports"]["fill_count"] == 1
        assert payload["reports"]["duplicate_fill_ignored"] is True
        assert payload["reports"]["position_count"] == 1
        assert payload["reports"]["account_state_reported"] is True
        assert payload["reports"]["account_id_redacted"] is True


class TestCtpClosePositionSemantics:
    def test_close_long_position_maps_to_sell_close_today_for_shfe_today_bucket(self) -> None:
        client = CtpExecutionClient()
        intent = client.build_close_position_intent(
            instrument_id="rb2610",
            exchange_id="SHFE",
            direction="LONG",
            position_qty=3,
            td_position_qty=2,
            yd_position_qty=1,
            close_quantity=2,
            requested_position_effect="CLOSE",
            limit_price=3550.0,
            client_order_id="close-1",
        )

        assert intent.error is None
        assert intent.submit_intent is not None
        assert intent.submit_intent.side == "SELL"
        assert intent.submit_intent.position_effect == "CLOSETODAY"
        assert intent.selected_bucket == "today"

    def test_close_short_position_maps_to_buy_close_yesterday_for_shfe_yesterday_bucket(self) -> None:
        client = CtpExecutionClient()
        intent = client.build_close_position_intent(
            instrument_id="rb2610",
            exchange_id="SHFE",
            direction="SHORT",
            position_qty=4,
            td_position_qty=0,
            yd_position_qty=4,
            close_quantity=3,
            requested_position_effect="CLOSEYESTERDAY",
            limit_price=3550.0,
            client_order_id="close-2",
        )

        assert intent.error is None
        assert intent.submit_intent is not None
        assert intent.submit_intent.side == "BUY"
        assert intent.submit_intent.position_effect == "CLOSEYESTERDAY"
        assert intent.selected_bucket == "yesterday"

    def test_shfe_generic_close_blocks_when_quantity_spans_today_and_yesterday(self) -> None:
        client = CtpExecutionClient()
        intent = client.build_close_position_intent(
            instrument_id="rb2610",
            exchange_id="SHFE",
            direction="LONG",
            position_qty=4,
            td_position_qty=2,
            yd_position_qty=2,
            close_quantity=3,
            requested_position_effect="CLOSE",
            limit_price=3550.0,
            client_order_id="close-3",
        )

        assert intent.submit_intent is None
        assert intent.error is not None
        assert intent.error.error_id == 9010
        assert "close_split_required" in intent.error.error_message

    def test_non_shfe_generic_close_keeps_close_offset_when_position_is_available(self) -> None:
        client = CtpExecutionClient()
        intent = client.build_close_position_intent(
            instrument_id="c2609",
            exchange_id="DCE",
            direction="SHORT",
            position_qty=3,
            td_position_qty=1,
            yd_position_qty=2,
            close_quantity=3,
            requested_position_effect="CLOSE",
            limit_price=2300.0,
            client_order_id="close-4",
        )

        assert intent.error is None
        assert intent.submit_intent is not None
        assert intent.submit_intent.side == "BUY"
        assert intent.submit_intent.position_effect == "CLOSE"
        assert intent.selected_bucket == "generic"

    def test_close_preflight_blocks_no_position_and_insufficient_position(self) -> None:
        client = CtpExecutionClient()

        no_position = client.build_close_position_intent(
            instrument_id="c2609",
            exchange_id="DCE",
            direction="SHORT",
            position_qty=0,
            td_position_qty=0,
            yd_position_qty=0,
            close_quantity=1,
            requested_position_effect="CLOSE",
            limit_price=2300.0,
            client_order_id="close-5",
        )
        insufficient = client.build_close_position_intent(
            instrument_id="c2609",
            exchange_id="DCE",
            direction="SHORT",
            position_qty=1,
            td_position_qty=0,
            yd_position_qty=1,
            close_quantity=2,
            requested_position_effect="CLOSE",
            limit_price=2300.0,
            client_order_id="close-6",
        )

        assert no_position.submit_intent is None
        assert no_position.error is not None
        assert "no_closable_position" in no_position.error.error_message
        assert insufficient.submit_intent is None
        assert insufficient.error is not None
        assert "insufficient_closable_position" in insufficient.error.error_message

    def test_close_preflight_caps_closable_quantity_to_current_position_qty(self) -> None:
        client = CtpExecutionClient()

        intent = client.build_close_position_intent(
            instrument_id="c2609",
            exchange_id="DCE",
            direction="SHORT",
            position_qty=2,
            td_position_qty=0,
            yd_position_qty=3,
            close_quantity=3,
            requested_position_effect="CLOSE",
            limit_price=2300.0,
            client_order_id="close-7",
        )

        assert intent.submit_intent is None
        assert intent.error is not None
        assert "insufficient_closable_position" in intent.error.error_message
        assert intent.closable_quantity == 2

    def test_native_offset_mapping_supports_close_variants_without_fallback(self) -> None:
        client = CtpExecutionClient()

        assert client._native_comb_offset_value("OPEN") == "0"
        assert client._native_comb_offset_value("CLOSE") == "1"
        assert client._native_comb_offset_value("CLOSETODAY") == "3"
        assert client._native_comb_offset_value("CLOSEYESTERDAY") == "4"
        with pytest.raises(ValueError, match="Unsupported position_effect"):
            client._native_comb_offset_value("FORCE_CLOSE")

    def test_native_offset_mapping_matches_vendor_ctp_constants(self) -> None:
        client = CtpExecutionClient()
        header = (
            Path(__file__).resolve().parents[1]
            / "vendor"
            / "ctp"
            / "sdk"
            / "ThostFtdcUserApiDataType.h"
        )
        text = header.read_bytes().decode("ascii", errors="ignore")

        constants = dict(
            re.findall(r"#define\s+(THOST_FTDC_OF_\w+)\s+'([^']+)'", text)
        )

        assert constants["THOST_FTDC_OF_Open"] == "0"
        assert constants["THOST_FTDC_OF_Close"] == "1"
        assert constants["THOST_FTDC_OF_CloseToday"] == "3"
        assert constants["THOST_FTDC_OF_CloseYesterday"] == "4"
        assert client._native_comb_offset_value("OPEN") == constants["THOST_FTDC_OF_Open"]
        assert client._native_comb_offset_value("CLOSE") == constants["THOST_FTDC_OF_Close"]
        assert client._native_comb_offset_value("CLOSETODAY") == constants["THOST_FTDC_OF_CloseToday"]
        assert client._native_comb_offset_value("CLOSEYESTERDAY") == constants["THOST_FTDC_OF_CloseYesterday"]

    def test_submit_payload_carries_native_offset_request_field_provenance(self) -> None:
        client = CtpExecutionClient()
        client._td_session_identity = CtpTdSessionIdentity(
            front_id=1,
            session_id=2,
            max_order_ref=100,
        )
        intent = CtpSubmitOrderIntent(
            instrument_id="rb2610",
            side="SELL",
            quantity=1,
            limit_price=3162.0,
            position_effect="CLOSETODAY",
            client_order_id="request-offset-trace",
        )

        mapped = client.map_submit_order(intent)

        assert mapped.command is not None
        payload = mapped.command.payload
        assert payload["position_effect"] == "CLOSETODAY"
        assert payload["native_comb_offset"] == "3"
        assert (
            payload["native_comb_offset_source_field"]
            == "CtpExecutionClient._native_comb_offset_value(position_effect)"
            " -> TdOrderSend.comb_offset"
            " -> CThostFtdcInputOrderField.CombOffsetFlag[0]"
        )
        assert payload["native_comb_offset_expected_from_position_effect"] == "3"
        assert mapped.command.request_id == "submit-1"
        assert payload["submit_request_id"] == "1"
        assert (
            payload["submit_request_id_source_field"]
            == "CtpRuntimeCommand.request_id"
            " -> TdOrderSend.request_id"
            " -> CTP ReqOrderInsert nRequestID"
        )

    def test_exec_callback_payload_preserves_native_error_msg_for_reject_classification(self) -> None:
        client = CtpExecutionClient()
        exec_view = NativeExecView(
            order_id="SYS-ERR",
            symbol="c2609",
            price=999999.0,
            qty=1,
            side=1,
            status=97,
            ts_epoch_us=123,
            order_ref="2",
            front_id=1,
            session_id=-1,
            direction=1,
            offset_flag=0,
            hedge_flag=1,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            error_msg="price rejected",
            leaves_qty=1,
            callback_source="OnRspOrderInsert",
        )

        client._on_td_exec_callback(exec_view, client_order_id="client-reject")
        events = client.runtime_bridge.drain_events()

        assert events[-1].message == "price rejected"
        assert events[-1].payload["error_msg"] == "price rejected"
        assert events[-1].payload["callback_source"] == "OnRspOrderInsert"

    def test_exec_callback_preserves_native_submit_offset_boundary(self) -> None:
        client = CtpExecutionClient()
        exec_view = NativeExecView(
            order_id="2",
            symbol="rb2610",
            price=3162.0,
            qty=1,
            side=1,
            status=53,
            ts_epoch_us=123,
            order_ref="2",
            front_id=1,
            session_id=-1,
            direction=1,
            offset_flag=1,
            hedge_flag=1,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            error_msg="持仓不足",
            leaves_qty=1,
            callback_source="OnRspOrderInsert",
            submit_request_offset_flag=3,
            submit_request_offset_source=(
                "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
            ),
            response_request_id=42,
            response_is_last=True,
            response_error_id=31,
        )

        client._on_td_exec_callback(exec_view, client_order_id="client-close-today")
        events = client.runtime_bridge.drain_events()

        assert events[-1].payload["offset_flag"] == "1"
        assert events[-1].payload["submit_request_offset_flag"] == "3"
        assert (
            events[-1].payload["submit_request_offset_source"]
            == "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
        )
        assert events[-1].payload["response_request_id"] == "42"
        assert events[-1].payload["response_is_last"] == "1"
        assert events[-1].payload["response_error_id"] == "31"

    def test_exec_callback_projection_must_succeed_before_match_is_counted(self, monkeypatch) -> None:
        client = CtpExecutionClient()
        exec_view = NativeExecView(
            order_id="2",
            symbol="rb2610",
            price=3172.0,
            qty=1,
            side=1,
            status=53,
            ts_epoch_us=123,
            order_ref="2",
            front_id=1,
            session_id=1334838132,
            direction=1,
            offset_flag=1,
            hedge_flag=1,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            error_msg="",
            leaves_qty=1,
            callback_source="OnRtnOrder",
            submit_request_offset_flag=3,
            submit_request_offset_source=(
                "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
            ),
            response_request_id=42,
            response_is_last=True,
            response_error_id=31,
        )
        state = {
            "login": None,
            "disconnects": [],
            "exec_views": [],
            "matched_exec_views": [],
            "matched_exec_events": [],
            "pre_send_exec_view_count": 0,
            "expected_client_order_id": "p077-t6-rb2610-fresh-close1-064825",
            "expected_order_ref": "2",
            "expected_instrument_id": "rb2610",
            "expected_quantity": 1,
            "expected_submit_request_id": "42",
            "expected_submit_request_id_source": (
                "CtpRuntimeCommand.request_id"
                " -> TdOrderSend.request_id"
                " -> CTP ReqOrderInsert nRequestID"
            ),
        }

        def fail_projection(*_args, **_kwargs):
            raise AttributeError("projection failed")

        monkeypatch.setattr(client, "_on_td_exec_callback", fail_projection)

        with pytest.raises(AttributeError, match="projection failed"):
            client._on_td_exec_callback_with_state(exec_view, state)

        assert state["exec_views"] == [exec_view]
        assert state["matched_exec_views"] == []
        assert state["matched_exec_events"] == []

    def test_exec_callback_match_summary_preserves_callback_and_offset_provenance(self) -> None:
        client = CtpExecutionClient()
        exec_view = NativeExecView(
            order_id="2",
            symbol="rb2610",
            price=3172.0,
            qty=1,
            side=1,
            status=53,
            ts_epoch_us=123,
            order_ref="2",
            front_id=1,
            session_id=1334838132,
            direction=1,
            offset_flag=1,
            hedge_flag=1,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            error_msg="",
            leaves_qty=1,
            callback_source="OnRtnOrder",
            submit_request_offset_flag=3,
            submit_request_offset_source=(
                "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
            ),
            response_request_id=42,
            response_is_last=True,
            response_error_id=31,
        )
        state = {
            "login": None,
            "disconnects": [],
            "exec_views": [],
            "matched_exec_views": [],
            "matched_exec_events": [],
            "pre_send_exec_view_count": 0,
            "expected_client_order_id": "p077-t6-rb2610-fresh-close1-064825",
            "expected_order_ref": "2",
            "expected_instrument_id": "rb2610",
            "expected_quantity": 1,
        }

        client._on_td_exec_callback_with_state(exec_view, state)

        matched_event = state["matched_exec_events"][0]
        assert matched_event.python_client_order_id == "p077-t6-rb2610-fresh-close1-064825"
        assert matched_event.callback_source == "OnRtnOrder"
        assert matched_event.offset_flag == 1
        assert matched_event.submit_request_offset_flag == 3
        assert (
            matched_event.submit_request_offset_source
            == "repo_ctp_td_order_send.CThostFtdcInputOrderField.CombOffsetFlag[0]"
        )
        assert matched_event.submit_request_id == 42
        assert (
            matched_event.submit_request_id_source
            == "CtpRuntimeCommand.request_id"
            " -> TdOrderSend.request_id"
            " -> CTP ReqOrderInsert nRequestID"
        )
        assert matched_event.response_request_id == 42
        assert matched_event.response_is_last is True
        assert matched_event.response_error_id == 31


class TestCtpOrderTypeAndPriceBoundary:
    def test_native_time_and_volume_condition_map_fak_and_fok_without_downgrade(self) -> None:
        client = CtpExecutionClient()

        assert client._native_order_type_value("LIMIT") == 0
        assert client._native_time_condition_value("FAK") == 1
        assert client._native_volume_condition_value("FAK") == 1
        assert client._native_time_condition_value("FOK") == 1
        assert client._native_volume_condition_value("FOK") == 3

    def test_submit_mapping_rejects_unsupported_order_type_before_command(self) -> None:
        client = CtpExecutionClient()

        class LoginResponse:
            success = True
            error_id = 0
            error_message = ""
            front_id = 1
            session_id = 2
            max_order_ref = 1

        client._on_td_login_callback(LoginResponse(), {"disconnects": []})
        mapped = client.map_submit_order(
            CtpSubmitOrderIntent(
                instrument_id="c2609",
                side="BUY",
                quantity=1,
                limit_price=2300.0,
                order_type="STOP_LIMIT",
                client_order_id="bad-order-type",
            )
        )

        assert mapped.command is None
        assert mapped.error is not None
        assert mapped.error.error_id == 9004
        assert "unsupported_order_type" in mapped.error.error_message

    def test_submit_mapping_rejects_unsupported_time_in_force_before_command(self) -> None:
        client = CtpExecutionClient()

        class LoginResponse:
            success = True
            error_id = 0
            error_message = ""
            front_id = 1
            session_id = 2
            max_order_ref = 1

        client._on_td_login_callback(LoginResponse(), {"disconnects": []})
        mapped = client.map_submit_order(
            CtpSubmitOrderIntent(
                instrument_id="c2609",
                side="BUY",
                quantity=1,
                limit_price=2300.0,
                time_in_force="GTC",
                client_order_id="bad-tif",
            )
        )

        assert mapped.command is None
        assert mapped.error is not None
        assert mapped.error.error_id == 9004
        assert "unsupported_time_in_force" in mapped.error.error_message


# ===========================================================================
# C5: E2E TradingNode registration smoke tests
# ===========================================================================


class TestTradingNodeRegistration:
    """Verify that CTP factories can be registered with TradingNode config."""

    def test_data_client_factory_create_signature_matches(self) -> None:
        """Factory.create has the expected parameter names."""
        import inspect

        sig = inspect.signature(CtpLiveDataClientFactory.create)
        param_names = list(sig.parameters.keys())
        assert param_names == ["loop", "name", "config", "msgbus", "cache", "clock"]

    def test_exec_client_factory_create_signature_matches(self) -> None:
        import inspect

        sig = inspect.signature(CtpLiveExecClientFactory.create)
        param_names = list(sig.parameters.keys())
        assert param_names == ["loop", "name", "config", "msgbus", "cache", "clock"]

    def test_data_config_can_be_serialized_roundtrip(self) -> None:
        """CtpDataClientConfig supports Nautilus json() / parse() roundtrip."""
        cfg = CtpDataClientConfig(
            md_front="tcp://1.2.3.4:10131",
            broker_id="9999",
            user_id="test",
            password="pw",
            subscribe_symbols=["rb2610"],
        )
        json_bytes = cfg.json()
        restored = CtpDataClientConfig.parse(json_bytes)
        assert restored.md_front == cfg.md_front
        assert restored.broker_id == cfg.broker_id
        assert restored.subscribe_symbols == cfg.subscribe_symbols

    def test_exec_config_can_be_serialized_roundtrip(self) -> None:
        """CtpExecClientConfig supports Nautilus json() / parse() roundtrip."""
        cfg = CtpExecClientConfig(
            td_front="tcp://1.2.3.4:10130",
            broker_id="9999",
            user_id="test",
            password="pw",
            app_id="simnow_client_test",
            auth_code="0000000000000000",
        )
        json_bytes = cfg.json()
        restored = CtpExecClientConfig.parse(json_bytes)
        assert restored.td_front == cfg.td_front
        assert restored.app_id == cfg.app_id

    def test_all_nautilus_exports_importable(self) -> None:
        """All Nautilus integration classes are importable from the package."""
        from nautilus_ctp_adapter.adapters.ctp import (
            CtpDataClientConfig,
            CtpExecClientConfig,
            CtpInstrumentProviderConfig,
            CtpLiveDataClient,
            CtpLiveExecutionClient,
            CtpLiveDataClientFactory,
            CtpLiveExecClientFactory,
            get_ctp_instrument_provider,
        )
        assert CtpDataClientConfig is not None
        assert CtpExecClientConfig is not None
        assert CtpInstrumentProviderConfig is not None
        assert CtpLiveDataClient is not None
        assert CtpLiveExecutionClient is not None
        assert CtpLiveDataClientFactory is not None
        assert CtpLiveExecClientFactory is not None
        assert get_ctp_instrument_provider is not None

    def test_trading_node_config_import(self) -> None:
        """TradingNode and TradingNodeConfig are importable."""
        from nautilus_trader.live.node import TradingNode
        from nautilus_trader.config import TradingNodeConfig
        assert TradingNode is not None
        assert TradingNodeConfig is not None
