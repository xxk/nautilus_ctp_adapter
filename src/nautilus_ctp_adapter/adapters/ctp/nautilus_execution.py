"""Nautilus-compatible CTP live execution client.

Wraps the standalone CtpExecutionClient behind the Nautilus
LiveExecutionClient interface, bridging CTP sync callbacks
into the asyncio event loop via loop.call_soon_threadsafe().
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from nautilus_trader.core.uuid import UUID4
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock, MessageBus
from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.execution.messages import (
    BatchCancelOrders,
    CancelAllOrders,
    CancelOrder,
    GenerateFillReports,
    GenerateOrderStatusReport,
    GenerateOrderStatusReports,
    GeneratePositionStatusReports,
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
from nautilus_trader.model.events import AccountState
from nautilus_trader.model.enums import (
    AccountType,
    LiquiditySide,
    OmsType,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
    TimeInForce,
)
from nautilus_trader.model.identifiers import (
    AccountId,
    ClientId,
    ClientOrderId,
    TradeId,
    Venue,
    VenueOrderId,
)
from nautilus_trader.model.objects import AccountBalance, Currency, MarginBalance, Money, Price, Quantity

from nautilus_ctp_adapter.native.pyo3_runtime import create_td_live_session
from nautilus_ctp_adapter.runtime.query import CtpAccountRecord, CtpPositionRecord

from .config import CtpAdapterConfig
from .execution_client import (
    CtpCancelOrderIntent,
    CtpExecutionClient,
    CtpSubmitOrderIntent,
    CtpTdExecEventPayload,
)
from .nautilus_config import CtpExecClientConfig
from .nautilus_data import resolve_ctp_tick_instrument_id

logger = logging.getLogger(__name__)


def _create_td_live_session(flow_path: Path):
    return create_td_live_session(flow_path)


def _account_id(value: str) -> AccountId:
    return AccountId(value or "CTP")


def _venue_order_id(payload: CtpTdExecEventPayload) -> VenueOrderId:
    value = payload.order_id or payload.order_ref or f"{payload.front_id}-{payload.session_id}"
    return VenueOrderId(value)


def _client_order_id(payload: CtpTdExecEventPayload) -> ClientOrderId | None:
    return ClientOrderId(payload.order_ref) if payload.order_ref else None


def _report_quantity(value: int | float) -> Quantity:
    return Quantity.from_str(str(abs(int(value))))


def _resolve_payload_instrument_id(
    instrument_provider: InstrumentProvider,
    venue_symbol: str,
):
    if not venue_symbol:
        return None
    return resolve_ctp_tick_instrument_id(instrument_provider, venue_symbol)


def _order_status_from_payload(payload: CtpTdExecEventPayload) -> OrderStatus:
    if payload.error_message:
        return OrderStatus.REJECTED
    if payload.status in {5, 53}:
        return OrderStatus.CANCELED
    if payload.is_trade or payload.leaves_qty == 0:
        return OrderStatus.FILLED
    return OrderStatus.ACCEPTED


def ctp_exec_event_to_order_status_report(
    payload: CtpTdExecEventPayload,
    *,
    account_id: str,
    instrument_provider: InstrumentProvider,
    ts_init: int,
) -> OrderStatusReport | None:
    """Convert a normalized CTP order callback into a Nautilus order report."""
    if payload.is_trade:
        return None
    instrument_id = _resolve_payload_instrument_id(instrument_provider, payload.venue_symbol)
    if instrument_id is None:
        return None

    leaves_qty = max(payload.leaves_qty, 0)
    filled_qty = max(payload.trade_volume, 0)
    total_qty = max(leaves_qty + filled_qty, 1)
    price = Price.from_str(str(payload.trade_price)) if payload.trade_price > 0 else None
    return OrderStatusReport(
        account_id=_account_id(account_id),
        instrument_id=instrument_id,
        venue_order_id=_venue_order_id(payload),
        order_side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.DAY,
        order_status=_order_status_from_payload(payload),
        quantity=_report_quantity(total_qty),
        filled_qty=_report_quantity(filled_qty),
        report_id=UUID4(),
        ts_accepted=ts_init,
        ts_last=ts_init,
        ts_init=ts_init,
        client_order_id=_client_order_id(payload),
        price=price,
    )


def ctp_exec_event_to_fill_report(
    payload: CtpTdExecEventPayload,
    *,
    account_id: str,
    instrument_provider: InstrumentProvider,
    ts_init: int,
) -> FillReport | None:
    """Convert a normalized CTP trade callback into a Nautilus fill report."""
    if not payload.is_trade or payload.trade_volume <= 0 or payload.trade_price <= 0:
        return None
    instrument_id = _resolve_payload_instrument_id(instrument_provider, payload.venue_symbol)
    if instrument_id is None:
        return None

    trade_id = payload.order_id or payload.order_ref or f"{payload.front_id}-{payload.session_id}"
    return FillReport(
        account_id=_account_id(account_id),
        instrument_id=instrument_id,
        venue_order_id=_venue_order_id(payload),
        trade_id=TradeId(trade_id),
        order_side=OrderSide.BUY,
        last_qty=_report_quantity(payload.trade_volume),
        last_px=Price.from_str(str(payload.trade_price)),
        commission=Money(0, Currency.from_str("CNY")),
        liquidity_side=LiquiditySide.NO_LIQUIDITY_SIDE,
        report_id=UUID4(),
        ts_event=ts_init,
        ts_init=ts_init,
        client_order_id=_client_order_id(payload),
    )


def ctp_position_record_to_status_report(
    record: CtpPositionRecord,
    *,
    account_id: str,
    instrument_provider: InstrumentProvider,
    ts_init: int,
) -> PositionStatusReport | None:
    """Convert a normalized CTP position query row into a Nautilus report."""
    instrument_id = _resolve_payload_instrument_id(instrument_provider, record.venue_symbol)
    if instrument_id is None:
        return None

    qty = int(record.position_qty or 0)
    direction = (record.direction or "").strip().upper()
    if qty == 0:
        side = PositionSide.FLAT
    elif direction in {"3", "SHORT", "SELL"}:
        side = PositionSide.SHORT
    else:
        side = PositionSide.LONG

    return PositionStatusReport(
        account_id=_account_id(account_id),
        instrument_id=instrument_id,
        position_side=side,
        quantity=_report_quantity(qty),
        report_id=UUID4(),
        ts_last=ts_init,
        ts_init=ts_init,
    )


def ctp_account_record_to_account_state(
    record: CtpAccountRecord,
    *,
    ts_init: int,
) -> AccountState:
    """Convert a normalized CTP account query row into a Nautilus account state."""
    currency = Currency.from_str("CNY")
    balance = float(record.balance or 0.0)
    available = float(record.available or 0.0)
    locked = max(balance - available, 0.0)
    margin = float(record.margin or 0.0)
    return AccountState(
        account_id=_account_id(record.account_id or "CTP"),
        account_type=AccountType.MARGIN,
        base_currency=currency,
        reported=True,
        balances=[
            AccountBalance(
                total=Money(balance, currency),
                locked=Money(locked, currency),
                free=Money(available, currency),
            )
        ],
        margins=[
            MarginBalance(
                initial=Money(margin, currency),
                maintenance=Money(margin, currency),
            )
        ],
        info={
            "commission": record.commission,
            "close_profit": record.close_profit,
            "position_profit": record.position_profit,
        },
        event_id=UUID4(),
        ts_event=ts_init,
        ts_init=ts_init,
    )


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
        self._order_status_reports: list[OrderStatusReport] = []
        self._fill_reports: list[FillReport] = []
        self._position_status_reports: list[PositionStatusReport] = []
        self._seen_exec_report_keys: set[tuple[object, ...]] = set()

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
        command: GenerateOrderStatusReport,
    ) -> OrderStatusReport | None:
        for report in reversed(self._order_status_reports):
            if command.client_order_id and report.client_order_id != command.client_order_id:
                continue
            if command.venue_order_id and report.venue_order_id != command.venue_order_id:
                continue
            return report
        return None

    async def generate_order_status_reports(
        self,
        command: GenerateOrderStatusReports,
    ) -> list[OrderStatusReport]:
        reports = list(self._order_status_reports)
        if command.instrument_id is not None:
            reports = [r for r in reports if r.instrument_id == command.instrument_id]
        if command.open_only:
            reports = [r for r in reports if r.is_open]
        return reports

    async def generate_fill_reports(
        self,
        command: GenerateFillReports,
    ) -> list[FillReport]:
        reports = list(self._fill_reports)
        if command.instrument_id is not None:
            reports = [r for r in reports if r.instrument_id == command.instrument_id]
        if command.venue_order_id is not None:
            reports = [r for r in reports if r.venue_order_id == command.venue_order_id]
        return reports

    async def generate_position_status_reports(
        self,
        command: GeneratePositionStatusReports,
    ) -> list[PositionStatusReport]:
        reports = list(self._position_status_reports)
        if command.instrument_id is not None:
            reports = [r for r in reports if r.instrument_id == command.instrument_id]
            if not reports:
                now = self._clock.timestamp_ns()
                reports = [
                    PositionStatusReport.create_flat(
                        account_id=_account_id(self._report_account_id()),
                        instrument_id=command.instrument_id,
                        size_precision=0,
                        ts_init=now,
                    )
                ]
        return reports

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

        Maps CTP order/trade callbacks into report caches consumed by
        Nautilus reconciliation APIs.
        """
        payload = self._coerce_exec_payload(exec_view)
        report_key = self._exec_report_key(payload)
        seen_keys = getattr(self, "_seen_exec_report_keys", None)
        if seen_keys is None:
            seen_keys = set()
            self._seen_exec_report_keys = seen_keys
        if report_key in seen_keys:
            self._log.debug(f"Duplicate CTP TD exec event ignored: {exec_view}")
            return
        seen_keys.add(report_key)

        ts_init = self._clock.timestamp_ns()
        order_report = ctp_exec_event_to_order_status_report(
            payload,
            account_id=self._report_account_id(),
            instrument_provider=self.instrument_provider,
            ts_init=ts_init,
        )
        if order_report is not None:
            self._order_status_reports.append(order_report)

        fill_report = ctp_exec_event_to_fill_report(
            payload,
            account_id=self._report_account_id(),
            instrument_provider=self.instrument_provider,
            ts_init=ts_init,
        )
        if fill_report is not None:
            self._fill_reports.append(fill_report)

        if order_report is None and fill_report is None:
            self._log.debug(f"CTP TD exec event not reportable: {exec_view}")

    def _handle_td_disconnect(self, reason: int) -> None:
        """Handle TD front disconnect in the asyncio event loop."""
        self._log.warning(f"CTP TD front disconnected: reason={reason}")

    # -- Helpers --------------------------------------------------------------

    def _resolve_flow_path(self) -> Path:
        return Path(__file__).resolve().parents[4] / "var" / "td_flow_nautilus"

    def _report_account_id(self) -> str:
        return self._ctp_config.user_id or "CTP"

    @staticmethod
    def _coerce_exec_payload(exec_view) -> CtpTdExecEventPayload:
        if isinstance(exec_view, CtpTdExecEventPayload):
            return exec_view
        return CtpTdExecEventPayload(
            order_id=str(getattr(exec_view, "order_id", "")),
            venue_symbol=str(getattr(exec_view, "venue_symbol", "")),
            order_ref=str(getattr(exec_view, "order_ref", "")),
            front_id=int(getattr(exec_view, "front_id", 0)),
            session_id=int(getattr(exec_view, "session_id", 0)),
            status=int(getattr(exec_view, "status", 0)),
            is_trade=bool(getattr(exec_view, "is_trade", False)),
            trade_price=float(getattr(exec_view, "trade_price", 0.0)),
            trade_volume=int(getattr(exec_view, "trade_volume", 0)),
            leaves_qty=int(getattr(exec_view, "leaves_qty", 0)),
            error_message=str(getattr(exec_view, "error_message", "")),
        )

    @staticmethod
    def _exec_report_key(payload: CtpTdExecEventPayload) -> tuple[object, ...]:
        return (
            "trade" if payload.is_trade else "order",
            payload.order_id,
            payload.order_ref,
            payload.front_id,
            payload.session_id,
            payload.venue_symbol,
            payload.status,
            payload.trade_price,
            payload.trade_volume,
            payload.leaves_qty,
            payload.error_message,
        )
