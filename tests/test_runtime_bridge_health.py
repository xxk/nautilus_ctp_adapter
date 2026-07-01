from __future__ import annotations

from nautilus_ctp_adapter.runtime import (
    CtpRuntimeBridge,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
)


def test_runtime_bridge_health_uses_session_state_instead_of_unconditional_pass() -> None:
    bridge = CtpRuntimeBridge()

    assert bridge.healthy() is False

    bridge.push_event(CtpRuntimeEvent(kind=CtpRuntimeEventKind.CONNECTED))
    assert bridge.healthy() is True

    bridge.push_event(CtpRuntimeEvent(kind=CtpRuntimeEventKind.DISCONNECTED))
    assert bridge.healthy() is False
