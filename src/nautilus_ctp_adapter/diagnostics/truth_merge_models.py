from __future__ import annotations

from dataclasses import dataclass

from nautilus_ctp_adapter.adapters.ctp.query_adapter import (
    CtpAccountQueryBaseline,
    CtpPositionQueryBaseline,
)

from .td_models import CtpTdOrderTruthEvidenceMatrix


@dataclass(slots=True)
class CtpTdTruthMergeSnapshot:
    order_truth: CtpTdOrderTruthEvidenceMatrix
    positions: CtpPositionQueryBaseline
    account: CtpAccountQueryBaseline


@dataclass(slots=True)
class CtpTdMergedReconciliationFinding:
    code: str
    severity: str
    action: str
    metric: str
    metric_value: float | int | str | None
    threshold: float | int | str | None
    message: str


@dataclass(slots=True)
class CtpTdMergedReconciliationPolicyResult:
    snapshot: CtpTdTruthMergeSnapshot
    disposition: str
    available_ratio: float | None
    margin_ratio: float | None
    findings: tuple[CtpTdMergedReconciliationFinding, ...]


@dataclass(slots=True)
class CtpTdMergedEvidenceMatrix:
    evidence_version: str
    captured_at_utc: str
    account_id: str | None
    disposition: str
    position_count: int
    observed_callback_count: int
    historical_callback_count: int
    current_session_callback_count: int
    available_ratio: float | None
    margin_ratio: float | None
    manual_review_codes: tuple[str, ...]
    boundary_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]


__all__ = [
    "CtpTdMergedEvidenceMatrix",
    "CtpTdMergedReconciliationFinding",
    "CtpTdMergedReconciliationPolicyResult",
    "CtpTdTruthMergeSnapshot",
]
