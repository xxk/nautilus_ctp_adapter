"""CTP-aware Nautilus instrument provider glue."""

from __future__ import annotations

from decimal import Decimal

from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.model.enums import AssetClass
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import FuturesContract
from nautilus_trader.model.objects import Currency, Price, Quantity

from .nautilus_config import CtpInstrumentProviderConfig
from .normalization import CtpProductKind, NormalizedCtpInstrument


class CtpNautilusInstrumentProvider(InstrumentProvider):
    """Nautilus provider carrying CTP metadata without owning CTP query truth."""

    def __init__(self, config: CtpInstrumentProviderConfig | None = None) -> None:
        super().__init__(config=config)
        self._ctp_metadata_by_display_symbol: dict[str, NormalizedCtpInstrument] = {}
        self._ctp_metadata_by_venue_symbol: dict[str, NormalizedCtpInstrument] = {}

    async def load_all_async(self, filters: dict | None = None) -> None:
        return None

    def add_ctp_metadata(self, instrument: NormalizedCtpInstrument) -> None:
        self._ctp_metadata_by_display_symbol[instrument.display_symbol] = instrument
        self._ctp_metadata_by_venue_symbol[instrument.venue_symbol] = instrument

    def add_ctp_metadata_bulk(self, instruments: tuple[NormalizedCtpInstrument, ...]) -> None:
        for instrument in instruments:
            self.add_ctp_metadata(instrument)

    def ctp_metadata(self, key: str) -> NormalizedCtpInstrument | None:
        return self._ctp_metadata_by_display_symbol.get(key) or self._ctp_metadata_by_venue_symbol.get(key)

    def list_ctp_metadata(self) -> tuple[NormalizedCtpInstrument, ...]:
        return tuple(self._ctp_metadata_by_display_symbol.values())

    def hydrate_ctp_metadata(self, instruments: tuple[NormalizedCtpInstrument, ...]) -> tuple[InstrumentId, ...]:
        hydrated: list[InstrumentId] = []
        for instrument in instruments:
            self.add_ctp_metadata(instrument)
            nautilus_instrument = self._to_futures_contract(instrument)
            if nautilus_instrument is None:
                continue
            self.add(nautilus_instrument)
            hydrated.append(nautilus_instrument.id)
        return tuple(hydrated)

    def _to_futures_contract(self, instrument: NormalizedCtpInstrument) -> FuturesContract | None:
        if instrument.product_kind != CtpProductKind.FUTURES:
            return None
        if not instrument.exchange_id or not instrument.venue_symbol:
            return None
        if instrument.price_tick is None or instrument.price_tick <= 0:
            return None
        if instrument.volume_multiple is None or instrument.volume_multiple <= 0:
            return None

        price_increment = Decimal(str(instrument.price_tick)).normalize()
        price_text = format(price_increment, "f")
        return FuturesContract(
            instrument_id=InstrumentId(Symbol(instrument.venue_symbol), Venue(instrument.exchange_id)),
            raw_symbol=Symbol(instrument.venue_symbol),
            asset_class=AssetClass.COMMODITY,
            currency=Currency.from_str("CNY"),
            price_precision=max(0, -price_increment.as_tuple().exponent),
            price_increment=Price.from_str(price_text),
            multiplier=Quantity.from_int(instrument.volume_multiple),
            lot_size=Quantity.from_int(1),
            underlying=instrument.underlying or instrument.venue_symbol,
            activation_ns=0,
            expiration_ns=4_102_444_800_000_000_000,
            ts_event=0,
            ts_init=0,
            exchange=instrument.exchange_id,
            info={
                "raw_symbol": instrument.raw_symbol,
                "raw_exchange_id": instrument.raw_exchange_id,
                "instrument_name": instrument.instrument_name,
                "contract_month": instrument.contract_month,
                "source": "ctp",
            },
        )
