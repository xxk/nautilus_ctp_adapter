from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping

from .md_models import CtpMdTruthEvidenceMatrix
from .td_models import CtpTdOrderTruthEvidenceMatrix


MD_TRUTH_EVIDENCE_MATRIX_BASELINE = "md-truth-evidence-matrix-v1"
TD_ORDER_TRUTH_EVIDENCE_MATRIX_BASELINE = "td-order-truth-evidence-matrix-v1"
STARTUP_TRUTH_EVIDENCE_MATRIX_BASELINE = "td-startup-truth-evidence-matrix-v1"
TD_MERGED_EVIDENCE_MATRIX_BASELINE = "td-merged-evidence-matrix-v1"
LIVE_OPS_SNAPSHOT_BASELINE = "live-ops-snapshot-v1"
LIVE_OPS_POLICY_BASELINE = "live-ops-policy-v1"
LIVE_OPS_EVIDENCE_MATRIX_BASELINE = "live-ops-evidence-matrix-v1"
RECONCILIATION_SNAPSHOT_BASELINE = "reconciliation-snapshot-v1"
RECONCILIATION_POLICY_BASELINE = "reconciliation-policy-v1"
RECONCILIATION_EVIDENCE_BASELINE = "reconciliation-evidence-v1"
TD_STARTUP_TRUTH_BASELINE = "td-startup-truth-v1"
TD_SESSION_REBUILD_POLICY_BASELINE = "td-session-rebuild-policy-v1"
MD_RESTORE_POLICY_BASELINE = "md-restore-policy-v1"
TD_TRUTH_MERGE_SNAPSHOT_BASELINE = "td-truth-merge-snapshot-v1"
TD_MERGED_RECONCILIATION_POLICY_BASELINE = "td-merged-reconciliation-policy-v1"
QUERY_ADAPTER_BASELINE = "nautilus-query-adapter-v1"
INSTRUMENT_QUERY_BASELINE = "instrument-query-smoke-v1"
ACCOUNT_QUERY_BASELINE = "account-query-smoke-v1"
POSITION_QUERY_BASELINE = "position-query-smoke-v1"
TD_ORDER_TRUTH_BASELINE = "td-order-truth-v1"
TD_HISTORICAL_CALLBACK_BOUNDARY_BASELINE = "td-historical-callback-boundary-v1"
MD_STARTUP_TRUTH_BASELINE = "md-startup-truth-v1"
MD_LOGIN_SMOKE_BASELINE = "md-login-smoke-v1"
TD_LOGIN_SMOKE_BASELINE = "td-login-smoke-v1"
MARKETDATA_SMOKE_BASELINE = "marketdata-smoke-v1"
LIVE_DATA_CLIENT_BOOTSTRAP_BASELINE = "live-data-client-bootstrap-smoke-v1"
NAUTILUS_LIVE_SMOKE_BASELINE = "nautilus-live-smoke-v1"
ORDER_TRADE_QUERY_BASELINE = "account-console.openctp-order-trade-query.v1"
REPO_DEBUG_SMOKE_BASELINE = "repo-debug-smoke-v1"
ORDER_LIFECYCLE_SMOKE_BASELINE = "nautilus-order-lifecycle-smoke-v1"
NAUTILUS_ENGINE_HARNESS_BASELINE = "ctp-nautilus-engine-harness-v1"
NAUTILUS_ENGINE_HARNESS_ACCOUNT_PROFILE = "openctp-tts-7x24-simulation"
NAUTILUS_ENGINE_HARNESS_EVIDENCE_CLASS = "openctp-tts-7x24-simulation"

_MD_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "restore_required",
    "evidence_only",
}
_TD_ORDER_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "boundary_required",
    "evidence_only",
}
_STARTUP_TRUTH_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "rebuild_required",
    "evidence_only",
}
_TD_MERGED_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "boundary_required",
    "evidence_only",
}
_LIVE_OPS_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "rebuild_required",
    "restore_required",
    "boundary_required",
    "evidence_only",
}
_RECONCILIATION_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "evidence_only",
}
_SESSION_REBUILD_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "rebuild_required",
    "evidence_only",
}
_TD_MERGED_RECONCILIATION_ALLOWED_DISPOSITIONS = {
    "clear",
    "manual_review_required",
    "boundary_required",
    "evidence_only",
}


def _kind_values(items: Iterable[object]) -> list[str]:
    values: list[str] = []
    for item in items:
        kind = getattr(item, "kind", None)
        value = getattr(kind, "value", kind)
        values.append(str(value))
    return values


