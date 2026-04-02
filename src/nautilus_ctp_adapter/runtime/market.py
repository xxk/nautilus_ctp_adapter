from __future__ import annotations

from dataclasses import dataclass, field

from .models import CtpRuntimeCommand, CtpRuntimeCommandKind


def _subscription_key(venue_symbol: str | None, exchange_id: str | None) -> str | None:
    if not venue_symbol:
        return None
    return venue_symbol if not exchange_id else f"{exchange_id}:{venue_symbol}"


@dataclass(slots=True)
class CtpMarketRuntime:
    _subscriptions: set[str] = field(default_factory=set)

    def on_command(self, command: CtpRuntimeCommand) -> None:
        key = _subscription_key(command.venue_symbol, command.exchange_id)
        if key is None:
            return

        if command.kind is CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA:
            self._subscriptions.add(key)
        elif command.kind is CtpRuntimeCommandKind.UNSUBSCRIBE_MARKET_DATA:
            self._subscriptions.discard(key)

    @property
    def subscription_count(self) -> int:
        return len(self._subscriptions)

    def is_subscribed(self, venue_symbol: str, exchange_id: str | None = None) -> bool:
        key = _subscription_key(venue_symbol, exchange_id)
        return False if key is None else key in self._subscriptions

    def snapshot(self) -> tuple[str, ...]:
        return tuple(sorted(self._subscriptions))
