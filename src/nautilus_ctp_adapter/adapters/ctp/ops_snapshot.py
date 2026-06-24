"""Read-only live operations snapshot helpers built from existing truth adapters."""

from __future__ import annotations

from pathlib import Path

from nautilus_ctp_adapter.diagnostics import live_ops_policy
from nautilus_ctp_adapter.diagnostics.live_ops_models import (
    CtpLiveOpsEvidenceMatrix,
    CtpLiveOpsPolicyFinding,
    CtpLiveOpsPolicyResult,
    CtpLiveOpsSnapshot,
    CtpLiveOpsSnapshotSummary,
)
from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .data_client import CtpDataClient
from .reconciliation import CtpReconciliationAdapter
from .startup_truth import CtpStartupTruthAdapter
from .truth_merge import CtpTruthMergeAdapter


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
        return live_ops_policy.summarize_live_ops_snapshot(snapshot)

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
        return live_ops_policy.evaluate_live_ops_summary(summary)

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
        return live_ops_policy.build_live_ops_evidence_matrix(result)

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
