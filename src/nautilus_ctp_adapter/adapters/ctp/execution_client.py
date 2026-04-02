"""Nautilus-facing CTP live execution client placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from .config import CtpAdapterConfig, CtpExecutionGuardrails


@dataclass(slots=True)
class CtpOrderPrecheck:
    allowed: bool
    violations: list[str]
    selected_price: float | None


class CtpExecutionClient:
    """Placeholder for Nautilus order routing and reconciliation."""

    def __init__(self, config: CtpAdapterConfig | None = None) -> None:
        self._connected = False
        self._config = config or CtpAdapterConfig()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def guardrails(self) -> CtpExecutionGuardrails:
        return self._config.execution_guardrails

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
