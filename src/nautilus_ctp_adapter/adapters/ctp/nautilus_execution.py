"""Nautilus-compatible CTP live execution client.

Wraps the standalone CtpExecutionClient behind the Nautilus
LiveExecutionClient interface, bridging CTP sync callbacks
into the asyncio event loop via loop.call_soon_threadsafe().
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock, MessageBus
from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.execution.messages import (
    BatchCancelOrders,
    CancelAllOrders,
    CancelOrder,
    ModifyOrder,
    SubmitOrder,
    SubmitOrderList,
)
from nautilus_trader.execution.reports import (
    FillReport,
    OrderStatusReport,
    PositionStatusReport,
)
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import ClientId, Venue
from nautilus_trader.model.objects import Currency

from .config import CtpAdapterConfig
from .execution_client import (
    CtpCancelOrderIntent,
    CtpExecutionClient,
    CtpSubmitOrderIntent,
    CtpTdExecEventPayload,
)
from .nautilus_config import CtpExecClientConfig

logger = logging.getLogger(__name__)


def _create_td_live_session(flow_path: Path):
    try:
        from ctp_runtime._ctp_runtime import CtpTdLiveSession
    except ImportError as exc:
        raise RuntimeError(
            "PyO3 TD bridge unavailable; run maturin develop or pip install -e . before TD operations"
        ) from exc
    return CtpTdLiveSession(str(flow_path))


class CtpLiveExecutionClient(LiveExecutionClient):
    """CTP execution client for Nautilus TradingNode integration.

    Internally holds a standalone ``CtpExecutionClient`` for order mapping,
    guardrail checks, and bootstrap logic, and manages a ``CtpTdLiveSession``
    (PyO3 bridge) for the actual CTP SDK interaction.

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
        config: CtpExecClientConfig,
    ) -> None:
        super().__init__(
            loop=loop,
            client_id=ClientId("CTP"),
            venue=Venue("CTP"),
            oms_type=OmsType.NETTING,
            instrument_provider=instrument_provider,
            account_type=AccountType.MARGIN,
            base_currency=Currency.from_str("CNY"),
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            config=config,
        )
        self._ctp_config = config
        self._inner = CtpExecutionClient(
            config=config.to_adapter_config(),
        )
        self._td_session = None
        self._login_future: asyncio.Future | None = None

    # -- Lifecycle ------------------------------------------------------------

    async def _connect(self) -> None:
        flow_path = self._resolve_flow_path()
        flow_path.mkdir(parents=True, exist_ok=True)

        session = _create_td_live_session(flow_path)
        self._td_session = session

        session.set_login_callback(self._on_td_login)
        session.set_exec_callback(self._on_td_exec_event)
        session.set_front_disconnected_callback(self._on_td_disconnect)

        adapter_cfg = self._ctp_config.to_adapter_config()

        init_code = session.init(self._ctp_config.td_front)
        if init_code != 0:
            raise RuntimeError(
                f"CTP TD session init failed: init_code={init_code}, "
                f"td_front={self._ctp_config.td_front}"
            )

        auth_code_result = session.authenticate(
            adapter_cfg.app_id,
            adapter_cfg.auth_code,
            adapter_cfg.product_info,
        )
        if auth_code_result != 0:
            raise RuntimeError(
                f"CTP TD authenticate failed: code={auth_code_result}"
            )

        self._login_future = self._loop.create_future()
        session.login(
            self._ctp_config.broker_id,
            self._ctp_config.user_id,
            self._ctp_config.password,
        )

        login_result = await asyncio.wait_for(self._login_future, timeout=30.0)
        if not login_result["success"]:
            raise RuntimeError(
                f"CTP TD login failed: error_id={login_result['error_id']}, "
                f"error_message={login_result['error_message']}"
            )

        settlement_code = session.confirm_settlement()
        if settlement_code != 0:
            raise RuntimeError(
                f"CTP TD settlement confirm failed: code={settlement_code}"
            )

        self._log.info("CTP TD login and settlement confirmed")

    async def _disconnect(self) -> None:
        if self._td_session is not None:
            self._td_session.dispose()
            self._td_session = None
        self._log.info("CTP TD session disconnected")

    # -- Order Operations (P0) ------------------------------------------------

    async def _submit_order(self, command: SubmitOrder) -> None:
        order = command.order
        intent = CtpSubmitOrderIntent(
            instrument_id=order.instrument_id.symbol.value,
            side=order.side.name,
            quantity=int(order.quantity),
            limit_price=float(order.price) if order.price is not None else 0.0,
            client_order_id=str(order.client_order_id),
        )
        mapped = self._inner.map_submit_order(intent)
        if mapped.error is not None:
            self._log.error(
                f"Order rejected by guardrails: {mapped.error.error_message}"
            )
            return

        if mapped.command is not None:
            self._inner.submit_mapped_order(mapped)
            self._log.info(
                f"Order submitted: client_order_id={mapped.client_order_id}, "
                f"order_ref={mapped.order_ref}"
            )

    async def _cancel_order(self, command: CancelOrder) -> None:
        intent = CtpCancelOrderIntent(
            instrument_id=command.instrument_id.symbol.value,
            client_order_id=str(command.client_order_id),
            order_ref=0,
            front_id=self._inner.td_session_identity.front_id if self._inner.td_session_identity else 0,
            session_id=self._inner.td_session_identity.session_id if self._inner.td_session_identity else 0,
        )
        mapped = self._inner.map_cancel_order(intent)
        if mapped.error is not None:
            self._log.error(
                f"Cancel rejected by guardrails: {mapped.error.error_message}"
            )
            return

        if mapped.command is not None:
            self._inner.submit_mapped_order(mapped)
            self._log.info(
                f"Cancel submitted: client_order_id={mapped.client_order_id}"
            )

    async def _cancel_all_orders(self, command: CancelAllOrders) -> None:
        self._log.warning(
            "CTP does not support batch cancel; "
            "cancel_all_orders is a no-op in P0 scope"
        )

    # -- Order Operations (P1 stubs) ------------------------------------------

    async def _submit_order_list(self, command: SubmitOrderList) -> None:
        for order in command.order_list.orders:
            single = SubmitOrder(
                trader_id=command.trader_id,
                strategy_id=command.strategy_id,
                order=order,
                command_id=command.id,
                ts_init=command.ts_init,
                position_id=command.position_id,
            )
            await self._submit_order(single)

    async def _modify_order(self, command: ModifyOrder) -> None:
        self._log.warning(
            "CTP does not support native modify order; "
            "_modify_order is not implemented in P0 scope"
        )

    async def _batch_cancel_orders(self, command: BatchCancelOrders) -> None:
        for cancel in command.cancels:
            await self._cancel_order(cancel)

    # -- Report Generation (P0 stubs for reconciliation) ----------------------

    async def generate_order_status_report(
        self,
        instrument_id,
        client_order_id=None,
        venue_order_id=None,
    ) -> OrderStatusReport | None:
        self._log.warning("generate_order_status_report not yet implemented for CTP")
        return None

    async def generate_order_status_reports(
        self,
        instrument_id=None,
        start=None,
        end=None,
        open_only: bool = False,
    ) -> list[OrderStatusReport]:
        self._log.warning("generate_order_status_reports not yet implemented for CTP")
        return []

    async def generate_fill_reports(
        self,
        instrument_id=None,
        venue_order_id=None,
        start=None,
        end=None,
    ) -> list[FillReport]:
        self._log.warning("generate_fill_reports not yet implemented for CTP")
        return []

    async def generate_position_status_reports(
        self,
        instrument_id=None,
        start=None,
        end=None,
    ) -> list[PositionStatusReport]:
        self._log.warning("generate_position_status_reports not yet implemented for CTP")
        return []

    # -- CTP Callbacks (called from CTP C++ thread) ---------------------------

    def _on_td_login(self, response) -> None:
        """Called from CTP C++ thread. Dispatches to event loop."""
        self._loop.call_soon_threadsafe(
            self._handle_td_login, response
        )

    def _on_td_exec_event(self, exec_view) -> None:
        """Called from CTP C++ thread. Dispatches to event loop."""
        self._loop.call_soon_threadsafe(
            self._handle_td_exec_event, exec_view
        )

    def _on_td_disconnect(self, reason: int) -> None:
        """Called from CTP C++ thread. Dispatches to event loop."""
        self._loop.call_soon_threadsafe(
            self._handle_td_disconnect, reason
        )

    # -- Event loop handlers (safe to touch Nautilus objects) ------------------

    def _handle_td_login(self, response) -> None:
        """Handle login response in the asyncio event loop."""
        result = {
            "success": response.success,
            "error_id": response.error_id,
            "error_message": response.error_message,
        }
        if self._login_future is not None and not self._login_future.done():
            self._login_future.set_result(result)

    def _handle_td_exec_event(self, exec_view) -> None:
        """Handle execution event in the asyncio event loop.

        Maps CTP order/trade callbacks to Nautilus OrderEvent calls.
        Full event mapping will be implemented in a follow-up change.
        """
        self._log.debug(f"CTP TD exec event received: {exec_view}")

    def _handle_td_disconnect(self, reason: int) -> None:
        """Handle TD front disconnect in the asyncio event loop."""
        self._log.warning(f"CTP TD front disconnected: reason={reason}")

    # -- Helpers --------------------------------------------------------------

    def _resolve_flow_path(self) -> Path:
        return Path(__file__).resolve().parents[4] / "var" / "td_flow_nautilus"
