"""Nautilus-compatible CTP factory classes.

Provides LiveDataClientFactory and LiveExecClientFactory implementations
for registering CTP adapters with a Nautilus TradingNode.
"""

from __future__ import annotations

import asyncio

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock, MessageBus
from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.live.factories import LiveDataClientFactory, LiveExecClientFactory

from .nautilus_config import (
    CtpDataClientConfig,
    CtpExecClientConfig,
    CtpInstrumentProviderConfig,
)
from .nautilus_data import CtpLiveDataClient
from .nautilus_execution import CtpLiveExecutionClient

# Module-level cache for shared InstrumentProvider instances.
# Key: "{td_front}:{broker_id}:{user_id}"
_CTP_PROVIDERS: dict[str, InstrumentProvider] = {}


def get_ctp_instrument_provider(
    config: CtpInstrumentProviderConfig,
) -> InstrumentProvider:
    """Return a cached InstrumentProvider for the given CTP config.

    Uses td_front:broker_id:user_id as the cache key so that
    DataClient and ExecClient factories share the same provider instance.
    """
    key = f"{config.td_front}:{config.broker_id}:{config.user_id}"
    if key not in _CTP_PROVIDERS:
        _CTP_PROVIDERS[key] = InstrumentProvider()
    return _CTP_PROVIDERS[key]


class CtpLiveDataClientFactory(LiveDataClientFactory):
    """Factory for creating CTP live data clients within a TradingNode."""

    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config: CtpDataClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> LiveMarketDataClient:
        provider = get_ctp_instrument_provider(config.instrument_provider)
        return CtpLiveDataClient(
            loop=loop,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=config,
        )


class CtpLiveExecClientFactory(LiveExecClientFactory):
    """Factory for creating CTP live execution clients within a TradingNode."""

    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config: CtpExecClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> LiveExecutionClient:
        provider = get_ctp_instrument_provider(config.instrument_provider)
        return CtpLiveExecutionClient(
            loop=loop,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=config,
        )
