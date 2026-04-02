from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CtpRuntimeCommandKind(StrEnum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    SUBSCRIBE_MARKET_DATA = "subscribe_market_data"
    UNSUBSCRIBE_MARKET_DATA = "unsubscribe_market_data"
    SUBMIT_ORDER = "submit_order"
    CANCEL_ORDER = "cancel_order"
    REPLACE_ORDER = "replace_order"
    QUERY_INSTRUMENTS = "query_instruments"
    QUERY_POSITIONS = "query_positions"
    QUERY_ACCOUNT = "query_account"
    QUERY_INSTRUMENT_STATUS = "query_instrument_status"


class CtpRuntimeEventKind(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    AUTH_SUCCEEDED = "auth_succeeded"
    AUTH_FAILED = "auth_failed"
    LOGIN_SUCCEEDED = "login_succeeded"
    LOGIN_FAILED = "login_failed"
    SETTLEMENT_CONFIRMED = "settlement_confirmed"
    TICK = "tick"
    ORDER = "order"
    TRADE = "trade"
    POSITION = "position"
    ACCOUNT = "account"
    INSTRUMENT = "instrument"
    INSTRUMENT_END = "instrument_end"
    INSTRUMENT_STATUS = "instrument_status"
    ERROR = "error"
    WARNING = "warning"


@dataclass(slots=True)
class CtpRuntimeCommand:
    kind: CtpRuntimeCommandKind
    venue_symbol: str | None = None
    exchange_id: str | None = None
    client_order_id: str | None = None
    request_id: str | None = None
    payload: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class CtpRuntimeEvent:
    kind: CtpRuntimeEventKind
    venue_symbol: str | None = None
    exchange_id: str | None = None
    client_order_id: str | None = None
    request_id: str | None = None
    message: str | None = None
    payload: dict[str, str] = field(default_factory=dict)
