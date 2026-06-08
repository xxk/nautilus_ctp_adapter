from __future__ import annotations

import json
from pathlib import Path

from scripts.ctp_paper_recovery_idempotency import (
    build_reconnect_disposition,
    build_resource_blocker_payload,
    classify_checkpoint_resume,
    classify_historical_residue,
    write_recovery_attempt,
)
from scripts.ctp_controlled_reconnect_harness import build_controlled_reconnect_evidence


def test_checkpoint_resume_reuses_run_id_and_increments_attempt(tmp_path: Path) -> None:
    checkpoint = {
        "run_id": "paper-recovery-1",
        "session_label": "paper-dev",
        "account_profile": "openctp-tts-7x24-simulation",
        "schema_version": "ctp-paper-recovery-idempotency-v1",
        "attempt": 1,
        "completed_steps": ["preflight", "snapshot"],
        "pending_steps": ["reconnect"],
    }

    verdict = classify_checkpoint_resume(
        checkpoint, current_account_profile="openctp-tts-7x24-simulation"
    )

    assert verdict["accepted"] is True
    assert verdict["run_id"] == "paper-recovery-1"
    assert verdict["next_attempt"] == 2
    assert verdict["resume_from"]["last_completed_step"] == "snapshot"
    assert verdict["resume_from"]["pending_steps"] == ["reconnect"]


def test_checkpoint_resume_rejects_profile_or_schema_mismatch() -> None:
    checkpoint = {
        "run_id": "paper-recovery-1",
        "session_label": "paper-dev",
        "account_profile": "formal-trading",
        "schema_version": "old",
        "attempt": 1,
        "completed_steps": [],
        "pending_steps": [],
    }

    verdict = classify_checkpoint_resume(
        checkpoint, current_account_profile="openctp-tts-7x24-simulation"
    )

    assert verdict["accepted"] is False
    assert verdict["disposition"] == "checkpoint_contract_failed"
    assert verdict["issues"] == ["account_profile_mismatch", "schema_version_mismatch"]


def test_reconnect_disposition_preserves_md_symbols_and_td_disarmed_state() -> None:
    verdict = build_reconnect_disposition(
        run_id="paper-recovery-1",
        attempt=2,
        md_symbols=["rb2610", "rb2610", "c2609"],
        md_disconnect_reason=4097,
        td_disconnect_reason=4098,
        td_login_success=True,
        settlement_code=0,
        paper_send_armed=False,
        max_attempts=3,
    )

    assert verdict["accepted"] is True
    assert verdict["recovery"]["disconnects"][0]["channel"] == "md"
    assert verdict["recovery"]["reconnects"][0]["resubscribed_symbols"] == ["rb2610", "c2609"]
    assert verdict["recovery"]["reconnects"][0]["resubscribe_counts"] == {"rb2610": 1, "c2609": 1}
    assert verdict["recovery"]["reconnects"][1]["guardrails_preserved"] is True
    assert verdict["recovery"]["timeline"][0]["event"] == "md_disconnect_detected"
    assert verdict["recovery"]["query_recovery"]["disposition"] == "query_ready"
    assert verdict["recovery"]["in_flight_order"]["disposition"] == "none"
    assert verdict["recovery"]["disposition"] == "passed"


def test_reconnect_disposition_fails_when_td_rearms_order_send_or_retry_budget_exhausts() -> None:
    verdict = build_reconnect_disposition(
        run_id="paper-recovery-1",
        attempt=4,
        md_symbols=["rb2610"],
        md_disconnect_reason=4097,
        td_disconnect_reason=4098,
        td_login_success=True,
        settlement_code=0,
        paper_send_armed=True,
        max_attempts=3,
    )

    assert verdict["accepted"] is False
    assert verdict["recovery"]["disposition"] == "typed_blocker"
    assert verdict["issues"] == ["retry_budget_exhausted", "paper_send_rearmed_after_reconnect"]


def test_reconnect_disposition_types_inflight_order_as_conservative_blocker() -> None:
    verdict = build_reconnect_disposition(
        run_id="paper-recovery-1",
        attempt=1,
        md_symbols=["c2609"],
        md_disconnect_reason=4097,
        td_disconnect_reason=4098,
        td_login_success=True,
        settlement_code=0,
        paper_send_armed=False,
        max_attempts=3,
        in_flight_client_order_id="order-1",
    )

    assert verdict["accepted"] is False
    assert verdict["recovery"]["in_flight_order"]["disposition"] == "conservative_blocker"
    assert verdict["issues"] == ["in_flight_order_requires_manual_reconciliation"]


def test_resource_blocker_payload_does_not_fake_real_reconnect_pass() -> None:
    payload = build_resource_blocker_payload(
        run_id="paper-recovery-1",
        attempt=1,
        code="forced_front_disconnect_unavailable",
        detail="operator cannot force OpenCTP public simulation front disconnect",
        md_symbols=["c2609", "zn2610", "c2609"],
    )

    assert payload["success"] is False
    assert payload["status"] == "blocked"
    assert payload["blocker_type"] == "paper-resource"
    assert payload["recovery"]["disposition"] == "typed_blocker"
    assert payload["recovery"]["reconnects"][0]["resubscribed_symbols"] == ["c2609", "zn2610"]
    assert payload["issues"] == ["forced_front_disconnect_unavailable"]


def test_controlled_reconnect_evidence_closes_forced_disconnect_blocker() -> None:
    payload = build_controlled_reconnect_evidence(
        run_id="controlled-reconnect-test",
        md_symbols=["c2609", "zn2610", "c2609"],
        td_ready=True,
        settlement_code=0,
        paper_send_armed=False,
        md_drop_count=1,
        td_drop_count=1,
    )

    assert payload["success"] is True
    assert payload["blocker_resolved"] == "forced_front_disconnect_unavailable"
    assert payload["recovery"]["reconnects"][0]["resubscribe_counts"] == {
        "c2609": 1,
        "zn2610": 1,
    }
    assert payload["recovery"]["reconnects"][1]["guardrails_preserved"] is True
    assert payload["paper_send_armed"] is False


def test_historical_residue_does_not_emit_current_reports() -> None:
    verdict = classify_historical_residue(
        [
            {"identity": "hist-1", "session": "old", "is_trade": True},
            {"identity": "hist-1", "session": "old", "is_trade": True},
            {"identity": "cur-1", "session": "current", "is_trade": True},
        ],
        current_session="current",
    )

    assert verdict["accepted"] is True
    assert verdict["historical_count"] == 2
    assert verdict["duplicate_input_count"] == 1
    assert verdict["emitted_current_report_count"] == 1


def test_write_recovery_attempt_appends_manifest_without_overwrite(tmp_path: Path) -> None:
    payload = {"recovery": {"run_id": "paper-recovery-1", "attempt": 1}}

    first = write_recovery_attempt(tmp_path, payload)
    second = write_recovery_attempt(tmp_path, {"recovery": {"run_id": "paper-recovery-1", "attempt": 2}})
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))

    assert first.name == "attempt-001.json"
    assert second.name == "attempt-002.json"
    assert [item["attempt"] for item in manifest["attempts"]] == [1, 2]
