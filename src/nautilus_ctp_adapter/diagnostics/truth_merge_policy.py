from __future__ import annotations

from datetime import datetime, timezone

from .truth_merge_models import (
    CtpTdMergedEvidenceMatrix,
    CtpTdMergedReconciliationFinding,
    CtpTdMergedReconciliationPolicyResult,
    CtpTdTruthMergeSnapshot,
)


def evaluate_merged_reconciliation_policy(
    snapshot: CtpTdTruthMergeSnapshot,
) -> CtpTdMergedReconciliationPolicyResult:
    findings: list[CtpTdMergedReconciliationFinding] = []

    account = snapshot.account.account
    available_ratio = None
    margin_ratio = None
    if account is not None and account.balance not in (None, 0.0):
        available_ratio = round(account.available / account.balance, 6)
        margin_ratio = round(account.margin / account.balance, 6)

    if snapshot.account.account is None:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="missing_account_snapshot",
                severity="critical",
                action="manual_review_required",
                metric="account_present",
                metric_value="false",
                threshold="true",
                message="Merged truth snapshot is missing account state and cannot be trusted.",
            )
        )

    if not snapshot.positions.completed or snapshot.positions.timed_out:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="position_snapshot_incomplete",
                severity="critical",
                action="manual_review_required",
                metric="positions_completed",
                metric_value=str(snapshot.positions.completed),
                threshold="true",
                message="Position snapshot did not complete cleanly in the merged truth window.",
            )
        )

    if snapshot.order_truth.historical_callback_count > 0:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="historical_callbacks_present",
                severity="warn",
                action="boundary_required",
                metric="historical_callback_count",
                metric_value=snapshot.order_truth.historical_callback_count,
                threshold=0,
                message="Merged snapshot still contains historical callback residue and must preserve that boundary.",
            )
        )

    if available_ratio is None:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="missing_available_ratio",
                severity="warn",
                action="manual_review_required",
                metric="available_ratio",
                metric_value=None,
                threshold="computed",
                message="Available ratio could not be computed from the merged account snapshot.",
            )
        )
    elif available_ratio < 0.25:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="available_ratio_warn",
                severity="warn",
                action="manual_review_required",
                metric="available_ratio",
                metric_value=available_ratio,
                threshold=0.25,
                message="Available ratio is below the merged truth comfort threshold.",
            )
        )

    if margin_ratio is None:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="missing_margin_ratio",
                severity="warn",
                action="manual_review_required",
                metric="margin_ratio",
                metric_value=None,
                threshold="computed",
                message="Margin ratio could not be computed from the merged account snapshot.",
            )
        )
    elif margin_ratio > 0.75:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="margin_ratio_warn",
                severity="warn",
                action="manual_review_required",
                metric="margin_ratio",
                metric_value=margin_ratio,
                threshold=0.75,
                message="Margin ratio is above the merged truth comfort threshold.",
            )
        )

    if snapshot.order_truth.current_session_callback_count == 0:
        findings.append(
            CtpTdMergedReconciliationFinding(
                code="no_current_session_callbacks",
                severity="info",
                action="evidence_only",
                metric="current_session_callback_count",
                metric_value=0,
                threshold="> 0 optional",
                message="No callbacks were classified as belonging to the current TD session truth.",
            )
        )

    disposition = "clear"
    if any(finding.action == "manual_review_required" for finding in findings):
        disposition = "manual_review_required"
    elif any(finding.action == "boundary_required" for finding in findings):
        disposition = "boundary_required"
    elif findings:
        disposition = "evidence_only"

    return CtpTdMergedReconciliationPolicyResult(
        snapshot=snapshot,
        disposition=disposition,
        available_ratio=available_ratio,
        margin_ratio=margin_ratio,
        findings=tuple(findings),
    )


def build_td_merged_evidence_matrix(
    result: CtpTdMergedReconciliationPolicyResult,
) -> CtpTdMergedEvidenceMatrix:
    manual_review_codes = tuple(
        finding.code for finding in result.findings if finding.action == "manual_review_required"
    )
    boundary_codes = tuple(
        finding.code for finding in result.findings if finding.action == "boundary_required"
    )
    evidence_only_codes = tuple(
        finding.code for finding in result.findings if finding.action == "evidence_only"
    )
    return CtpTdMergedEvidenceMatrix(
        evidence_version="td-merged-evidence-v1",
        captured_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        account_id=result.snapshot.order_truth.account_id,
        disposition=result.disposition,
        position_count=result.snapshot.positions.position_count,
        observed_callback_count=result.snapshot.order_truth.observed_callback_count,
        historical_callback_count=result.snapshot.order_truth.historical_callback_count,
        current_session_callback_count=result.snapshot.order_truth.current_session_callback_count,
        available_ratio=result.available_ratio,
        margin_ratio=result.margin_ratio,
        manual_review_codes=manual_review_codes,
        boundary_codes=boundary_codes,
        evidence_only_codes=evidence_only_codes,
    )


__all__ = [
    "build_td_merged_evidence_matrix",
    "evaluate_merged_reconciliation_policy",
]