def classify_md_truth_evidence_matrix_failure(
    evidence: CtpMdTruthEvidenceMatrix,
) -> str | None:
    if evidence.account_id is None:
        return "account_id_missing"
    if evidence.symbol is None:
        return "symbol_missing"
    if not evidence.restore_succeeded:
        return "restore_not_succeeded"
    if evidence.disposition not in _MD_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_md_truth_evidence_matrix_payload(
    evidence: CtpMdTruthEvidenceMatrix,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_md_truth_evidence_matrix_failure(evidence)
    return {
        "baseline": MD_TRUTH_EVIDENCE_MATRIX_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "evidence_version": evidence.evidence_version,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "symbol": evidence.symbol,
        "disposition": evidence.disposition,
        "startup_ready": evidence.startup_ready,
        "restore_triggered": evidence.restore_triggered,
        "restore_succeeded": evidence.restore_succeeded,
        "startup_flow_path": evidence.startup_flow_path,
        "restored_flow_path": evidence.restored_flow_path,
        "startup_first_tick_ts_epoch_us": evidence.startup_first_tick_ts_epoch_us,
        "restored_first_tick_ts_epoch_us": evidence.restored_first_tick_ts_epoch_us,
        "manual_review_codes": list(evidence.manual_review_codes),
        "restore_required_codes": list(evidence.restore_required_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_td_order_truth_evidence_matrix_failure(
    evidence: CtpTdOrderTruthEvidenceMatrix,
) -> str | None:
    if evidence.account_id is None:
        return "account_id_missing"
    if evidence.disposition not in _TD_ORDER_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_td_order_truth_evidence_matrix_payload(
    evidence: CtpTdOrderTruthEvidenceMatrix,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_td_order_truth_evidence_matrix_failure(evidence)
    return {
        "baseline": TD_ORDER_TRUTH_EVIDENCE_MATRIX_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "evidence_version": evidence.evidence_version,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "disposition": evidence.disposition,
        "observed_callback_count": evidence.observed_callback_count,
        "historical_callback_count": evidence.historical_callback_count,
        "delayed_callback_count": evidence.delayed_callback_count,
        "current_session_callback_count": evidence.current_session_callback_count,
        "first_historical_order_id": evidence.first_historical_order_id,
        "first_current_session_order_id": evidence.first_current_session_order_id,
        "manual_review_codes": list(evidence.manual_review_codes),
        "boundary_codes": list(evidence.boundary_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_startup_truth_evidence_matrix_failure(evidence: object) -> str | None:
    if getattr(evidence, "account_id") is None:
        return "account_id_missing"
    if getattr(evidence, "disposition") not in _STARTUP_TRUTH_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_startup_truth_evidence_matrix_payload(
    evidence: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_startup_truth_evidence_matrix_failure(evidence)
    return {
        "baseline": STARTUP_TRUTH_EVIDENCE_MATRIX_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "evidence_version": getattr(evidence, "evidence_version"),
        "captured_at_utc": getattr(evidence, "captured_at_utc"),
        "account_id": getattr(evidence, "account_id"),
        "disposition": getattr(evidence, "disposition"),
        "shared_flow_reuse_allowed": getattr(evidence, "shared_flow_reuse_allowed"),
        "session_rotated": getattr(evidence, "session_rotated"),
        "max_order_ref_reset": getattr(evidence, "max_order_ref_reset"),
        "shared_flow_path": getattr(evidence, "shared_flow_path"),
        "isolated_flow_path": getattr(evidence, "isolated_flow_path"),
        "shared_session_id": getattr(evidence, "shared_session_id"),
        "isolated_session_id": getattr(evidence, "isolated_session_id"),
        "shared_max_order_ref": getattr(evidence, "shared_max_order_ref"),
        "isolated_max_order_ref": getattr(evidence, "isolated_max_order_ref"),
        "shared_disconnect_count": getattr(evidence, "shared_disconnect_count"),
        "isolated_disconnect_count": getattr(evidence, "isolated_disconnect_count"),
        "manual_review_codes": list(getattr(evidence, "manual_review_codes")),
        "rebuild_required_codes": list(getattr(evidence, "rebuild_required_codes")),
        "evidence_only_codes": list(getattr(evidence, "evidence_only_codes")),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_td_merged_evidence_matrix_failure(evidence: object) -> str | None:
    if getattr(evidence, "account_id") is None:
        return "account_id_missing"
    if getattr(evidence, "position_count") < 0:
        return "position_count_invalid"
    if getattr(evidence, "disposition") not in _TD_MERGED_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_td_merged_evidence_matrix_payload(
    evidence: object,
    *,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_td_merged_evidence_matrix_failure(evidence)
    return {
        "baseline": TD_MERGED_EVIDENCE_MATRIX_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "evidence_version": getattr(evidence, "evidence_version"),
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "captured_at_utc": getattr(evidence, "captured_at_utc"),
        "account_id": getattr(evidence, "account_id"),
        "disposition": getattr(evidence, "disposition"),
        "position_count": getattr(evidence, "position_count"),
        "observed_callback_count": getattr(evidence, "observed_callback_count"),
        "historical_callback_count": getattr(evidence, "historical_callback_count"),
        "current_session_callback_count": getattr(evidence, "current_session_callback_count"),
        "available_ratio": getattr(evidence, "available_ratio"),
        "margin_ratio": getattr(evidence, "margin_ratio"),
        "manual_review_codes": list(getattr(evidence, "manual_review_codes")),
        "boundary_codes": list(getattr(evidence, "boundary_codes")),
        "evidence_only_codes": list(getattr(evidence, "evidence_only_codes")),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_live_ops_summary_failure(summary: object, disposition: str) -> str | None:
    if getattr(summary, "account_id") is None:
        return "account_id_missing"
    if getattr(summary, "symbol") is None:
        return "symbol_missing"
    if disposition not in _LIVE_OPS_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def classify_live_ops_evidence_matrix_failure(evidence: object) -> str | None:
    if getattr(evidence, "account_id") is None:
        return "account_id_missing"
    if getattr(evidence, "symbol") is None:
        return "symbol_missing"
    if getattr(evidence, "disposition") not in _LIVE_OPS_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def _finding_payloads(findings: Iterable[object]) -> list[dict[str, object]]:
    return [
        {
            "code": getattr(finding, "code"),
            "severity": getattr(finding, "severity"),
            "action": getattr(finding, "action"),
            "metric": getattr(finding, "metric"),
            "metric_value": getattr(finding, "metric_value"),
            "threshold": getattr(finding, "threshold"),
            "message": getattr(finding, "message"),
        }
        for finding in findings
    ]


def _exposure_payloads(exposures: Iterable[object]) -> list[dict[str, object]]:
    return [
        {
            "venue_symbol": getattr(exposure, "venue_symbol"),
            "exchange_id": getattr(exposure, "exchange_id"),
            "long_qty": getattr(exposure, "long_qty"),
            "short_qty": getattr(exposure, "short_qty"),
            "gross_qty": getattr(exposure, "gross_qty"),
            "net_qty": getattr(exposure, "net_qty"),
            "abs_net_qty": getattr(exposure, "abs_net_qty"),
            "position_cost": getattr(exposure, "position_cost"),
        }
        for exposure in exposures
    ]


def classify_reconciliation_snapshot_failure(snapshot: object, summary: object) -> str | None:
    positions = snapshot.query_snapshot.positions
    account = snapshot.query_snapshot.account
    if positions.query_code != 0:
        return "positions_query_failed"
    if positions.timed_out:
        return "positions_timed_out"
    if not positions.completed:
        return "positions_incomplete"
    if account.query_code != 0:
        return "account_query_failed"
    if account.timed_out:
        return "account_timed_out"
    if not account.completed:
        return "account_incomplete"
    if getattr(summary, "account_id") is None:
        return "account_id_missing"
    if getattr(summary, "account_balance") is None:
        return "account_balance_missing"
    return None


def classify_reconciliation_policy_failure(result: object) -> str | None:
    if result.summary.account_id is None:
        return "account_id_missing"
    if len(result.findings) == 0:
        return "findings_missing"
    if result.disposition not in _RECONCILIATION_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def classify_reconciliation_evidence_failure(evidence: object) -> str | None:
    if evidence.account_id is None:
        return "account_id_missing"
    if evidence.finding_count <= 0:
        return "finding_count_missing"
    if evidence.disposition not in _RECONCILIATION_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_reconciliation_snapshot_payload(
    *,
    snapshot: object,
    summary: object,
    policy_result: object,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_reconciliation_snapshot_failure(snapshot, summary)
    positions = snapshot.query_snapshot.positions
    account_snapshot = snapshot.query_snapshot.account
    account = account_snapshot.account
    manual_review_codes = tuple(
        finding.code for finding in policy_result.findings if finding.action == "manual_review_required"
    )
    evidence_only_codes = tuple(
        finding.code for finding in policy_result.findings if finding.action == "evidence_only"
    )
    return {
        "baseline": RECONCILIATION_SNAPSHOT_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "session_label": session_label,
        "positions": {
            "request_id": positions.request_id,
            "query_code": positions.query_code,
            "completed": positions.completed,
            "timed_out": positions.timed_out,
            "no_positions": positions.no_positions,
            "position_count": positions.position_count,
        },
        "account": {
            "request_id": account_snapshot.request_id,
            "query_code": account_snapshot.query_code,
            "completed": account_snapshot.completed,
            "timed_out": account_snapshot.timed_out,
            "account_id": None if account is None else account.account_id,
        },
        "position_request_id": summary.position_request_id,
        "account_request_id": summary.account_request_id,
        "account_id": summary.account_id,
        "position_line_count": summary.position_line_count,
        "symbol_count": summary.symbol_count,
        "total_long_qty": summary.total_long_qty,
        "total_short_qty": summary.total_short_qty,
        "gross_position_qty": summary.gross_position_qty,
        "total_position_cost": summary.total_position_cost,
        "account_balance": summary.account_balance,
        "account_available": summary.account_available,
        "account_margin": summary.account_margin,
        "available_ratio": summary.available_ratio,
        "margin_ratio": summary.margin_ratio,
        "dominant_exposure_symbol": summary.dominant_exposure_symbol,
        "dominant_exposure_exchange": summary.dominant_exposure_exchange,
        "dominant_exposure_abs_net_qty": summary.dominant_exposure_abs_net_qty,
        "disposition": policy_result.disposition,
        "requires_manual_review": policy_result.requires_manual_review,
        "finding_count": len(policy_result.findings),
        "manual_review_codes": list(manual_review_codes),
        "evidence_only_codes": list(evidence_only_codes),
        "findings": _finding_payloads(policy_result.findings),
        "top_exposures": _exposure_payloads(summary.exposures[:10]),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def build_reconciliation_policy_payload(
    result: object,
    *,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_reconciliation_policy_failure(result)
    return {
        "baseline": RECONCILIATION_POLICY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "session_label": session_label,
        "disposition": result.disposition,
        "requires_manual_review": result.requires_manual_review,
        "account_id": result.summary.account_id,
        "position_line_count": result.summary.position_line_count,
        "gross_position_qty": result.summary.gross_position_qty,
        "available_ratio": result.summary.available_ratio,
        "margin_ratio": result.summary.margin_ratio,
        "dominant_exposure_symbol": result.summary.dominant_exposure_symbol,
        "dominant_exposure_abs_net_qty": result.summary.dominant_exposure_abs_net_qty,
        "findings": _finding_payloads(result.findings),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def build_reconciliation_evidence_payload(
    evidence: object,
    *,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_reconciliation_evidence_failure(evidence)
    return {
        "baseline": RECONCILIATION_EVIDENCE_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "evidence_version": evidence.evidence_version,
        "session_label": session_label,
        "captured_at_utc": evidence.captured_at_utc,
        "account_id": evidence.account_id,
        "disposition": evidence.disposition,
        "requires_manual_review": evidence.requires_manual_review,
        "finding_count": evidence.finding_count,
        "manual_review_codes": list(evidence.manual_review_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "position_line_count": evidence.position_line_count,
        "symbol_count": evidence.symbol_count,
        "gross_position_qty": evidence.gross_position_qty,
        "available_ratio": evidence.available_ratio,
        "margin_ratio": evidence.margin_ratio,
        "dominant_exposure_symbol": evidence.dominant_exposure_symbol,
        "dominant_exposure_abs_net_qty": evidence.dominant_exposure_abs_net_qty,
        "top_exposures": _exposure_payloads(evidence.top_exposures),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_td_startup_truth_failure(evidence: object) -> str | None:
    if not evidence.ready:
        return "bootstrap_not_ready"
    if evidence.login_success is not True:
        return "login_failed"
    if evidence.settlement_code != 0:
        return "settlement_not_confirmed"
    return None


def build_td_startup_truth_payload(
    evidence: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_td_startup_truth_failure(evidence)
    return {
        "baseline": TD_STARTUP_TRUTH_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": evidence.flow_path,
        "ready": evidence.ready,
        "login_success": evidence.login_success,
        "settlement_code": evidence.settlement_code,
        "front_id": evidence.front_id,
        "session_id": evidence.session_id,
        "max_order_ref": evidence.max_order_ref,
        "disconnect_count": evidence.disconnect_count,
        "disconnect_reasons": list(evidence.disconnect_reasons),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_session_rebuild_policy_failure(result: object) -> str | None:
    if not result.shared_truth.ready:
        return "shared_bootstrap_not_ready"
    if not result.isolated_truth.ready:
        return "isolated_bootstrap_not_ready"
    if len(result.findings) == 0:
        return "findings_missing"
    if result.disposition not in _SESSION_REBUILD_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_session_rebuild_policy_payload(
    result: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_session_rebuild_policy_failure(result)
    return {
        "baseline": TD_SESSION_REBUILD_POLICY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "disposition": result.disposition,
        "shared_flow_reuse_allowed": result.shared_flow_reuse_allowed,
        "session_rotated": result.session_rotated,
        "max_order_ref_reset": result.max_order_ref_reset,
        "shared_truth": {
            "flow_path": result.shared_truth.flow_path,
            "flow_mode": result.shared_truth.flow_mode,
            "ready": result.shared_truth.ready,
            "login_success": result.shared_truth.login_success,
            "settlement_code": result.shared_truth.settlement_code,
            "front_id": result.shared_truth.front_id,
            "session_id": result.shared_truth.session_id,
            "max_order_ref": result.shared_truth.max_order_ref,
            "disconnect_count": result.shared_truth.disconnect_count,
        },
        "isolated_truth": {
            "flow_path": result.isolated_truth.flow_path,
            "flow_mode": result.isolated_truth.flow_mode,
            "ready": result.isolated_truth.ready,
            "login_success": result.isolated_truth.login_success,
            "settlement_code": result.isolated_truth.settlement_code,
            "front_id": result.isolated_truth.front_id,
            "session_id": result.isolated_truth.session_id,
            "max_order_ref": result.isolated_truth.max_order_ref,
            "disconnect_count": result.isolated_truth.disconnect_count,
        },
        "findings": _finding_payloads(result.findings),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_md_restore_policy_failure(result: object) -> str | None:
    if not result.startup_truth.ready:
        return "startup_not_ready"
    if not result.restore_result.triggered:
        return "restore_not_triggered"
    if not result.restore_succeeded:
        return "restore_not_succeeded"
    if result.restored_truth.first_tick_symbol is None:
        return "restored_tick_missing"
    if result.disposition not in _MD_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_md_restore_policy_payload(
    result: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_md_restore_policy_failure(result)
    return {
        "baseline": MD_RESTORE_POLICY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "disposition": result.disposition,
        "restore_triggered": result.restore_result.triggered,
        "restore_succeeded": result.restore_succeeded,
        "startup_truth": {
            "flow_path": result.startup_truth.flow_path,
            "flow_mode": result.startup_truth.flow_mode,
            "selected_symbols": list(result.startup_truth.selected_symbols),
            "ready": result.startup_truth.ready,
            "first_tick_symbol": result.startup_truth.first_tick_symbol,
            "first_tick_ts_epoch_us": result.startup_truth.first_tick_ts_epoch_us,
        },
        "restored_truth": {
            "flow_path": result.restored_truth.flow_path,
            "flow_mode": result.restored_truth.flow_mode,
            "selected_symbols": list(result.restored_truth.selected_symbols),
            "ready": result.restored_truth.ready,
            "first_tick_symbol": result.restored_truth.first_tick_symbol,
            "first_tick_ts_epoch_us": result.restored_truth.first_tick_ts_epoch_us,
        },
        "restored_symbols": list(result.restore_result.restored_symbols),
        "findings": _finding_payloads(result.findings),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_td_truth_merge_snapshot_failure(snapshot: object) -> str | None:
    if snapshot.order_truth.account_id is None:
        return "order_truth_account_missing"
    if not snapshot.positions.completed:
        return "positions_incomplete"
    if snapshot.account.account is None:
        return "account_missing"
    return None


def _order_truth_payload(order_truth: object) -> dict[str, object]:
    return {
        "account_id": order_truth.account_id,
        "disposition": order_truth.disposition,
        "observed_callback_count": order_truth.observed_callback_count,
        "historical_callback_count": order_truth.historical_callback_count,
        "delayed_callback_count": order_truth.delayed_callback_count,
        "current_session_callback_count": order_truth.current_session_callback_count,
        "first_historical_order_id": order_truth.first_historical_order_id,
        "first_current_session_order_id": order_truth.first_current_session_order_id,
        "manual_review_codes": list(order_truth.manual_review_codes),
        "boundary_codes": list(order_truth.boundary_codes),
        "evidence_only_codes": list(order_truth.evidence_only_codes),
    }


def _positions_payload(positions: object) -> dict[str, object]:
    return {
        "request_id": positions.request_id,
        "query_code": positions.query_code,
        "completed": positions.completed,
        "timed_out": positions.timed_out,
        "no_positions": positions.no_positions,
        "position_count": positions.position_count,
    }


def _account_payload(account_snapshot: object) -> dict[str, object]:
    account = account_snapshot.account
    return {
        "request_id": account_snapshot.request_id,
        "query_code": account_snapshot.query_code,
        "completed": account_snapshot.completed,
        "timed_out": account_snapshot.timed_out,
        "account_present": account is not None,
        "account_id": None if account is None else account.account_id,
        "balance": None if account is None else account.balance,
        "available": None if account is None else account.available,
        "margin": None if account is None else account.margin,
    }


def build_td_truth_merge_snapshot_payload(
    snapshot: object,
    *,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_td_truth_merge_snapshot_failure(snapshot)
    return {
        "baseline": TD_TRUTH_MERGE_SNAPSHOT_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": snapshot.order_truth.account_id,
        "order_truth": _order_truth_payload(snapshot.order_truth),
        "positions": _positions_payload(snapshot.positions),
        "account": _account_payload(snapshot.account),
        "order_truth_disposition": snapshot.order_truth.disposition,
        "observed_callback_count": snapshot.order_truth.observed_callback_count,
        "historical_callback_count": snapshot.order_truth.historical_callback_count,
        "position_count": snapshot.positions.position_count,
        "positions_completed": snapshot.positions.completed,
        "account_query_code": snapshot.account.query_code,
        "account_present": snapshot.account.account is not None,
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_td_merged_reconciliation_policy_failure(result: object) -> str | None:
    if result.snapshot.positions.query_code != 0:
        return "positions_query_failed"
    if result.snapshot.positions.timed_out:
        return "positions_timed_out"
    if not result.snapshot.positions.completed:
        return "positions_incomplete"
    if result.snapshot.account.query_code != 0:
        return "account_query_failed"
    if result.snapshot.account.timed_out:
        return "account_timed_out"
    if not result.snapshot.account.completed:
        return "account_incomplete"
    if result.snapshot.account.account is None:
        return "account_missing"
    if result.disposition not in _TD_MERGED_RECONCILIATION_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_td_merged_reconciliation_policy_payload(
    result: object,
    *,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_td_merged_reconciliation_policy_failure(result)
    return {
        "baseline": TD_MERGED_RECONCILIATION_POLICY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": result.snapshot.order_truth.account_id,
        "order_truth": _order_truth_payload(result.snapshot.order_truth),
        "positions": _positions_payload(result.snapshot.positions),
        "account": _account_payload(result.snapshot.account),
        "disposition": result.disposition,
        "position_count": result.snapshot.positions.position_count,
        "observed_callback_count": result.snapshot.order_truth.observed_callback_count,
        "historical_callback_count": result.snapshot.order_truth.historical_callback_count,
        "current_session_callback_count": result.snapshot.order_truth.current_session_callback_count,
        "available_ratio": result.available_ratio,
        "margin_ratio": result.margin_ratio,
        "manual_review_codes": [
            finding.code for finding in result.findings if finding.action == "manual_review_required"
        ],
        "boundary_codes": [
            finding.code for finding in result.findings if finding.action == "boundary_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in result.findings if finding.action == "evidence_only"
        ],
        "findings": _finding_payloads(result.findings),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def instrument_matches_requested_symbol(
    *,
    requested_symbol: str,
    venue_symbol: str,
    display_symbol: str,
) -> bool:
    requested = requested_symbol.strip().lower()
    if not requested:
        return False
    candidates = {
        venue_symbol.strip().lower(),
        display_symbol.strip().lower(),
        display_symbol.split(".", 1)[0].strip().lower(),
    }
    return requested in candidates


def _query_adapter_base_failure(snapshot: object) -> str | None:
    if snapshot.positions.query_code != 0:
        return "positions_query_failed"
    if snapshot.positions.timed_out:
        return "positions_timed_out"
    if not snapshot.positions.completed:
        return "positions_incomplete"
    if snapshot.account.query_code != 0:
        return "account_query_failed"
    if snapshot.account.timed_out:
        return "account_timed_out"
    if not snapshot.account.completed:
        return "account_incomplete"
    if snapshot.account.account is None:
        return "account_missing"
    return None


def classify_query_adapter_failure(
    *,
    snapshot: object,
    instrument_result: object | None,
    requested_instrument_symbol: str | None,
    order_truth_result: object | None,
    order_trade_snapshot_result: object | None,
    reconciliation_policy: object | None,
    merged_policy_result: object | None,
) -> str | None:
    failure_reason = _query_adapter_base_failure(snapshot)
    if failure_reason is not None:
        return failure_reason

    if instrument_result is not None:
        matched_symbols = _matched_instrument_symbols(
            instrument_result,
            requested_symbol=requested_instrument_symbol or "",
        )
        if not instrument_result.loaded:
            return "instrument_query_incomplete"
        if instrument_result.instrument_count == 0:
            return "instrument_missing"
        if not matched_symbols:
            return "instrument_symbol_mismatch"

    if order_truth_result is not None and order_truth_result.disposition == "manual_review_required":
        return "order_truth_manual_review_required"
    if (
        order_trade_snapshot_result is not None
        and order_trade_snapshot_result.disposition == "manual_review_required"
    ):
        return "order_trade_snapshot_manual_review_required"
    if reconciliation_policy is not None and reconciliation_policy.disposition == "manual_review_required":
        return "reconciliation_manual_review_required"
    if merged_policy_result is not None and merged_policy_result.disposition == "manual_review_required":
        return "merged_policy_manual_review_required"
    return None


def _matched_instrument_symbols(
    instrument_result: object,
    *,
    requested_symbol: str,
) -> list[str]:
    return [
        item.display_symbol
        for item in instrument_result.instruments
        if instrument_matches_requested_symbol(
            requested_symbol=requested_symbol,
            venue_symbol=item.venue_symbol,
            display_symbol=item.display_symbol,
        )
    ]


def _query_account_payload(account_snapshot: object) -> dict[str, object]:
    account = account_snapshot.account
    return {
        "request_id": account_snapshot.request_id,
        "query_code": account_snapshot.query_code,
        "completed": account_snapshot.completed,
        "timed_out": account_snapshot.timed_out,
        "account_id": None if account is None else account.account_id,
        "balance": None if account is None else account.balance,
        "available": None if account is None else account.available,
    }


def _instrument_payload(instrument_result: object | None, requested_symbol: str | None) -> dict[str, object] | None:
    if instrument_result is None:
        return None
    matched_symbols = _matched_instrument_symbols(
        instrument_result,
        requested_symbol=requested_symbol or "",
    )
    first_instrument = None
    if instrument_result.instruments:
        instrument = instrument_result.instruments[0]
        product_kind = getattr(instrument.product_kind, "value", instrument.product_kind)
        first_instrument = {
            "display_symbol": instrument.display_symbol,
            "underlying": instrument.underlying,
            "contract_month": instrument.contract_month,
            "product_kind": product_kind,
            "price_tick": instrument.price_tick,
            "volume_multiple": instrument.volume_multiple,
        }
    return {
        "requested_symbol": requested_symbol,
        "request_id": instrument_result.request_id,
        "loaded": instrument_result.loaded,
        "instrument_count": instrument_result.instrument_count,
        "symbols": [item.display_symbol for item in instrument_result.instruments],
        "matched_symbols": matched_symbols,
        "exact_symbol_found": bool(matched_symbols),
        "first_instrument": first_instrument,
    }


def _order_truth_policy_payload(
    order_truth_result: object | None,
    *,
    account_id: str | None,
) -> dict[str, object] | None:
    if order_truth_result is None:
        return None
    return {
        "account_id": account_id,
        "ready": order_truth_result.baseline.ready,
        "login_success": order_truth_result.baseline.login_success,
        "settlement_code": order_truth_result.baseline.settlement_code,
        "disposition": order_truth_result.disposition,
        "observed_callback_count": order_truth_result.baseline.observed_callback_count,
        "observed_order_event_count": order_truth_result.baseline.observed_order_event_count,
        "observed_trade_event_count": order_truth_result.baseline.observed_trade_event_count,
        "no_callbacks_observed": order_truth_result.baseline.no_callbacks_observed,
        "historical_callback_count": order_truth_result.historical_callback_count,
        "delayed_callback_count": order_truth_result.delayed_callback_count,
        "current_session_callback_count": order_truth_result.current_session_callback_count,
        "first_order_id": order_truth_result.baseline.first_order_id,
        "first_order_ref": order_truth_result.baseline.first_order_ref,
        "first_is_trade": order_truth_result.baseline.first_is_trade,
        "first_historical_order_id": order_truth_result.first_historical_order_id,
        "first_current_session_order_id": order_truth_result.first_current_session_order_id,
        "manual_review_codes": [
            finding.code for finding in order_truth_result.findings if finding.action == "manual_review_required"
        ],
        "boundary_codes": [
            finding.code for finding in order_truth_result.findings if finding.action == "boundary_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in order_truth_result.findings if finding.action == "evidence_only"
        ],
    }


def _order_trade_snapshot_payload(
    order_trade_snapshot_result: object | None,
    *,
    account_id: str | None,
) -> dict[str, object] | None:
    if order_trade_snapshot_result is None:
        return None
    return {
        "account_id": account_id,
        "flow_path": order_trade_snapshot_result.baseline.flow_path,
        "flow_mode": order_trade_snapshot_result.baseline.flow_mode,
        "ready": order_trade_snapshot_result.baseline.ready,
        "login_success": order_trade_snapshot_result.baseline.login_success,
        "settlement_code": order_trade_snapshot_result.baseline.settlement_code,
        "disposition": order_trade_snapshot_result.disposition,
        "observed_callback_count": order_trade_snapshot_result.baseline.observed_callback_count,
        "observed_order_event_count": order_trade_snapshot_result.observed_order_event_count,
        "observed_trade_event_count": order_trade_snapshot_result.observed_trade_event_count,
        "no_order_events": order_trade_snapshot_result.no_order_events,
        "no_trade_events": order_trade_snapshot_result.no_trade_events,
        "historical_order_count": order_trade_snapshot_result.historical_order_count,
        "historical_trade_count": order_trade_snapshot_result.historical_trade_count,
        "delayed_order_count": order_trade_snapshot_result.delayed_order_count,
        "delayed_trade_count": order_trade_snapshot_result.delayed_trade_count,
        "historical_residue_order_count": order_trade_snapshot_result.historical_residue_order_count,
        "historical_residue_trade_count": order_trade_snapshot_result.historical_residue_trade_count,
        "current_session_order_count": order_trade_snapshot_result.current_session_order_count,
        "current_session_trade_count": order_trade_snapshot_result.current_session_trade_count,
        "first_order_event_id": order_trade_snapshot_result.first_order_event_id,
        "first_trade_event_id": order_trade_snapshot_result.first_trade_event_id,
        "first_historical_order_id": order_trade_snapshot_result.first_historical_order_id,
        "first_historical_trade_id": order_trade_snapshot_result.first_historical_trade_id,
        "first_current_session_order_id": order_trade_snapshot_result.first_current_session_order_id,
        "first_current_session_trade_id": order_trade_snapshot_result.first_current_session_trade_id,
        "manual_review_codes": [
            finding.code
            for finding in order_trade_snapshot_result.findings
            if finding.action == "manual_review_required"
        ],
        "boundary_codes": [
            finding.code for finding in order_trade_snapshot_result.findings if finding.action == "boundary_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in order_trade_snapshot_result.findings if finding.action == "evidence_only"
        ],
    }


def _query_reconciliation_payload(
    *,
    summary: object | None,
    policy: object | None,
    evidence: object | None,
) -> dict[str, object] | None:
    if summary is None or policy is None or evidence is None:
        return None
    return {
        "account_id": summary.account_id,
        "position_request_id": summary.position_request_id,
        "account_request_id": summary.account_request_id,
        "position_line_count": summary.position_line_count,
        "symbol_count": summary.symbol_count,
        "total_long_qty": summary.total_long_qty,
        "total_short_qty": summary.total_short_qty,
        "gross_position_qty": summary.gross_position_qty,
        "total_position_cost": summary.total_position_cost,
        "account_balance": summary.account_balance,
        "account_available": summary.account_available,
        "account_margin": summary.account_margin,
        "available_ratio": summary.available_ratio,
        "margin_ratio": summary.margin_ratio,
        "dominant_exposure_symbol": summary.dominant_exposure_symbol,
        "dominant_exposure_exchange": summary.dominant_exposure_exchange,
        "dominant_exposure_abs_net_qty": summary.dominant_exposure_abs_net_qty,
        "disposition": policy.disposition,
        "requires_manual_review": policy.requires_manual_review,
        "finding_count": len(policy.findings),
        "manual_review_codes": list(evidence.manual_review_codes),
        "evidence_only_codes": list(evidence.evidence_only_codes),
        "captured_at_utc": evidence.captured_at_utc,
        "evidence_version": evidence.evidence_version,
        "findings": _finding_payloads(policy.findings),
        "top_exposures": _exposure_payloads(evidence.top_exposures),
    }


def _query_merged_policy_payload(merged_policy_result: object | None) -> dict[str, object] | None:
    if merged_policy_result is None:
        return None
    return {
        "account_id": merged_policy_result.snapshot.order_truth.account_id,
        "order_truth": _order_truth_payload(merged_policy_result.snapshot.order_truth),
        "positions": _positions_payload(merged_policy_result.snapshot.positions),
        "account": _account_payload(merged_policy_result.snapshot.account),
        "disposition": merged_policy_result.disposition,
        "position_count": merged_policy_result.snapshot.positions.position_count,
        "observed_callback_count": merged_policy_result.snapshot.order_truth.observed_callback_count,
        "historical_callback_count": merged_policy_result.snapshot.order_truth.historical_callback_count,
        "current_session_callback_count": merged_policy_result.snapshot.order_truth.current_session_callback_count,
        "available_ratio": merged_policy_result.available_ratio,
        "margin_ratio": merged_policy_result.margin_ratio,
        "manual_review_codes": [
            finding.code for finding in merged_policy_result.findings if finding.action == "manual_review_required"
        ],
        "boundary_codes": [
            finding.code for finding in merged_policy_result.findings if finding.action == "boundary_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in merged_policy_result.findings if finding.action == "evidence_only"
        ],
        "findings": _finding_payloads(merged_policy_result.findings),
    }


def build_query_adapter_payload(
    *,
    snapshot: object,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    instrument_result: object | None,
    requested_instrument_symbol: str | None,
    account_id: str | None,
    order_truth_result: object | None,
    order_trade_snapshot_result: object | None,
    reconciliation_summary: object | None,
    reconciliation_policy: object | None,
    reconciliation_evidence: object | None,
    merged_policy_result: object | None,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_query_adapter_failure(
        snapshot=snapshot,
        instrument_result=instrument_result,
        requested_instrument_symbol=requested_instrument_symbol,
        order_truth_result=order_truth_result,
        order_trade_snapshot_result=order_trade_snapshot_result,
        reconciliation_policy=reconciliation_policy,
        merged_policy_result=merged_policy_result,
    )
    return {
        "baseline": QUERY_ADAPTER_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "positions": _positions_payload(snapshot.positions),
        "account": _query_account_payload(snapshot.account),
        "instrument": _instrument_payload(instrument_result, requested_instrument_symbol),
        "order_truth": _order_truth_policy_payload(order_truth_result, account_id=account_id),
        "order_trade_snapshot": _order_trade_snapshot_payload(
            order_trade_snapshot_result,
            account_id=account_id,
        ),
        "reconciliation": _query_reconciliation_payload(
            summary=reconciliation_summary,
            policy=reconciliation_policy,
            evidence=reconciliation_evidence,
        ),
        "merged_policy": _query_merged_policy_payload(merged_policy_result),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_instrument_query_failure(result: object, requested_symbol: str) -> str | None:
    matched_symbols = _matched_instrument_symbols(result, requested_symbol=requested_symbol)
    if not result.loaded:
        return "instrument_query_incomplete"
    if result.instrument_count == 0:
        return "instrument_missing"
    if not matched_symbols:
        return "instrument_symbol_mismatch"
    return None


def build_instrument_query_payload(
    result: object,
    *,
    requested_symbol: str,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_instrument_query_failure(result, requested_symbol)
    instrument_payload = _instrument_payload(result, requested_symbol)
    assert instrument_payload is not None
    return {
        "baseline": INSTRUMENT_QUERY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        **instrument_payload,
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_account_query_failure(result: object) -> str | None:
    if not result.bootstrap.ready:
        return "bootstrap_not_ready"
    if result.query_code != 0:
        return "account_query_failed"
    if result.timed_out:
        return "account_query_timed_out"
    if not result.completed:
        return "account_snapshot_incomplete"
    if result.account is None:
        return "account_missing"
    return None


def build_account_query_payload(
    result: object,
    *,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_account_query_failure(result)
    return {
        "baseline": ACCOUNT_QUERY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "query_request_id": result.query_request_id,
        "query_code": result.query_code,
        "completed": result.completed,
        "timed_out": result.timed_out,
        "account": None
        if result.account is None
        else {
            "account_id": result.account.account_id,
            "balance": result.account.balance,
            "available": result.account.available,
            "margin": result.account.margin,
            "commission": result.account.commission,
            "close_profit": result.account.close_profit,
            "position_profit": result.account.position_profit,
        },
        "bootstrap_ready": result.bootstrap.ready,
        "td_login_success": result.bootstrap.execution_bootstrap.td_smoke.login_success,
        "td_settlement_code": result.bootstrap.execution_bootstrap.td_smoke.settlement_code,
        "disconnects": result.disconnects,
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_position_query_failure(result: object) -> str | None:
    if not result.bootstrap.ready:
        return "bootstrap_not_ready"
    if result.query_code != 0:
        return "position_query_failed"
    if result.timed_out:
        return "position_query_timed_out"
    if not result.completed:
        return "position_snapshot_incomplete"
    return None


def _position_record_payloads(positions: Iterable[object]) -> list[dict[str, object]]:
    return [
        {
            "venue_symbol": position.venue_symbol,
            "exchange_id": position.exchange_id,
            "direction": position.direction,
            "position_qty": position.position_qty,
            "yd_position_qty": position.yd_position_qty,
            "td_position_qty": position.td_position_qty,
            "position_cost": position.position_cost,
        }
        for position in positions
    ]


def build_position_query_payload(
    result: object,
    *,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_position_query_failure(result)
    return {
        "baseline": POSITION_QUERY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "query_request_id": result.query_request_id,
        "query_code": result.query_code,
        "completed": result.completed,
        "timed_out": result.timed_out,
        "no_positions": result.no_positions,
        "position_count": result.position_count,
        "positions": _position_record_payloads(result.positions),
        "bootstrap_ready": result.bootstrap.ready,
        "td_login_success": result.bootstrap.execution_bootstrap.td_smoke.login_success,
        "td_settlement_code": result.bootstrap.execution_bootstrap.td_smoke.settlement_code,
        "disconnects": result.disconnects,
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_td_order_truth_failure(result: object) -> str | None:
    if not result.ready:
        return "bootstrap_not_ready"
    if result.login_success is not True:
        return "login_failed"
    if result.settlement_code != 0:
        return "settlement_not_confirmed"
    return None


def _observed_callback_payloads(callbacks: Iterable[object]) -> list[dict[str, object]]:
    return [
        {
            "order_id": callback.order_id,
            "order_ref": callback.order_ref,
            "front_id": callback.front_id,
            "session_id": callback.session_id,
            "is_trade": callback.is_trade,
            "ts_epoch_us": callback.ts_epoch_us,
            "status": callback.status,
        }
        for callback in callbacks
    ]


def build_td_order_truth_payload(
    result: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_td_order_truth_failure(result)
    return {
        "baseline": TD_ORDER_TRUTH_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": result.flow_path,
        "ready": result.ready,
        "login_success": result.login_success,
        "settlement_code": result.settlement_code,
        "disconnect_count": result.disconnect_count,
        "disconnect_reasons": list(result.disconnect_reasons),
        "observed_callback_count": result.observed_callback_count,
        "observed_order_event_count": result.observed_order_event_count,
        "observed_trade_event_count": result.observed_trade_event_count,
        "no_callbacks_observed": result.no_callbacks_observed,
        "first_order_id": result.first_order_id,
        "first_order_ref": result.first_order_ref,
        "first_session_id": result.first_session_id,
        "first_front_id": result.first_front_id,
        "first_is_trade": result.first_is_trade,
        "observed_callbacks": _observed_callback_payloads(result.observed_callbacks),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_td_historical_callback_boundary_failure(result: object) -> str | None:
    if not result.baseline.ready:
        return "bootstrap_not_ready"
    if result.disposition not in _TD_ORDER_ALLOWED_DISPOSITIONS:
        return "unexpected_disposition"
    return None


def build_td_historical_callback_boundary_payload(
    result: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_td_historical_callback_boundary_failure(result)
    return {
        "baseline": TD_HISTORICAL_CALLBACK_BOUNDARY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "disposition": result.disposition,
        "observed_callback_count": result.baseline.observed_callback_count,
        "historical_callback_count": result.historical_callback_count,
        "delayed_callback_count": result.delayed_callback_count,
        "current_session_callback_count": result.current_session_callback_count,
        "first_historical_order_id": result.first_historical_order_id,
        "first_current_session_order_id": result.first_current_session_order_id,
        "login_front_id": result.baseline.login_front_id,
        "login_session_id": result.baseline.login_session_id,
        "login_max_order_ref": result.baseline.login_max_order_ref,
        "findings": _finding_payloads(result.findings),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_md_startup_truth_failure(evidence: object) -> str | None:
    if not evidence.ready:
        return "bootstrap_not_ready"
    if evidence.login_success is not True:
        return "login_failed"
    if evidence.subscribe_code != 0:
        return "subscribe_failed"
    if evidence.first_tick_symbol is None:
        return "first_tick_missing"
    return None


def build_md_startup_truth_payload(
    evidence: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_md_startup_truth_failure(evidence)
    return {
        "baseline": MD_STARTUP_TRUTH_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": evidence.flow_path,
        "selected_symbols": list(evidence.selected_symbols),
        "ready": evidence.ready,
        "login_success": evidence.login_success,
        "login_error_id": evidence.login_error_id,
        "subscribe_code": evidence.subscribe_code,
        "first_tick_symbol": evidence.first_tick_symbol,
        "first_tick_last": evidence.first_tick_last,
        "first_tick_bid": evidence.first_tick_bid,
        "first_tick_ask": evidence.first_tick_ask,
        "first_tick_ts_epoch_us": evidence.first_tick_ts_epoch_us,
        "disconnect_count": evidence.disconnect_count,
        "disconnect_reasons": list(evidence.disconnect_reasons),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def classify_md_login_smoke_failure(result: object) -> str | None:
    if not result.login_success:
        return "login_failed"
    if result.subscribe_code != 0:
        return "subscribe_failed"
    if result.first_tick_symbol is None:
        return "first_tick_missing"
    return None


def build_md_login_smoke_payload(
    result: object,
    *,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    instruments: Iterable[object],
    instrument_override: bool,
    md_front_override: dict[str, object],
    md_login_override: dict[str, object],
    runtime_pack_override: dict[str, object],
    export: dict[str, object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    events = tuple(bridge_events)
    failure_reason = classify_md_login_smoke_failure(result)
    return {
        "baseline": MD_LOGIN_SMOKE_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": flow_path,
        "instruments": list(instruments),
        "instrument_override": instrument_override,
        "md_front_override": md_front_override,
        "md_login_override": md_login_override,
        "runtime_pack_override": runtime_pack_override,
        "init_code": result.init_code,
        "login_request_code": result.login_request_code,
        "subscribe_code": result.subscribe_code,
        "login_success": result.login_success,
        "login_error_id": result.login_error_id,
        "login_error_message": result.login_error_message,
        "front_connected": bool(getattr(result, "front_connected", False)),
        "front_connected_count": int(getattr(result, "front_connected_count", 0)),
        "disconnect_count": int(getattr(result, "disconnect_count", 0)),
        "disconnect_reasons": list(getattr(result, "disconnect_reasons", [])),
        "first_tick_symbol": result.first_tick_symbol,
        "first_tick_last": result.first_tick_last,
        "first_tick_bid": result.first_tick_bid,
        "first_tick_ask": result.first_tick_ask,
        "first_tick_ts_epoch_us": result.first_tick_ts_epoch_us,
        "bridge_event_kinds": _kind_values(events),
        "bridge_tick_symbol": next(
            (event.venue_symbol for event in events if getattr(event, "venue_symbol", None)),
            None,
        ),
        "export": export,
    }


def classify_td_login_smoke_failure(login: object | None, settlement_code: int) -> str | None:
    if login is None:
        return "login_response_missing"
    if login.success is not True:
        return "login_failed"
    if settlement_code != 0:
        return "settlement_not_confirmed"
    return None


def build_td_login_smoke_payload(
    *,
    login: object | None,
    settlement_code: int,
    init_code: int,
    authenticate_code: int,
    login_code: int,
    flow_path: str,
    flow_mode: str,
    session_label: str,
    disconnects: Iterable[object],
    export: dict[str, object],
) -> dict[str, object]:
    failure_reason = classify_td_login_smoke_failure(login, settlement_code)
    return {
        "baseline": TD_LOGIN_SMOKE_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": flow_path,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "init_code": init_code,
        "authenticate_code": authenticate_code,
        "login_code": login_code,
        "settlement_code": settlement_code,
        "login_success": None if login is None else login.success,
        "login_error_id": None if login is None else login.error_id,
        "login_error_message": None if login is None else login.error_message,
        "front_id": None if login is None else login.front_id,
        "session_id": None if login is None else login.session_id,
        "max_order_ref": None if login is None else login.max_order_ref,
        "disconnects": list(disconnects),
        "export": export,
    }


def classify_marketdata_smoke_failure(result: object, requested_symbol: str) -> str | None:
    if not result.instrument_loaded:
        return "instrument_not_loaded"
    if requested_symbol not in result.selected_symbols:
        return "symbol_not_selected"
    if not result.bootstrap_state.started:
        return "bootstrap_not_started"
    if not result.md_smoke.login_success:
        return "login_failed"
    if result.md_smoke.subscribe_code != 0:
        return "subscribe_failed"
    if result.md_smoke.first_tick_symbol is None:
        return "first_tick_missing"
    if result.md_smoke.first_tick_symbol != requested_symbol:
        return "unexpected_tick_symbol"
    return None


def build_marketdata_smoke_payload(
    result: object,
    *,
    requested_symbol: str,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    events = tuple(bridge_events)
    failure_reason = classify_marketdata_smoke_failure(result, requested_symbol)
    return {
        "baseline": MARKETDATA_SMOKE_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": flow_path,
        "requested_symbol": requested_symbol,
        "instrument_request_id": result.instrument_request_id,
        "instrument_loaded": result.instrument_loaded,
        "source_instrument_count": result.source_instrument_count,
        "selected_symbols": list(result.selected_symbols),
        "bootstrap_started": result.bootstrap_state.started,
        "connect_request_id": result.bootstrap_state.connect_request_id,
        "subscribe_request_ids": list(result.bootstrap_state.subscribe_request_ids),
        "md": {
            "init_code": result.md_smoke.init_code,
            "login_request_code": result.md_smoke.login_request_code,
            "subscribe_code": result.md_smoke.subscribe_code,
            "login_success": result.md_smoke.login_success,
            "login_error_id": result.md_smoke.login_error_id,
            "login_error_message": result.md_smoke.login_error_message,
            "first_tick_symbol": result.md_smoke.first_tick_symbol,
            "first_tick_last": result.md_smoke.first_tick_last,
            "first_tick_bid": result.md_smoke.first_tick_bid,
            "first_tick_ask": result.md_smoke.first_tick_ask,
            "first_tick_ts_epoch_us": result.md_smoke.first_tick_ts_epoch_us,
        },
        "marketdata_batch_event_kinds": _kind_values(result.event_batch.events),
        "marketdata_batch_should_restore": result.event_batch.should_restore,
        "bridge_event_kinds": _kind_values(events),
        "bridge_tick_symbol": next((event.venue_symbol for event in events if event.venue_symbol), None),
        "export": export,
    }


def classify_live_data_client_bootstrap_failure(
    *,
    load_result: object,
    bootstrap_result: object,
    requested_symbol: str,
) -> str | None:
    if not load_result.loaded:
        return "instrument_not_loaded"
    if load_result.instrument_count <= 0:
        return "instrument_missing"
    if requested_symbol not in bootstrap_result.selected_symbols:
        return "symbol_not_selected"
    if not bootstrap_result.bootstrap_state.started:
        return "bootstrap_not_started"
    if bootstrap_result.bootstrap_state.connect_request_id is None:
        return "connect_request_missing"
    if not bootstrap_result.bootstrap_state.subscribe_request_ids:
        return "subscribe_requests_missing"
    return None


def build_live_data_client_bootstrap_payload(
    *,
    load_result: object,
    bootstrap_result: object,
    requested_symbol: str,
    flow_path: str | None,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bootstrap_commands: Iterable[object],
    instrument_events: Iterable[object],
) -> dict[str, object]:
    commands = tuple(bootstrap_commands)
    events = tuple(instrument_events)
    failure_reason = classify_live_data_client_bootstrap_failure(
        load_result=load_result,
        bootstrap_result=bootstrap_result,
        requested_symbol=requested_symbol,
    )
    return {
        "baseline": LIVE_DATA_CLIENT_BOOTSTRAP_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": flow_path,
        "requested_symbol": requested_symbol,
        "instrument_request_id": load_result.request_id,
        "instrument_loaded": load_result.loaded,
        "instrument_count": load_result.instrument_count,
        "instrument_symbols": [instrument.display_symbol for instrument in load_result.instruments[:5]],
        "selected_symbols": list(bootstrap_result.selected_symbols),
        "bootstrap_started": bootstrap_result.bootstrap_state.started,
        "connect_request_id": bootstrap_result.bootstrap_state.connect_request_id,
        "subscribe_request_ids": list(bootstrap_result.bootstrap_state.subscribe_request_ids),
        "bootstrap_command_kinds": _kind_values(commands),
        "bootstrap_subscribe_symbols": [
            command.venue_symbol
            for command in commands
            if command.venue_symbol
        ],
        "instrument_event_kinds_tail": _kind_values(events[-5:]),
        "export": export,
    }


def classify_nautilus_live_smoke_failure(
    *,
    bootstrap: object,
    md_result: object,
    td_result: object,
    configured_instruments: Iterable[object],
) -> str | None:
    if not bootstrap.started:
        return "md_bootstrap_not_started"
    if md_result.login_success is not True:
        return "md_login_failed"
    if md_result.first_tick_symbol not in configured_instruments:
        return "md_first_tick_missing"
    if td_result.login_success is not True:
        return "td_login_failed"
    if td_result.settlement_code != 0:
        return "td_settlement_not_confirmed"
    return None


def build_nautilus_live_smoke_payload(
    *,
    bootstrap: object,
    md_result: object,
    td_result: object,
    configured_instruments: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    events = tuple(bridge_events)
    failure_reason = classify_nautilus_live_smoke_failure(
        bootstrap=bootstrap,
        md_result=md_result,
        td_result=td_result,
        configured_instruments=configured_instruments,
    )
    return {
        "baseline": NAUTILUS_LIVE_SMOKE_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "bootstrap_started": bootstrap.started,
        "connect_request_id": bootstrap.connect_request_id,
        "subscribe_request_ids": list(bootstrap.subscribe_request_ids),
        "md": {
            "init_code": md_result.init_code,
            "login_request_code": md_result.login_request_code,
            "subscribe_code": md_result.subscribe_code,
            "login_success": md_result.login_success,
            "login_error_id": md_result.login_error_id,
            "first_tick_symbol": md_result.first_tick_symbol,
            "first_tick_last": md_result.first_tick_last,
            "first_tick_bid": md_result.first_tick_bid,
            "first_tick_ask": md_result.first_tick_ask,
            "first_tick_ts_epoch_us": md_result.first_tick_ts_epoch_us,
        },
        "td": {
            "init_code": td_result.init_code,
            "authenticate_code": td_result.authenticate_code,
            "login_code": td_result.login_code,
            "settlement_code": td_result.settlement_code,
            "login_success": td_result.login_success,
            "login_error_id": td_result.login_error_id,
            "front_id": td_result.front_id,
            "session_id": td_result.session_id,
            "max_order_ref": td_result.max_order_ref,
            "disconnects": td_result.disconnects,
        },
        "bridge_event_kinds": _kind_values(events),
        "bridge_tick_symbol": next((event.venue_symbol for event in events if event.venue_symbol), None),
        "bridge_td_login_seen": any(
            getattr(getattr(event, "kind", None), "value", None) == "login_succeeded"
            and getattr(event, "payload", {}).get("channel") == "td"
            for event in events
        ),
        "bridge_settlement_seen": any(
            getattr(getattr(event, "kind", None), "value", None) == "settlement_confirmed"
            for event in events
        ),
    }


def build_order_trade_query_failure_payload(
    *,
    captured_at_utc: str,
    failure_stage: str,
    failure_reason: str,
    extra: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": ORDER_TRADE_QUERY_BASELINE,
        "success": False,
        "failure_reason": failure_reason,
        "failure_stage": failure_stage,
        "captured_at_utc": captured_at_utc,
        "raw_secret_values_recorded": False,
        "raw_broker_endpoint_recorded": False,
        "order_send_called": False,
        "order_action_sent": False,
        "cancel_order_sent": False,
        "replace_order_sent": False,
    }
    if extra:
        payload.update(dict(extra))
    return payload


def build_order_trade_query_config_missing_payload(
    *,
    captured_at_utc: str,
    config_ref: str,
) -> dict[str, object]:
    return build_order_trade_query_failure_payload(
        captured_at_utc=captured_at_utc,
        failure_stage="config",
        failure_reason="config_missing",
        extra={"config_ref": config_ref},
    )


def build_order_trade_query_native_missing_payload(
    *,
    captured_at_utc: str,
    native_dll_ref: str,
) -> dict[str, object]:
    return build_order_trade_query_failure_payload(
        captured_at_utc=captured_at_utc,
        failure_stage="native",
        failure_reason="native_dll_missing",
        extra={"native_dll_ref": native_dll_ref},
    )


def build_order_trade_query_config_invalid_payload(
    *,
    captured_at_utc: str,
    config_ref: str,
    missing_fields: Iterable[object],
) -> dict[str, object]:
    return build_order_trade_query_failure_payload(
        captured_at_utc=captured_at_utc,
        failure_stage="config",
        failure_reason="config_invalid",
        extra={"config_ref": config_ref, "missing_fields": list(missing_fields)},
    )


def classify_order_trade_query_failure(
    *,
    ready: bool,
    query_order_code: int,
    query_trade_code: int,
) -> str | None:
    if ready and query_order_code == 0 and query_trade_code == 0:
        return None
    return "query_not_ready"


def build_order_trade_query_payload(
    *,
    captured_at_utc: str,
    account_id: str,
    display_alias: str,
    config_ref: str,
    native_dll_ref: str,
    native_dll_checksum: str,
    flow_path: str,
    login: object | None,
    settlement_code: int,
    ready: bool,
    init_code: int,
    authenticate_code: int,
    login_code: int,
    query_order_code: int,
    query_trade_code: int,
    order_is_last: bool,
    trade_is_last: bool,
    order_callback_observed: bool,
    trade_callback_observed: bool,
    disconnects: Iterable[object],
    orders: Iterable[Mapping[str, object]],
    trades: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    order_items = [dict(row) for row in orders]
    trade_items = [dict(row) for row in trades]
    disconnect_items = tuple(disconnects)
    failure_reason = classify_order_trade_query_failure(
        ready=ready,
        query_order_code=query_order_code,
        query_trade_code=query_trade_code,
    )
    return {
        "schema": ORDER_TRADE_QUERY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "captured_at_utc": captured_at_utc,
        "account_id": account_id,
        "display_alias": display_alias,
        "source_kind": "ctp_trader_api",
        "query_kind": "order_trade_query",
        "config_ref": config_ref,
        "native_dll_ref": native_dll_ref,
        "native_dll_checksum": native_dll_checksum,
        "flow_path": flow_path,
        "login_success": None if login is None else bool(login.success),
        "login_error_id": None if login is None else int(login.error_id),
        "settlement_code": settlement_code,
        "ready": ready,
        "init_code": init_code,
        "authenticate_code": authenticate_code,
        "login_code": login_code,
        "query_order_code": query_order_code,
        "query_trade_code": query_trade_code,
        "order_query_is_last_observed": order_is_last,
        "trade_query_is_last_observed": trade_is_last,
        "order_query_callback_observed": order_callback_observed,
        "trade_query_callback_observed": trade_callback_observed,
        "disconnect_count": len(disconnect_items),
        "disconnect_reasons": list(disconnect_items),
        "readonly_api_calls": ["ReqQryOrder", "ReqQryTrade"],
        "order_send_called": False,
        "order_action_sent": False,
        "cancel_order_sent": False,
        "replace_order_sent": False,
        "raw_secret_values_recorded": False,
        "raw_broker_endpoint_recorded": False,
        "orders": order_items,
        "trades": trade_items,
        "order_count": len(order_items),
        "trade_count": len(trade_items),
    }


def classify_repo_debug_smoke_failure(snapshot: Mapping[str, object]) -> str | None:
    scaffold_code = snapshot["scaffold_not_implemented"]
    invalid_handle = snapshot["invalid_handle"]
    if not snapshot["has_internal_md_live_session"]:
        return "internal_md_live_session_missing"
    if not (
        snapshot["has_internal_md_live_session"]
        and snapshot["md_init_code"] == scaffold_code
        and snapshot["md_login_code"] == scaffold_code
        and snapshot["md_subscribe_code"] == scaffold_code
        and snapshot["td_init_code"] == scaffold_code
        and snapshot["td_authenticate_code"] == scaffold_code
        and snapshot["td_login_code"] == scaffold_code
        and snapshot["md_init_after_dispose_code"] == invalid_handle
    ):
        return "scaffold_contract_mismatch"
    return None


def build_repo_debug_smoke_payload(snapshot: Mapping[str, object]) -> dict[str, object]:
    failure_reason = classify_repo_debug_smoke_failure(snapshot)
    return {
        "baseline": REPO_DEBUG_SMOKE_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        **dict(snapshot),
    }


def _td_session_identity_payload(identity: object | None) -> dict[str, object] | None:
    if identity is None:
        return None
    return {
        "front_id": identity.front_id,
        "session_id": identity.session_id,
        "max_order_ref": identity.max_order_ref,
    }


def _serialize_exec_event_payload(event: object) -> dict[str, object]:
    return {
        "kind": event.kind.value,
        "client_order_id": event.client_order_id,
        "venue_symbol": event.venue_symbol,
        "message": event.message,
        "native_order_id": event.payload.get("native_order_id", event.payload.get("order_id")),
        "native_order_ref": event.payload.get("native_order_ref", event.payload.get("order_ref")),
        "status": event.payload.get("status"),
        "trade_volume": event.payload.get("trade_volume"),
        "leaves_qty": event.payload.get("leaves_qty"),
        "match_reason": event.payload.get("match_reason"),
    }


def _order_lifecycle_exec_event_payloads(events: Iterable[object]) -> list[dict[str, object]]:
    return [
        _serialize_exec_event_payload(event)
        for event in events
        if getattr(getattr(event, "kind", None), "value", None) in {"order", "trade"}
    ]


def build_order_lifecycle_exception_payload(
    *,
    dry_run: bool,
    live_send_requested: bool,
    td_session_identity: object | None,
    error: str,
    commands: Iterable[object],
    events: Iterable[object],
) -> dict[str, object]:
    event_items = tuple(events)
    return {
        "baseline": ORDER_LIFECYCLE_SMOKE_BASELINE,
        "dry_run": dry_run,
        "live_send_requested": live_send_requested,
        "td_session_identity": _td_session_identity_payload(td_session_identity),
        "error": error,
        "command_kinds": _kind_values(commands),
        "event_kinds": _kind_values(event_items),
        "exec_events": _order_lifecycle_exec_event_payloads(event_items),
    }


def _matched_exec_payloads(matched_execs: Iterable[object] | None) -> list[dict[str, object]]:
    if not matched_execs:
        return []
    return [
        {
            "python_client_order_id": matched.python_client_order_id,
            "native_order_id": matched.native_order_id,
            "native_order_ref": matched.native_order_ref,
            "venue_symbol": matched.venue_symbol,
            "front_id": matched.front_id,
            "session_id": matched.session_id,
            "status": matched.status,
            "is_trade": matched.is_trade,
            "trade_volume": matched.trade_volume,
            "leaves_qty": matched.leaves_qty,
            "match_reason": matched.match_reason,
        }
        for matched in matched_execs
    ]


def classify_order_lifecycle_success(result: object, *, matched_exec_count: int) -> bool:
    success = (
        result.bootstrap.ready
        and result.mapped_submit.error is None
        and result.mapped_submit.command is not None
    )
    if result.dry_run:
        return success and result.live_send_armed is False
    return success and result.live_send_armed and matched_exec_count > 0


def build_order_lifecycle_payload(
    *,
    result: object,
    live_send_requested: bool,
    commands: Iterable[object],
    events: Iterable[object],
) -> dict[str, object]:
    event_items = tuple(events)
    matched_execs = _matched_exec_payloads(result.matched_execs)
    return {
        "baseline": ORDER_LIFECYCLE_SMOKE_BASELINE,
        "dry_run": result.dry_run,
        "live_send_requested": live_send_requested,
        "live_send_armed": result.live_send_armed,
        "bootstrap_ready": result.bootstrap.ready,
        "connect_request_id": result.bootstrap.execution_bootstrap.bootstrap_state.connect_request_id,
        "td_session_identity": _td_session_identity_payload(result.bootstrap.td_session_identity),
        "mapped_submit_error": None
        if result.mapped_submit.error is None
        else {
            "error_id": result.mapped_submit.error.error_id,
            "error_message": result.mapped_submit.error.error_message,
        },
        "mapped_submit_order_ref": result.mapped_submit.order_ref,
        "matched_exec_count": len(matched_execs),
        "matched_execs": matched_execs,
        "command_kinds": _kind_values(commands),
        "submit_payload": None if result.mapped_submit.command is None else result.mapped_submit.command.payload,
        "event_kinds": _kind_values(event_items),
        "exec_events": _order_lifecycle_exec_event_payloads(event_items),
    }


def classify_nautilus_engine_harness_success(
    *,
    accepted_count: int,
    canceled_count: int,
    rejected_count: int,
    fill_count: int,
    position_count: int,
    account_state_reported: bool,
    account_id_redacted: bool,
    script_only_smoke: bool,
) -> bool:
    return (
        accepted_count == 1
        and canceled_count == 1
        and rejected_count == 1
        and fill_count == 1
        and position_count == 1
        and account_state_reported
        and account_id_redacted
        and not script_only_smoke
    )


def build_nautilus_engine_harness_payload(
    *,
    run_id: str,
    instrument_ids: Iterable[object],
    order_statuses: Iterable[str],
    order_report_count: int,
    fill_report_count: int,
    position_report_count: int,
    account_state_reported: bool,
    account_id_redacted: bool,
) -> dict[str, object]:
    order_status_items = list(order_statuses)
    script_only_smoke = False
    accepted_count = order_status_items.count("ACCEPTED")
    canceled_count = order_status_items.count("CANCELED")
    rejected_count = order_status_items.count("REJECTED")
    success = classify_nautilus_engine_harness_success(
        accepted_count=accepted_count,
        canceled_count=canceled_count,
        rejected_count=rejected_count,
        fill_count=fill_report_count,
        position_count=position_report_count,
        account_state_reported=account_state_reported,
        account_id_redacted=account_id_redacted,
        script_only_smoke=script_only_smoke,
    )
    return {
        "baseline": NAUTILUS_ENGINE_HARNESS_BASELINE,
        "run_id": run_id,
        "proposal_id": "p004-openctp-tts-simulation-provider-completeness",
        "change_id": "20260608__openctp-tts-simulation-provider__nautilus-engine-harness",
        "account_profile": NAUTILUS_ENGINE_HARNESS_ACCOUNT_PROFILE,
        "evidence_class": NAUTILUS_ENGINE_HARNESS_EVIDENCE_CLASS,
        "success": success,
        "status": "passed" if success else "blocked",
        "provider_entrypoint": "CtpLiveExecutionClient",
        "script_only_smoke": script_only_smoke,
        "paper_send_armed": False,
        "instrument_provider": {
            "loaded": True,
            "instrument_ids": list(instrument_ids),
        },
        "engine_commands": {
            "submit_order": {"report_statuses": order_status_items},
            "cancel_order": {"report_statuses": order_status_items},
            "generate_order_status_reports": {"count": order_report_count},
            "generate_fill_reports": {"count": fill_report_count},
            "generate_position_status_reports": {"count": position_report_count},
        },
        "reports": {
            "order_statuses": order_status_items,
            "accepted_count": accepted_count,
            "canceled_count": canceled_count,
            "rejected_count": rejected_count,
            "fill_count": fill_report_count,
            "duplicate_fill_ignored": fill_report_count == 1,
            "position_count": position_report_count,
            "account_state_reported": account_state_reported,
            "account_id_redacted": account_id_redacted,
        },
        "issues": [],
    }


def build_live_ops_snapshot_payload(
    *,
    snapshot: object,
    summary: object,
    policy_result: object,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_live_ops_summary_failure(summary, getattr(policy_result, "disposition"))
    return {
        "baseline": LIVE_OPS_SNAPSHOT_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": getattr(summary, "account_id"),
        "symbol": getattr(summary, "symbol"),
        "startup": {
            "account_id": getattr(snapshot.startup_truth, "account_id"),
            "disposition": getattr(snapshot.startup_truth, "disposition"),
            "shared_flow_reuse_allowed": getattr(snapshot.startup_truth, "shared_flow_reuse_allowed"),
            "session_rotated": getattr(snapshot.startup_truth, "session_rotated"),
            "manual_review_codes": list(getattr(snapshot.startup_truth, "manual_review_codes")),
            "rebuild_required_codes": list(getattr(snapshot.startup_truth, "rebuild_required_codes")),
            "evidence_only_codes": list(getattr(snapshot.startup_truth, "evidence_only_codes")),
        },
        "md": {
            "account_id": getattr(snapshot.md_truth, "account_id"),
            "symbol": getattr(snapshot.md_truth, "symbol"),
            "disposition": getattr(snapshot.md_truth, "disposition"),
            "startup_ready": getattr(snapshot.md_truth, "startup_ready"),
            "restore_triggered": getattr(snapshot.md_truth, "restore_triggered"),
            "restore_succeeded": getattr(snapshot.md_truth, "restore_succeeded"),
            "manual_review_codes": list(getattr(snapshot.md_truth, "manual_review_codes")),
            "restore_required_codes": list(getattr(snapshot.md_truth, "restore_required_codes")),
            "evidence_only_codes": list(getattr(snapshot.md_truth, "evidence_only_codes")),
        },
        "td": {
            "account_id": getattr(snapshot.td_truth, "account_id"),
            "disposition": getattr(snapshot.td_truth, "disposition"),
            "position_count": getattr(snapshot.td_truth, "position_count"),
            "observed_callback_count": getattr(snapshot.td_truth, "observed_callback_count"),
            "historical_callback_count": getattr(snapshot.td_truth, "historical_callback_count"),
            "current_session_callback_count": getattr(snapshot.td_truth, "current_session_callback_count"),
            "available_ratio": getattr(snapshot.td_truth, "available_ratio"),
            "margin_ratio": getattr(snapshot.td_truth, "margin_ratio"),
            "manual_review_codes": list(getattr(snapshot.td_truth, "manual_review_codes")),
            "boundary_codes": list(getattr(snapshot.td_truth, "boundary_codes")),
            "evidence_only_codes": list(getattr(snapshot.td_truth, "evidence_only_codes")),
        },
        "reconciliation": {
            "account_id": getattr(snapshot.reconciliation, "account_id"),
            "disposition": getattr(snapshot.reconciliation, "disposition"),
            "requires_manual_review": getattr(snapshot.reconciliation, "requires_manual_review"),
            "finding_count": getattr(snapshot.reconciliation, "finding_count"),
            "position_line_count": getattr(snapshot.reconciliation, "position_line_count"),
            "symbol_count": getattr(snapshot.reconciliation, "symbol_count"),
            "gross_position_qty": getattr(snapshot.reconciliation, "gross_position_qty"),
            "available_ratio": getattr(snapshot.reconciliation, "available_ratio"),
            "margin_ratio": getattr(snapshot.reconciliation, "margin_ratio"),
            "manual_review_codes": list(getattr(snapshot.reconciliation, "manual_review_codes")),
            "evidence_only_codes": list(getattr(snapshot.reconciliation, "evidence_only_codes")),
        },
        **_live_ops_summary_payload(summary, getattr(policy_result, "disposition"), getattr(policy_result, "findings")),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def _live_ops_summary_payload(
    summary: object,
    disposition: str,
    findings: Iterable[object],
) -> dict[str, object]:
    finding_items = tuple(findings)
    return {
        "startup_disposition": getattr(summary, "startup_disposition"),
        "md_disposition": getattr(summary, "md_disposition"),
        "td_disposition": getattr(summary, "td_disposition"),
        "reconciliation_disposition": getattr(summary, "reconciliation_disposition"),
        "disposition": disposition,
        "requires_manual_review": disposition == "manual_review_required",
        "finding_count": len(finding_items),
        "startup_shared_flow_reuse_allowed": getattr(summary, "startup_shared_flow_reuse_allowed"),
        "startup_session_rotated": getattr(summary, "startup_session_rotated"),
        "md_restore_succeeded": getattr(summary, "md_restore_succeeded"),
        "position_count": getattr(summary, "position_count"),
        "observed_callback_count": getattr(summary, "observed_callback_count"),
        "historical_callback_count": getattr(summary, "historical_callback_count"),
        "current_session_callback_count": getattr(summary, "current_session_callback_count"),
        "available_ratio": getattr(summary, "available_ratio"),
        "margin_ratio": getattr(summary, "margin_ratio"),
        "manual_review_codes": list(getattr(summary, "manual_review_codes")),
        "rebuild_required_codes": list(getattr(summary, "rebuild_required_codes")),
        "restore_required_codes": list(getattr(summary, "restore_required_codes")),
        "boundary_codes": list(getattr(summary, "boundary_codes")),
        "evidence_only_codes": list(getattr(summary, "evidence_only_codes")),
        "findings": _finding_payloads(finding_items),
    }


def build_live_ops_policy_payload(
    result: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_live_ops_summary_failure(result.summary, result.disposition)
    return {
        "baseline": LIVE_OPS_POLICY_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": result.summary.account_id,
        "symbol": result.summary.symbol,
        **_live_ops_summary_payload(result.summary, result.disposition, result.findings),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


def build_live_ops_evidence_matrix_payload(
    evidence: object,
    *,
    flow_mode: str,
    session_label: str,
    export: dict[str, object],
    bridge_commands: Iterable[object],
    bridge_events: Iterable[object],
) -> dict[str, object]:
    failure_reason = classify_live_ops_evidence_matrix_failure(evidence)
    return {
        "baseline": LIVE_OPS_EVIDENCE_MATRIX_BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "evidence_version": getattr(evidence, "evidence_version"),
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": getattr(evidence, "account_id"),
        "symbol": getattr(evidence, "symbol"),
        "disposition": getattr(evidence, "disposition"),
        "requires_manual_review": getattr(evidence, "disposition") == "manual_review_required",
        "startup_disposition": getattr(evidence, "startup_disposition"),
        "md_disposition": getattr(evidence, "md_disposition"),
        "td_disposition": getattr(evidence, "td_disposition"),
        "reconciliation_disposition": getattr(evidence, "reconciliation_disposition"),
        "startup_shared_flow_reuse_allowed": getattr(evidence, "startup_shared_flow_reuse_allowed"),
        "startup_session_rotated": getattr(evidence, "startup_session_rotated"),
        "md_restore_succeeded": getattr(evidence, "md_restore_succeeded"),
        "position_count": getattr(evidence, "position_count"),
        "observed_callback_count": getattr(evidence, "observed_callback_count"),
        "historical_callback_count": getattr(evidence, "historical_callback_count"),
        "current_session_callback_count": getattr(evidence, "current_session_callback_count"),
        "available_ratio": getattr(evidence, "available_ratio"),
        "margin_ratio": getattr(evidence, "margin_ratio"),
        "manual_review_codes": list(getattr(evidence, "manual_review_codes")),
        "rebuild_required_codes": list(getattr(evidence, "rebuild_required_codes")),
        "restore_required_codes": list(getattr(evidence, "restore_required_codes")),
        "boundary_codes": list(getattr(evidence, "boundary_codes")),
        "evidence_only_codes": list(getattr(evidence, "evidence_only_codes")),
        "export": export,
        "bridge_command_kinds": _kind_values(bridge_commands),
        "bridge_event_kinds": _kind_values(bridge_events),
    }


__all__ = [
    "ACCOUNT_QUERY_BASELINE",
    "INSTRUMENT_QUERY_BASELINE",
    "LIVE_DATA_CLIENT_BOOTSTRAP_BASELINE",
    "LIVE_OPS_EVIDENCE_MATRIX_BASELINE",
    "LIVE_OPS_POLICY_BASELINE",
    "LIVE_OPS_SNAPSHOT_BASELINE",
    "MARKETDATA_SMOKE_BASELINE",
    "MD_LOGIN_SMOKE_BASELINE",
    "MD_STARTUP_TRUTH_BASELINE",
    "MD_TRUTH_EVIDENCE_MATRIX_BASELINE",
    "MD_RESTORE_POLICY_BASELINE",
    "NAUTILUS_LIVE_SMOKE_BASELINE",
    "NAUTILUS_ENGINE_HARNESS_ACCOUNT_PROFILE",
    "NAUTILUS_ENGINE_HARNESS_BASELINE",
    "NAUTILUS_ENGINE_HARNESS_EVIDENCE_CLASS",
    "ORDER_TRADE_QUERY_BASELINE",
    "ORDER_LIFECYCLE_SMOKE_BASELINE",
    "POSITION_QUERY_BASELINE",
    "QUERY_ADAPTER_BASELINE",
    "RECONCILIATION_EVIDENCE_BASELINE",
    "RECONCILIATION_POLICY_BASELINE",
    "RECONCILIATION_SNAPSHOT_BASELINE",
    "REPO_DEBUG_SMOKE_BASELINE",
    "TD_HISTORICAL_CALLBACK_BOUNDARY_BASELINE",
    "TD_LOGIN_SMOKE_BASELINE",
    "TD_ORDER_TRUTH_BASELINE",
    "STARTUP_TRUTH_EVIDENCE_MATRIX_BASELINE",
    "TD_MERGED_RECONCILIATION_POLICY_BASELINE",
    "TD_MERGED_EVIDENCE_MATRIX_BASELINE",
    "TD_ORDER_TRUTH_EVIDENCE_MATRIX_BASELINE",
    "TD_SESSION_REBUILD_POLICY_BASELINE",
    "TD_STARTUP_TRUTH_BASELINE",
    "TD_TRUTH_MERGE_SNAPSHOT_BASELINE",
    "build_account_query_payload",
    "build_instrument_query_payload",
    "build_live_data_client_bootstrap_payload",
    "build_live_ops_evidence_matrix_payload",
    "build_live_ops_policy_payload",
    "build_live_ops_snapshot_payload",
    "build_marketdata_smoke_payload",
    "build_md_login_smoke_payload",
    "build_md_startup_truth_payload",
    "build_md_truth_evidence_matrix_payload",
    "build_md_restore_policy_payload",
    "build_nautilus_live_smoke_payload",
    "build_nautilus_engine_harness_payload",
    "build_order_trade_query_failure_payload",
    "build_order_trade_query_config_invalid_payload",
    "build_order_trade_query_config_missing_payload",
    "build_order_trade_query_native_missing_payload",
    "build_order_trade_query_payload",
    "build_order_lifecycle_exception_payload",
    "build_order_lifecycle_payload",
    "build_position_query_payload",
    "build_query_adapter_payload",
    "build_reconciliation_evidence_payload",
    "build_reconciliation_policy_payload",
    "build_reconciliation_snapshot_payload",
    "build_repo_debug_smoke_payload",
    "build_session_rebuild_policy_payload",
    "build_td_historical_callback_boundary_payload",
    "build_td_login_smoke_payload",
    "build_td_order_truth_payload",
    "build_startup_truth_evidence_matrix_payload",
    "build_td_merged_reconciliation_policy_payload",
    "build_td_merged_evidence_matrix_payload",
    "build_td_order_truth_evidence_matrix_payload",
    "build_td_startup_truth_payload",
    "build_td_truth_merge_snapshot_payload",
    "classify_account_query_failure",
    "classify_instrument_query_failure",
    "classify_live_data_client_bootstrap_failure",
    "classify_live_ops_evidence_matrix_failure",
    "classify_live_ops_summary_failure",
    "classify_marketdata_smoke_failure",
    "classify_md_login_smoke_failure",
    "classify_md_startup_truth_failure",
    "classify_md_truth_evidence_matrix_failure",
    "classify_md_restore_policy_failure",
    "classify_nautilus_live_smoke_failure",
    "classify_nautilus_engine_harness_success",
    "classify_order_trade_query_failure",
    "classify_order_lifecycle_success",
    "classify_position_query_failure",
    "classify_query_adapter_failure",
    "classify_reconciliation_evidence_failure",
    "classify_reconciliation_policy_failure",
    "classify_reconciliation_snapshot_failure",
    "classify_repo_debug_smoke_failure",
    "classify_session_rebuild_policy_failure",
    "classify_td_historical_callback_boundary_failure",
    "classify_td_login_smoke_failure",
    "classify_td_order_truth_failure",
    "classify_startup_truth_evidence_matrix_failure",
    "classify_td_merged_reconciliation_policy_failure",
    "classify_td_merged_evidence_matrix_failure",
    "classify_td_order_truth_evidence_matrix_failure",
    "classify_td_startup_truth_failure",
    "classify_td_truth_merge_snapshot_failure",
    "instrument_matches_requested_symbol",
]
