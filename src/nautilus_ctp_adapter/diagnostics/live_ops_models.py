from __future__ import annotations

from dataclasses import dataclass

from .md_models import CtpMdTruthEvidenceMatrix
from .reconciliation_models import CtpReconciliationEvidence
from .startup_models import CtpStartupTruthEvidenceMatrix
from .truth_merge_models import CtpTdMergedEvidenceMatrix


@dataclass(slots=True)
class CtpLiveOpsSnapshot:
    startup_truth: CtpStartupTruthEvidenceMatrix
    md_truth: CtpMdTruthEvidenceMatrix
    td_truth: CtpTdMergedEvidenceMatrix
    reconciliation: CtpReconciliationEvidence


@dataclass(slots=True)
class CtpLiveOpsSnapshotSummary:
    baseline: str
    account_id: str | None
    symbol: str | None
    startup_disposition: str
    md_disposition: str
    td_disposition: str
    reconciliation_disposition: str
    startup_shared_flow_reuse_allowed: bool
    startup_session_rotated: bool
    md_restore_succeeded: bool
    position_count: int
    observed_callback_count: int
    historical_callback_count: int
    current_session_callback_count: int
    available_ratio: float | None
    margin_ratio: float | None
    manual_review_codes: tuple[str, ...]
    rebuild_required_codes: tuple[str, ...]
    restore_required_codes: tuple[str, ...]
    boundary_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]


@dataclass(slots=True)
class CtpLiveOpsPolicyFinding:
    code: str
    severity: str
    action: str
    metric: str
    metric_value: float | int | str | bool | None
    threshold: float | int | str | bool | None
    message: str


@dataclass(slots=True)
class CtpLiveOpsPolicyResult:
    summary: CtpLiveOpsSnapshotSummary
    disposition: str
    findings: tuple[CtpLiveOpsPolicyFinding, ...]


@dataclass(slots=True)
class CtpLiveOpsEvidenceMatrix:
    evidence_version: str
    account_id: str | None
    symbol: str | None
    disposition: str
    startup_disposition: str
    md_disposition: str
    td_disposition: str
    reconciliation_disposition: str
    startup_shared_flow_reuse_allowed: bool
    startup_session_rotated: bool
    md_restore_succeeded: bool
    position_count: int
    observed_callback_count: int
    historical_callback_count: int
    current_session_callback_count: int
    available_ratio: float | None
    margin_ratio: float | None
    manual_review_codes: tuple[str, ...]
    rebuild_required_codes: tuple[str, ...]
    restore_required_codes: tuple[str, ...]
    boundary_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]


__all__ = [
    "CtpLiveOpsEvidenceMatrix",
    "CtpLiveOpsPolicyFinding",
    "CtpLiveOpsPolicyResult",
    "CtpLiveOpsSnapshot",
    "CtpLiveOpsSnapshotSummary",
]
