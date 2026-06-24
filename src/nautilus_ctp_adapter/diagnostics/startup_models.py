from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CtpTdStartupTruthEvidence:
    flow_path: str
    flow_mode: str
    ready: bool
    login_success: bool | None
    settlement_code: int
    front_id: int | None
    session_id: int | None
    max_order_ref: int | None
    disconnect_count: int
    disconnect_reasons: tuple[int, ...]


@dataclass(slots=True)
class CtpSessionRebuildFinding:
    code: str
    severity: str
    action: str
    metric: str
    metric_value: str | int | None
    threshold: str | int | None
    message: str


@dataclass(slots=True)
class CtpSessionRebuildPolicyResult:
    shared_truth: CtpTdStartupTruthEvidence
    isolated_truth: CtpTdStartupTruthEvidence
    disposition: str
    shared_flow_reuse_allowed: bool
    session_rotated: bool
    max_order_ref_reset: bool
    findings: tuple[CtpSessionRebuildFinding, ...]


@dataclass(slots=True)
class CtpStartupTruthEvidenceMatrix:
    evidence_version: str
    captured_at_utc: str
    account_id: str | None
    disposition: str
    shared_flow_reuse_allowed: bool
    session_rotated: bool
    max_order_ref_reset: bool
    shared_flow_path: str
    isolated_flow_path: str
    shared_session_id: int | None
    isolated_session_id: int | None
    shared_max_order_ref: int | None
    isolated_max_order_ref: int | None
    shared_disconnect_count: int
    isolated_disconnect_count: int
    manual_review_codes: tuple[str, ...]
    rebuild_required_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]


__all__ = [
    "CtpSessionRebuildFinding",
    "CtpSessionRebuildPolicyResult",
    "CtpStartupTruthEvidenceMatrix",
    "CtpTdStartupTruthEvidence",
]
