"""Nautilus-facing CTP live execution client placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

from nautilus_ctp_adapter.native import NativeExecView, NativePositionView, NativeTradingAccountView
from nautilus_ctp_adapter.runtime import (
    CtpAccountRecord,
    CtpPositionRecord,
    CtpRuntimeBridge,
    CtpRuntimeCommand,
    CtpRuntimeCommandKind,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
)

from .config import CtpAdapterConfig, CtpExecutionGuardrails


def _create_td_live_session(flow_path: Path):
    try:
        from ctp_runtime._ctp_runtime import CtpTdLiveSession
    except ImportError as exc:
        raise RuntimeError(
            "PyO3 TD bridge unavailable; run maturin develop or pip install -e . before TD bootstrap smoke"
        ) from exc
    return CtpTdLiveSession(str(flow_path))


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
    matched_execs: list["CtpMatchedExecEvent"] | None = None


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
    is_trade: bool
    trade_volume: int
    leaves_qty: int
    match_reason: str


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


class CtpExecutionClient:
    """Placeholder for Nautilus order routing and reconciliation."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
    ) -> None:
        self._connected = False
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._request_sequence = 0
        self._bootstrap_state = CtpTdBootstrapState()
        self._td_session_identity: CtpTdSessionIdentity | None = None
        self._next_order_ref: int | None = None
        self._native_order_id_aliases: dict[str, str] = {}
        self._native_order_ref_aliases: dict[tuple[int, int, str], str] = {}

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def guardrails(self) -> CtpExecutionGuardrails:
        return self._config.execution_guardrails

    @property
    def bootstrap_state(self) -> CtpTdBootstrapState:
        return self._bootstrap_state

    @property
    def td_session_identity(self) -> CtpTdSessionIdentity | None:
        return self._td_session_identity

    def resolve_td_flow_path(self, flow_path: str | Path | None = None) -> Path:
        return Path(flow_path) if flow_path else self._default_flow_path()

    def bootstrap_execution_mainline(self) -> CtpTdBootstrapState:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        connect_request_id = self._next_request_id("td-connect")
        self._runtime_bridge.submit_command(
            CtpRuntimeCommand(
                kind=CtpRuntimeCommandKind.CONNECT,
                request_id=connect_request_id,
                payload={
                    "channel": "td",
                    "broker_id": self._config.broker_id,
                    "user_id": self._config.user_id,
                    "front": self._config.td_front,
                    "app_id": self._config.app_id,
                    "auth_code_present": "true" if bool(self._config.auth_code) else "false",
                },
            )
        )
        self._bootstrap_state = CtpTdBootstrapState(
            started=True,
            connect_request_id=connect_request_id,
        )
        return self._bootstrap_state

    def run_td_mainline_login_bootstrap(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpExecutionBootstrapResult:
        bootstrap_state = self.bootstrap_execution_mainline()
        td_smoke = self.run_live_td_readiness_smoke(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        return CtpExecutionBootstrapResult(
            bootstrap_state=bootstrap_state,
            td_smoke=td_smoke,
        )

    def bootstrap_live_execution_client_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpLiveExecutionClientBootstrapResult:
        execution_bootstrap = self.run_td_mainline_login_bootstrap(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        self._capture_identity_from_td_smoke(execution_bootstrap.td_smoke)
        ready = (
            execution_bootstrap.bootstrap_state.started
            and bool(execution_bootstrap.td_smoke.login_success)
            and execution_bootstrap.td_smoke.settlement_code == 0
            and self._td_session_identity is not None
        )
        return CtpLiveExecutionClientBootstrapResult(
            execution_bootstrap=execution_bootstrap,
            ready=ready,
            td_session_identity=self._td_session_identity,
        )

    def map_submit_order(
        self,
        intent: CtpSubmitOrderIntent,
    ) -> CtpMappedOrderCommand:
        precheck = self.precheck_debug_order(
            instrument_id=intent.instrument_id,
            side=intent.side,
            quantity=intent.quantity,
            projected_net_position=intent.quantity,
            submit_count_last_minute=0,
            best_bid=intent.limit_price,
            best_ask=intent.limit_price,
            last_price=intent.limit_price,
        )
        if not precheck.allowed:
            return CtpMappedOrderCommand(
                command=None,
                client_order_id=intent.client_order_id,
                order_ref=None,
                front_id=self._td_session_identity.front_id if self._td_session_identity else None,
                session_id=self._td_session_identity.session_id if self._td_session_identity else None,
                error=CtpExecutionError(
                    error_id=9001,
                    error_message="; ".join(precheck.violations),
                ),
            )

        identity = self._require_td_session_identity()
        order_ref = self._allocate_order_ref()
        client_order_id = intent.client_order_id or self._next_request_id("order")
        command = CtpRuntimeCommand(
            kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
            venue_symbol=intent.instrument_id,
            client_order_id=client_order_id,
            request_id=self._next_request_id("submit"),
            payload={
                "channel": "td",
                "side": intent.side.strip().upper(),
                "quantity": str(intent.quantity),
                "limit_price": str(intent.limit_price),
                "position_effect": intent.position_effect,
                "order_type": intent.order_type,
                "time_in_force": intent.time_in_force,
                "order_ref": str(order_ref),
                "front_id": str(identity.front_id),
                "session_id": str(identity.session_id),
            },
        )
        return CtpMappedOrderCommand(
            command=command,
            client_order_id=client_order_id,
            order_ref=order_ref,
            front_id=identity.front_id,
            session_id=identity.session_id,
            error=None,
        )

    def map_cancel_order(
        self,
        intent: CtpCancelOrderIntent,
    ) -> CtpMappedOrderCommand:
        if self.guardrails.enabled and self.guardrails.allowed_instruments:
            if intent.instrument_id not in self.guardrails.allowed_instruments:
                return CtpMappedOrderCommand(
                    command=None,
                    client_order_id=intent.client_order_id,
                    order_ref=intent.order_ref,
                    front_id=intent.front_id,
                    session_id=intent.session_id,
                    error=CtpExecutionError(
                        error_id=9002,
                        error_message=(
                            f"instrument {intent.instrument_id} is not in allowed debug list "
                            f"{self.guardrails.allowed_instruments}"
                        ),
                    ),
                )

        command = CtpRuntimeCommand(
            kind=CtpRuntimeCommandKind.CANCEL_ORDER,
            venue_symbol=intent.instrument_id,
            exchange_id=intent.exchange_id,
            client_order_id=intent.client_order_id,
            request_id=self._next_request_id("cancel"),
            payload={
                "channel": "td",
                "order_ref": str(intent.order_ref),
                "front_id": str(intent.front_id),
                "session_id": str(intent.session_id),
            },
        )
        return CtpMappedOrderCommand(
            command=command,
            client_order_id=intent.client_order_id,
            order_ref=intent.order_ref,
            front_id=intent.front_id,
            session_id=intent.session_id,
            error=None,
        )

    def submit_mapped_order(self, mapped: CtpMappedOrderCommand) -> CtpMappedOrderCommand:
        if mapped.command is None:
            return mapped
        self._runtime_bridge.submit_command(mapped.command)
        return mapped

    def submit_debug_order_mainline(
        self,
        intent: CtpSubmitOrderIntent,
    ) -> CtpMappedOrderCommand:
        return self.submit_mapped_order(self.map_submit_order(intent))

    def cancel_debug_order_mainline(
        self,
        intent: CtpCancelOrderIntent,
    ) -> CtpMappedOrderCommand:
        return self.submit_mapped_order(self.map_cancel_order(intent))

    def run_order_lifecycle_smoke_baseline(
        self,
        *,
        instrument_id: str,
        side: str,
        quantity: int,
        limit_price: float,
        client_order_id: str | None = None,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        dry_run: bool = True,
        time_in_force: str = "GFD",
        order_type: str = "LIMIT",
    ) -> CtpOrderLifecycleSmokeResult:
        live_send_armed = self.guardrails.allow_live_order_smoke and not dry_run
        submit_intent = CtpSubmitOrderIntent(
            instrument_id=instrument_id,
            side=side,
            quantity=quantity,
            limit_price=limit_price,
            client_order_id=client_order_id,
            time_in_force=time_in_force,
            order_type=order_type,
        )
        if not dry_run:
            if not self.guardrails.allow_live_order_smoke:
                raise RuntimeError(
                    "live order smoke requires ExecutionGuardrails.AllowLiveOrderSmoke=true in config"
                )
            return self._run_live_order_lifecycle_smoke(
                submit_intent=submit_intent,
                timeout_seconds=timeout_seconds,
                flow_path=flow_path,
            )

        bootstrap = self.bootstrap_live_execution_client_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        mapped_submit = self.map_submit_order(submit_intent)
        self.submit_mapped_order(mapped_submit)
        return CtpOrderLifecycleSmokeResult(
            bootstrap=bootstrap,
            mapped_submit=mapped_submit,
            dry_run=dry_run,
            live_send_armed=live_send_armed,
            matched_execs=[],
        )

    def run_live_td_readiness_smoke(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpTdSmokeResult:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        session = _create_td_live_session(effective_flow_path)
        state: dict[str, object] = {"login": None, "disconnects": []}

        try:
            session.set_login_callback(lambda resp: self._on_td_login_callback(resp, state))
            session.set_front_disconnected_callback(lambda reason: self._on_td_disconnect(reason, state))

            init_code = session.init(self._config.td_front)
            authenticate_code = session.authenticate(
                self._config.app_id,
                self._config.auth_code,
                self._config.product_info,
            )
            login_code = session.login(
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
            )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and state["login"] is None:
                time.sleep(0.1)

            login = state["login"]
            settlement_code = -1
            if login is not None and login.success:
                settlement_code = session.confirm_settlement()
                self._runtime_bridge.push_event(
                    CtpRuntimeEvent(
                        kind=CtpRuntimeEventKind.SETTLEMENT_CONFIRMED,
                        payload={"channel": "td"},
                    )
                )

            return CtpTdSmokeResult(
                init_code=init_code,
                authenticate_code=authenticate_code,
                login_code=login_code,
                settlement_code=settlement_code,
                login_success=None if login is None else login.success,
                login_error_id=None if login is None else login.error_id,
                login_error_message=None if login is None else login.error_message,
                front_id=None if login is None else login.front_id,
                session_id=None if login is None else login.session_id,
                max_order_ref=None if login is None else login.max_order_ref,
                disconnects=list(state["disconnects"]),
            )
        finally:
            session.dispose()

    def capture_td_order_truth_baseline_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
    ) -> CtpTdOrderTruthBaseline:
        bootstrap_state = self.bootstrap_execution_mainline()
        effective_flow_path = self.resolve_td_flow_path(flow_path)
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        session = _create_td_live_session(effective_flow_path)
        state: dict[str, object] = {
            "login": None,
            "disconnects": [],
            "exec_views": [],
        }

        try:
            session.set_login_callback(lambda resp: self._on_td_login_callback(resp, state))
            session.set_front_disconnected_callback(lambda reason: self._on_td_disconnect(reason, state))
            session.set_exec_callback(lambda exec_view: self._on_td_exec_observation_callback(exec_view, state))

            init_code = session.init(self._config.td_front)
            authenticate_code = session.authenticate(
                self._config.app_id,
                self._config.auth_code,
                self._config.product_info,
            )
            login_code = session.login(
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
            )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and state["login"] is None:
                time.sleep(0.1)

            login = state["login"]
            settlement_code = -1
            ready = False
            if (
                init_code == 0
                and authenticate_code == 0
                and login_code == 0
                and login is not None
                and login.success
            ):
                settlement_code = session.confirm_settlement()
                ready = settlement_code == 0
                if ready:
                    self._runtime_bridge.push_event(
                        CtpRuntimeEvent(
                            kind=CtpRuntimeEventKind.SETTLEMENT_CONFIRMED,
                            payload={"channel": "td"},
                        )
                    )

            if ready:
                observation_deadline = time.time() + max(observation_grace_seconds, 0.1)
                while time.time() < observation_deadline:
                    time.sleep(0.1)

            exec_views: list[NativeExecView] = list(state["exec_views"])
            first_exec = None if not exec_views else exec_views[0]
            return CtpTdOrderTruthBaseline(
                flow_path=str(effective_flow_path),
                flow_mode="explicit_override" if flow_path is not None else "default_shared_flow",
                ready=bool(bootstrap_state.started and ready and self._td_session_identity is not None),
                login_success=None if login is None else login.success,
                settlement_code=settlement_code,
                login_front_id=None if login is None else int(login.front_id),
                login_session_id=None if login is None else int(login.session_id),
                login_max_order_ref=None if login is None else int(login.max_order_ref),
                disconnect_count=len(state["disconnects"]),
                disconnect_reasons=tuple(state["disconnects"]),
                observed_callback_count=len(exec_views),
                observed_order_event_count=sum(1 for exec_view in exec_views if not exec_view.is_trade),
                observed_trade_event_count=sum(1 for exec_view in exec_views if exec_view.is_trade),
                no_callbacks_observed=len(exec_views) == 0,
                first_order_id=None if first_exec is None else self._normalize_native_text(first_exec.order_id) or None,
                first_order_ref=None if first_exec is None else self._normalize_native_text(first_exec.order_ref) or None,
                first_session_id=None if first_exec is None else int(first_exec.session_id),
                first_front_id=None if first_exec is None else int(first_exec.front_id),
                first_is_trade=None if first_exec is None else bool(first_exec.is_trade),
                observed_callbacks=tuple(
                    CtpTdObservedCallback(
                        order_id=self._normalize_native_text(exec_view.order_id),
                        order_ref=self._normalize_native_text(exec_view.order_ref),
                        front_id=int(exec_view.front_id),
                        session_id=int(exec_view.session_id),
                        is_trade=bool(exec_view.is_trade),
                        ts_epoch_us=int(exec_view.ts_epoch_us),
                        status=int(exec_view.status),
                    )
                    for exec_view in exec_views
                ),
            )
        finally:
            session.dispose()

    def evaluate_historical_callback_boundary_policy(
        self,
        baseline: CtpTdOrderTruthBaseline,
    ) -> CtpTdHistoricalCallbackBoundaryPolicyResult:
        findings: list[CtpTdHistoricalCallbackBoundaryFinding] = []

        if not baseline.ready:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="td_order_truth_unready",
                    severity="critical",
                    action="manual_review_required",
                    metric="ready",
                    metric_value=str(baseline.ready),
                    threshold="true",
                    message="TD order truth baseline is not ready enough to classify callback boundaries.",
                )
            )

        if baseline.login_front_id is None or baseline.login_session_id is None:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="missing_login_identity",
                    severity="critical",
                    action="manual_review_required",
                    metric="login_session_identity",
                    metric_value=None,
                    threshold="present",
                    message="Current TD login identity is missing, so callback boundary classification cannot be trusted.",
                )
            )

        historical_callback_count = 0
        delayed_callback_count = 0
        current_session_callback_count = 0
        first_historical_order_id = None
        first_current_session_order_id = None

        for callback in baseline.observed_callbacks:
            same_session = (
                baseline.login_front_id is not None
                and baseline.login_session_id is not None
                and callback.front_id == baseline.login_front_id
                and callback.session_id == baseline.login_session_id
            )
            callback_order_ref = self._parse_native_int(callback.order_ref)
            if not same_session:
                historical_callback_count += 1
                if first_historical_order_id is None:
                    first_historical_order_id = callback.order_id or None
                continue

            if (
                baseline.login_max_order_ref is not None
                and callback_order_ref is not None
                and callback_order_ref <= baseline.login_max_order_ref
            ):
                delayed_callback_count += 1
                if first_historical_order_id is None:
                    first_historical_order_id = callback.order_id or None
                continue

            current_session_callback_count += 1
            if first_current_session_order_id is None:
                first_current_session_order_id = callback.order_id or None

        if baseline.no_callbacks_observed:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="no_callbacks_observed",
                    severity="info",
                    action="evidence_only",
                    metric="observed_callback_count",
                    metric_value=0,
                    threshold="> 0 optional",
                    message="No real callbacks were observed during the live read-only observation window.",
                )
            )

        if historical_callback_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="historical_callbacks_present",
                    severity="warn",
                    action="boundary_required",
                    metric="historical_callback_count",
                    metric_value=historical_callback_count,
                    threshold=0,
                    message="Observed callbacks whose front/session identity does not match the current login truth.",
                )
            )

        if delayed_callback_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="delayed_callbacks_present",
                    severity="warn",
                    action="boundary_required",
                    metric="delayed_callback_count",
                    metric_value=delayed_callback_count,
                    threshold=0,
                    message="Observed callbacks that match the current session but use order refs at or below the login baseline.",
                )
            )

        if current_session_callback_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="current_session_callbacks_present",
                    severity="info",
                    action="evidence_only",
                    metric="current_session_callback_count",
                    metric_value=current_session_callback_count,
                    threshold=0,
                    message="Observed callbacks that belong to the current TD session identity.",
                )
            )

        disposition = "clear"
        if any(finding.action == "manual_review_required" for finding in findings):
            disposition = "manual_review_required"
        elif any(finding.action == "boundary_required" for finding in findings):
            disposition = "boundary_required"
        elif findings:
            disposition = "evidence_only"

        return CtpTdHistoricalCallbackBoundaryPolicyResult(
            baseline=baseline,
            disposition=disposition,
            historical_callback_count=historical_callback_count,
            delayed_callback_count=delayed_callback_count,
            current_session_callback_count=current_session_callback_count,
            first_historical_order_id=first_historical_order_id,
            first_current_session_order_id=first_current_session_order_id,
            findings=tuple(findings),
        )

    def capture_historical_callback_boundary_policy_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
    ) -> CtpTdHistoricalCallbackBoundaryPolicyResult:
        baseline = self.capture_td_order_truth_baseline_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            observation_grace_seconds=observation_grace_seconds,
        )
        return self.evaluate_historical_callback_boundary_policy(baseline)

    def evaluate_order_trade_snapshot(
        self,
        baseline: CtpTdOrderTruthBaseline,
    ) -> CtpTdOrderTradeSnapshot:
        findings: list[CtpTdHistoricalCallbackBoundaryFinding] = []

        if not baseline.ready:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="order_trade_snapshot_unready",
                    severity="critical",
                    action="manual_review_required",
                    metric="ready",
                    metric_value=str(baseline.ready),
                    threshold="true",
                    message="TD order/trade snapshot is not ready enough to classify read-only order/trade evidence.",
                )
            )

        if baseline.login_front_id is None or baseline.login_session_id is None:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="missing_login_identity",
                    severity="critical",
                    action="manual_review_required",
                    metric="login_session_identity",
                    metric_value=None,
                    threshold="present",
                    message="Current TD login identity is missing, so read-only order/trade snapshot cannot be trusted.",
                )
            )

        historical_order_count = 0
        historical_trade_count = 0
        delayed_order_count = 0
        delayed_trade_count = 0
        current_session_order_count = 0
        current_session_trade_count = 0
        first_order_event_id = None
        first_trade_event_id = None
        first_historical_order_id = None
        first_historical_trade_id = None
        first_current_session_order_id = None
        first_current_session_trade_id = None

        for callback in baseline.observed_callbacks:
            if callback.is_trade:
                if first_trade_event_id is None:
                    first_trade_event_id = callback.order_id or None
            elif first_order_event_id is None:
                first_order_event_id = callback.order_id or None

            same_session = (
                baseline.login_front_id is not None
                and baseline.login_session_id is not None
                and callback.front_id == baseline.login_front_id
                and callback.session_id == baseline.login_session_id
            )
            callback_order_ref = self._parse_native_int(callback.order_ref)
            is_delayed = (
                same_session
                and baseline.login_max_order_ref is not None
                and callback_order_ref is not None
                and callback_order_ref <= baseline.login_max_order_ref
            )

            if not same_session:
                if callback.is_trade:
                    historical_trade_count += 1
                    if first_historical_trade_id is None:
                        first_historical_trade_id = callback.order_id or None
                else:
                    historical_order_count += 1
                    if first_historical_order_id is None:
                        first_historical_order_id = callback.order_id or None
                continue

            if is_delayed:
                if callback.is_trade:
                    delayed_trade_count += 1
                    if first_historical_trade_id is None:
                        first_historical_trade_id = callback.order_id or None
                else:
                    delayed_order_count += 1
                    if first_historical_order_id is None:
                        first_historical_order_id = callback.order_id or None
                continue

            if callback.is_trade:
                current_session_trade_count += 1
                if first_current_session_trade_id is None:
                    first_current_session_trade_id = callback.order_id or None
            else:
                current_session_order_count += 1
                if first_current_session_order_id is None:
                    first_current_session_order_id = callback.order_id or None

        if baseline.observed_order_event_count == 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="no_order_events_observed",
                    severity="info",
                    action="evidence_only",
                    metric="observed_order_event_count",
                    metric_value=0,
                    threshold="> 0 optional",
                    message="No order callbacks were observed during the read-only TD snapshot window.",
                )
            )

        if baseline.observed_trade_event_count == 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="no_trade_events_observed",
                    severity="info",
                    action="evidence_only",
                    metric="observed_trade_event_count",
                    metric_value=0,
                    threshold="> 0 optional",
                    message="No trade callbacks were observed during the read-only TD snapshot window.",
                )
            )

        if historical_order_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="historical_order_events_present",
                    severity="warn",
                    action="boundary_required",
                    metric="historical_order_count",
                    metric_value=historical_order_count,
                    threshold=0,
                    message="Observed order callbacks whose front/session identity does not match the current login truth.",
                )
            )

        if historical_trade_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="historical_trade_events_present",
                    severity="warn",
                    action="boundary_required",
                    metric="historical_trade_count",
                    metric_value=historical_trade_count,
                    threshold=0,
                    message="Observed trade callbacks whose front/session identity does not match the current login truth.",
                )
            )

        if delayed_order_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="delayed_order_events_present",
                    severity="warn",
                    action="boundary_required",
                    metric="delayed_order_count",
                    metric_value=delayed_order_count,
                    threshold=0,
                    message="Observed order callbacks that match the current session but use order refs at or below the login baseline.",
                )
            )

        if delayed_trade_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="delayed_trade_events_present",
                    severity="warn",
                    action="boundary_required",
                    metric="delayed_trade_count",
                    metric_value=delayed_trade_count,
                    threshold=0,
                    message="Observed trade callbacks that match the current session but use order refs at or below the login baseline.",
                )
            )

        if current_session_order_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="current_session_order_events_present",
                    severity="info",
                    action="evidence_only",
                    metric="current_session_order_count",
                    metric_value=current_session_order_count,
                    threshold=0,
                    message="Observed order callbacks that belong to the current TD session identity.",
                )
            )

        if current_session_trade_count > 0:
            findings.append(
                CtpTdHistoricalCallbackBoundaryFinding(
                    code="current_session_trade_events_present",
                    severity="info",
                    action="evidence_only",
                    metric="current_session_trade_count",
                    metric_value=current_session_trade_count,
                    threshold=0,
                    message="Observed trade callbacks that belong to the current TD session identity.",
                )
            )

        disposition = "clear"
        if any(finding.action == "manual_review_required" for finding in findings):
            disposition = "manual_review_required"
        elif any(finding.action == "boundary_required" for finding in findings):
            disposition = "boundary_required"
        elif findings:
            disposition = "evidence_only"

        return CtpTdOrderTradeSnapshot(
            baseline=baseline,
            disposition=disposition,
            observed_order_event_count=baseline.observed_order_event_count,
            observed_trade_event_count=baseline.observed_trade_event_count,
            no_order_events=baseline.observed_order_event_count == 0,
            no_trade_events=baseline.observed_trade_event_count == 0,
            historical_order_count=historical_order_count,
            historical_trade_count=historical_trade_count,
            delayed_order_count=delayed_order_count,
            delayed_trade_count=delayed_trade_count,
            historical_residue_order_count=historical_order_count + delayed_order_count,
            historical_residue_trade_count=historical_trade_count + delayed_trade_count,
            current_session_order_count=current_session_order_count,
            current_session_trade_count=current_session_trade_count,
            first_order_event_id=first_order_event_id,
            first_trade_event_id=first_trade_event_id,
            first_historical_order_id=first_historical_order_id,
            first_historical_trade_id=first_historical_trade_id,
            first_current_session_order_id=first_current_session_order_id,
            first_current_session_trade_id=first_current_session_trade_id,
            findings=tuple(findings),
        )

    def capture_td_order_trade_snapshot_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
    ) -> CtpTdOrderTradeSnapshot:
        baseline = self.capture_td_order_truth_baseline_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            observation_grace_seconds=observation_grace_seconds,
        )
        return self.evaluate_order_trade_snapshot(baseline)

    def build_td_order_truth_evidence_matrix(
        self,
        result: CtpTdHistoricalCallbackBoundaryPolicyResult,
    ) -> CtpTdOrderTruthEvidenceMatrix:
        manual_review_codes = tuple(
            finding.code for finding in result.findings if finding.action == "manual_review_required"
        )
        boundary_codes = tuple(
            finding.code for finding in result.findings if finding.action == "boundary_required"
        )
        evidence_only_codes = tuple(
            finding.code for finding in result.findings if finding.action == "evidence_only"
        )
        return CtpTdOrderTruthEvidenceMatrix(
            evidence_version="td-order-truth-evidence-v1",
            captured_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            account_id=self._config.user_id or None,
            disposition=result.disposition,
            observed_callback_count=result.baseline.observed_callback_count,
            historical_callback_count=result.historical_callback_count,
            delayed_callback_count=result.delayed_callback_count,
            current_session_callback_count=result.current_session_callback_count,
            first_historical_order_id=result.first_historical_order_id,
            first_current_session_order_id=result.first_current_session_order_id,
            manual_review_codes=manual_review_codes,
            boundary_codes=boundary_codes,
            evidence_only_codes=evidence_only_codes,
        )

    def capture_td_order_truth_evidence_matrix_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
    ) -> CtpTdOrderTruthEvidenceMatrix:
        result = self.capture_historical_callback_boundary_policy_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            observation_grace_seconds=observation_grace_seconds,
        )
        return self.build_td_order_truth_evidence_matrix(result)

    def run_live_position_query_smoke(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        completion_grace_seconds: float = 1.0,
    ) -> CtpPositionQuerySmokeResult:
        bootstrap = self.bootstrap_live_execution_client_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        if not bootstrap.ready:
            return CtpPositionQuerySmokeResult(
                bootstrap=bootstrap,
                query_request_id="",
                query_code=-1,
                completed=False,
                timed_out=False,
                no_positions=False,
                position_count=0,
                positions=(),
                disconnects=list(bootstrap.execution_bootstrap.td_smoke.disconnects or []),
            )

        request_id = self._next_request_id("query-positions")
        self._runtime_bridge.submit_command(
            CtpRuntimeCommand(
                kind=CtpRuntimeCommandKind.QUERY_POSITIONS,
                request_id=request_id,
                payload={
                    "channel": "td",
                    "query_scope": "positions",
                    "account_id": self._config.user_id,
                },
            )
        )

        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        session = _create_td_live_session(effective_flow_path)
        state: dict[str, object] = {
            "login": None,
            "disconnects": [],
            "position_views": [],
            "last_position_ts": None,
            "positions_complete": False,
        }

        try:
            session.set_login_callback(lambda resp: self._on_td_login_callback(resp, state))
            session.set_front_disconnected_callback(lambda reason: self._on_td_disconnect(reason, state))
            session.set_position_callback(
                lambda position_view, req_id, is_last: self._on_td_position_callback(
                    position_view,
                    request_id=request_id,
                    req_id=req_id,
                    is_last=is_last,
                    state=state,
                ),
            )

            init_code = session.init(self._config.td_front)
            authenticate_code = session.authenticate(
                self._config.app_id,
                self._config.auth_code,
                self._config.product_info,
            )
            login_code = session.login(
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
            )
            if init_code != 0 or authenticate_code != 0 or login_code != 0:
                return CtpPositionQuerySmokeResult(
                    bootstrap=bootstrap,
                    query_request_id=request_id,
                    query_code=-1,
                    completed=False,
                    timed_out=False,
                    no_positions=False,
                    position_count=0,
                    positions=(),
                    disconnects=list(state["disconnects"]),
                )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and state["login"] is None:
                time.sleep(0.1)

            login = state["login"]
            if login is None or not login.success:
                return CtpPositionQuerySmokeResult(
                    bootstrap=bootstrap,
                    query_request_id=request_id,
                    query_code=-1,
                    completed=False,
                    timed_out=True,
                    no_positions=False,
                    position_count=0,
                    positions=(),
                    disconnects=list(state["disconnects"]),
                )

            settlement_code = session.confirm_settlement()
            if settlement_code != 0:
                return CtpPositionQuerySmokeResult(
                    bootstrap=bootstrap,
                    query_request_id=request_id,
                    query_code=-1,
                    completed=False,
                    timed_out=False,
                    no_positions=False,
                    position_count=0,
                    positions=(),
                    disconnects=list(state["disconnects"]),
                )

            query_code = session.qry_position()
            while time.time() < deadline:
                if state["positions_complete"]:
                    break
                time.sleep(0.1)

            timed_out = not bool(state["positions_complete"]) and time.time() >= deadline
            self._runtime_bridge.push_event(
                CtpRuntimeEvent(
                    kind=CtpRuntimeEventKind.POSITION,
                    request_id=request_id,
                    payload={
                        "snapshot_complete": "true",
                        "snapshot_empty": "true" if not state["position_views"] else "false",
                        "query_code": str(query_code),
                    },
                )
            )
            positions = self._runtime_bridge.query.positions_for_request(request_id)
            return CtpPositionQuerySmokeResult(
                bootstrap=bootstrap,
                query_request_id=request_id,
                query_code=query_code,
                completed=self._runtime_bridge.query.is_query_completed(request_id),
                timed_out=timed_out,
                no_positions=len(positions) == 0 and query_code == 0,
                position_count=len(positions),
                positions=positions,
                disconnects=list(state["disconnects"]),
            )
        finally:
            session.dispose()

    def run_live_account_query_smoke(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpAccountQuerySmokeResult:
        bootstrap = self.bootstrap_live_execution_client_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        if not bootstrap.ready:
            return CtpAccountQuerySmokeResult(
                bootstrap=bootstrap,
                query_request_id="",
                query_code=-1,
                completed=False,
                timed_out=False,
                account=None,
                disconnects=list(bootstrap.execution_bootstrap.td_smoke.disconnects or []),
            )

        request_id = self._next_request_id("query-account")
        self._runtime_bridge.submit_command(
            CtpRuntimeCommand(
                kind=CtpRuntimeCommandKind.QUERY_ACCOUNT,
                request_id=request_id,
                payload={
                    "channel": "td",
                    "query_scope": "account",
                    "account_id": self._config.user_id,
                },
            )
        )

        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        session = _create_td_live_session(effective_flow_path)
        state: dict[str, object] = {
            "login": None,
            "disconnects": [],
            "account_view": None,
        }

        try:
            session.set_login_callback(lambda resp: self._on_td_login_callback(resp, state))
            session.set_front_disconnected_callback(lambda reason: self._on_td_disconnect(reason, state))
            session.set_account_callback(
                lambda account_view: self._on_td_account_callback(
                    account_view,
                    request_id=request_id,
                    state=state,
                ),
            )

            init_code = session.init(self._config.td_front)
            authenticate_code = session.authenticate(
                self._config.app_id,
                self._config.auth_code,
                self._config.product_info,
            )
            login_code = session.login(
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
            )
            if init_code != 0 or authenticate_code != 0 or login_code != 0:
                return CtpAccountQuerySmokeResult(
                    bootstrap=bootstrap,
                    query_request_id=request_id,
                    query_code=-1,
                    completed=False,
                    timed_out=False,
                    account=None,
                    disconnects=list(state["disconnects"]),
                )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and state["login"] is None:
                time.sleep(0.1)

            login = state["login"]
            if login is None or not login.success:
                return CtpAccountQuerySmokeResult(
                    bootstrap=bootstrap,
                    query_request_id=request_id,
                    query_code=-1,
                    completed=False,
                    timed_out=True,
                    account=None,
                    disconnects=list(state["disconnects"]),
                )

            settlement_code = session.confirm_settlement()
            if settlement_code != 0:
                return CtpAccountQuerySmokeResult(
                    bootstrap=bootstrap,
                    query_request_id=request_id,
                    query_code=-1,
                    completed=False,
                    timed_out=False,
                    account=None,
                    disconnects=list(state["disconnects"]),
                )

            query_code = session.qry_account()
            while time.time() < deadline and state["account_view"] is None:
                time.sleep(0.1)

            account = self._runtime_bridge.query.account_for_request(request_id)
            return CtpAccountQuerySmokeResult(
                bootstrap=bootstrap,
                query_request_id=request_id,
                query_code=query_code,
                completed=self._runtime_bridge.query.is_query_completed(request_id),
                timed_out=state["account_view"] is None,
                account=account,
                disconnects=list(state["disconnects"]),
            )
        finally:
            session.dispose()

    def select_level1_price(
        self,
        *,
        side: str,
        best_bid: float | None,
        best_ask: float | None,
        last_price: float | None = None,
    ) -> float | None:
        normalized_side = side.strip().upper()
        if normalized_side == "BUY":
            return best_ask if best_ask is not None else best_bid if best_bid is not None else last_price
        if normalized_side == "SELL":
            return best_bid if best_bid is not None else best_ask if best_ask is not None else last_price
        raise ValueError(f"Unsupported side: {side}")

    def precheck_debug_order(
        self,
        *,
        instrument_id: str,
        side: str,
        quantity: int,
        projected_net_position: int,
        submit_count_last_minute: int,
        best_bid: float | None,
        best_ask: float | None,
        last_price: float | None = None,
    ) -> CtpOrderPrecheck:
        violations: list[str] = []
        guardrails = self.guardrails

        if guardrails.enabled:
            if guardrails.allowed_instruments and instrument_id not in guardrails.allowed_instruments:
                violations.append(
                    f"instrument {instrument_id} is not in allowed debug list {guardrails.allowed_instruments}"
                )
            if quantity <= 0 or (guardrails.max_order_qty and quantity > guardrails.max_order_qty):
                violations.append(f"quantity {quantity} exceeds max_order_qty {guardrails.max_order_qty}")
            if guardrails.max_net_position and abs(projected_net_position) > guardrails.max_net_position:
                violations.append(
                    f"projected_net_position {projected_net_position} exceeds max_net_position "
                    f"{guardrails.max_net_position}"
                )
            if (
                guardrails.max_submit_per_minute
                and submit_count_last_minute >= guardrails.max_submit_per_minute
            ):
                violations.append(
                    f"submit_count_last_minute {submit_count_last_minute} exceeds limit "
                    f"{guardrails.max_submit_per_minute}"
                )
            if guardrails.price_mode != "best_level_1":
                violations.append(f"unsupported price_mode {guardrails.price_mode}")

        selected_price = None
        if not violations:
            selected_price = self.select_level1_price(
                side=side,
                best_bid=best_bid,
                best_ask=best_ask,
                last_price=last_price,
            )
            if selected_price is None:
                violations.append("level_1_price_unavailable")

        return CtpOrderPrecheck(
            allowed=not violations,
            violations=violations,
            selected_price=selected_price,
        )

    def _repository_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    def _next_request_id(self, prefix: str) -> str:
        self._request_sequence += 1
        return f"{prefix}-{self._request_sequence}"

    def _allocate_order_ref(self) -> int:
        identity = self._require_td_session_identity()
        if self._next_order_ref is None:
            self._next_order_ref = identity.max_order_ref + 1
        order_ref = self._next_order_ref
        self._next_order_ref += 1
        return order_ref

    def _capture_identity_from_td_smoke(self, td_smoke: CtpTdSmokeResult) -> None:
        if not td_smoke.login_success:
            return
        if td_smoke.front_id is None or td_smoke.session_id is None or td_smoke.max_order_ref is None:
            return
        self._td_session_identity = CtpTdSessionIdentity(
            front_id=int(td_smoke.front_id),
            session_id=int(td_smoke.session_id),
            max_order_ref=int(td_smoke.max_order_ref),
        )
        if self._next_order_ref is None or self._next_order_ref <= self._td_session_identity.max_order_ref:
            self._next_order_ref = self._td_session_identity.max_order_ref + 1

    def _require_td_session_identity(self) -> CtpTdSessionIdentity:
        if self._td_session_identity is None:
            raise RuntimeError("td session identity unavailable; login bootstrap must complete first")
        return self._td_session_identity

    def _default_flow_path(self) -> Path:
        return self._repository_root() / "var" / "td_flow_smoke"

    def _default_live_order_flow_path(self) -> Path:
        return self._repository_root() / "output" / "debug" / f"live_order_smoke_{time.time_ns()}"

    def _run_live_order_lifecycle_smoke(
        self,
        *,
        submit_intent: CtpSubmitOrderIntent,
        timeout_seconds: int,
        flow_path: str | Path | None,
    ) -> CtpOrderLifecycleSmokeResult:
        bootstrap_state = self.bootstrap_execution_mainline()
        effective_flow_path = Path(flow_path) if flow_path else self._default_live_order_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        session = _create_td_live_session(effective_flow_path)
        state: dict[str, object] = {
            "login": None,
            "disconnects": [],
            "exec_views": [],
            "matched_exec_views": [],
            "matched_exec_events": [],
            "pre_send_exec_view_count": 0,
            "expected_client_order_id": None,
            "expected_order_ref": None,
            "expected_instrument_id": None,
            "expected_quantity": None,
        }

        try:
            session.set_login_callback(lambda resp: self._on_td_login_callback(resp, state))
            session.set_front_disconnected_callback(lambda reason: self._on_td_disconnect(reason, state))
            session.set_exec_callback(lambda exec_view: self._on_td_exec_callback_with_state(exec_view, state))

            init_code = session.init(self._config.td_front)
            authenticate_code = session.authenticate(
                self._config.app_id,
                self._config.auth_code,
                self._config.product_info,
            )
            login_code = session.login(
                self._config.broker_id,
                self._config.user_id,
                self._config.password,
            )

            deadline = time.time() + timeout_seconds
            while time.time() < deadline and state["login"] is None:
                time.sleep(0.1)

            login = state["login"]
            settlement_code = -1
            if login is not None and login.success:
                settlement_code = session.confirm_settlement()
                self._runtime_bridge.push_event(
                    CtpRuntimeEvent(
                        kind=CtpRuntimeEventKind.SETTLEMENT_CONFIRMED,
                        payload={"channel": "td"},
                    )
                )

            td_smoke = CtpTdSmokeResult(
                init_code=init_code,
                authenticate_code=authenticate_code,
                login_code=login_code,
                settlement_code=settlement_code,
                login_success=None if login is None else login.success,
                login_error_id=None if login is None else login.error_id,
                login_error_message=None if login is None else login.error_message,
                front_id=None if login is None else login.front_id,
                session_id=None if login is None else login.session_id,
                max_order_ref=None if login is None else login.max_order_ref,
                disconnects=list(state["disconnects"]),
            )
            self._capture_identity_from_td_smoke(td_smoke)
            bootstrap = CtpLiveExecutionClientBootstrapResult(
                execution_bootstrap=CtpExecutionBootstrapResult(
                    bootstrap_state=bootstrap_state,
                    td_smoke=td_smoke,
                ),
                ready=(
                    bootstrap_state.started
                    and bool(td_smoke.login_success)
                    and td_smoke.settlement_code == 0
                    and self._td_session_identity is not None
                ),
                td_session_identity=self._td_session_identity,
            )
            mapped_submit = self.map_submit_order(submit_intent)
            if mapped_submit.error is not None or mapped_submit.command is None:
                return CtpOrderLifecycleSmokeResult(
                    bootstrap=bootstrap,
                    mapped_submit=mapped_submit,
                    dry_run=False,
                    live_send_armed=True,
                    matched_execs=[],
                )

            state["expected_client_order_id"] = mapped_submit.client_order_id
            state["expected_order_ref"] = None if mapped_submit.order_ref is None else str(mapped_submit.order_ref)
            state["expected_instrument_id"] = submit_intent.instrument_id
            state["expected_quantity"] = submit_intent.quantity
            state["pre_send_exec_view_count"] = len(state["exec_views"])
            self.submit_mapped_order(mapped_submit)
            native_code = session.order_send(
                order_id=str(mapped_submit.order_ref),
                symbol=submit_intent.instrument_id,
                price=submit_intent.limit_price,
                qty=submit_intent.quantity,
                side=self._native_side_value(submit_intent.side),
                order_type=self._native_order_type_value(submit_intent.order_type),
                comb_offset=self._native_comb_offset_value(submit_intent.position_effect),
                comb_hedge=self._native_comb_hedge_value(),
                time_condition=self._native_time_condition_value(submit_intent.time_in_force),
                volume_condition=self._native_volume_condition_value(submit_intent.time_in_force),
                contingent_condition=self._native_contingent_condition_value(),
                stop_price=0.0,
                force_close_reason=self._native_force_close_reason_value(),
                min_volume=1,
            )
            if native_code != 0:
                raise RuntimeError(f"TdOrderSend failed with native code {native_code}")

            while time.time() < deadline and not state["matched_exec_views"]:
                time.sleep(0.1)

            if not state["matched_exec_views"]:
                raise RuntimeError("live order send did not produce matching exec callback within timeout")

            return CtpOrderLifecycleSmokeResult(
                bootstrap=bootstrap,
                mapped_submit=mapped_submit,
                dry_run=False,
                live_send_armed=True,
                matched_execs=list(state["matched_exec_events"]),
            )
        finally:
            session.dispose()

    def _normalize_native_text(self, value: str | None) -> str:
        return "" if value is None else value.strip()

    def _normalize_symbol(self, value: str | None) -> str:
        return self._normalize_native_text(value).upper()

    def _native_order_ref_key(self, exec_view: NativeExecView) -> tuple[int, int, str] | None:
        normalized_order_ref = self._normalize_native_text(exec_view.order_ref)
        if not normalized_order_ref:
            return None
        return (int(exec_view.front_id), int(exec_view.session_id), normalized_order_ref)

    def _parse_native_int(self, value: str | None) -> int | None:
        normalized_value = self._normalize_native_text(value)
        if not normalized_value or not normalized_value.isdigit():
            return None
        return int(normalized_value)

    def _lookup_native_exec_alias(self, exec_view: NativeExecView) -> str | None:
        normalized_order_id = self._normalize_native_text(exec_view.order_id)
        if normalized_order_id and normalized_order_id in self._native_order_id_aliases:
            return self._native_order_id_aliases[normalized_order_id]

        order_ref_key = self._native_order_ref_key(exec_view)
        if order_ref_key is not None and order_ref_key in self._native_order_ref_aliases:
            return self._native_order_ref_aliases[order_ref_key]
        return None

    def _register_native_exec_alias(self, exec_view: NativeExecView, python_client_order_id: str) -> None:
        normalized_order_id = self._normalize_native_text(exec_view.order_id)
        if normalized_order_id:
            self._native_order_id_aliases[normalized_order_id] = python_client_order_id

        order_ref_key = self._native_order_ref_key(exec_view)
        if order_ref_key is not None:
            self._native_order_ref_aliases[order_ref_key] = python_client_order_id

    def _match_exec_callback_reason(
        self,
        exec_view: NativeExecView,
        *,
        state: dict[str, object],
    ) -> tuple[str | None, str | None]:
        aliased_client_order_id = self._lookup_native_exec_alias(exec_view)
        expected_client_order_id = self._normalize_native_text(str(state.get("expected_client_order_id") or ""))
        expected_order_ref = self._normalize_native_text(str(state.get("expected_order_ref") or ""))
        expected_instrument_id = self._normalize_symbol(str(state.get("expected_instrument_id") or ""))
        expected_quantity = state.get("expected_quantity")
        exec_order_id = self._normalize_native_text(exec_view.order_id)
        exec_order_ref = self._normalize_native_text(exec_view.order_ref)
        is_post_send_callback = len(state["exec_views"]) > int(state.get("pre_send_exec_view_count") or 0)
        login = state.get("login")
        login_max_order_ref = None if login is None else self._parse_native_int(str(getattr(login, "max_order_ref", "") or ""))
        exec_order_id_numeric = self._parse_native_int(exec_order_id)

        if aliased_client_order_id:
            return aliased_client_order_id, "native_alias"
        if expected_client_order_id and exec_order_id == expected_client_order_id:
            return expected_client_order_id, "client_order_id_echo"
        if expected_order_ref and exec_order_ref == expected_order_ref:
            return expected_client_order_id or expected_order_ref, "order_ref_echo"
        if (
            is_post_send_callback
            and expected_client_order_id
            and expected_instrument_id
            and self._normalize_symbol(exec_view.symbol) == expected_instrument_id
            and (expected_quantity is None or int(exec_view.qty) == int(expected_quantity))
        ):
            if login_max_order_ref is not None and exec_order_id_numeric is not None:
                if exec_order_id_numeric > login_max_order_ref:
                    return expected_client_order_id, "post_send_native_order_id_boundary"
                return None, None
            return expected_client_order_id, "post_send_symbol_qty"
        return None, None

    def _native_side_value(self, side: str) -> int:
        normalized_side = side.strip().upper()
        if normalized_side == "BUY":
            return 0
        if normalized_side == "SELL":
            return 1
        raise ValueError(f"Unsupported side: {side}")

    def _native_order_type_value(self, order_type: str) -> int:
        normalized_order_type = order_type.strip().upper()
        if normalized_order_type == "LIMIT":
            return 0
        if normalized_order_type == "MARKET":
            return 1
        raise ValueError(f"Unsupported order_type: {order_type}")

    def _native_comb_offset_value(self, position_effect: str) -> str:
        normalized_position_effect = position_effect.strip().upper()
        if normalized_position_effect == "OPEN":
            return "0"
        raise ValueError(f"Unsupported position_effect: {position_effect}")

    def _native_comb_hedge_value(self) -> str:
        return "1"

    def _native_time_condition_value(self, time_in_force: str) -> int:
        normalized_time_in_force = time_in_force.strip().upper()
        if normalized_time_in_force == "GFD":
            return 3
        if normalized_time_in_force == "IOC":
            return 1
        raise ValueError(f"Unsupported time_in_force: {time_in_force}")

    def _native_volume_condition_value(self, time_in_force: str) -> int:
        normalized_time_in_force = time_in_force.strip().upper()
        if normalized_time_in_force in {"GFD", "IOC"}:
            return 1
        raise ValueError(f"Unsupported time_in_force: {time_in_force}")

    def _native_contingent_condition_value(self) -> int:
        return 1

    def _native_force_close_reason_value(self) -> int:
        return 0

    def _native_position_direction_value(self, pos_direction: int) -> str:
        if int(pos_direction) == 2:
            return "LONG"
        if int(pos_direction) == 3:
            return "SHORT"
        return "UNKNOWN"

    def _on_td_login_callback(self, response, state: dict[str, object]) -> None:
        state["login"] = response
        self._td_session_identity = CtpTdSessionIdentity(
            front_id=int(response.front_id),
            session_id=int(response.session_id),
            max_order_ref=int(response.max_order_ref),
        )
        self._next_order_ref = self._td_session_identity.max_order_ref + 1
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=(
                    CtpRuntimeEventKind.LOGIN_SUCCEEDED
                    if response.success
                    else CtpRuntimeEventKind.LOGIN_FAILED
                ),
                message=response.error_message,
                payload={
                    "channel": "td",
                    "front_id": str(response.front_id),
                    "session_id": str(response.session_id),
                    "max_order_ref": str(response.max_order_ref),
                    "error_id": str(response.error_id),
                },
            )
        )

    def _on_td_disconnect(self, reason: int, state: dict[str, object]) -> None:
        state["disconnects"].append(reason)
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.DISCONNECTED,
                message=f"td_disconnected:{reason}",
                payload={"channel": "td"},
            )
        )

    def _on_td_position_callback(
        self,
        position_view: NativePositionView | None,
        *,
        request_id: str,
        req_id: int,
        is_last: bool,
        state: dict[str, object],
    ) -> None:
        if position_view is not None:
            state["position_views"].append(position_view)
            state["last_position_ts"] = time.time()
            self._runtime_bridge.push_event(
                CtpRuntimeEvent(
                    kind=CtpRuntimeEventKind.POSITION,
                    request_id=request_id,
                    venue_symbol=position_view.symbol,
                    payload={
                        "broker_id": position_view.broker_id,
                        "investor_id": position_view.investor_id,
                        "direction": self._native_position_direction_value(position_view.pos_direction),
                        "hedge_flag": str(position_view.hedge_flag),
                        "date_type": str(position_view.date_type),
                        "position_qty": str(position_view.position),
                        "yd_position_qty": str(position_view.yd_position),
                        "td_position_qty": str(position_view.today_position),
                        "position_cost": str(position_view.position_cost),
                        "open_cost": str(position_view.open_cost),
                        "exchange_margin": str(position_view.exchange_margin),
                        "use_margin": str(position_view.use_margin),
                        "position_profit": str(position_view.position_profit),
                        "ts_epoch_us": str(position_view.ts_epoch_us),
                        "snapshot_complete": "false",
                        "callback_request_id": str(req_id),
                        "is_last": str(is_last).lower(),
                    },
                )
            )
        if is_last:
            state["positions_complete"] = True
            if state["last_position_ts"] is None:
                state["last_position_ts"] = time.time()

    def _on_td_account_callback(
        self,
        account_view: NativeTradingAccountView,
        *,
        request_id: str,
        state: dict[str, object],
    ) -> None:
        state["account_view"] = account_view
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.ACCOUNT,
                request_id=request_id,
                payload={
                    "broker_id": account_view.broker_id,
                    "account_id": account_view.account_id,
                    "balance": str(account_view.balance),
                    "available": str(account_view.available),
                    "withdraw_quota": str(account_view.withdraw_quota),
                    "margin": str(account_view.curr_margin),
                    "frozen_margin": str(account_view.frozen_margin),
                    "commission": str(account_view.commission),
                    "frozen_commission": str(account_view.frozen_commission),
                    "position_profit": str(account_view.position_profit),
                    "close_profit": str(account_view.close_profit),
                    "currency_id": account_view.currency_id,
                    "ts_epoch_us": str(account_view.ts_epoch_us),
                },
            )
        )

    def _on_td_exec_callback(
        self,
        exec_view: NativeExecView,
        *,
        client_order_id: str | None = None,
        match_reason: str | None = None,
    ) -> None:
        event_kind = CtpRuntimeEventKind.TRADE if exec_view.is_trade else CtpRuntimeEventKind.ORDER
        resolved_client_order_id = (
            client_order_id
            or self._lookup_native_exec_alias(exec_view)
            or self._normalize_native_text(exec_view.order_id)
            or None
        )
        self._runtime_bridge.push_event(
            CtpRuntimeEvent(
                kind=event_kind,
                venue_symbol=exec_view.symbol,
                client_order_id=resolved_client_order_id,
                message=exec_view.error_msg or None,
                payload={
                    "channel": "td",
                    "order_id": exec_view.order_id,
                    "order_ref": exec_view.order_ref,
                    "native_order_id": exec_view.order_id,
                    "native_order_ref": exec_view.order_ref,
                    "front_id": str(exec_view.front_id),
                    "session_id": str(exec_view.session_id),
                    "status": str(exec_view.status),
                    "trade_price": str(exec_view.trade_price),
                    "trade_volume": str(exec_view.trade_volume),
                    "leaves_qty": str(exec_view.leaves_qty),
                    "side": str(exec_view.side),
                    "direction": str(exec_view.direction),
                    "offset_flag": str(exec_view.offset_flag),
                    "hedge_flag": str(exec_view.hedge_flag),
                    "match_reason": match_reason or "",
                },
            )
        )

    def _on_td_exec_callback_with_state(self, exec_view: NativeExecView, state: dict[str, object]) -> None:
        state["exec_views"].append(exec_view)
        matched_client_order_id, match_reason = self._match_exec_callback_reason(exec_view, state=state)
        if matched_client_order_id and match_reason:
            self._register_native_exec_alias(exec_view, matched_client_order_id)
            state["matched_exec_views"].append(exec_view)
            state["matched_exec_events"].append(
                CtpMatchedExecEvent(
                    python_client_order_id=matched_client_order_id,
                    native_order_id=self._normalize_native_text(exec_view.order_id),
                    native_order_ref=self._normalize_native_text(exec_view.order_ref),
                    venue_symbol=exec_view.symbol,
                    front_id=int(exec_view.front_id),
                    session_id=int(exec_view.session_id),
                    status=int(exec_view.status),
                    is_trade=bool(exec_view.is_trade),
                    trade_volume=int(exec_view.trade_volume),
                    leaves_qty=int(exec_view.leaves_qty),
                    match_reason=match_reason,
                )
            )
        self._on_td_exec_callback(
            exec_view,
            client_order_id=matched_client_order_id,
            match_reason=match_reason,
        )

    def _on_td_exec_observation_callback(self, exec_view: NativeExecView, state: dict[str, object]) -> None:
        state["exec_views"].append(exec_view)
        self._on_td_exec_callback(exec_view)
