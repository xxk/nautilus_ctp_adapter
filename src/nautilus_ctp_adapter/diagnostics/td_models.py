from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nautilus_ctp_adapter.runtime import CtpRuntimeEvent, CtpRuntimeEventKind
from nautilus_ctp_adapter.runtime.query import CtpAccountRecord, CtpPositionRecord

if TYPE_CHECKING:
    from nautilus_ctp_adapter.runtime import CtpRuntimeCommand


@dataclass(slots=True)
class CtpOrderPrecheck:
    allowed: bool
    violations: list[str]
    selected_price: float | None


@dataclass(slots=True)
class CtpTdSmokeResult:
    init_code: int
    authenticate_code: int
    login_code: int
    settlement_code: int
    login_success: bool | None
    login_error_id: int | None
    login_error_message: str | None
    front_id: int | None = None
    session_id: int | None = None
    max_order_ref: int | None = None
    disconnects: list[int] | None = None


@dataclass(slots=True)
class CtpTdSessionIdentity:
    front_id: int
    session_id: int
    max_order_ref: int


@dataclass(slots=True)
class CtpTdBootstrapState:
    started: bool = False
    connect_request_id: str | None = None


@dataclass(slots=True)
class CtpExecutionBootstrapResult:
    bootstrap_state: CtpTdBootstrapState
    td_smoke: CtpTdSmokeResult


@dataclass(slots=True)
class CtpSubmitOrderIntent:
    instrument_id: str
    side: str
    quantity: int
    limit_price: float
    position_effect: str = "OPEN"
    order_type: str = "LIMIT"
    time_in_force: str = "GFD"
    client_order_id: str | None = None


@dataclass(slots=True)
class CtpCancelOrderIntent:
    instrument_id: str
    client_order_id: str
    order_ref: int
    front_id: int
    session_id: int
    exchange_id: str | None = None


@dataclass(slots=True)
class CtpClosePositionPlan:
    submit_intent: CtpSubmitOrderIntent | None
    selected_bucket: str | None
    closable_quantity: int
    error: CtpExecutionError | None = None


@dataclass(slots=True)
class CtpExecutionError:
    error_id: int
    error_message: str


@dataclass(slots=True)
class CtpMappedOrderCommand:
    command: CtpRuntimeCommand | None
    client_order_id: str | None
    order_ref: int | None
    front_id: int | None
    session_id: int | None
    error: CtpExecutionError | None = None


@dataclass(slots=True)
class CtpLiveExecutionClientBootstrapResult:
    execution_bootstrap: CtpExecutionBootstrapResult
    ready: bool
    td_session_identity: CtpTdSessionIdentity | None


@dataclass(slots=True)
class CtpOrderLifecycleSmokeResult:
    bootstrap: CtpLiveExecutionClientBootstrapResult
    mapped_submit: CtpMappedOrderCommand
    dry_run: bool
    live_send_armed: bool = False
    matched_execs: list[CtpMatchedExecEvent] | None = None


@dataclass(slots=True)
class CtpPositionQuerySmokeResult:
    bootstrap: CtpLiveExecutionClientBootstrapResult
    query_request_id: str
    query_code: int
    completed: bool
    timed_out: bool
    no_positions: bool
    position_count: int
    positions: tuple[CtpPositionRecord, ...]
    disconnects: list[int]


@dataclass(slots=True)
class CtpAccountQuerySmokeResult:
    bootstrap: CtpLiveExecutionClientBootstrapResult
    query_request_id: str
    query_code: int
    completed: bool
    timed_out: bool
    account: CtpAccountRecord | None
    disconnects: list[int]


@dataclass(slots=True)
class CtpMatchedExecEvent:
    python_client_order_id: str
    native_order_id: str
    native_order_ref: str
    venue_symbol: str
    front_id: int
    session_id: int
    status: int
    callback_source: str
    offset_flag: int
    submit_request_offset_flag: int
    submit_request_offset_source: str
    is_trade: bool
    trade_volume: int
    leaves_qty: int
    match_reason: str
    submit_request_id: int = -1
    submit_request_id_source: str = ""
    response_request_id: int = -1
    response_is_last: bool = False
    response_error_id: int = 0


@dataclass(slots=True)
class CtpTdObservedCallback:
    order_id: str
    order_ref: str
    front_id: int
    session_id: int
    is_trade: bool
    ts_epoch_us: int
    status: int


