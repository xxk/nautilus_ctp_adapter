from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from nautilus_ctp_adapter.diagnostics.guarded_paper_order import (
    finalize_order_lifecycle_payload,
)
from nautilus_ctp_adapter.diagnostics.send_mode import (
    SendMode,
    SendModeConfigurationError,
    resolve_send_mode,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_send_mode_exhaustive_resolution_and_legacy_wrapper() -> None:
    dry_run = resolve_send_mode(SendMode.DRY_RUN)
    assert dry_run.send_mode is SendMode.DRY_RUN
    assert dry_run.action_mode == "dry_run"
    assert dry_run.dry_run is True
    assert dry_run.paper_send_armed is False
    assert dry_run.live_send_armed is False

    armed_paper = resolve_send_mode(SendMode.ARMED_PAPER)
    assert armed_paper.send_mode is SendMode.ARMED_PAPER
    assert armed_paper.action_mode == "paper_send"
    assert armed_paper.dry_run is False
    assert armed_paper.paper_send_armed is True
    assert armed_paper.live_send_armed is True

    armed_live = resolve_send_mode(SendMode.ARMED_LIVE)
    assert armed_live.send_mode is SendMode.ARMED_LIVE
    assert armed_live.action_mode == "live_send"
    assert armed_live.dry_run is False
    assert armed_live.paper_send_armed is False
    assert armed_live.live_send_armed is True

    assert resolve_send_mode(arm_paper_send=False).send_mode is SendMode.DRY_RUN
    assert resolve_send_mode(arm_paper_send=True).send_mode is SendMode.ARMED_PAPER


def test_send_mode_rejects_illegal_legacy_bool_combinations() -> None:
    illegal_cases = [
        {"dry_run": True, "arm_paper_send": True},
        {"dry_run": True, "live_send_armed": True},
        {"arm_paper_send": False, "live_send_armed": True},
        {"dry_run": False, "arm_paper_send": False},
    ]
    for kwargs in illegal_cases:
        with pytest.raises(SendModeConfigurationError):
            resolve_send_mode(**kwargs)


def test_finalize_order_lifecycle_payload_uses_send_mode_as_authority() -> None:
    payload = {
        "success": False,
        "status": "blocked",
        "failure_reason": None,
        "blocker_type": None,
    }

    result = finalize_order_lifecycle_payload(
        payload=payload,
        bootstrap_ready=True,
        mapped_error=None,
        mapped_command=SimpleNamespace(kind="submit"),
        order_contract={"accepted": True},
        lifecycle_verdict={"accepted": True},
        reconciliation=None,
        send_mode=SendMode.DRY_RUN,
        dry_run=True,
        live_send_armed=False,
    )

    assert result["success"] is True
    assert result["status"] == "passed"

    with pytest.raises(SendModeConfigurationError):
        finalize_order_lifecycle_payload(
            payload=dict(payload),
            bootstrap_ready=True,
            mapped_error=None,
            mapped_command=SimpleNamespace(kind="submit"),
            order_contract={"accepted": True},
            lifecycle_verdict={"accepted": True},
            reconciliation=None,
            send_mode=SendMode.DRY_RUN,
            dry_run=False,
            live_send_armed=True,
        )


def test_guarded_order_entries_do_not_bypass_send_mode() -> None:
    finalizer_source = (
        REPO_ROOT / "src" / "nautilus_ctp_adapter" / "diagnostics" / "guarded_paper_order.py"
    ).read_text(encoding="utf-8")
    runner_source = (
        REPO_ROOT / "scripts" / "ctp_guarded_paper_order_loop.py"
    ).read_text(encoding="utf-8")

    assert "resolve_send_mode" in finalizer_source
    assert "if not arm_paper_send" not in finalizer_source
    assert "send_mode_resolution" in runner_source
    assert '"paper_send" if arm_paper_send else "dry_run"' not in runner_source
