"""Startup truth helpers for live TD bootstrap evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import time

from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .execution_client import CtpExecutionClient


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

    def build_evidence_matrix(
        self,
        result: CtpSessionRebuildPolicyResult,
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
            account_id=self._config.user_id or None,
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
