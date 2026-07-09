from __future__ import annotations

import time

from .td_models import (
    CtpTdHistoricalCallbackBoundaryFinding,
    CtpTdHistoricalCallbackBoundaryPolicyResult,
    CtpTdOrderTradeSnapshot,
    CtpTdOrderTruthBaseline,
    CtpTdOrderTruthEvidenceMatrix,
)


def _parse_native_int(value: str | None) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def evaluate_historical_callback_boundary_policy(
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
        callback_order_ref = _parse_native_int(callback.order_ref)
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


def evaluate_order_trade_snapshot(
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
        callback_order_ref = _parse_native_int(callback.order_ref)
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


def build_td_order_truth_evidence_matrix(
    result: CtpTdHistoricalCallbackBoundaryPolicyResult,
    *,
    account_id: str | None,
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
        account_id=account_id,
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

