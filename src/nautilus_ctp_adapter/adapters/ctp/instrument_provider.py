"""Nautilus-facing CTP instrument provider placeholder."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time

from nautilus_ctp_adapter.native.pyo3_runtime import create_td_live_session
from nautilus_ctp_adapter.runtime import (
    CtpRuntimeBridge,
    CtpRuntimeCommand,
    CtpRuntimeCommandKind,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
)

from .config import CtpAdapterConfig
from .normalization import NormalizedCtpInstrument, normalize_instrument_record


def _create_td_live_session(flow_path: Path):
    return create_td_live_session(flow_path)


@dataclass(slots=True)
class CtpInstrumentQueryBootstrapState:
    started: bool = False
    request_id: str | None = None


@dataclass(slots=True)
class CtpInstrumentProviderLoadResult:
    request_id: str
    loaded: bool
    instrument_count: int
    instruments: tuple[NormalizedCtpInstrument, ...] = field(default_factory=tuple)


class CtpInstrumentProvider:
    """Placeholder for Nautilus instrument loading built on the shared runtime."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
    ) -> None:
        self._loaded = False
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._request_sequence = 0
        self._bootstrap_state = CtpInstrumentQueryBootstrapState()
        self._latest_load_result: CtpInstrumentProviderLoadResult | None = None

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def bootstrap_state(self) -> CtpInstrumentQueryBootstrapState:
        return self._bootstrap_state

    @property
    def latest_load_result(self) -> CtpInstrumentProviderLoadResult | None:
        return self._latest_load_result

    def bootstrap_instrument_query_mainline(self) -> CtpInstrumentQueryBootstrapState:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        request_id = self._next_request_id("instrument-query")
        self._runtime_bridge.submit_command(
            CtpRuntimeCommand(
                kind=CtpRuntimeCommandKind.QUERY_INSTRUMENTS,
                request_id=request_id,
                payload={
                    "channel": "td",
                    "front": self._config.td_front,
                    "broker_id": self._config.broker_id,
                    "user_id": self._config.user_id,
                    "query_scope": "instruments",
                },
            )
        )
        self._bootstrap_state = CtpInstrumentQueryBootstrapState(
            started=True,
            request_id=request_id,
        )
        return self._bootstrap_state

    def push_instrument_snapshot(
        self,
        *,
        request_id: str,
        venue_symbol: str,
        exchange_id: str,
        product_class: str,
        instrument_name: str,
        price_tick: float,
        volume_multiple: int,
    ) -> None:
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.INSTRUMENT,
                request_id=request_id,
                venue_symbol=venue_symbol,
                exchange_id=exchange_id,
                payload={
                    "venue_symbol": venue_symbol,
                    "exchange_id": exchange_id,
                    "product_class": product_class,
                    "instrument_name": instrument_name,
                    "price_tick": str(price_tick),
                    "volume_multiple": str(volume_multiple),
                },
            )
        )

    def complete_instrument_query(self, *, request_id: str, instrument_count: int | None = None) -> None:
        payload: dict[str, str] = {"channel": "td"}
        if instrument_count is not None:
            payload["instrument_count"] = str(instrument_count)
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.INSTRUMENT_END,
                request_id=request_id,
                payload=payload,
            )
        )
        self._loaded = True
        self._latest_load_result = self.load_result_for_request(request_id)

    def normalized_instruments_for_request(self, request_id: str) -> tuple[NormalizedCtpInstrument, ...]:
        records = self._runtime_bridge.query.instruments_for_request(request_id)
        return tuple(normalize_instrument_record(record) for record in records)

    def load_result_for_request(self, request_id: str) -> CtpInstrumentProviderLoadResult:
        instruments = self.normalized_instruments_for_request(request_id)
        return CtpInstrumentProviderLoadResult(
            request_id=request_id,
            loaded=self._runtime_bridge.query.is_query_completed(request_id),
            instrument_count=len(instruments),
            instruments=instruments,
        )

    def load_all_instruments_mainline(self) -> CtpInstrumentProviderLoadResult:
        state = self.bootstrap_instrument_query_mainline()
        if not state.request_id:
            raise RuntimeError("instrument query bootstrap did not produce request_id")
        return self.load_result_for_request(state.request_id)

    def run_live_instrument_smoke(
        self,
        *,
        symbol: str,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpInstrumentProviderLoadResult:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        state = self.bootstrap_instrument_query_mainline()
        if not state.request_id:
            raise RuntimeError("instrument query bootstrap did not produce request_id")

        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        session = _create_td_live_session(effective_flow_path)
        login_state: dict[str, object] = {"login": None}

        try:
            session.set_login_callback(lambda resp: login_state.__setitem__("login", resp))
            session.set_front_disconnected_callback(
                lambda reason: self._runtime_bridge.push_event(
                    CtpRuntimeEvent(
                        kind=CtpRuntimeEventKind.DISCONNECTED,
                        message=f"td_disconnected:{reason}",
                        payload={"channel": "td"},
                    )
                ),
            )
            session.set_instrument_callback(
                lambda inst, req_id, is_last: self._on_td_instrument_callback(
                    request_id=state.request_id or "",
                    instrument=inst,
                    req_id=req_id,
                    is_last=is_last,
                ),
            )

            session.init(self._config.td_front)
            session.authenticate(self._config.app_id, self._config.auth_code, self._config.product_info)
            session.login(self._config.broker_id, self._config.user_id, self._config.password)

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and login_state["login"] is None:
                time.sleep(0.1)

            login = login_state["login"]
            if login is None or not login.success:
                return self.load_result_for_request(state.request_id)

            session.confirm_settlement()
            session.qry_instrument(symbol)

            while time.time() < deadline and not self._runtime_bridge.query.is_query_completed(state.request_id):
                time.sleep(0.1)

            self._latest_load_result = self.load_result_for_request(state.request_id)
            return self._latest_load_result
        finally:
            session.dispose()

    def _next_request_id(self, prefix: str) -> str:
        self._request_sequence += 1
        return f"{prefix}-{self._request_sequence}"

    def _repository_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    def _default_flow_path(self) -> Path:
        return self._repository_root() / "var" / "td_instrument_query_flow"

    def _on_td_instrument_callback(self, *, request_id: str, instrument, req_id: int, is_last: bool) -> None:
        self.push_instrument_snapshot(
            request_id=request_id,
            venue_symbol=instrument.symbol,
            exchange_id=instrument.exchange,
            product_class=str(instrument.product_class),
            instrument_name=instrument.instrument_name,
            price_tick=instrument.tick_size,
            volume_multiple=instrument.volume_multiple,
        )
        if is_last:
            self.complete_instrument_query(request_id=request_id)
