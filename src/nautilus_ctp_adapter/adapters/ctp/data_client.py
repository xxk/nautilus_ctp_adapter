"""Nautilus-facing CTP live data client placeholder."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import time

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


def _create_md_live_session(flow_path: Path):
    return create_md_live_session(flow_path)


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


@dataclass(slots=True)
class CtpMdStartupTruthEvidence:
    flow_path: str
    flow_mode: str
    selected_symbols: tuple[str, ...]
    ready: bool
    login_success: bool
    login_error_id: int
    subscribe_code: int
    first_tick_symbol: str | None
    first_tick_last: float | None
    first_tick_bid: float | None
    first_tick_ask: float | None
    first_tick_ts_epoch_us: int | None
    disconnect_count: int
    disconnect_reasons: tuple[int, ...]


@dataclass(slots=True)
class CtpMdRestorePolicyFinding:
    code: str
    severity: str
    action: str
    metric: str
    metric_value: float | int | str | bool | None
    threshold: float | int | str | bool | None
    message: str


@dataclass(slots=True)
class CtpMdRestorePolicyResult:
    startup_truth: CtpMdStartupTruthEvidence
    restored_truth: CtpMdStartupTruthEvidence
    restore_result: CtpMdRestoreResult
    disposition: str
    restore_succeeded: bool
    findings: tuple[CtpMdRestorePolicyFinding, ...]


@dataclass(slots=True)
class CtpMdTruthEvidenceMatrix:
    evidence_version: str
    captured_at_utc: str
    account_id: str | None
    symbol: str | None
    disposition: str
    startup_ready: bool
    restore_triggered: bool
    restore_succeeded: bool
    startup_flow_path: str
    restored_flow_path: str
    startup_first_tick_ts_epoch_us: int | None
    restored_first_tick_ts_epoch_us: int | None
    manual_review_codes: tuple[str, ...]
    restore_required_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]


@dataclass(slots=True)
class CtpLiveDataBootstrapResult:
    instrument_request_id: str
    instrument_loaded: bool
    source_instrument_count: int
    selected_symbols: tuple[str, ...]
    bootstrap_state: CtpMdBootstrapState


@dataclass(slots=True)
class CtpMdEventBatch:
    events: tuple[CtpRuntimeEvent, ...]
    contains_disconnect: bool
    should_restore: bool


@dataclass(slots=True)
class CtpMdRestoreResult:
    triggered: bool
    restored_symbols: tuple[str, ...]
    bootstrap_state: CtpMdBootstrapState | None = None


@dataclass(slots=True)
class CtpMarketdataSmokeBaselineResult:
    instrument_request_id: str
    instrument_loaded: bool
    source_instrument_count: int
    selected_symbols: tuple[str, ...]
    bootstrap_state: CtpMdBootstrapState
    md_smoke: CtpMdSmokeResult
    event_batch: CtpMdEventBatch


@dataclass(slots=True)
class CtpMdLoginEventPayload:
    channel: str
    success: bool
    front_id: int
    session_id: int
    max_order_ref: int
    error_id: int
    error_message: str

    @classmethod
    def from_runtime_event(cls, event: CtpRuntimeEvent) -> "CtpMdLoginEventPayload":
        return cls(
            channel=event.payload.get("channel", ""),
            success=event.kind is CtpRuntimeEventKind.LOGIN_SUCCEEDED,
            front_id=int(event.payload.get("front_id", "0")),
            session_id=int(event.payload.get("session_id", "0")),
            max_order_ref=int(event.payload.get("max_order_ref", "0")),
            error_id=int(event.payload.get("error_id", "0")),
            error_message=event.message or "",
        )


@dataclass(slots=True)
class CtpMdTickEventPayload:
    channel: str
    venue_symbol: str
    last: float
    bid: float
    ask: float
    ts_epoch_us: int

    @classmethod
    def from_runtime_event(cls, event: CtpRuntimeEvent) -> "CtpMdTickEventPayload":
        return cls(
            channel=event.payload.get("channel", "md"),
            venue_symbol=event.venue_symbol or "",
            last=float(event.payload.get("last", "0")),
            bid=float(event.payload.get("bid", "0")),
            ask=float(event.payload.get("ask", "0")),
            ts_epoch_us=int(event.payload.get("ts_epoch_us", "0")),
        )


@dataclass(slots=True)
class CtpMdDisconnectEventPayload:
    channel: str
    reason: int

    @classmethod
    def from_runtime_event(cls, event: CtpRuntimeEvent) -> "CtpMdDisconnectEventPayload":
        return cls(
            channel=event.payload.get("channel", ""),
            reason=int(event.payload.get("reason", "0")),
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
        session = _create_md_live_session(effective_flow_path)
        state: dict[str, object] = {
            "login_success": False,
            "login_error_id": -1,
            "login_error_message": "",
            "tick": None,
        }

        try:
            session.set_login_callback(lambda resp: self._on_md_login_callback(resp, state))
            session.set_tick_callback(lambda tick: self._on_md_tick_callback(tick, state))
            session.set_front_disconnected_callback(
                lambda reason: self._emit_marketdata_event(
                    CtpRuntimeEvent(
                        kind=CtpRuntimeEventKind.DISCONNECTED,
                        message=f"md_disconnected:{reason}",
                        payload={
                            "channel": "md",
                            "reason": str(reason),
                        },
                    )
                )
            )

            init_code = session.init(self._config.md_front)
            login_request_code = session.login(
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
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
                first_tick_symbol=None if tick is None else tick["symbol"],
                first_tick_last=None if tick is None else tick["last"],
                first_tick_bid=None if tick is None else tick["bid"],
                first_tick_ask=None if tick is None else tick["ask"],
                first_tick_ts_epoch_us=None if tick is None else tick["ts_epoch_us"],
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
        findings: list[CtpMdRestorePolicyFinding] = []

        if not startup_truth.ready:
            findings.append(
                CtpMdRestorePolicyFinding(
                    code="startup_truth_unready",
                    severity="critical",
                    action="manual_review_required",
                    metric="startup_ready",
                    metric_value=startup_truth.ready,
                    threshold=True,
                    message="Initial MD startup truth is not ready enough to judge restore behavior.",
                )
            )

        if not restore_result.triggered:
            findings.append(
                CtpMdRestorePolicyFinding(
                    code="restore_not_triggered",
                    severity="critical",
                    action="manual_review_required",
                    metric="restore_triggered",
                    metric_value=restore_result.triggered,
                    threshold=True,
                    message="MD restore was not triggered, so restore success cannot be declared.",
                )
            )

        if not restored_truth.ready:
            findings.append(
                CtpMdRestorePolicyFinding(
                    code="restored_truth_unready",
                    severity="critical",
                    action="manual_review_required",
                    metric="restored_ready",
                    metric_value=restored_truth.ready,
                    threshold=True,
                    message="Post-restore MD truth is not ready, so restore success cannot be trusted.",
                )
            )

        if (
            startup_truth.first_tick_ts_epoch_us is not None
            and restored_truth.first_tick_ts_epoch_us is not None
            and restored_truth.first_tick_ts_epoch_us <= startup_truth.first_tick_ts_epoch_us
        ):
            findings.append(
                CtpMdRestorePolicyFinding(
                    code="restore_missing_fresh_tick",
                    severity="warn",
                    action="restore_required",
                    metric="restored_first_tick_ts_epoch_us",
                    metric_value=restored_truth.first_tick_ts_epoch_us,
                    threshold=f"> {startup_truth.first_tick_ts_epoch_us}",
                    message="Restore success requires a fresh post-restore tick, not reuse of a pre-restore tick timestamp.",
                )
            )

        if restore_result.triggered:
            findings.append(
                CtpMdRestorePolicyFinding(
                    code="restore_resubscribe_triggered",
                    severity="info",
                    action="evidence_only",
                    metric="restored_symbols",
                    metric_value=",".join(restore_result.restored_symbols),
                    threshold="non-empty",
                    message="MD restore re-submitted the tracked symbols.",
                )
            )

        restore_succeeded = (
            restore_result.triggered
            and restored_truth.ready
            and restored_truth.first_tick_symbol is not None
            and startup_truth.first_tick_ts_epoch_us is not None
            and restored_truth.first_tick_ts_epoch_us is not None
            and restored_truth.first_tick_ts_epoch_us > startup_truth.first_tick_ts_epoch_us
        )

        disposition = "clear"
        if any(finding.action == "manual_review_required" for finding in findings):
            disposition = "manual_review_required"
        elif any(finding.action == "restore_required" for finding in findings):
            disposition = "restore_required"
        elif findings:
            disposition = "evidence_only"

        return CtpMdRestorePolicyResult(
            startup_truth=startup_truth,
            restored_truth=restored_truth,
            restore_result=restore_result,
            disposition=disposition,
            restore_succeeded=restore_succeeded,
            findings=tuple(findings),
        )

    def build_md_truth_evidence_matrix(
        self,
        result: CtpMdRestorePolicyResult,
    ) -> CtpMdTruthEvidenceMatrix:
        manual_review_codes = tuple(
            finding.code for finding in result.findings if finding.action == "manual_review_required"
        )
        restore_required_codes = tuple(
            finding.code for finding in result.findings if finding.action == "restore_required"
        )
        evidence_only_codes = tuple(
            finding.code for finding in result.findings if finding.action == "evidence_only"
        )
        symbol = None
        if result.restored_truth.selected_symbols:
            symbol = result.restored_truth.selected_symbols[0]
        elif result.startup_truth.selected_symbols:
            symbol = result.startup_truth.selected_symbols[0]

        return CtpMdTruthEvidenceMatrix(
            evidence_version="md-truth-evidence-v1",
            captured_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            account_id=self._config.user_id or None,
            symbol=symbol,
            disposition=result.disposition,
            startup_ready=result.startup_truth.ready,
            restore_triggered=result.restore_result.triggered,
            restore_succeeded=result.restore_succeeded,
            startup_flow_path=result.startup_truth.flow_path,
            restored_flow_path=result.restored_truth.flow_path,
            startup_first_tick_ts_epoch_us=result.startup_truth.first_tick_ts_epoch_us,
            restored_first_tick_ts_epoch_us=result.restored_truth.first_tick_ts_epoch_us,
            manual_review_codes=manual_review_codes,
            restore_required_codes=restore_required_codes,
            evidence_only_codes=evidence_only_codes,
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
        state["tick"] = {
            "symbol": tick.symbol,
            "last": tick.last,
            "bid": tick.bid,
            "ask": tick.ask,
            "ts_epoch_us": tick.ts_epoch_us,
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
        disconnect_reasons = tuple(
            CtpMdDisconnectEventPayload.from_runtime_event(event).reason
            for event in event_batch.events
            if event.kind is CtpRuntimeEventKind.DISCONNECTED
        )
        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        return CtpMdStartupTruthEvidence(
            flow_path=str(effective_flow_path),
            flow_mode="explicit_override" if flow_path is not None else "default_shared_flow",
            selected_symbols=selected_symbols,
            ready=md_smoke.login_success and md_smoke.subscribe_code == 0 and md_smoke.first_tick_symbol is not None,
            login_success=md_smoke.login_success,
            login_error_id=md_smoke.login_error_id,
            subscribe_code=md_smoke.subscribe_code,
            first_tick_symbol=md_smoke.first_tick_symbol,
            first_tick_last=md_smoke.first_tick_last,
            first_tick_bid=md_smoke.first_tick_bid,
            first_tick_ask=md_smoke.first_tick_ask,
            first_tick_ts_epoch_us=md_smoke.first_tick_ts_epoch_us,
            disconnect_count=len(disconnect_reasons),
            disconnect_reasons=disconnect_reasons,
        )
