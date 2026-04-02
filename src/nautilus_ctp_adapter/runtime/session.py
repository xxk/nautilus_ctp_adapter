from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .models import CtpRuntimeCommand, CtpRuntimeCommandKind, CtpRuntimeEvent, CtpRuntimeEventKind


class CtpSessionState(StrEnum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    LOGGED_IN = "logged_in"


@dataclass(slots=True)
class CtpSessionRuntime:
    state: CtpSessionState = CtpSessionState.DISCONNECTED

    def on_command(self, command: CtpRuntimeCommand) -> None:
        if command.kind is CtpRuntimeCommandKind.CONNECT:
            self.state = CtpSessionState.CONNECTING
        elif command.kind is CtpRuntimeCommandKind.DISCONNECT:
            self.state = CtpSessionState.DISCONNECTED

    def on_event(self, event: CtpRuntimeEvent) -> None:
        if event.kind is CtpRuntimeEventKind.CONNECTED:
            self.state = CtpSessionState.CONNECTED
        elif event.kind is CtpRuntimeEventKind.AUTH_SUCCEEDED:
            self.state = CtpSessionState.AUTHENTICATED
        elif event.kind is CtpRuntimeEventKind.LOGIN_SUCCEEDED:
            self.state = CtpSessionState.LOGGED_IN
        elif event.kind in {
            CtpRuntimeEventKind.DISCONNECTED,
            CtpRuntimeEventKind.AUTH_FAILED,
            CtpRuntimeEventKind.LOGIN_FAILED,
        }:
            self.state = CtpSessionState.DISCONNECTED

    @property
    def is_connected(self) -> bool:
        return self.state in {
            CtpSessionState.CONNECTED,
            CtpSessionState.AUTHENTICATED,
            CtpSessionState.LOGGED_IN,
        }

