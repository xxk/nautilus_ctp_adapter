from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from nautilus_ctp_adapter.runtime import CtpInstrumentRecord


EXCHANGE_ALIASES = {
    "SHF": "SHFE",
    "SHFE": "SHFE",
    "CZC": "CZCE",
    "CZCE": "CZCE",
    "ZCE": "CZCE",
    "DL": "DCE",
    "DCE": "DCE",
    "CFF": "CFFEX",
    "CFE": "CFFEX",
    "CFFEX": "CFFEX",
    "INE": "INE",
    "XINE": "INE",
    "GFEX": "GFEX",
}

LOWERCASE_SYMBOL_EXCHANGES = {"SHFE", "DCE", "INE", "GFEX"}
UPPERCASE_SYMBOL_EXCHANGES = {"CZCE", "CFFEX"}
_SYMBOL_PATTERN = re.compile(r"^([A-Za-z]+)(\d{3,4})$")


class CtpProductKind(StrEnum):
    FUTURES = "futures"
    OPTION = "option"
    COMBINATION = "combination"
    SPOT = "spot"
    EFP = "efp"
    SPOT_OPTION = "spot_option"
    TAS = "tas"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class NormalizedCtpInstrument:
    raw_symbol: str
    raw_exchange_id: str | None
    venue_symbol: str
    exchange_id: str | None
    display_symbol: str
    underlying: str | None
    contract_month: str | None
    product_kind: CtpProductKind
    instrument_name: str | None
    price_tick: float | None
    volume_multiple: int | None


def normalize_exchange_id(exchange_id: str | None) -> str | None:
    text = str(exchange_id or "").strip().upper()
    if not text:
        return None
    return EXCHANGE_ALIASES.get(text, text)


def normalize_product_kind(value: str | None) -> CtpProductKind:
    text = str(value or "").strip()
    if not text:
        return CtpProductKind.UNKNOWN

    if text.isdigit():
        numeric = int(text)
        if 48 <= numeric <= 57:
            text = chr(numeric)

    normalized = text.lower()
    mapping = {
        "1": CtpProductKind.FUTURES,
        "future": CtpProductKind.FUTURES,
        "futures": CtpProductKind.FUTURES,
        "2": CtpProductKind.OPTION,
        "option": CtpProductKind.OPTION,
        "options": CtpProductKind.OPTION,
        "3": CtpProductKind.COMBINATION,
        "combination": CtpProductKind.COMBINATION,
        "4": CtpProductKind.SPOT,
        "spot": CtpProductKind.SPOT,
        "5": CtpProductKind.EFP,
        "efp": CtpProductKind.EFP,
        "6": CtpProductKind.SPOT_OPTION,
        "spot_option": CtpProductKind.SPOT_OPTION,
        "spotoption": CtpProductKind.SPOT_OPTION,
        "7": CtpProductKind.TAS,
        "tas": CtpProductKind.TAS,
    }
    return mapping.get(normalized, CtpProductKind.UNKNOWN)


def normalize_symbol(symbol: str, exchange_id: str | None) -> str:
    text = str(symbol or "").strip()
    if not text:
        return ""

    normalized_exchange = normalize_exchange_id(exchange_id)
    if normalized_exchange in LOWERCASE_SYMBOL_EXCHANGES:
        return text.lower()
    if normalized_exchange in UPPERCASE_SYMBOL_EXCHANGES:
        return text.upper()
    return text


def extract_underlying(symbol: str) -> str | None:
    match = _SYMBOL_PATTERN.match(symbol)
    if not match:
        return None
    return match.group(1)


def extract_contract_month(symbol: str) -> str | None:
    match = _SYMBOL_PATTERN.match(symbol)
    if not match:
        return None
    return match.group(2)


def format_display_symbol(symbol: str, exchange_id: str | None) -> str:
    normalized_exchange = normalize_exchange_id(exchange_id)
    return symbol if not normalized_exchange else f"{symbol}.{normalized_exchange}"


def normalize_instrument_record(record: CtpInstrumentRecord) -> NormalizedCtpInstrument:
    normalized_exchange = normalize_exchange_id(record.exchange_id)
    normalized_symbol = normalize_symbol(record.venue_symbol, normalized_exchange)
    underlying = extract_underlying(normalized_symbol)
    contract_month = extract_contract_month(normalized_symbol)
    return NormalizedCtpInstrument(
        raw_symbol=record.venue_symbol,
        raw_exchange_id=record.exchange_id,
        venue_symbol=normalized_symbol,
        exchange_id=normalized_exchange,
        display_symbol=format_display_symbol(normalized_symbol, normalized_exchange),
        underlying=underlying,
        contract_month=contract_month,
        product_kind=normalize_product_kind(record.product_class),
        instrument_name=record.instrument_name,
        price_tick=record.price_tick,
        volume_multiple=record.volume_multiple,
    )
