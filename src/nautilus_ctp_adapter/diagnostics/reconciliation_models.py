from __future__ import annotations

from dataclasses import dataclass

from nautilus_ctp_adapter.adapters.ctp.query_adapter import CtpQueryAdapterSnapshot


@dataclass(slots=True)
class CtpReconciliationSymbolExposure:
    venue_symbol: str
    exchange_id: str | None
    long_qty: int
    short_qty: int
    gross_qty: int
    net_qty: int
    abs_net_qty: int
    position_cost: float


@dataclass(slots=True)
class CtpReconciliationSnapshot:
    query_snapshot: CtpQueryAdapterSnapshot


@dataclass(slots=True)
class CtpReconciliationSummary:
    position_request_id: str
    account_request_id: str
    account_id: str | None
    position_line_count: int
    symbol_count: int
    total_long_qty: int
    total_short_qty: int
    gross_position_qty: int
    total_position_cost: float
    account_balance: float | None
    account_available: float | None
    account_margin: float | None
    available_ratio: float | None
    margin_ratio: float | None
    dominant_exposure_symbol: str | None
    dominant_exposure_exchange: str | None
    dominant_exposure_abs_net_qty: int
    exposures: tuple[CtpReconciliationSymbolExposure, ...]


@dataclass(slots=True)
class CtpReconciliationPolicyFinding:
    code: str
    severity: str
    action: str
    metric: str
    metric_value: float | int | str | None
    threshold: float | int | str | None
    message: str


@dataclass(slots=True)
class CtpReconciliationPolicyResult:
    summary: CtpReconciliationSummary
    disposition: str
    requires_manual_review: bool
    findings: tuple[CtpReconciliationPolicyFinding, ...]


@dataclass(slots=True)
class CtpReconciliationEvidence:
    evidence_version: str
    captured_at_utc: str
    account_id: str | None
    disposition: str
    requires_manual_review: bool
    finding_count: int
    manual_review_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]
    position_line_count: int
    symbol_count: int
    gross_position_qty: int
    available_ratio: float | None
    margin_ratio: float | None
    dominant_exposure_symbol: str | None
    dominant_exposure_abs_net_qty: int
    top_exposures: tuple[CtpReconciliationSymbolExposure, ...]


__all__ = [
    "CtpReconciliationEvidence",
    "CtpReconciliationPolicyFinding",
    "CtpReconciliationPolicyResult",
    "CtpReconciliationSnapshot",
    "CtpReconciliationSummary",
    "CtpReconciliationSymbolExposure",
]
