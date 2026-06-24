from __future__ import annotations

from typing import Any


def build_callback_source_observability(
    *,
    lifecycle_events: list[dict[str, Any]],
    lifecycle_verdict: dict[str, Any],
    paper_send_armed: bool = False,
) -> dict[str, Any]:
    callback_sources = sorted(
        {
            str(event.get("callback_source", "")).strip()
            for event in lifecycle_events
            if str(event.get("callback_source", "")).strip()
        }
    )
    zero_fill_rejection = (
        lifecycle_verdict.get("disposition") in {"cancelled", "rejected"}
        and int(lifecycle_verdict.get("fill_volume", 0) or 0) == 0
    )
    lifecycle_timeout = lifecycle_verdict.get("disposition") == "timeout"
    source_observed = bool(callback_sources)
    source_required = zero_fill_rejection or (paper_send_armed and lifecycle_timeout)
    accepted = not source_required or source_observed
    return {
        "accepted": accepted,
        "disposition": (
            "callback_source_observed"
            if source_observed
            else "missing_callback_source_for_armed_lifecycle_timeout"
            if paper_send_armed and lifecycle_timeout
            else "callback_source_not_required_for_non_rejection"
            if not source_required
            else "missing_callback_source_for_zero_fill_rejection"
        ),
        "callback_sources": callback_sources,
        "zero_fill_rejection": zero_fill_rejection,
        "armed_lifecycle_timeout": paper_send_armed and lifecycle_timeout,
        "acceptance_implication": "diagnostic_only_not_fill_or_closeout_truth",
        "fill_producing_acceptance_satisfied": False,
        "requires_owner_resolution_before_retry": source_required and not source_observed,
        "writes_truth": False,
    }


def finalize_order_lifecycle_payload(
    *,
    payload: dict[str, Any],
    bootstrap_ready: bool,
    mapped_error: Any | None,
    mapped_command: Any | None,
    order_contract: dict[str, Any],
    lifecycle_verdict: dict[str, Any],
    reconciliation: dict[str, Any] | None,
    arm_paper_send: bool,
    dry_run: bool,
    live_send_armed: bool,
) -> dict[str, Any]:
    success = (
        bootstrap_ready
        and mapped_error is None
        and mapped_command is not None
        and order_contract["accepted"]
        and lifecycle_verdict["accepted"]
    )
    if reconciliation is not None:
        success = success and reconciliation["accepted"]
    if not arm_paper_send:
        success = success and dry_run and live_send_armed is False
    else:
        success = success and live_send_armed
    payload["success"] = success
    payload["status"] = "passed" if success else "blocked"
    payload["failure_reason"] = None if success else "order_lifecycle_not_ready"
    payload["blocker_type"] = None if success else "paper-resource"
    return payload


__all__ = [
    "build_callback_source_observability",
    "finalize_order_lifecycle_payload",
]
