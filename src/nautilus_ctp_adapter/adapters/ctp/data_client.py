"""Nautilus-facing CTP live data client placeholder."""

from __future__ import annotations

from collections import deque
from pathlib import Path
import time

from nautilus_ctp_adapter.diagnostics import md_policy
from nautilus_ctp_adapter.diagnostics.md_models import (
    CtpLiveDataBootstrapResult,
    CtpMarketdataSmokeBaselineResult,
    CtpMdBootstrapState,
    CtpMdEventBatch,
    CtpMdLoginEventPayload,
    CtpMdRestorePolicyFinding,
    CtpMdRestorePolicyResult,
    CtpMdRestoreResult,
    CtpMdSmokeResult,
    CtpMdStartupTruthEvidence,
    CtpMdTickEventPayload,
    CtpMdTruthEvidenceMatrix,
)
from nautilus_ctp_adapter.native.pyo3_runtime import create_md_live_session
from nautilus_ctp_adapter.runtime import (
    CtpRuntimeBridge,
    CtpRuntimeCommand,
    CtpRuntimeCommandKind,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
)

from .config import CtpAdapterConfig
from .instrument_provider import CtpInstrumentProviderLoadResult


def _create_md_live_session(
    flow_path: Path,
    runtime_pack_bin: str | Path | None = None,
    *,
    strict_runtime_pack: bool = False,
):
    return create_md_live_session(
        flow_path,
        runtime_pack_bin=runtime_pack_bin,
        strict_runtime_pack=strict_runtime_pack,
    )


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
        self._marketdata_events: deque[CtpRuntimeEvent] = deque()
        self._active_subscription_symbols: tuple[str, ...] = ()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def bootstrap_state(self) -> CtpMdBootstrapState:
        return self._bootstrap_state

    @property
    def active_subscription_symbols(self) -> tuple[str, ...]:
        return self._active_subscription_symbols

    def drain_marketdata_events(self, limit: int | None = None) -> list[CtpRuntimeEvent]:
        if limit is not None and limit < 0:
            raise ValueError("limit must be >= 0")

        drained: list[CtpRuntimeEvent] = []
        remaining = len(self._marketdata_events) if limit is None else min(limit, len(self._marketdata_events))
        for _ in range(remaining):
            drained.append(self._marketdata_events.popleft())
        return drained

    def drain_marketdata_event_batch(self, limit: int | None = None) -> CtpMdEventBatch:
        events = tuple(self.drain_marketdata_events(limit=limit))
        contains_disconnect = any(event.kind is CtpRuntimeEventKind.DISCONNECTED for event in events)
        return CtpMdEventBatch(
            events=events,
            contains_disconnect=contains_disconnect,
            should_restore=contains_disconnect and bool(self._active_subscription_symbols),
        )

    def bootstrap_market_data_mainline(self) -> CtpMdBootstrapState:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        return self.bootstrap_market_data_for_symbols(self._config.instruments)

    def bootstrap_market_data_from_provider_result(
        self,
        load_result: CtpInstrumentProviderLoadResult,
    ) -> CtpMdBootstrapState:
        return self.bootstrap_live_data_client_mainline(load_result).bootstrap_state

    def bootstrap_live_data_client_mainline(
        self,
        load_result: CtpInstrumentProviderLoadResult,
    ) -> CtpLiveDataBootstrapResult:
        if not load_result.loaded:
            raise ValueError("instrument provider result must be loaded before bootstrapping market data")

        symbols = self.select_subscription_symbols(load_result)
        bootstrap_state = self.bootstrap_market_data_for_symbols(list(symbols))
        return CtpLiveDataBootstrapResult(
            instrument_request_id=load_result.request_id,
            instrument_loaded=load_result.loaded,
            source_instrument_count=load_result.instrument_count,
            selected_symbols=symbols,
            bootstrap_state=bootstrap_state,
        )

    def bootstrap_market_data_for_symbols(self, symbols: list[str]) -> CtpMdBootstrapState:
        if not symbols:
            raise ValueError("symbols must not be empty")
        ordered_symbols = tuple(dict.fromkeys(symbols))

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
        for instrument_id in ordered_symbols:
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
        self._active_subscription_symbols = ordered_symbols
        return self._bootstrap_state

    def select_subscription_symbols(
        self,
        load_result: CtpInstrumentProviderLoadResult,
    ) -> tuple[str, ...]:
        available_by_key: dict[str, str] = {}
        for instrument in load_result.instruments:
            key = instrument.venue_symbol.casefold()
            if key not in available_by_key:
                available_by_key[key] = instrument.venue_symbol

        selected: list[str] = []
        for configured_symbol in self._config.instruments:
            resolved = available_by_key.get(configured_symbol.casefold())
            if resolved and resolved not in selected:
                selected.append(resolved)

        if selected:
            return tuple(selected)

        fallback: list[str] = []
        for instrument in load_result.instruments:
            if instrument.venue_symbol not in fallback:
                fallback.append(instrument.venue_symbol)
        if not fallback:
            raise ValueError("instrument provider result did not contain any symbols")
        return tuple(fallback)

    def restore_market_data_subscriptions(self) -> CtpMdRestoreResult:
        if not self._active_subscription_symbols:
            return CtpMdRestoreResult(
                triggered=False,
                restored_symbols=(),
                bootstrap_state=None,
            )

        bootstrap_state = self.bootstrap_market_data_for_symbols(list(self._active_subscription_symbols))
        return CtpMdRestoreResult(
            triggered=True,
            restored_symbols=self._active_subscription_symbols,
            bootstrap_state=bootstrap_state,
        )

    def run_marketdata_smoke_baseline(
        self,
        load_result: CtpInstrumentProviderLoadResult,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpMarketdataSmokeBaselineResult:
        bootstrap_result = self.bootstrap_live_data_client_mainline(load_result)
        md_smoke = self.run_live_md_smoke(timeout_seconds=timeout_seconds, flow_path=flow_path)
        event_batch = self.drain_marketdata_event_batch()
        return CtpMarketdataSmokeBaselineResult(
            instrument_request_id=bootstrap_result.instrument_request_id,
            instrument_loaded=bootstrap_result.instrument_loaded,
            source_instrument_count=bootstrap_result.source_instrument_count,
            selected_symbols=bootstrap_result.selected_symbols,
            bootstrap_state=bootstrap_result.bootstrap_state,
            md_smoke=md_smoke,
            event_batch=event_batch,
        )

    def run_live_md_smoke(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpMdSmokeResult:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        session = _create_md_live_session(
            effective_flow_path,
            runtime_pack_bin=self._config.native_pack_dir or None,
            strict_runtime_pack=bool(self._config.native_pack_dir),
        )
        state: dict[str, object] = {
            "front_connected_count": 0,
            "disconnect_reasons": [],
            "login_success": False,
            "login_error_id": -1,
            "login_error_message": "",
            "tick": None,
        }

        try:
            session.set_front_connected_callback(lambda: self._on_md_front_connected(state))
            session.set_login_callback(lambda resp: self._on_md_login_callback(resp, state))
            session.set_tick_callback(lambda tick: self._on_md_tick_callback(tick, state))
            session.set_front_disconnected_callback(
                lambda reason: self._on_md_front_disconnected(reason, state)
            )

            init_code = session.init(self._config.md_front)
            login_request_code = session.login(
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
                self._config.product_info,
                *self._config.md_login_compatibility.as_login_args(),
            )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and state["login_error_id"] == -1:
                time.sleep(0.1)

            subscribe_code = -1
            if state["login_success"]:
                subscribe_code = session.subscribe(self._config.instruments)
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
                front_connected=int(state["front_connected_count"]) > 0,
                front_connected_count=int(state["front_connected_count"]),
                disconnect_count=len(state["disconnect_reasons"]),
                disconnect_reasons=tuple(int(reason) for reason in state["disconnect_reasons"]),
                first_tick_symbol=None if tick is None else tick["symbol"],
                first_tick_last=None if tick is None else tick["last"],
                first_tick_bid=None if tick is None else tick["bid"],
                first_tick_ask=None if tick is None else tick["ask"],
                first_tick_ts_epoch_us=None if tick is None else tick["ts_epoch_us"],
                first_tick_received_at_epoch_us=None if tick is None else tick["received_at_epoch_us"],
            )
        finally:
            session.dispose()

    def capture_md_startup_truth_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpMdStartupTruthEvidence:
        self.bootstrap_market_data_mainline()
        md_smoke = self.run_live_md_smoke(timeout_seconds=timeout_seconds, flow_path=flow_path)
        event_batch = self.drain_marketdata_event_batch()
        return self._build_md_startup_truth_evidence(
            md_smoke=md_smoke,
            flow_path=flow_path,
            selected_symbols=self._active_subscription_symbols,
            event_batch=event_batch,
        )

    def capture_md_restore_policy_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpMdRestorePolicyResult:
        startup_truth = self.capture_md_startup_truth_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        restore_result = self.restore_market_data_subscriptions()
        restored_smoke = self.run_live_md_smoke(timeout_seconds=timeout_seconds, flow_path=flow_path)
        restored_event_batch = self.drain_marketdata_event_batch()
        restored_truth = self._build_md_startup_truth_evidence(
            md_smoke=restored_smoke,
            flow_path=flow_path,
            selected_symbols=restore_result.restored_symbols or startup_truth.selected_symbols,
            event_batch=restored_event_batch,
        )
        return self.evaluate_md_restore_policy(startup_truth, restore_result, restored_truth)

    def evaluate_md_restore_policy(
        self,
        startup_truth: CtpMdStartupTruthEvidence,
        restore_result: CtpMdRestoreResult,
        restored_truth: CtpMdStartupTruthEvidence,
    ) -> CtpMdRestorePolicyResult:
        return md_policy.evaluate_md_restore_policy(
            startup_truth,
            restore_result,
            restored_truth,
        )

    def build_md_truth_evidence_matrix(
        self,
        result: CtpMdRestorePolicyResult,
    ) -> CtpMdTruthEvidenceMatrix:
        return md_policy.build_md_truth_evidence_matrix(
            result,
            account_id=self._config.user_id or None,
        )

    def capture_md_truth_evidence_matrix_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpMdTruthEvidenceMatrix:
        result = self.capture_md_restore_policy_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        return self.build_md_truth_evidence_matrix(result)

    def _next_request_id(self, prefix: str) -> str:
        self._request_sequence += 1
        return f"{prefix}-{self._request_sequence}"

    def _repository_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    def _default_flow_path(self) -> Path:
        return self._repository_root() / "var" / "md_flow_smoke"

    def _on_md_front_connected(self, state: dict[str, object]) -> None:
        state["front_connected_count"] = int(state["front_connected_count"]) + 1
        self._emit_marketdata_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.CONNECTED,
                message="md_front_connected",
                payload={
                    "channel": "md",
                    "front_connected_count": str(state["front_connected_count"]),
                },
            )
        )

    def _on_md_front_disconnected(self, reason: int, state: dict[str, object]) -> None:
        disconnect_reasons = state["disconnect_reasons"]
        if not isinstance(disconnect_reasons, list):
            raise TypeError("disconnect_reasons state must be a list")
        disconnect_reasons.append(int(reason))
        self._emit_marketdata_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.DISCONNECTED,
                message=f"md_disconnected:{reason}",
                payload={
                    "channel": "md",
                    "reason": str(reason),
                },
            )
        )

    def _on_md_login_callback(self, response, state: dict[str, object]) -> None:
        state["login_success"] = response.success
        state["login_error_id"] = response.error_id
        state["login_error_message"] = response.error_message
        self._emit_marketdata_event(
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
        received_at_epoch_us = int(time.time() * 1_000_000)
        state["tick"] = {
            "symbol": tick.symbol,
            "last": tick.last,
            "bid": tick.bid,
            "ask": tick.ask,
            "ts_epoch_us": tick.ts_epoch_us,
            "received_at_epoch_us": received_at_epoch_us,
        }
        self._emit_marketdata_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.TICK,
                venue_symbol=tick.symbol,
                payload={
                    "channel": "md",
                    "last": str(tick.last),
                    "bid": str(tick.bid),
                    "ask": str(tick.ask),
                    "ts_epoch_us": str(tick.ts_epoch_us),
                    "received_at_epoch_us": str(received_at_epoch_us),
                },
            )
        )

    def _emit_marketdata_event(self, event: CtpRuntimeEvent) -> None:
        self._marketdata_events.append(event)
        self._runtime_bridge.push_event(event)

    def _build_md_startup_truth_evidence(
        self,
        *,
        md_smoke: CtpMdSmokeResult,
        flow_path: str | Path | None,
        selected_symbols: tuple[str, ...],
        event_batch: CtpMdEventBatch,
    ) -> CtpMdStartupTruthEvidence:
        return md_policy.build_md_startup_truth_evidence(
            md_smoke=md_smoke,
            flow_path=flow_path,
            default_flow_path=self._default_flow_path(),
            selected_symbols=selected_symbols,
            event_batch=event_batch,
        )
