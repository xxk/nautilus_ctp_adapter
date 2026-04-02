from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .models import CtpRuntimeCommand, CtpRuntimeCommandKind, CtpRuntimeEvent, CtpRuntimeEventKind


class CtpOrderState(StrEnum):
    UNKNOWN = "unknown"
    PENDING_SUBMIT = "pending_submit"
    WORKING = "working"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class CtpTradingRuntime:
    _order_states: dict[str, CtpOrderState] = field(default_factory=dict)

    def on_command(self, command: CtpRuntimeCommand) -> None:
        client_order_id = command.client_order_id
        if not client_order_id:
            return

        if command.kind is CtpRuntimeCommandKind.SUBMIT_ORDER:
            self._order_states[client_order_id] = CtpOrderState.PENDING_SUBMIT
        elif command.kind is CtpRuntimeCommandKind.CANCEL_ORDER:
            self._order_states[client_order_id] = CtpOrderState.PENDING_CANCEL
        elif command.kind is CtpRuntimeCommandKind.REPLACE_ORDER:
            self._order_states[client_order_id] = CtpOrderState.PENDING_REPLACE

    def on_event(self, event: CtpRuntimeEvent) -> None:
        client_order_id = event.client_order_id
        if not client_order_id:
            return

        if event.kind is CtpRuntimeEventKind.ORDER:
            self._order_states[client_order_id] = CtpOrderState.WORKING
        elif event.kind is CtpRuntimeEventKind.TRADE:
            self._order_states[client_order_id] = CtpOrderState.FILLED
        elif event.kind is CtpRuntimeEventKind.ERROR:
            self._order_states.setdefault(client_order_id, CtpOrderState.UNKNOWN)

    def state_for(self, client_order_id: str) -> CtpOrderState:
        return self._order_states.get(client_order_id, CtpOrderState.UNKNOWN)

    @property
    def tracked_order_count(self) -> int:
        return len(self._order_states)
