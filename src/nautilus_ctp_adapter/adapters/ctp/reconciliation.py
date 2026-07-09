"""Nautilus-facing reconciliation snapshot helpers built on top of query baseline."""

from __future__ import annotations

from pathlib import Path

from nautilus_ctp_adapter.diagnostics import reconciliation_policy
from nautilus_ctp_adapter.diagnostics.reconciliation_models import (
    CtpReconciliationEvidence,
    CtpReconciliationPolicyFinding,
    CtpReconciliationPolicyResult,
    CtpReconciliationSnapshot,
    CtpReconciliationSummary,
    CtpReconciliationSymbolExposure,
)
from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .query_adapter import CtpQueryAdapter


class CtpReconciliationAdapter:
    """Minimal reconciliation baseline using shared query adapter snapshots."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
        query_adapter: CtpQueryAdapter | None = None,
    ) -> None:
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._query_adapter = query_adapter or CtpQueryAdapter(self._config, self._runtime_bridge)

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def query_adapter(self) -> CtpQueryAdapter:
        return self._query_adapter

    def capture_snapshot_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        completion_grace_seconds: float = 1.0,
    ) -> CtpReconciliationSnapshot:
        return CtpReconciliationSnapshot(
            query_snapshot=self._query_adapter.query_snapshot_mainline(
                timeout_seconds=timeout_seconds,
                flow_path=flow_path,
                completion_grace_seconds=completion_grace_seconds,
            )
        )

    def summarize_snapshot(self, snapshot: CtpReconciliationSnapshot) -> CtpReconciliationSummary:
        return reconciliation_policy.summarize_reconciliation_snapshot(snapshot)

    def capture_summary_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        completion_grace_seconds: float = 1.0,
    ) -> CtpReconciliationSummary:
        snapshot = self.capture_snapshot_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.summarize_snapshot(snapshot)

    def evaluate_summary(self, summary: CtpReconciliationSummary) -> CtpReconciliationPolicyResult:
        return reconciliation_policy.evaluate_reconciliation_summary(summary)

    def capture_policy_result_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        completion_grace_seconds: float = 1.0,
    ) -> CtpReconciliationPolicyResult:
        summary = self.capture_summary_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.evaluate_summary(summary)

    def build_evidence(self, result: CtpReconciliationPolicyResult) -> CtpReconciliationEvidence:
        return reconciliation_policy.build_reconciliation_evidence(result)

    def capture_evidence_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        completion_grace_seconds: float = 1.0,
    ) -> CtpReconciliationEvidence:
        result = self.capture_policy_result_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self.build_evidence(result)