@dataclass(slots=True)
class CtpTdOrderTruthBaseline:
    flow_path: str
    flow_mode: str
    ready: bool
    login_success: bool | None
    settlement_code: int
    login_front_id: int | None
    login_session_id: int | None
    login_max_order_ref: int | None
    disconnect_count: int
    disconnect_reasons: tuple[int, ...]
    observed_callback_count: int
    observed_order_event_count: int
    observed_trade_event_count: int
    no_callbacks_observed: bool
    first_order_id: str | None
    first_order_ref: str | None
    first_session_id: int | None
    first_front_id: int | None
    first_is_trade: bool | None
    observed_callbacks: tuple[CtpTdObservedCallback, ...] = ()


@dataclass(slots=True)
class CtpTdHistoricalCallbackBoundaryFinding:
    code: str
    severity: str
    action: str
    metric: str
    metric_value: int | str | None
    threshold: int | str | None
    message: str


@dataclass(slots=True)
class CtpTdHistoricalCallbackBoundaryPolicyResult:
    baseline: CtpTdOrderTruthBaseline
    disposition: str
    historical_callback_count: int
    delayed_callback_count: int
    current_session_callback_count: int
    first_historical_order_id: str | None
    first_current_session_order_id: str | None
    findings: tuple[CtpTdHistoricalCallbackBoundaryFinding, ...]


@dataclass(slots=True)
class CtpTdOrderTradeSnapshot:
    baseline: CtpTdOrderTruthBaseline
    disposition: str
    observed_order_event_count: int
    observed_trade_event_count: int
    no_order_events: bool
    no_trade_events: bool
    historical_order_count: int
    historical_trade_count: int
    delayed_order_count: int
    delayed_trade_count: int
    historical_residue_order_count: int
    historical_residue_trade_count: int
    current_session_order_count: int
    current_session_trade_count: int
    first_order_event_id: str | None
    first_trade_event_id: str | None
    first_historical_order_id: str | None
    first_historical_trade_id: str | None
    first_current_session_order_id: str | None
    first_current_session_trade_id: str | None
    findings: tuple[CtpTdHistoricalCallbackBoundaryFinding, ...]


@dataclass(slots=True)
class CtpTdOrderTruthEvidenceMatrix:
    evidence_version: str
    captured_at_utc: str
    account_id: str | None
    disposition: str
    observed_callback_count: int
    historical_callback_count: int
    delayed_callback_count: int
    current_session_callback_count: int
    first_historical_order_id: str | None
    first_current_session_order_id: str | None
    manual_review_codes: tuple[str, ...]
    boundary_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]


@dataclass(slots=True)
class CtpTdExecEventPayload:
    order_id: str
    venue_symbol: str
    order_ref: str
    front_id: int
    session_id: int
    status: int
    is_trade: bool
    trade_price: float
    trade_volume: int
    leaves_qty: int
    error_message: str

    @classmethod
    def from_runtime_event(cls, event: CtpRuntimeEvent) -> "CtpTdExecEventPayload":
        return cls(
            order_id=event.payload.get("order_id", ""),
            venue_symbol=event.venue_symbol or "",
            order_ref=event.payload.get("order_ref", ""),
            front_id=int(event.payload.get("front_id", "0")),
            session_id=int(event.payload.get("session_id", "0")),
            status=int(event.payload.get("status", "0")),
            is_trade=event.kind is CtpRuntimeEventKind.TRADE,
            trade_price=float(event.payload.get("trade_price", "0")),
            trade_volume=int(event.payload.get("trade_volume", "0")),
            leaves_qty=int(event.payload.get("leaves_qty", "0")),
            error_message=event.message or "",
        )


__all__ = [
    "CtpAccountQuerySmokeResult",
    "CtpCancelOrderIntent",
    "CtpClosePositionPlan",
    "CtpExecutionBootstrapResult",
    "CtpExecutionError",
    "CtpLiveExecutionClientBootstrapResult",
    "CtpMappedOrderCommand",
    "CtpMatchedExecEvent",
    "CtpOrderLifecycleSmokeResult",
    "CtpOrderPrecheck",
    "CtpPositionQuerySmokeResult",
    "CtpSubmitOrderIntent",
    "CtpTdBootstrapState",
    "CtpTdExecEventPayload",
    "CtpTdHistoricalCallbackBoundaryFinding",
    "CtpTdHistoricalCallbackBoundaryPolicyResult",
    "CtpTdObservedCallback",
    "CtpTdOrderTradeSnapshot",
    "CtpTdOrderTruthBaseline",
    "CtpTdOrderTruthEvidenceMatrix",
    "CtpTdSessionIdentity",
    "CtpTdSmokeResult",
]
