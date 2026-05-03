"""Unit tests for Nautilus-compatible CTP data/execution client and config."""

from __future__ import annotations

import asyncio

import pytest

from nautilus_trader.config import LiveDataClientConfig, LiveExecClientConfig, InstrumentProviderConfig
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.live.execution_client import LiveExecutionClient

from nautilus_ctp_adapter.adapters.ctp.nautilus_config import (
    CtpDataClientConfig,
    CtpExecClientConfig,
    CtpInstrumentProviderConfig,
)
from nautilus_ctp_adapter.adapters.ctp.nautilus_data import CtpLiveDataClient
from nautilus_ctp_adapter.adapters.ctp.nautilus_execution import CtpLiveExecutionClient
from nautilus_ctp_adapter.adapters.ctp.nautilus_factories import (
    CtpLiveDataClientFactory,
    CtpLiveExecClientFactory,
    get_ctp_instrument_provider,
    _CTP_PROVIDERS,
)
from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig


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
