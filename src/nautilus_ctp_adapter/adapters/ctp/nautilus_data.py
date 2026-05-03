"""Nautilus-compatible CTP live data client.

Wraps the standalone CtpDataClient and CtpMdLiveSession behind the
Nautilus LiveMarketDataClient interface, bridging CTP sync callbacks
into the asyncio event loop via loop.call_soon_threadsafe().
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock, MessageBus
from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.data.messages import (
    RequestInstrument,
    RequestInstruments,
    SubscribeInstrument,
    SubscribeInstruments,
    SubscribeQuoteTicks,
    UnsubscribeQuoteTicks,
)
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.identifiers import ClientId, InstrumentId, Venue
from nautilus_trader.model.objects import Price, Quantity

from .config import CtpAdapterConfig
from .data_client import CtpDataClient
from .nautilus_config import CtpDataClientConfig

logger = logging.getLogger(__name__)


def _create_md_live_session(flow_path: Path):
    try:
        from ctp_runtime._ctp_runtime import CtpMdLiveSession
    except ImportError as exc:
        raise RuntimeError(
            "PyO3 MD bridge unavailable; run maturin develop or pip install -e . before MD operations"
        ) from exc
    return CtpMdLiveSession(str(flow_path))


class CtpLiveDataClient(LiveMarketDataClient):
    """CTP market data client for Nautilus TradingNode integration.

    Internally holds a standalone ``CtpDataClient`` for bootstrap and
    subscription logic, and manages a ``CtpMdLiveSession`` (PyO3 bridge)
    for the actual CTP SDK interaction.

    CTP callbacks arrive on the CTP C++ thread and are dispatched to the
    asyncio event loop via ``loop.call_soon_threadsafe()``.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        instrument_provider: InstrumentProvider,
        config: CtpDataClientConfig,
    ) -> None:
        super().__init__(
            loop=loop,
            client_id=ClientId("CTP"),
            venue=Venue("CTP"),
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=instrument_provider,
            config=config,
        )
        self._ctp_config = config
        self._inner = CtpDataClient(
            config=config.to_adapter_config(),
        )
        self._md_session = None
        self._login_future: asyncio.Future | None = None
        self._subscribed_symbols: set[str] = set()

    # -- Lifecycle ------------------------------------------------------------

    async def _connect(self) -> None:
        flow_path = self._resolve_flow_path()
        flow_path.mkdir(parents=True, exist_ok=True)

        session = _create_md_live_session(flow_path)
        self._md_session = session

        # Set up callbacks with thread-safe bridge
        session.set_login_callback(self._on_md_login)
        session.set_tick_callback(self._on_md_tick)
        session.set_front_disconnected_callback(self._on_md_disconnect)

        init_code = session.init(self._ctp_config.md_front)
        if init_code != 0:
            raise RuntimeError(
                f"CTP MD session init failed: init_code={init_code}, "
                f"md_front={self._ctp_config.md_front}"
            )

        self._login_future = self._loop.create_future()
        session.login(
            self._ctp_config.broker_id,
            self._ctp_config.user_id,
            self._ctp_config.password,
        )

        # Wait for login callback (dispatched via call_soon_threadsafe)
        login_result = await asyncio.wait_for(self._login_future, timeout=30.0)
        if not login_result["success"]:
            raise RuntimeError(
                f"CTP MD login failed: error_id={login_result['error_id']}, "
                f"error_message={login_result['error_message']}"
            )
        self._log.info("CTP MD login succeeded")

    async def _disconnect(self) -> None:
        if self._md_session is not None:
            self._md_session.dispose()
            self._md_session = None
        self._subscribed_symbols.clear()
        self._log.info("CTP MD session disconnected")

    # -- Subscribe / Unsubscribe (P0) -----------------------------------------

    async def _subscribe_quote_ticks(self, command: SubscribeQuoteTicks) -> None:
        symbol = command.instrument_id.symbol.value
        if symbol in self._subscribed_symbols:
            return

        if self._md_session is None:
            self._log.error("Cannot subscribe: MD session not connected")
            return

        result = self._md_session.subscribe([symbol])
        if result != 0:
            self._log.error(
                f"CTP MD subscribe failed for {symbol}: code={result}"
            )
            return

        self._subscribed_symbols.add(symbol)
        self._add_subscription_quote_ticks(command.instrument_id)
        self._log.info(f"Subscribed to quote ticks: {symbol}")

    async def _unsubscribe_quote_ticks(self, command: UnsubscribeQuoteTicks) -> None:
        symbol = command.instrument_id.symbol.value
        self._subscribed_symbols.discard(symbol)
        self._remove_subscription_quote_ticks(command.instrument_id)
        self._log.info(f"Unsubscribed from quote ticks: {symbol}")

    # -- Subscribe / Request instruments (P0) ---------------------------------

    async def _subscribe_instrument(self, command: SubscribeInstrument) -> None:
        instrument = self.instrument_provider.find(command.instrument_id)
        if instrument is not None:
            self._handle_data(instrument)

    async def _subscribe_instruments(self, command: SubscribeInstruments) -> None:
        for instrument in self.instrument_provider.list_all():
            self._handle_data(instrument)

    async def _request_instrument(self, request: RequestInstrument) -> None:
        await self.instrument_provider.load_async(request.instrument_id)
        instrument = self.instrument_provider.find(request.instrument_id)
        if instrument is not None:
            self._handle_data(instrument)

    async def _request_instruments(self, request: RequestInstruments) -> None:
        await self.instrument_provider.load_all_async()
        for instrument in self.instrument_provider.list_all():
            self._handle_data(instrument)

    # -- CTP Callbacks (called from CTP C++ thread) ---------------------------

    def _on_md_login(self, response) -> None:
        """Called from CTP C++ thread. Dispatches to event loop."""
        self._loop.call_soon_threadsafe(
            self._handle_md_login, response
        )

    def _on_md_tick(self, tick) -> None:
        """Called from CTP C++ thread. Dispatches to event loop."""
        self._loop.call_soon_threadsafe(
            self._handle_md_tick, tick
        )

    def _on_md_disconnect(self, reason: int) -> None:
        """Called from CTP C++ thread. Dispatches to event loop."""
        self._loop.call_soon_threadsafe(
            self._handle_md_disconnect, reason
        )

    # -- Event loop handlers (safe to touch Nautilus objects) ------------------

    def _handle_md_login(self, response) -> None:
        """Handle login response in the asyncio event loop."""
        result = {
            "success": response.success,
            "error_id": response.error_id,
            "error_message": response.error_message,
        }
        if self._login_future is not None and not self._login_future.done():
            self._login_future.set_result(result)

    def _handle_md_tick(self, tick) -> None:
        """Handle tick data in the asyncio event loop. Build QuoteTick."""
        instrument_id = InstrumentId.from_str(f"{tick.symbol}.CTP")
        instrument = self._cache.instrument(instrument_id)
        if instrument is None:
            self._log.warning(f"Tick for unknown instrument: {tick.symbol}")
            return

        quote_tick = QuoteTick(
            instrument_id=instrument_id,
            bid_price=instrument.make_price(tick.bid),
            ask_price=instrument.make_price(tick.ask),
            bid_size=Quantity.from_int(max(int(getattr(tick, "bid_volume", 0)), 0)),
            ask_size=Quantity.from_int(max(int(getattr(tick, "ask_volume", 0)), 0)),
            ts_event=self._parse_ctp_timestamp(tick),
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(quote_tick)

    def _handle_md_disconnect(self, reason: int) -> None:
        """Handle MD front disconnect in the asyncio event loop."""
        self._log.warning(f"CTP MD front disconnected: reason={reason}")

    # -- Helpers --------------------------------------------------------------

    def _resolve_flow_path(self) -> Path:
        return Path(__file__).resolve().parents[4] / "var" / "md_flow_nautilus"

    @staticmethod
    def _parse_ctp_timestamp(tick) -> int:
        """Convert CTP tick timestamp (epoch microseconds) to nanoseconds."""
        ts_epoch_us = getattr(tick, "ts_epoch_us", 0) or 0
        return int(ts_epoch_us) * 1_000  # us → ns
