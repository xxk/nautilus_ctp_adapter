"""Startup truth helpers for live TD bootstrap evidence."""

from __future__ import annotations

from pathlib import Path
import time

from nautilus_ctp_adapter.diagnostics import startup_policy
from nautilus_ctp_adapter.diagnostics.startup_models import (
    CtpSessionRebuildFinding,
    CtpSessionRebuildPolicyResult,
    CtpStartupTruthEvidenceMatrix,
    CtpTdStartupTruthEvidence,
)
from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .execution_client import CtpExecutionClient


class CtpStartupTruthAdapter:
    """Capture live TD startup truth without introducing trading behavior."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
        execution_client: CtpExecutionClient | None = None,
    ) -> None:
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._execution_client = execution_client or CtpExecutionClient(self._config, self._runtime_bridge)

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def execution_client(self) -> CtpExecutionClient:
        return self._execution_client

    def capture_td_startup_truth_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpTdStartupTruthEvidence:
        effective_flow_path = self._execution_client.resolve_td_flow_path(flow_path)
        bootstrap = self._execution_client.bootstrap_live_execution_client_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=effective_flow_path,
        )
        td_smoke = bootstrap.execution_bootstrap.td_smoke
        identity = bootstrap.td_session_identity
        return CtpTdStartupTruthEvidence(
            flow_path=str(effective_flow_path),
            flow_mode="explicit_override" if flow_path is not None else "default_shared_flow",
            ready=bootstrap.ready,
            login_success=td_smoke.login_success,
            settlement_code=td_smoke.settlement_code,
            front_id=None if identity is None else identity.front_id,
            session_id=None if identity is None else identity.session_id,
            max_order_ref=None if identity is None else identity.max_order_ref,
            disconnect_count=len(td_smoke.disconnects or []),
            disconnect_reasons=tuple(td_smoke.disconnects or []),
        )

    def capture_session_rebuild_policy_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        shared_flow_path: str | Path | None = None,
        isolated_flow_path: str | Path | None = None,
    ) -> CtpSessionRebuildPolicyResult:
        shared_truth = self.capture_td_startup_truth_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=shared_flow_path,
        )
        isolated_truth = self.capture_td_startup_truth_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=isolated_flow_path or self._default_isolated_flow_path(),
        )
        return self.evaluate_session_rebuild_policy(shared_truth, isolated_truth)

    def evaluate_session_rebuild_policy(
        self,
        shared_truth: CtpTdStartupTruthEvidence,
        isolated_truth: CtpTdStartupTruthEvidence,
    ) -> CtpSessionRebuildPolicyResult:
        return startup_policy.evaluate_session_rebuild_policy(shared_truth, isolated_truth)

    def build_evidence_matrix(
        self,
        result: CtpSessionRebuildPolicyResult,
    ) -> CtpStartupTruthEvidenceMatrix:
        return startup_policy.build_startup_truth_evidence_matrix(
            result,
            account_id=self._config.user_id or None,
        )

    def capture_evidence_matrix_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        shared_flow_path: str | Path | None = None,
        isolated_flow_path: str | Path | None = None,
    ) -> CtpStartupTruthEvidenceMatrix:
        result = self.capture_session_rebuild_policy_mainline(
            timeout_seconds=timeout_seconds,
            shared_flow_path=shared_flow_path,
            isolated_flow_path=isolated_flow_path,
        )
        return self.build_evidence_matrix(result)

    def _default_isolated_flow_path(self) -> Path:
        return self._repository_root() / "output" / "debug" / f"session_rebuild_truth_{time.time_ns()}"

    def _repository_root(self) -> Path:
        return Path(__file__).resolve().parents[4]
