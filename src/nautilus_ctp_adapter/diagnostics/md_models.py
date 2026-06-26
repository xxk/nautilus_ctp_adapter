from __future__ import annotations

from dataclasses import dataclass, field

from nautilus_ctp_adapter.runtime import CtpRuntimeEvent, CtpRuntimeEventKind


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
    front_connected: bool = False
    front_connected_count: int = 0
    disconnect_count: int = 0
    disconnect_reasons: tuple[int, ...] = ()
    first_tick_symbol: str | None = None
    first_tick_last: float | None = None
    first_tick_bid: float | None = None
    first_tick_ask: float | None = None
    first_tick_ts_epoch_us: int | None = None
    first_tick_received_at_epoch_us: int | None = None


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


__all__ = [
    "CtpLiveDataBootstrapResult",
    "CtpMarketdataSmokeBaselineResult",
    "CtpMdBootstrapState",
    "CtpMdDisconnectEventPayload",
    "CtpMdEventBatch",
    "CtpMdLoginEventPayload",
    "CtpMdRestorePolicyFinding",
    "CtpMdRestorePolicyResult",
    "CtpMdRestoreResult",
    "CtpMdSmokeResult",
    "CtpMdStartupTruthEvidence",
    "CtpMdTickEventPayload",
    "CtpMdTruthEvidenceMatrix",
]

