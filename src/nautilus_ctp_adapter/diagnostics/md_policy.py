from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from nautilus_ctp_adapter.runtime import CtpRuntimeEventKind

from .md_models import (
    CtpMdDisconnectEventPayload,
    CtpMdEventBatch,
    CtpMdRestorePolicyFinding,
    CtpMdRestorePolicyResult,
    CtpMdRestoreResult,
    CtpMdSmokeResult,
    CtpMdStartupTruthEvidence,
    CtpMdTruthEvidenceMatrix,
)


def build_md_startup_truth_evidence(
    *,
    md_smoke: CtpMdSmokeResult,
    flow_path: str | Path | None,
    default_flow_path: Path,
    selected_symbols: tuple[str, ...],
    event_batch: CtpMdEventBatch,
) -> CtpMdStartupTruthEvidence:
    disconnect_reasons = tuple(
        CtpMdDisconnectEventPayload.from_runtime_event(event).reason
        for event in event_batch.events
        if event.kind is CtpRuntimeEventKind.DISCONNECTED
    )
    effective_flow_path = Path(flow_path) if flow_path else default_flow_path
    return CtpMdStartupTruthEvidence(
        flow_path=str(effective_flow_path),
        flow_mode="explicit_override" if flow_path is not None else "default_shared_flow",
        selected_symbols=selected_symbols,
        ready=md_smoke.login_success and md_smoke.subscribe_code == 0 and md_smoke.first_tick_symbol is not None,
        login_success=md_smoke.login_success,
        login_error_id=md_smoke.login_error_id,
        subscribe_code=md_smoke.subscribe_code,
        first_tick_symbol=md_smoke.first_tick_symbol,
        first_tick_last=md_smoke.first_tick_last,
        first_tick_bid=md_smoke.first_tick_bid,
        first_tick_ask=md_smoke.first_tick_ask,
        first_tick_ts_epoch_us=md_smoke.first_tick_ts_epoch_us,
        disconnect_count=len(disconnect_reasons),
        disconnect_reasons=disconnect_reasons,
    )


def evaluate_md_restore_policy(
    startup_truth: CtpMdStartupTruthEvidence,
    restore_result: CtpMdRestoreResult,
    restored_truth: CtpMdStartupTruthEvidence,
) -> CtpMdRestorePolicyResult:
    findings: list[CtpMdRestorePolicyFinding] = []

    if not startup_truth.ready:
        findings.append(
            CtpMdRestorePolicyFinding(
                code="startup_truth_unready",
                severity="critical",
                action="manual_review_required",
                metric="startup_ready",
                metric_value=startup_truth.ready,
                threshold=True,
                message="Initial MD startup truth is not ready enough to judge restore behavior.",
            )
        )

    if not restore_result.triggered:
        findings.append(
            CtpMdRestorePolicyFinding(
                code="restore_not_triggered",
                severity="critical",
                action="manual_review_required",
                metric="restore_triggered",
                metric_value=restore_result.triggered,
                threshold=True,
                message="MD restore was not triggered, so restore success cannot be declared.",
            )
        )

    if not restored_truth.ready:
        findings.append(
            CtpMdRestorePolicyFinding(
                code="restored_truth_unready",
                severity="critical",
                action="manual_review_required",
                metric="restored_ready",
                metric_value=restored_truth.ready,
                threshold=True,
                message="Post-restore MD truth is not ready, so restore success cannot be trusted.",
            )
        )

    if (
        startup_truth.first_tick_ts_epoch_us is not None
        and restored_truth.first_tick_ts_epoch_us is not None
        and restored_truth.first_tick_ts_epoch_us <= startup_truth.first_tick_ts_epoch_us
    ):
        findings.append(
            CtpMdRestorePolicyFinding(
                code="restore_missing_fresh_tick",
                severity="warn",
                action="restore_required",
                metric="restored_first_tick_ts_epoch_us",
                metric_value=restored_truth.first_tick_ts_epoch_us,
                threshold=f"> {startup_truth.first_tick_ts_epoch_us}",
                message="Restore success requires a fresh post-restore tick, not reuse of a pre-restore tick timestamp.",
            )
        )

    if restore_result.triggered:
        findings.append(
            CtpMdRestorePolicyFinding(
                code="restore_resubscribe_triggered",
                severity="info",
                action="evidence_only",
                metric="restored_symbols",
                metric_value=",".join(restore_result.restored_symbols),
                threshold="non-empty",
                message="MD restore re-submitted the tracked symbols.",
            )
        )

    restore_succeeded = (
        restore_result.triggered
        and restored_truth.ready
        and restored_truth.first_tick_symbol is not None
        and startup_truth.first_tick_ts_epoch_us is not None
        and restored_truth.first_tick_ts_epoch_us is not None
        and restored_truth.first_tick_ts_epoch_us > startup_truth.first_tick_ts_epoch_us
    )

    disposition = "clear"
    if any(finding.action == "manual_review_required" for finding in findings):
        disposition = "manual_review_required"
    elif any(finding.action == "restore_required" for finding in findings):
        disposition = "restore_required"
    elif findings:
        disposition = "evidence_only"

    return CtpMdRestorePolicyResult(
        startup_truth=startup_truth,
        restored_truth=restored_truth,
        restore_result=restore_result,
        disposition=disposition,
        restore_succeeded=restore_succeeded,
        findings=tuple(findings),
    )


def build_md_truth_evidence_matrix(
    result: CtpMdRestorePolicyResult,
    *,
    account_id: str | None,
) -> CtpMdTruthEvidenceMatrix:
    manual_review_codes = tuple(
        finding.code for finding in result.findings if finding.action == "manual_review_required"
    )
    restore_required_codes = tuple(
        finding.code for finding in result.findings if finding.action == "restore_required"
    )
    evidence_only_codes = tuple(
        finding.code for finding in result.findings if finding.action == "evidence_only"
    )
    symbol = None
    if result.restored_truth.selected_symbols:
        symbol = result.restored_truth.selected_symbols[0]
    elif result.startup_truth.selected_symbols:
        symbol = result.startup_truth.selected_symbols[0]

    return CtpMdTruthEvidenceMatrix(
        evidence_version="md-truth-evidence-v1",
        captured_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        account_id=account_id,
        symbol=symbol,
        disposition=result.disposition,
        startup_ready=result.startup_truth.ready,
        restore_triggered=result.restore_result.triggered,
        restore_succeeded=result.restore_succeeded,
        startup_flow_path=result.startup_truth.flow_path,
        restored_flow_path=result.restored_truth.flow_path,
        startup_first_tick_ts_epoch_us=result.startup_truth.first_tick_ts_epoch_us,
        restored_first_tick_ts_epoch_us=result.restored_truth.first_tick_ts_epoch_us,
        manual_review_codes=manual_review_codes,
        restore_required_codes=restore_required_codes,
        evidence_only_codes=evidence_only_codes,
    )

