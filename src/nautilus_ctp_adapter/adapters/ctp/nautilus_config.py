"""Nautilus-compatible CTP configuration classes.

Bridges between Nautilus TradingNode config system (msgspec frozen Struct)
and standalone CtpAdapterConfig (dataclass).
"""

from __future__ import annotations

from nautilus_trader.config import InstrumentProviderConfig, LiveDataClientConfig, LiveExecClientConfig

from .config import CtpAdapterConfig


class CtpInstrumentProviderConfig(InstrumentProviderConfig, frozen=True):
    """Configuration for CTP instrument provider within Nautilus."""

    td_front: str = ""
    broker_id: str = ""
    user_id: str = ""
    password: str = ""
    app_id: str = ""
    auth_code: str = ""
    load_contracts_on_start: bool = True
    contract_filter: list[str] = []


class CtpDataClientConfig(LiveDataClientConfig, frozen=True):
    """CTP market data client configuration for Nautilus TradingNode."""

    md_front: str = ""
    broker_id: str = ""
    user_id: str = ""
    password: str = ""
    subscribe_symbols: list[str] = []
    instrument_provider: CtpInstrumentProviderConfig = CtpInstrumentProviderConfig()

    def to_adapter_config(self) -> CtpAdapterConfig:
        """Convert to standalone CtpAdapterConfig for inner client delegation."""
        return CtpAdapterConfig(
            broker_id=self.broker_id,
            user_id=self.user_id,
            password=self.password,
            md_front=self.md_front,
            instruments=list(self.subscribe_symbols),
        )


class CtpExecClientConfig(LiveExecClientConfig, frozen=True):
    """CTP execution client configuration for Nautilus TradingNode."""

    td_front: str = ""
    broker_id: str = ""
    user_id: str = ""
    password: str = ""
    app_id: str = ""
    auth_code: str = ""
    product_info: str = ""
    instrument_provider: CtpInstrumentProviderConfig = CtpInstrumentProviderConfig()

    def to_adapter_config(self) -> CtpAdapterConfig:
        """Convert to standalone CtpAdapterConfig for inner client delegation."""
        return CtpAdapterConfig(
            broker_id=self.broker_id,
            user_id=self.user_id,
            password=self.password,
            td_front=self.td_front,
            app_id=self.app_id,
            auth_code=self.auth_code,
            product_info=self.product_info,
        )
