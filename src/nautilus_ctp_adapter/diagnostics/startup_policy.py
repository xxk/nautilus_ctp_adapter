from __future__ import annotations

from datetime import datetime, timezone

from .startup_models import (
    CtpSessionRebuildFinding,
    CtpSessionRebuildPolicyResult,
    CtpStartupTruthEvidenceMatrix,
    CtpTdStartupTruthEvidence,
)


def evaluate_session_rebuild_policy(
    shared_truth: CtpTdStartupTruthEvidence,
    isolated_truth: CtpTdStartupTruthEvidence,
) -> CtpSessionRebuildPolicyResult:
    findings: list[CtpSessionRebuildFinding] = []

    if not shared_truth.ready or shared_truth.login_success is not True or shared_truth.settlement_code != 0:
        findings.append(
            CtpSessionRebuildFinding(
                code="shared_startup_truth_unready",
                severity="critical",
                action="manual_review_required",
                metric="shared_ready",
                metric_value=str(shared_truth.ready),
                threshold="ready=true && settlement_code=0",
                message="Shared-flow startup truth is not ready enough to be trusted for rebuild decisions.",
            )
        )

    if not isolated_truth.ready or isolated_truth.login_success is not True or isolated_truth.settlement_code != 0:
        findings.append(
            CtpSessionRebuildFinding(
                code="isolated_startup_truth_unready",
                severity="critical",
                action="manual_review_required",
                metric="isolated_ready",
                metric_value=str(isolated_truth.ready),
                threshold="ready=true && settlement_code=0",
                message="Isolated-flow startup truth is not ready, so rebuild truth cannot be confirmed.",
            )
        )

    if shared_truth.flow_mode == "default_shared_flow":
        findings.append(
            CtpSessionRebuildFinding(
                code="shared_flow_requires_isolated_rebuild",
                severity="warn",
                action="rebuild_required",
                metric="shared_flow_mode",
                metric_value=shared_truth.flow_mode,
                threshold="explicit_override",
                message="Shared default TD flow must not be treated as rebuild-safe truth for session-sensitive checks.",
            )
        )

    if isolated_truth.flow_mode == "explicit_override":
        findings.append(
            CtpSessionRebuildFinding(
                code="isolated_flow_verified",
                severity="info",
                action="evidence_only",
                metric="isolated_flow_mode",
                metric_value=isolated_truth.flow_mode,
                threshold="explicit_override",
                message="Isolated override flow was used and can serve as rebuild-safe session truth.",
            )
        )

    session_rotated = (
        shared_truth.session_id is not None
        and isolated_truth.session_id is not None
        and shared_truth.session_id != isolated_truth.session_id
    )
    max_order_ref_reset = (
        shared_truth.max_order_ref is not None
        and isolated_truth.max_order_ref is not None
        and isolated_truth.max_order_ref <= shared_truth.max_order_ref
    )

    if session_rotated:
        findings.append(
            CtpSessionRebuildFinding(
                code="fresh_session_identity_observed",
                severity="info",
                action="evidence_only",
                metric="session_id",
                metric_value=isolated_truth.session_id,
                threshold="!= shared_session_id",
                message="A fresh session identity was observed after isolated rebuild bootstrap.",
            )
        )

    if max_order_ref_reset:
        findings.append(
            CtpSessionRebuildFinding(
                code="max_order_ref_reinitialized",
                severity="info",
                action="evidence_only",
                metric="max_order_ref",
                metric_value=isolated_truth.max_order_ref,
                threshold="<= shared_max_order_ref",
                message="Isolated rebuild bootstrap reinitialized max_order_ref, so old order-ref chains must not be inherited.",
            )
        )

    disposition = "clear"
    if any(finding.action == "manual_review_required" for finding in findings):
        disposition = "manual_review_required"
    elif any(finding.action == "rebuild_required" for finding in findings):
        disposition = "rebuild_required"
    elif findings:
        disposition = "evidence_only"

    return CtpSessionRebuildPolicyResult(
        shared_truth=shared_truth,
        isolated_truth=isolated_truth,
        disposition=disposition,
        shared_flow_reuse_allowed=False,
        session_rotated=session_rotated,
        max_order_ref_reset=max_order_ref_reset,
        findings=tuple(findings),
    )


def build_startup_truth_evidence_matrix(
    result: CtpSessionRebuildPolicyResult,
    *,
    account_id: str | None,
) -> CtpStartupTruthEvidenceMatrix:
    manual_review_codes = tuple(
        finding.code for finding in result.findings if finding.action == "manual_review_required"
    )
    rebuild_required_codes = tuple(
        finding.code for finding in result.findings if finding.action == "rebuild_required"
    )
    evidence_only_codes = tuple(
        finding.code for finding in result.findings if finding.action == "evidence_only"
    )
    return CtpStartupTruthEvidenceMatrix(
        evidence_version="startup-truth-evidence-v1",
        captured_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        account_id=account_id,
        disposition=result.disposition,
        shared_flow_reuse_allowed=result.shared_flow_reuse_allowed,
        session_rotated=result.session_rotated,
        max_order_ref_reset=result.max_order_ref_reset,
        shared_flow_path=result.shared_truth.flow_path,
        isolated_flow_path=result.isolated_truth.flow_path,
        shared_session_id=result.shared_truth.session_id,
        isolated_session_id=result.isolated_truth.session_id,
        shared_max_order_ref=result.shared_truth.max_order_ref,
        isolated_max_order_ref=result.isolated_truth.max_order_ref,
        shared_disconnect_count=result.shared_truth.disconnect_count,
        isolated_disconnect_count=result.isolated_truth.disconnect_count,
        manual_review_codes=manual_review_codes,
        rebuild_required_codes=rebuild_required_codes,
        evidence_only_codes=evidence_only_codes,
    )


__all__ = [
    "build_startup_truth_evidence_matrix",
    "evaluate_session_rebuild_policy",
]
