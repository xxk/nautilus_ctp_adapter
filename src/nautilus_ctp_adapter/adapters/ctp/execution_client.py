"""Nautilus-facing CTP live execution client placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

from nautilus_ctp_adapter.native import CtpTdApi
from nautilus_ctp_adapter.runtime import CtpRuntimeBridge, CtpRuntimeEvent, CtpRuntimeEventKind

from .config import CtpAdapterConfig, CtpExecutionGuardrails


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

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def guardrails(self) -> CtpExecutionGuardrails:
        return self._config.execution_guardrails

    def run_live_td_readiness_smoke(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpTdSmokeResult:
        missing = self._config.validate()
        if missing:
            raise ValueError(f"missing config fields: {missing}")

        api = CtpTdApi.load(self._repository_root())
        effective_flow_path = Path(flow_path) if flow_path else self._default_flow_path()
        effective_flow_path.mkdir(parents=True, exist_ok=True)
        handle = api.create(effective_flow_path)
        state: dict[str, object] = {"login": None, "disconnects": []}

        try:
            api.set_login_callback(handle, lambda resp: self._on_td_login_callback(resp, state))
            api.set_front_disconnected_callback(handle, lambda reason: self._on_td_disconnect(reason, state))

            init_code = api.init(handle, self._config.td_front)
            authenticate_code = api.authenticate(
                handle,
                self._config.app_id,
                self._config.auth_code,
                self._config.product_info,
            )
            login_code = api.login(
                handle,
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
                settlement_code = api.confirm_settlement(handle)
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
            api.dispose(handle)

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

    def _default_flow_path(self) -> Path:
        return self._repository_root() / "var" / "td_flow_smoke"

    def _on_td_login_callback(self, response, state: dict[str, object]) -> None:
        state["login"] = response
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
