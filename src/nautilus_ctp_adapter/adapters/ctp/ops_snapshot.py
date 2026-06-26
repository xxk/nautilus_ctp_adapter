"""Read-only live operations snapshot helpers built from existing truth adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .data_client import CtpDataClient, CtpMdTruthEvidenceMatrix
from .reconciliation import CtpReconciliationAdapter, CtpReconciliationEvidence
from .startup_truth import CtpStartupTruthAdapter, CtpStartupTruthEvidenceMatrix
from .truth_merge import CtpTdMergedEvidenceMatrix, CtpTruthMergeAdapter


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


class CtpLiveOpsSnapshotAdapter:
    """Compose the repository's read-only live truth surfaces into one snapshot."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
        startup_truth_adapter: CtpStartupTruthAdapter | None = None,
        data_client: CtpDataClient | None = None,
        truth_merge_adapter: CtpTruthMergeAdapter | None = None,
        reconciliation_adapter: CtpReconciliationAdapter | None = None,
    ) -> None:
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._startup_truth_adapter = startup_truth_adapter or CtpStartupTruthAdapter(
            self._config,
            self._runtime_bridge,
        )
        self._data_client = data_client or CtpDataClient(self._config, self._runtime_bridge)
        self._truth_merge_adapter = truth_merge_adapter or CtpTruthMergeAdapter(
            self._config,
            self._runtime_bridge,
        )
        self._reconciliation_adapter = reconciliation_adapter or CtpReconciliationAdapter(
            self._config,
            self._runtime_bridge,
        )

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    def capture_live_ops_snapshot_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        td_shared_flow_path: str | Path | None = None,
        td_isolated_flow_path: str | Path | None = None,
        md_flow_path: str | Path | None = None,
        td_flow_path: str | Path | None = None,
        query_flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
        completion_grace_seconds: float = 1.0,
    ) -> CtpLiveOpsSnapshot:
        startup_truth = self._startup_truth_adapter.capture_evidence_matrix_mainline(
            timeout_seconds=timeout_seconds,
            shared_flow_path=td_shared_flow_path,
            isolated_flow_path=td_isolated_flow_path,
        )
        md_truth = self._data_client.capture_md_truth_evidence_matrix_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=md_flow_path,
        )
        td_truth = self._truth_merge_adapter.capture_merged_evidence_matrix_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=td_flow_path,
            observation_grace_seconds=observation_grace_seconds,
            completion_grace_seconds=completion_grace_seconds,
        )
        reconciliation = self._reconciliation_adapter.capture_evidence_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=query_flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        return CtpLiveOpsSnapshot(
            startup_truth=startup_truth,
            md_truth=md_truth,
            td_truth=td_truth,
            reconciliation=reconciliation,
        )

    def summarize_live_ops_snapshot(self, snapshot: CtpLiveOpsSnapshot) -> CtpLiveOpsSnapshotSummary:
        account_id = snapshot.td_truth.account_id or snapshot.reconciliation.account_id or snapshot.startup_truth.account_id
        symbol = snapshot.md_truth.symbol

        manual_review_codes = tuple(
            dict.fromkeys(
                (
                    *snapshot.startup_truth.manual_review_codes,
                    *snapshot.md_truth.manual_review_codes,
                    *snapshot.td_truth.manual_review_codes,
                    *snapshot.reconciliation.manual_review_codes,
                )
            )
        )
        rebuild_required_codes = tuple(dict.fromkeys(snapshot.startup_truth.rebuild_required_codes))
        restore_required_codes = tuple(dict.fromkeys(snapshot.md_truth.restore_required_codes))
        boundary_codes = tuple(dict.fromkeys(snapshot.td_truth.boundary_codes))
        evidence_only_codes = tuple(
            dict.fromkeys(
                (
                    *snapshot.startup_truth.evidence_only_codes,
                    *snapshot.md_truth.evidence_only_codes,
                    *snapshot.td_truth.evidence_only_codes,
                    *snapshot.reconciliation.evidence_only_codes,
                )
            )
        )

        return CtpLiveOpsSnapshotSummary(
            baseline="live-ops-snapshot-v1",
            account_id=account_id,
            symbol=symbol,
            startup_disposition=snapshot.startup_truth.disposition,
            md_disposition=snapshot.md_truth.disposition,
            td_disposition=snapshot.td_truth.disposition,
            reconciliation_disposition=snapshot.reconciliation.disposition,
            startup_shared_flow_reuse_allowed=snapshot.startup_truth.shared_flow_reuse_allowed,
            startup_session_rotated=snapshot.startup_truth.session_rotated,
            md_restore_succeeded=snapshot.md_truth.restore_succeeded,
            position_count=snapshot.td_truth.position_count,
            observed_callback_count=snapshot.td_truth.observed_callback_count,
            historical_callback_count=snapshot.td_truth.historical_callback_count,
            current_session_callback_count=snapshot.td_truth.current_session_callback_count,
            available_ratio=snapshot.reconciliation.available_ratio,
            margin_ratio=snapshot.reconciliation.margin_ratio,
            manual_review_codes=manual_review_codes,
            rebuild_required_codes=rebuild_required_codes,
            restore_required_codes=restore_required_codes,
            boundary_codes=boundary_codes,
            evidence_only_codes=evidence_only_codes,
        )

    def capture_live_ops_snapshot_summary_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        td_shared_flow_path: str | Path | None = None,
        td_isolated_flow_path: str | Path | None = None,
        md_flow_path: str | Path | None = None,
        td_flow_path: str | Path | None = None,
        query_flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
        completion_grace_seconds: float = 1.0,
    ) -> CtpLiveOpsSnapshotSummary:
        snapshot = self.capture_live_ops_snapshot_mainline(
            timeout_seconds=timeout_seconds,
            td_shared_flow_path=td_shared_flow_path,
            td_isolated_flow_path=td_isolated_flow_path,
            md_flow_path=md_flow_path,
            td_flow_path=td_flow_path,
            query_flow_path=query_flow_path,
            observation_grace_seconds=observation_grace_seconds,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.summarize_live_ops_snapshot(snapshot)

    def evaluate_live_ops_policy(
        self,
        summary: CtpLiveOpsSnapshotSummary,
    ) -> CtpLiveOpsPolicyResult:
        findings: list[CtpLiveOpsPolicyFinding] = []

        if summary.account_id is None:
            findings.append(
                CtpLiveOpsPolicyFinding(
                    code="missing_account_identity",
                    severity="critical",
                    action="manual_review_required",
                    metric="account_id",
                    metric_value=None,
                    threshold="present",
                    message="Live ops snapshot is missing account identity and cannot be trusted for operations decisions.",
                )
            )

        if summary.manual_review_codes:
            findings.append(
                CtpLiveOpsPolicyFinding(
                    code="manual_review_codes_present",
                    severity="warn",
                    action="manual_review_required",
                    metric="manual_review_codes",
                    metric_value=",".join(summary.manual_review_codes),
                    threshold="empty",
                    message="Underlying truth layers raised manual review findings, so live ops disposition must stay manual_review_required.",
                )
            )

        if summary.rebuild_required_codes or not summary.startup_shared_flow_reuse_allowed:
            findings.append(
                CtpLiveOpsPolicyFinding(
                    code="startup_rebuild_required",
                    severity="warn",
                    action="rebuild_required",
                    metric="startup_shared_flow_reuse_allowed",
                    metric_value=summary.startup_shared_flow_reuse_allowed,
                    threshold=True,
                    message="TD startup truth still requires isolated rebuild-safe flow handling.",
                )
            )

        if summary.restore_required_codes or not summary.md_restore_succeeded:
            findings.append(
                CtpLiveOpsPolicyFinding(
                    code="md_restore_attention_required",
                    severity="warn",
                    action="restore_required",
                    metric="md_restore_succeeded",
                    metric_value=summary.md_restore_succeeded,
                    threshold=True,
                    message="MD restore truth is not strong enough to declare the market-data path self-healed.",
                )
            )

        if summary.boundary_codes:
            findings.append(
                CtpLiveOpsPolicyFinding(
                    code="td_boundary_required",
                    severity="warn",
                    action="boundary_required",
                    metric="boundary_codes",
                    metric_value=",".join(summary.boundary_codes),
                    threshold="empty",
                    message="TD truth still contains boundary findings that must remain explicit in operations decisions.",
                )
            )

        if summary.evidence_only_codes:
            findings.append(
                CtpLiveOpsPolicyFinding(
                    code="evidence_only_signals_present",
                    severity="info",
                    action="evidence_only",
                    metric="evidence_only_codes",
                    metric_value=",".join(summary.evidence_only_codes),
                    threshold="empty",
                    message="Live ops snapshot also contains evidence-only signals that should stay visible to operators.",
                )
            )

        disposition = "clear"
        if any(finding.action == "manual_review_required" for finding in findings):
            disposition = "manual_review_required"
        elif any(finding.action == "rebuild_required" for finding in findings):
            disposition = "rebuild_required"
        elif any(finding.action == "restore_required" for finding in findings):
            disposition = "restore_required"
        elif any(finding.action == "boundary_required" for finding in findings):
            disposition = "boundary_required"
        elif findings:
            disposition = "evidence_only"

        return CtpLiveOpsPolicyResult(
            summary=summary,
            disposition=disposition,
            findings=tuple(findings),
        )

    def capture_live_ops_policy_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        td_shared_flow_path: str | Path | None = None,
        td_isolated_flow_path: str | Path | None = None,
        md_flow_path: str | Path | None = None,
        td_flow_path: str | Path | None = None,
        query_flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
        completion_grace_seconds: float = 1.0,
    ) -> CtpLiveOpsPolicyResult:
        summary = self.capture_live_ops_snapshot_summary_mainline(
            timeout_seconds=timeout_seconds,
            td_shared_flow_path=td_shared_flow_path,
            td_isolated_flow_path=td_isolated_flow_path,
            md_flow_path=md_flow_path,
            td_flow_path=td_flow_path,
            query_flow_path=query_flow_path,
            observation_grace_seconds=observation_grace_seconds,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.evaluate_live_ops_policy(summary)

    def build_live_ops_evidence_matrix(
        self,
        result: CtpLiveOpsPolicyResult,
    ) -> CtpLiveOpsEvidenceMatrix:
        summary = result.summary
        return CtpLiveOpsEvidenceMatrix(
            evidence_version="live-ops-evidence-v1",
            account_id=summary.account_id,
            symbol=summary.symbol,
            disposition=result.disposition,
            startup_disposition=summary.startup_disposition,
            md_disposition=summary.md_disposition,
            td_disposition=summary.td_disposition,
            reconciliation_disposition=summary.reconciliation_disposition,
            startup_shared_flow_reuse_allowed=summary.startup_shared_flow_reuse_allowed,
            startup_session_rotated=summary.startup_session_rotated,
            md_restore_succeeded=summary.md_restore_succeeded,
            position_count=summary.position_count,
            observed_callback_count=summary.observed_callback_count,
            historical_callback_count=summary.historical_callback_count,
            current_session_callback_count=summary.current_session_callback_count,
            available_ratio=summary.available_ratio,
            margin_ratio=summary.margin_ratio,
            manual_review_codes=summary.manual_review_codes,
            rebuild_required_codes=summary.rebuild_required_codes,
            restore_required_codes=summary.restore_required_codes,
            boundary_codes=summary.boundary_codes,
            evidence_only_codes=summary.evidence_only_codes,
        )

    def capture_live_ops_evidence_matrix_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        td_shared_flow_path: str | Path | None = None,
        td_isolated_flow_path: str | Path | None = None,
        md_flow_path: str | Path | None = None,
        td_flow_path: str | Path | None = None,
        query_flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
        completion_grace_seconds: float = 1.0,
    ) -> CtpLiveOpsEvidenceMatrix:
        result = self.capture_live_ops_policy_mainline(
            timeout_seconds=timeout_seconds,
            td_shared_flow_path=td_shared_flow_path,
            td_isolated_flow_path=td_isolated_flow_path,
            md_flow_path=md_flow_path,
            td_flow_path=td_flow_path,
            query_flow_path=query_flow_path,
            observation_grace_seconds=observation_grace_seconds,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.build_live_ops_evidence_matrix(result)
