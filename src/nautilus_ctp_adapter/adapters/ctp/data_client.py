"""Nautilus-facing CTP live data client placeholder."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time

from nautilus_ctp_adapter.native import CtpMdApi
from nautilus_ctp_adapter.runtime import (
    CtpRuntimeBridge,
    CtpRuntimeCommand,
    CtpRuntimeCommandKind,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
)

from .config import CtpAdapterConfig


@dataclass(slots=True)
class CtpMdBootstrapState:
    started: bool = False
    connect_request_id: str | None = None
    subscribe_request_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CtpMdSmokeResult:
    init_code: int
    login_request_code: int
    subscribe_code: int
    login_success: bool
    login_error_id: int
    login_error_message: str
    first_tick_symbol: str | None = None
    first_tick_last: float | None = None
    first_tick_bid: float | None = None
    first_tick_ask: float | None = None
    first_tick_ts_epoch_us: int | None = None


class CtpDataClient:
    """Placeholder for Nautilus market data integration."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
    ) -> None:
        self._connected = False
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._request_sequence = 0
        self._bootstrap_state = CtpMdBootstrapState()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def bootstrap_state(self) -> CtpMdBootstrapState:
        return self._bootstrap_state

    def bootstrap_market_data_mainline(self) -> CtpMdBootstrapState:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        connect_request_id = self._next_request_id("md-connect")
        self._runtime_bridge.submit_command(
            CtpRuntimeCommand(
                kind=CtpRuntimeCommandKind.CONNECT,
                request_id=connect_request_id,
                payload={
                    "channel": "md",
                    "broker_id": self._config.broker_id,
                    "user_id": self._config.user_id,
                    "front": self._config.md_front,
                    "app_id": self._config.app_id,
                    "auth_code_present": "true" if bool(self._config.auth_code) else "false",
                },
            )
        )

        subscribe_request_ids: list[str] = []
        for instrument_id in self._config.instruments:
            request_id = self._next_request_id("md-subscribe")
            self._runtime_bridge.submit_command(
                CtpRuntimeCommand(
                    kind=CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA,
                    venue_symbol=instrument_id,
                    request_id=request_id,
                    payload={
                        "channel": "md",
                        "front": self._config.md_front,
                    },
                )
            )
            subscribe_request_ids.append(request_id)

        self._bootstrap_state = CtpMdBootstrapState(
            started=True,
            connect_request_id=connect_request_id,
            subscribe_request_ids=subscribe_request_ids,
        )
        return self._bootstrap_state

    def run_live_md_smoke(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpMdSmokeResult:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        api = CtpMdApi.load(self._repository_root())
        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        handle = api.create(effective_flow_path)
        state: dict[str, object] = {
            "login_success": False,
            "login_error_id": -1,
            "login_error_message": "",
            "tick": None,
        }

        try:
            api.set_login_callback(handle, lambda resp: self._on_md_login_callback(resp, state))
            api.set_tick_callback(handle, lambda tick: self._on_md_tick_callback(tick, state))
            api.set_front_disconnected_callback(
                handle,
                lambda reason: self._runtime_bridge.push_event(
                    CtpRuntimeEvent(
                        kind=CtpRuntimeEventKind.DISCONNECTED,
                        message=f"md_disconnected:{reason}",
                    )
                ),
            )

            init_code = api.init(handle, self._config.md_front)
            login_request_code = api.login(
                handle,
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
            )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and state["login_error_id"] == -1:
                time.sleep(0.1)

            subscribe_code = -1
            if state["login_success"]:
                subscribe_code = api.subscribe(handle, self._config.instruments)
                while time.time() < deadline and state["tick"] is None:
                    time.sleep(0.1)

            tick = state["tick"]
            return CtpMdSmokeResult(
                init_code=init_code,
                login_request_code=login_request_code,
                subscribe_code=subscribe_code,
                login_success=bool(state["login_success"]),
                login_error_id=int(state["login_error_id"]),
                login_error_message=str(state["login_error_message"]),
                first_tick_symbol=None if tick is None else tick["symbol"],
                first_tick_last=None if tick is None else tick["last"],
                first_tick_bid=None if tick is None else tick["bid"],
                first_tick_ask=None if tick is None else tick["ask"],
                first_tick_ts_epoch_us=None if tick is None else tick["ts_epoch_us"],
            )
        finally:
            api.dispose(handle)

    def _next_request_id(self, prefix: str) -> str:
        self._request_sequence += 1
        return f"{prefix}-{self._request_sequence}"

    def _repository_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    def _default_flow_path(self) -> Path:
        return self._repository_root() / "var" / "md_flow_smoke"

    def _on_md_login_callback(self, response, state: dict[str, object]) -> None:
        state["login_success"] = response.success
        state["login_error_id"] = response.error_id
        state["login_error_message"] = response.error_message
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=(
                    CtpRuntimeEventKind.LOGIN_SUCCEEDED
                    if response.success
                    else CtpRuntimeEventKind.LOGIN_FAILED
                ),
                message=response.error_message,
                payload={
                    "channel": "md",
                    "front_id": str(response.front_id),
                    "session_id": str(response.session_id),
                    "max_order_ref": str(response.max_order_ref),
                    "error_id": str(response.error_id),
                },
            )
        )

    def _on_md_tick_callback(self, tick, state: dict[str, object]) -> None:
        state["tick"] = {
            "symbol": tick.symbol,
            "last": tick.last,
            "bid": tick.bid,
            "ask": tick.ask,
            "ts_epoch_us": tick.ts_epoch_us,
        }
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.TICK,
                venue_symbol=tick.symbol,
                payload={
                    "last": str(tick.last),
                    "bid": str(tick.bid),
                    "ask": str(tick.ask),
                    "ts_epoch_us": str(tick.ts_epoch_us),
                },
            )
        )
