from __future__ import annotations

from dataclasses import dataclass, field

from .models import CtpRuntimeCommand, CtpRuntimeCommandKind, CtpRuntimeEvent, CtpRuntimeEventKind


@dataclass(slots=True)
class CtpInstrumentRecord:
    venue_symbol: str
    exchange_id: str | None
    product_class: str | None
    instrument_name: str | None
    price_tick: float | None
    volume_multiple: int | None


@dataclass(slots=True)
class CtpPositionRecord:
    venue_symbol: str
    exchange_id: str | None
    direction: str | None
    position_qty: int | None
    yd_position_qty: int | None
    td_position_qty: int | None
    position_cost: float | None


@dataclass(slots=True)
class CtpAccountRecord:
    account_id: str | None
    balance: float | None
    available: float | None
    margin: float | None
    commission: float | None
    close_profit: float | None
    position_profit: float | None


@dataclass(slots=True)
class CtpQueryRuntime:
    _pending_instrument_requests: set[str] = field(default_factory=set)
    _pending_position_requests: set[str] = field(default_factory=set)
    _pending_account_requests: set[str] = field(default_factory=set)
    _completed_requests: set[str] = field(default_factory=set)
    _instrument_records: dict[str, list[CtpInstrumentRecord]] = field(default_factory=dict)
    _position_records: dict[str, list[CtpPositionRecord]] = field(default_factory=dict)
    _account_records: dict[str, CtpAccountRecord] = field(default_factory=dict)

    def on_command(self, command: CtpRuntimeCommand) -> None:
        if not command.request_id:
            return

        if command.kind is CtpRuntimeCommandKind.QUERY_INSTRUMENTS:
            self._pending_instrument_requests.add(command.request_id)
            self._completed_requests.discard(command.request_id)
            self._instrument_records.setdefault(command.request_id, [])
            return

        if command.kind is CtpRuntimeCommandKind.QUERY_POSITIONS:
            self._pending_position_requests.add(command.request_id)
            self._completed_requests.discard(command.request_id)
            self._position_records.setdefault(command.request_id, [])
            return

        if command.kind is CtpRuntimeCommandKind.QUERY_ACCOUNT:
            self._pending_account_requests.add(command.request_id)
            self._completed_requests.discard(command.request_id)
            self._account_records.pop(command.request_id, None)

    def on_event(self, event: CtpRuntimeEvent) -> None:
        if not event.request_id:
            return

        if event.kind is CtpRuntimeEventKind.INSTRUMENT:
            self._instrument_records.setdefault(event.request_id, []).append(
                CtpInstrumentRecord(
                    venue_symbol=event.venue_symbol or event.payload.get("venue_symbol") or "",
                    exchange_id=event.exchange_id or event.payload.get("exchange_id"),
                    product_class=event.payload.get("product_class"),
                    instrument_name=event.payload.get("instrument_name"),
                    price_tick=_parse_float(event.payload.get("price_tick")),
                    volume_multiple=_parse_int(event.payload.get("volume_multiple")),
                )
            )
            return

        if event.kind is CtpRuntimeEventKind.INSTRUMENT_END:
            self._pending_instrument_requests.discard(event.request_id)
            self._completed_requests.add(event.request_id)
            return

        if event.kind is CtpRuntimeEventKind.POSITION:
            has_position_payload = any(
                (
                    event.venue_symbol,
                    event.payload.get("venue_symbol"),
                    event.exchange_id,
                    event.payload.get("exchange_id"),
                    event.payload.get("direction"),
                    event.payload.get("position_qty"),
                    event.payload.get("yd_position_qty"),
                    event.payload.get("td_position_qty"),
                    event.payload.get("position_cost"),
                )
            )
            if has_position_payload:
                self._position_records.setdefault(event.request_id, []).append(
                    CtpPositionRecord(
                        venue_symbol=event.venue_symbol or event.payload.get("venue_symbol") or "",
                        exchange_id=event.exchange_id or event.payload.get("exchange_id"),
                        direction=event.payload.get("direction"),
                        position_qty=_parse_int(event.payload.get("position_qty")),
                        yd_position_qty=_parse_int(event.payload.get("yd_position_qty")),
                        td_position_qty=_parse_int(event.payload.get("td_position_qty")),
                        position_cost=_parse_float(event.payload.get("position_cost")),
                    )
                )
            if _parse_bool(event.payload.get("snapshot_complete")):
                self._pending_position_requests.discard(event.request_id)
                self._completed_requests.add(event.request_id)
            return

        if event.kind is CtpRuntimeEventKind.ACCOUNT:
            self._account_records[event.request_id] = CtpAccountRecord(
                account_id=event.payload.get("account_id"),
                balance=_parse_float(event.payload.get("balance")),
                available=_parse_float(event.payload.get("available")),
                margin=_parse_float(event.payload.get("margin")),
                commission=_parse_float(event.payload.get("commission")),
                close_profit=_parse_float(event.payload.get("close_profit")),
                position_profit=_parse_float(event.payload.get("position_profit")),
            )
            self._pending_account_requests.discard(event.request_id)
            self._completed_requests.add(event.request_id)

    @property
    def pending_instrument_query_count(self) -> int:
        return len(self._pending_instrument_requests)

    @property
    def pending_position_query_count(self) -> int:
        return len(self._pending_position_requests)

    @property
    def pending_account_query_count(self) -> int:
        return len(self._pending_account_requests)

    def is_query_pending(self, request_id: str) -> bool:
        return (
            request_id in self._pending_instrument_requests
            or request_id in self._pending_position_requests
            or request_id in self._pending_account_requests
        )

    def is_query_completed(self, request_id: str) -> bool:
        return request_id in self._completed_requests

    def instruments_for_request(self, request_id: str) -> tuple[CtpInstrumentRecord, ...]:
        return tuple(self._instrument_records.get(request_id, ()))

    def positions_for_request(self, request_id: str) -> tuple[CtpPositionRecord, ...]:
        return tuple(self._position_records.get(request_id, ()))

    def account_for_request(self, request_id: str) -> CtpAccountRecord | None:
        return self._account_records.get(request_id)

    def instrument_count_for_request(self, request_id: str) -> int:
        return len(self._instrument_records.get(request_id, ()))

    def position_count_for_request(self, request_id: str) -> int:
        return len(self._position_records.get(request_id, ()))


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y"}
