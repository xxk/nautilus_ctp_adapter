from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .market import CtpMarketRuntime
from .models import CtpRuntimeCommand, CtpRuntimeEvent
from .query import CtpQueryRuntime
from .session import CtpSessionRuntime
from .trading import CtpTradingRuntime

@dataclass(slots=True)
class CtpRuntimeBridge:
    """Python-side placeholder for the future Rust runtime bridge.

    Adapter-specific layers such as Nautilus or SmartQuant should consume this
    bridge instead of talking directly to native CTP bindings.
    """

    backend: str = "ctp-runtime-core-placeholder"
    session: CtpSessionRuntime = field(default_factory=CtpSessionRuntime)
    market: CtpMarketRuntime = field(default_factory=CtpMarketRuntime)
    query: CtpQueryRuntime = field(default_factory=CtpQueryRuntime)
    trading: CtpTradingRuntime = field(default_factory=CtpTradingRuntime)
    _commands: deque[CtpRuntimeCommand] = field(default_factory=deque)
    _events: deque[CtpRuntimeEvent] = field(default_factory=deque)

    def healthy(self) -> bool:
        return True

    @property
    def pending_command_count(self) -> int:
        return len(self._commands)

    @property
    def pending_event_count(self) -> int:
        return len(self._events)

    def submit_command(self, command: CtpRuntimeCommand) -> None:
        self.session.on_command(command)
        self.market.on_command(command)
        self.query.on_command(command)
        self.trading.on_command(command)
        self._commands.append(command)

    def drain_submitted_commands(self, limit: int | None = None) -> list[CtpRuntimeCommand]:
        if limit is not None and limit < 0:
            raise ValueError("limit must be >= 0")

        drained: list[CtpRuntimeCommand] = []
        remaining = len(self._commands) if limit is None else min(limit, len(self._commands))
        for _ in range(remaining):
            drained.append(self._commands.popleft())
        return drained

    def push_event(self, event: CtpRuntimeEvent) -> None:
        self.session.on_event(event)
        self.query.on_event(event)
        self.trading.on_event(event)
        self._events.append(event)

    def drain_events(self, limit: int | None = None) -> list[CtpRuntimeEvent]:
        if limit is not None and limit < 0:
            raise ValueError("limit must be >= 0")

        drained: list[CtpRuntimeEvent] = []
        remaining = len(self._events) if limit is None else min(limit, len(self._events))
        for _ in range(remaining):
            drained.append(self._events.popleft())
        return drained

    def next_event(self) -> CtpRuntimeEvent | None:
        if not self._events:
            return None
        return self._events.popleft()
