"""TD truth merge snapshot helpers for live read-only reconciliation."""

from __future__ import annotations

from pathlib import Path

from nautilus_ctp_adapter.diagnostics import truth_merge_policy
from nautilus_ctp_adapter.diagnostics.truth_merge_models import (
    CtpTdMergedEvidenceMatrix,
    CtpTdMergedReconciliationFinding,
    CtpTdMergedReconciliationPolicyResult,
    CtpTdTruthMergeSnapshot,
)
from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .execution_client import CtpExecutionClient, CtpTdOrderTruthEvidenceMatrix
from .query_adapter import CtpQueryAdapter


class CtpTruthMergeAdapter:
    """Merge live TD callback truth with position/account query baselines."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
        execution_client: CtpExecutionClient | None = None,
        query_adapter: CtpQueryAdapter | None = None,
    ) -> None:
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._execution_client = execution_client or CtpExecutionClient(self._config, self._runtime_bridge)
        self._query_adapter = query_adapter or CtpQueryAdapter(
            self._config,
            self._runtime_bridge,
            self._execution_client,
        )

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def execution_client(self) -> CtpExecutionClient:
        return self._execution_client

    @property
    def query_adapter(self) -> CtpQueryAdapter:
        return self._query_adapter

    def capture_truth_merge_snapshot_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
        completion_grace_seconds: float = 1.0,
    ) -> CtpTdTruthMergeSnapshot:
        order_truth = self._execution_client.capture_td_order_truth_evidence_matrix_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            observation_grace_seconds=observation_grace_seconds,
        )
        positions = self._query_adapter.query_positions_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        account = self._query_adapter.query_account_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        return CtpTdTruthMergeSnapshot(
            order_truth=order_truth,
            positions=positions,
            account=account,
        )

    def evaluate_merged_reconciliation_policy(
        self,
        snapshot: CtpTdTruthMergeSnapshot,
    ) -> CtpTdMergedReconciliationPolicyResult:
        return truth_merge_policy.evaluate_merged_reconciliation_policy(snapshot)

    def capture_merged_reconciliation_policy_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
        completion_grace_seconds: float = 1.0,
    ) -> CtpTdMergedReconciliationPolicyResult:
        snapshot = self.capture_truth_merge_snapshot_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            observation_grace_seconds=observation_grace_seconds,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.evaluate_merged_reconciliation_policy(snapshot)

    def build_merged_evidence_matrix(
        self,
        result: CtpTdMergedReconciliationPolicyResult,
    ) -> CtpTdMergedEvidenceMatrix:
        return truth_merge_policy.build_td_merged_evidence_matrix(result)

    def capture_merged_evidence_matrix_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        observation_grace_seconds: float = 1.5,
        completion_grace_seconds: float = 1.0,
    ) -> CtpTdMergedEvidenceMatrix:
        result = self.capture_merged_reconciliation_policy_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            observation_grace_seconds=observation_grace_seconds,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.build_merged_evidence_matrix(result)
