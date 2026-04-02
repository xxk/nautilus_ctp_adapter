"""Nautilus-facing reconciliation snapshot helpers built on top of query baseline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from nautilus_ctp_adapter.runtime import CtpAccountRecord, CtpPositionRecord, CtpRuntimeBridge

from .config import CtpAdapterConfig
from .query_adapter import CtpQueryAdapter, CtpQueryAdapterSnapshot


@dataclass(slots=True)
class CtpReconciliationSymbolExposure:
    venue_symbol: str
    exchange_id: str | None
    long_qty: int
    short_qty: int
    gross_qty: int
    net_qty: int
    abs_net_qty: int
    position_cost: float


@dataclass(slots=True)
class CtpReconciliationSnapshot:
    query_snapshot: CtpQueryAdapterSnapshot


@dataclass(slots=True)
class CtpReconciliationSummary:
    position_request_id: str
    account_request_id: str
    account_id: str | None
    position_line_count: int
    symbol_count: int
    total_long_qty: int
    total_short_qty: int
    gross_position_qty: int
    total_position_cost: float
    account_balance: float | None
    account_available: float | None
    account_margin: float | None
    available_ratio: float | None
    margin_ratio: float | None
    dominant_exposure_symbol: str | None
    dominant_exposure_exchange: str | None
    dominant_exposure_abs_net_qty: int
    exposures: tuple[CtpReconciliationSymbolExposure, ...]


@dataclass(slots=True)
class CtpReconciliationPolicyFinding:
    code: str
    severity: str
    action: str
    metric: str
    metric_value: float | int | str | None
    threshold: float | int | str | None
    message: str


@dataclass(slots=True)
class CtpReconciliationPolicyResult:
    summary: CtpReconciliationSummary
    disposition: str
    requires_manual_review: bool
    findings: tuple[CtpReconciliationPolicyFinding, ...]


@dataclass(slots=True)
class CtpReconciliationEvidence:
    evidence_version: str
    captured_at_utc: str
    account_id: str | None
    disposition: str
    requires_manual_review: bool
    finding_count: int
    manual_review_codes: tuple[str, ...]
    evidence_only_codes: tuple[str, ...]
    position_line_count: int
    symbol_count: int
    gross_position_qty: int
    available_ratio: float | None
    margin_ratio: float | None
    dominant_exposure_symbol: str | None
    dominant_exposure_abs_net_qty: int
    top_exposures: tuple[CtpReconciliationSymbolExposure, ...]


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
        positions = snapshot.query_snapshot.positions.positions
        account = snapshot.query_snapshot.account.account
        exposures = self._build_exposures(positions)

        total_long_qty = sum(exposure.long_qty for exposure in exposures)
        total_short_qty = sum(exposure.short_qty for exposure in exposures)
        gross_position_qty = total_long_qty + total_short_qty
        total_position_cost = round(sum(exposure.position_cost for exposure in exposures), 6)

        balance = None if account is None else account.balance
        available = None if account is None else account.available
        margin = None if account is None else account.margin

        available_ratio = None
        margin_ratio = None
        if balance not in (None, 0.0):
            if available is not None:
                available_ratio = round(available / balance, 6)
            if margin is not None:
                margin_ratio = round(margin / balance, 6)

        dominant_exposure = None if not exposures else exposures[0]

        return CtpReconciliationSummary(
            position_request_id=snapshot.query_snapshot.positions.request_id,
            account_request_id=snapshot.query_snapshot.account.request_id,
            account_id=None if account is None else account.account_id,
            position_line_count=len(positions),
            symbol_count=len(exposures),
            total_long_qty=total_long_qty,
            total_short_qty=total_short_qty,
            gross_position_qty=gross_position_qty,
            total_position_cost=total_position_cost,
            account_balance=balance,
            account_available=available,
            account_margin=margin,
            available_ratio=available_ratio,
            margin_ratio=margin_ratio,
            dominant_exposure_symbol=None if dominant_exposure is None else dominant_exposure.venue_symbol,
            dominant_exposure_exchange=None if dominant_exposure is None else dominant_exposure.exchange_id,
            dominant_exposure_abs_net_qty=0 if dominant_exposure is None else dominant_exposure.abs_net_qty,
            exposures=tuple(exposures),
        )

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
        findings: list[CtpReconciliationPolicyFinding] = []

        if summary.account_id is None:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="missing_account_id",
                    severity="critical",
                    action="manual_review_required",
                    metric="account_id",
                    metric_value=None,
                    threshold="present",
                    message="Reconciliation summary is missing account identity and cannot be trusted.",
                )
            )

        if summary.account_balance in (None, 0.0):
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="missing_account_balance",
                    severity="critical",
                    action="manual_review_required",
                    metric="account_balance",
                    metric_value=summary.account_balance,
                    threshold="> 0",
                    message="Account balance is missing or zero, so summary ratios cannot be trusted.",
                )
            )

        if summary.available_ratio is None:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="missing_available_ratio",
                    severity="warn",
                    action="manual_review_required",
                    metric="available_ratio",
                    metric_value=None,
                    threshold="computed",
                    message="Available ratio could not be computed from the live account snapshot.",
                )
            )
        elif summary.available_ratio < 0.15:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="available_ratio_critical",
                    severity="critical",
                    action="manual_review_required",
                    metric="available_ratio",
                    metric_value=summary.available_ratio,
                    threshold=0.15,
                    message="Available ratio is below the critical threshold and requires manual review.",
                )
            )
        elif summary.available_ratio < 0.25:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="available_ratio_warn",
                    severity="warn",
                    action="manual_review_required",
                    metric="available_ratio",
                    metric_value=summary.available_ratio,
                    threshold=0.25,
                    message="Available ratio is below the baseline comfort threshold.",
                )
            )

        if summary.margin_ratio is None:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="missing_margin_ratio",
                    severity="warn",
                    action="manual_review_required",
                    metric="margin_ratio",
                    metric_value=None,
                    threshold="computed",
                    message="Margin ratio could not be computed from the live account snapshot.",
                )
            )
        elif summary.margin_ratio > 0.85:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="margin_ratio_critical",
                    severity="critical",
                    action="manual_review_required",
                    metric="margin_ratio",
                    metric_value=summary.margin_ratio,
                    threshold=0.85,
                    message="Margin ratio is above the critical threshold and requires manual review.",
                )
            )
        elif summary.margin_ratio > 0.75:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="margin_ratio_warn",
                    severity="warn",
                    action="manual_review_required",
                    metric="margin_ratio",
                    metric_value=summary.margin_ratio,
                    threshold=0.75,
                    message="Margin ratio is above the baseline comfort threshold.",
                )
            )

        if summary.dominant_exposure_abs_net_qty >= 10:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="dominant_exposure_watch",
                    severity="info",
                    action="evidence_only",
                    metric="dominant_exposure_abs_net_qty",
                    metric_value=summary.dominant_exposure_abs_net_qty,
                    threshold=10,
                    message="Dominant single-symbol exposure is large enough to keep in live evidence.",
                )
            )

        if summary.position_line_count == 0:
            findings.append(
                CtpReconciliationPolicyFinding(
                    code="flat_positions",
                    severity="info",
                    action="evidence_only",
                    metric="position_line_count",
                    metric_value=0,
                    threshold="> 0",
                    message="No open position lines were returned by the live snapshot.",
                )
            )

        disposition = "clear"
        if any(finding.action == "manual_review_required" for finding in findings):
            disposition = "manual_review_required"
        elif findings:
            disposition = "evidence_only"

        return CtpReconciliationPolicyResult(
            summary=summary,
            disposition=disposition,
            requires_manual_review=disposition == "manual_review_required",
            findings=tuple(findings),
        )

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
        manual_review_codes = tuple(
            finding.code for finding in result.findings if finding.action == "manual_review_required"
        )
        evidence_only_codes = tuple(
            finding.code for finding in result.findings if finding.action == "evidence_only"
        )
        return CtpReconciliationEvidence(
            evidence_version="reconciliation-evidence-v1",
            captured_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            account_id=result.summary.account_id,
            disposition=result.disposition,
            requires_manual_review=result.requires_manual_review,
            finding_count=len(result.findings),
            manual_review_codes=manual_review_codes,
            evidence_only_codes=evidence_only_codes,
            position_line_count=result.summary.position_line_count,
            symbol_count=result.summary.symbol_count,
            gross_position_qty=result.summary.gross_position_qty,
            available_ratio=result.summary.available_ratio,
            margin_ratio=result.summary.margin_ratio,
            dominant_exposure_symbol=result.summary.dominant_exposure_symbol,
            dominant_exposure_abs_net_qty=result.summary.dominant_exposure_abs_net_qty,
            top_exposures=result.summary.exposures[:10],
        )

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

    def _build_exposures(
        self,
        positions: tuple[CtpPositionRecord, ...],
    ) -> list[CtpReconciliationSymbolExposure]:
        grouped: dict[tuple[str, str | None], dict[str, object]] = {}
        for position in positions:
            key = (position.venue_symbol, position.exchange_id)
            bucket = grouped.setdefault(
                key,
                {
                    "venue_symbol": position.venue_symbol,
                    "exchange_id": position.exchange_id,
                    "long_qty": 0,
                    "short_qty": 0,
                    "position_cost": 0.0,
                },
            )
            qty = position.position_qty or 0
            direction = (position.direction or "").upper()
            if direction == "LONG":
                bucket["long_qty"] = int(bucket["long_qty"]) + qty
            elif direction == "SHORT":
                bucket["short_qty"] = int(bucket["short_qty"]) + qty
            bucket["position_cost"] = float(bucket["position_cost"]) + float(position.position_cost or 0.0)

        exposures: list[CtpReconciliationSymbolExposure] = []
        for _, bucket in grouped.items():
            long_qty = int(bucket["long_qty"])
            short_qty = int(bucket["short_qty"])
            gross_qty = long_qty + short_qty
            net_qty = long_qty - short_qty
            exposures.append(
                CtpReconciliationSymbolExposure(
                    venue_symbol=str(bucket["venue_symbol"]),
                    exchange_id=bucket["exchange_id"],
                    long_qty=long_qty,
                    short_qty=short_qty,
                    gross_qty=gross_qty,
                    net_qty=net_qty,
                    abs_net_qty=abs(net_qty),
                    position_cost=round(float(bucket["position_cost"]), 6),
                )
            )
        exposures.sort(
            key=lambda exposure: (
                -exposure.abs_net_qty,
                -exposure.gross_qty,
                -exposure.position_cost,
                exposure.venue_symbol,
                exposure.exchange_id or "",
            )
        )
        return exposures
