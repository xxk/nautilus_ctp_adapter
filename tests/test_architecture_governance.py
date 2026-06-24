from __future__ import annotations

from pathlib import Path

from scripts.check_architecture_governance import validate_architecture_governance


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_architecture_governance_gate_accepts_owner_truth_and_retirement_boundary() -> None:
    assert validate_architecture_governance(PROJECT_ROOT) == []


def test_architecture_governance_doc_declares_no_second_truth_red_lines() -> None:
    text = (
        PROJECT_ROOT
        / "docs"
        / "architecture"
        / "adapter-governance-owner-truth-retirement.md"
    ).read_text(encoding="utf-8")

    for token in (
        "second runtime core",
        "second native loader",
        "second adapter stack builder",
        "second live-ready verdict",
        "chat-only architecture decisions",
    ):
        assert token in text


def test_adapter_legacy_model_exports_delegate_to_diagnostics_owner() -> None:
    from nautilus_ctp_adapter.adapters.ctp import data_client, execution_client
    from nautilus_ctp_adapter.adapters.ctp import ops_snapshot, reconciliation, startup_truth, truth_merge
    from nautilus_ctp_adapter.diagnostics import (
        live_ops_models,
        md_models,
        reconciliation_models,
        startup_models,
        td_models,
        truth_merge_models,
    )

    for name in (
        "CtpMdSmokeResult",
        "CtpMdStartupTruthEvidence",
        "CtpMdRestorePolicyResult",
        "CtpMdTruthEvidenceMatrix",
    ):
        assert getattr(data_client, name) is getattr(md_models, name)

    for name in (
        "CtpTdSmokeResult",
        "CtpMappedOrderCommand",
        "CtpTdOrderTruthBaseline",
        "CtpTdOrderTruthEvidenceMatrix",
    ):
        assert getattr(execution_client, name) is getattr(td_models, name)

    for name in (
        "CtpTdStartupTruthEvidence",
        "CtpSessionRebuildFinding",
        "CtpSessionRebuildPolicyResult",
        "CtpStartupTruthEvidenceMatrix",
    ):
        assert getattr(startup_truth, name) is getattr(startup_models, name)

    for name in (
        "CtpTdTruthMergeSnapshot",
        "CtpTdMergedReconciliationFinding",
        "CtpTdMergedReconciliationPolicyResult",
        "CtpTdMergedEvidenceMatrix",
    ):
        assert getattr(truth_merge, name) is getattr(truth_merge_models, name)

    for name in (
        "CtpReconciliationSymbolExposure",
        "CtpReconciliationSnapshot",
        "CtpReconciliationSummary",
        "CtpReconciliationPolicyFinding",
        "CtpReconciliationPolicyResult",
        "CtpReconciliationEvidence",
    ):
        assert getattr(reconciliation, name) is getattr(reconciliation_models, name)

    for name in (
        "CtpLiveOpsSnapshot",
        "CtpLiveOpsSnapshotSummary",
        "CtpLiveOpsPolicyFinding",
        "CtpLiveOpsPolicyResult",
        "CtpLiveOpsEvidenceMatrix",
    ):
        assert getattr(ops_snapshot, name) is getattr(live_ops_models, name)


def test_adapter_files_do_not_redeclare_diagnostics_dataclasses() -> None:
    adapter_root = PROJECT_ROOT / "src" / "nautilus_ctp_adapter" / "adapters" / "ctp"

    for relative in (
        "data_client.py",
        "execution_client.py",
        "startup_truth.py",
        "truth_merge.py",
        "reconciliation.py",
        "ops_snapshot.py",
    ):
        text = (adapter_root / relative).read_text(encoding="utf-8")
        assert "from dataclasses import dataclass" not in text
        assert "@dataclass" not in text


def test_data_client_md_policy_methods_delegate_to_diagnostics_owner(monkeypatch) -> None:
    from nautilus_ctp_adapter.adapters.ctp.data_client import CtpDataClient
    from nautilus_ctp_adapter.diagnostics import md_policy

    calls: list[tuple[str, object]] = []

    class Sentinel:
        pass

    def fake_evaluate(*args):
        calls.append(("evaluate", args))
        return Sentinel()

    def fake_matrix(*args, **kwargs):
        calls.append(("matrix", (args, kwargs)))
        return Sentinel()

    def fake_startup(**kwargs):
        calls.append(("startup", kwargs))
        return Sentinel()

    monkeypatch.setattr(md_policy, "evaluate_md_restore_policy", fake_evaluate)
    monkeypatch.setattr(md_policy, "build_md_truth_evidence_matrix", fake_matrix)
    monkeypatch.setattr(md_policy, "build_md_startup_truth_evidence", fake_startup)

    client = CtpDataClient()

    assert isinstance(client.evaluate_md_restore_policy("startup", "restore", "restored"), Sentinel)
    assert calls[-1] == ("evaluate", ("startup", "restore", "restored"))

    assert isinstance(client.build_md_truth_evidence_matrix("result"), Sentinel)
    assert calls[-1] == ("matrix", (("result",), {"account_id": None}))

    assert isinstance(
        client._build_md_startup_truth_evidence(
            md_smoke="smoke",
            flow_path=None,
            selected_symbols=("rb2610",),
            event_batch="batch",
        ),
        Sentinel,
    )
    assert calls[-1][0] == "startup"
    assert calls[-1][1]["md_smoke"] == "smoke"
    assert calls[-1][1]["selected_symbols"] == ("rb2610",)


def test_execution_client_td_policy_methods_delegate_to_diagnostics_owner(monkeypatch) -> None:
    from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpExecutionClient
    from nautilus_ctp_adapter.diagnostics import td_policy

    calls: list[tuple[str, object]] = []

    class Sentinel:
        pass

    def fake_boundary(*args):
        calls.append(("boundary", args))
        return Sentinel()

    def fake_snapshot(*args):
        calls.append(("snapshot", args))
        return Sentinel()

    def fake_matrix(*args, **kwargs):
        calls.append(("matrix", (args, kwargs)))
        return Sentinel()

    monkeypatch.setattr(td_policy, "evaluate_historical_callback_boundary_policy", fake_boundary)
    monkeypatch.setattr(td_policy, "evaluate_order_trade_snapshot", fake_snapshot)
    monkeypatch.setattr(td_policy, "build_td_order_truth_evidence_matrix", fake_matrix)

    client = CtpExecutionClient()

    assert isinstance(client.evaluate_historical_callback_boundary_policy("baseline"), Sentinel)
    assert calls[-1] == ("boundary", ("baseline",))

    assert isinstance(client.evaluate_order_trade_snapshot("baseline"), Sentinel)
    assert calls[-1] == ("snapshot", ("baseline",))

    assert isinstance(client.build_td_order_truth_evidence_matrix("result"), Sentinel)
    assert calls[-1] == ("matrix", (("result",), {"account_id": None}))


def test_reconciliation_policy_methods_delegate_to_diagnostics_owner(monkeypatch) -> None:
    from nautilus_ctp_adapter.adapters.ctp.reconciliation import CtpReconciliationAdapter
    from nautilus_ctp_adapter.diagnostics import reconciliation_policy

    calls: list[tuple[str, object]] = []

    class Sentinel:
        pass

    def fake_summary(*args):
        calls.append(("summary", args))
        return Sentinel()

    def fake_evaluate(*args):
        calls.append(("evaluate", args))
        return Sentinel()

    def fake_evidence(*args):
        calls.append(("evidence", args))
        return Sentinel()

    monkeypatch.setattr(reconciliation_policy, "summarize_reconciliation_snapshot", fake_summary)
    monkeypatch.setattr(reconciliation_policy, "evaluate_reconciliation_summary", fake_evaluate)
    monkeypatch.setattr(reconciliation_policy, "build_reconciliation_evidence", fake_evidence)

    adapter = CtpReconciliationAdapter()

    assert isinstance(adapter.summarize_snapshot("snapshot"), Sentinel)
    assert calls[-1] == ("summary", ("snapshot",))

    assert isinstance(adapter.evaluate_summary("summary"), Sentinel)
    assert calls[-1] == ("evaluate", ("summary",))

    assert isinstance(adapter.build_evidence("result"), Sentinel)
    assert calls[-1] == ("evidence", ("result",))


def test_live_ops_policy_methods_delegate_to_diagnostics_owner(monkeypatch) -> None:
    from nautilus_ctp_adapter.adapters.ctp.ops_snapshot import CtpLiveOpsSnapshotAdapter
    from nautilus_ctp_adapter.diagnostics import live_ops_policy

    calls: list[tuple[str, object]] = []

    class Sentinel:
        pass

    def fake_summary(*args):
        calls.append(("summary", args))
        return Sentinel()

    def fake_evaluate(*args):
        calls.append(("evaluate", args))
        return Sentinel()

    def fake_evidence(*args):
        calls.append(("evidence", args))
        return Sentinel()

    monkeypatch.setattr(live_ops_policy, "summarize_live_ops_snapshot", fake_summary)
    monkeypatch.setattr(live_ops_policy, "evaluate_live_ops_summary", fake_evaluate)
    monkeypatch.setattr(live_ops_policy, "build_live_ops_evidence_matrix", fake_evidence)

    adapter = CtpLiveOpsSnapshotAdapter()

    assert isinstance(adapter.summarize_live_ops_snapshot("snapshot"), Sentinel)
    assert calls[-1] == ("summary", ("snapshot",))

    assert isinstance(adapter.evaluate_live_ops_policy("summary"), Sentinel)
    assert calls[-1] == ("evaluate", ("summary",))

    assert isinstance(adapter.build_live_ops_evidence_matrix("result"), Sentinel)
    assert calls[-1] == ("evidence", ("result",))


def test_startup_policy_methods_delegate_to_diagnostics_owner(monkeypatch) -> None:
    from nautilus_ctp_adapter.adapters.ctp.startup_truth import CtpStartupTruthAdapter
    from nautilus_ctp_adapter.diagnostics import startup_policy

    calls: list[tuple[str, object]] = []

    class Sentinel:
        pass

    def fake_evaluate(*args):
        calls.append(("evaluate", args))
        return Sentinel()

    def fake_evidence(*args, **kwargs):
        calls.append(("evidence", (args, kwargs)))
        return Sentinel()

    monkeypatch.setattr(startup_policy, "evaluate_session_rebuild_policy", fake_evaluate)
    monkeypatch.setattr(startup_policy, "build_startup_truth_evidence_matrix", fake_evidence)

    adapter = CtpStartupTruthAdapter()

    assert isinstance(adapter.evaluate_session_rebuild_policy("shared", "isolated"), Sentinel)
    assert calls[-1] == ("evaluate", ("shared", "isolated"))

    assert isinstance(adapter.build_evidence_matrix("result"), Sentinel)
    assert calls[-1] == ("evidence", (("result",), {"account_id": None}))


def test_truth_merge_policy_methods_delegate_to_diagnostics_owner(monkeypatch) -> None:
    from nautilus_ctp_adapter.adapters.ctp.truth_merge import CtpTruthMergeAdapter
    from nautilus_ctp_adapter.diagnostics import truth_merge_policy

    calls: list[tuple[str, object]] = []

    class Sentinel:
        pass

    def fake_evaluate(*args):
        calls.append(("evaluate", args))
        return Sentinel()

    def fake_evidence(*args):
        calls.append(("evidence", args))
        return Sentinel()

    monkeypatch.setattr(truth_merge_policy, "evaluate_merged_reconciliation_policy", fake_evaluate)
    monkeypatch.setattr(truth_merge_policy, "build_td_merged_evidence_matrix", fake_evidence)

    adapter = CtpTruthMergeAdapter()

    assert isinstance(adapter.evaluate_merged_reconciliation_policy("snapshot"), Sentinel)
    assert calls[-1] == ("evaluate", ("snapshot",))

    assert isinstance(adapter.build_merged_evidence_matrix("result"), Sentinel)
    assert calls[-1] == ("evidence", ("result",))


def test_diagnostics_owner_evaluates_md_restore_policy_without_adapter_state() -> None:
    from nautilus_ctp_adapter.diagnostics.md_models import (
        CtpMdRestoreResult,
        CtpMdStartupTruthEvidence,
    )
    from nautilus_ctp_adapter.diagnostics.md_policy import (
        build_md_truth_evidence_matrix,
        evaluate_md_restore_policy,
    )

    startup = CtpMdStartupTruthEvidence(
        flow_path="startup",
        flow_mode="explicit_override",
        selected_symbols=("rb2610",),
        ready=True,
        login_success=True,
        login_error_id=0,
        subscribe_code=0,
        first_tick_symbol="rb2610",
        first_tick_last=1.0,
        first_tick_bid=0.9,
        first_tick_ask=1.1,
        first_tick_ts_epoch_us=100,
        disconnect_count=0,
        disconnect_reasons=(),
    )
    restored = CtpMdStartupTruthEvidence(
        flow_path="restored",
        flow_mode="explicit_override",
        selected_symbols=("rb2610",),
        ready=True,
        login_success=True,
        login_error_id=0,
        subscribe_code=0,
        first_tick_symbol="rb2610",
        first_tick_last=1.2,
        first_tick_bid=1.1,
        first_tick_ask=1.3,
        first_tick_ts_epoch_us=200,
        disconnect_count=0,
        disconnect_reasons=(),
    )

    result = evaluate_md_restore_policy(
        startup,
        CtpMdRestoreResult(triggered=True, restored_symbols=("rb2610",)),
        restored,
    )
    matrix = build_md_truth_evidence_matrix(result, account_id="redacted-account")

    assert result.restore_succeeded is True
    assert result.disposition == "evidence_only"
    assert matrix.account_id == "redacted-account"
    assert matrix.restore_succeeded is True
    assert matrix.evidence_only_codes == ("restore_resubscribe_triggered",)


def test_diagnostics_owner_evaluates_td_policy_without_adapter_state() -> None:
    from nautilus_ctp_adapter.diagnostics.td_models import (
        CtpTdObservedCallback,
        CtpTdOrderTruthBaseline,
    )
    from nautilus_ctp_adapter.diagnostics.td_policy import (
        build_td_order_truth_evidence_matrix,
        evaluate_historical_callback_boundary_policy,
        evaluate_order_trade_snapshot,
    )

    baseline = CtpTdOrderTruthBaseline(
        flow_path="td-order-truth",
        flow_mode="explicit_override",
        ready=True,
        login_success=True,
        settlement_code=0,
        login_front_id=10,
        login_session_id=20,
        login_max_order_ref=100,
        disconnect_count=0,
        disconnect_reasons=(),
        observed_callback_count=4,
        observed_order_event_count=3,
        observed_trade_event_count=1,
        no_callbacks_observed=False,
        first_order_id="hist-order",
        first_order_ref="99",
        first_session_id=19,
        first_front_id=10,
        first_is_trade=False,
        observed_callbacks=(
            CtpTdObservedCallback(
                order_id="hist-order",
                order_ref="99",
                front_id=10,
                session_id=19,
                is_trade=False,
                ts_epoch_us=100,
                status=0,
            ),
            CtpTdObservedCallback(
                order_id="delayed-order",
                order_ref="100",
                front_id=10,
                session_id=20,
                is_trade=False,
                ts_epoch_us=200,
                status=0,
            ),
            CtpTdObservedCallback(
                order_id="current-order",
                order_ref="101",
                front_id=10,
                session_id=20,
                is_trade=False,
                ts_epoch_us=300,
                status=0,
            ),
            CtpTdObservedCallback(
                order_id="current-trade",
                order_ref="102",
                front_id=10,
                session_id=20,
                is_trade=True,
                ts_epoch_us=400,
                status=0,
            ),
        ),
    )

    boundary = evaluate_historical_callback_boundary_policy(baseline)
    snapshot = evaluate_order_trade_snapshot(baseline)
    matrix = build_td_order_truth_evidence_matrix(boundary, account_id="redacted-account")

    assert boundary.disposition == "boundary_required"
    assert boundary.historical_callback_count == 1
    assert boundary.delayed_callback_count == 1
    assert boundary.current_session_callback_count == 2
    assert boundary.first_historical_order_id == "hist-order"
    assert boundary.first_current_session_order_id == "current-order"

    assert snapshot.disposition == "boundary_required"
    assert snapshot.historical_residue_order_count == 2
    assert snapshot.current_session_order_count == 1
    assert snapshot.current_session_trade_count == 1
    assert snapshot.first_current_session_trade_id == "current-trade"

    assert matrix.account_id == "redacted-account"
    assert matrix.boundary_codes == (
        "historical_callbacks_present",
        "delayed_callbacks_present",
    )
    assert matrix.evidence_only_codes == ("current_session_callbacks_present",)


def test_diagnostics_owner_evaluates_reconciliation_policy_without_adapter_state() -> None:
    from nautilus_ctp_adapter.diagnostics.reconciliation_models import (
        CtpReconciliationSummary,
        CtpReconciliationSymbolExposure,
    )
    from nautilus_ctp_adapter.diagnostics.reconciliation_policy import (
        build_reconciliation_evidence,
        evaluate_reconciliation_summary,
    )

    summary = CtpReconciliationSummary(
        position_request_id="position-request",
        account_request_id="account-request",
        account_id="redacted-account",
        position_line_count=1,
        symbol_count=1,
        total_long_qty=10,
        total_short_qty=0,
        gross_position_qty=10,
        total_position_cost=1000.0,
        account_balance=10000.0,
        account_available=1000.0,
        account_margin=9000.0,
        available_ratio=0.1,
        margin_ratio=0.9,
        dominant_exposure_symbol="rb2610",
        dominant_exposure_exchange="SHFE",
        dominant_exposure_abs_net_qty=10,
        exposures=(
            CtpReconciliationSymbolExposure(
                venue_symbol="rb2610",
                exchange_id="SHFE",
                long_qty=10,
                short_qty=0,
                gross_qty=10,
                net_qty=10,
                abs_net_qty=10,
                position_cost=1000.0,
            ),
        ),
    )

    result = evaluate_reconciliation_summary(summary)
    evidence = build_reconciliation_evidence(result)

    assert result.disposition == "manual_review_required"
    assert result.requires_manual_review is True
    assert evidence.account_id == "redacted-account"
    assert evidence.manual_review_codes == (
        "available_ratio_critical",
        "margin_ratio_critical",
    )
    assert evidence.evidence_only_codes == ("dominant_exposure_watch",)


def test_diagnostics_owner_evaluates_startup_policy_without_adapter_state() -> None:
    from nautilus_ctp_adapter.diagnostics.startup_models import CtpTdStartupTruthEvidence
    from nautilus_ctp_adapter.diagnostics.startup_policy import (
        build_startup_truth_evidence_matrix,
        evaluate_session_rebuild_policy,
    )

    shared = CtpTdStartupTruthEvidence(
        flow_path="shared",
        flow_mode="default_shared_flow",
        ready=True,
        login_success=True,
        settlement_code=0,
        front_id=1,
        session_id=10,
        max_order_ref=50,
        disconnect_count=0,
        disconnect_reasons=(),
    )
    isolated = CtpTdStartupTruthEvidence(
        flow_path="isolated",
        flow_mode="explicit_override",
        ready=True,
        login_success=True,
        settlement_code=0,
        front_id=1,
        session_id=11,
        max_order_ref=1,
        disconnect_count=0,
        disconnect_reasons=(),
    )

    result = evaluate_session_rebuild_policy(shared, isolated)
    evidence = build_startup_truth_evidence_matrix(result, account_id="redacted-account")

    assert result.disposition == "rebuild_required"
    assert result.session_rotated is True
    assert result.max_order_ref_reset is True
    assert [finding.code for finding in result.findings] == [
        "shared_flow_requires_isolated_rebuild",
        "isolated_flow_verified",
        "fresh_session_identity_observed",
        "max_order_ref_reinitialized",
    ]
    assert evidence.account_id == "redacted-account"
    assert evidence.rebuild_required_codes == ("shared_flow_requires_isolated_rebuild",)
    assert evidence.evidence_only_codes == (
        "isolated_flow_verified",
        "fresh_session_identity_observed",
        "max_order_ref_reinitialized",
    )


def test_diagnostics_owner_evaluates_truth_merge_policy_without_adapter_state() -> None:
    from nautilus_ctp_adapter.diagnostics.td_models import CtpTdOrderTruthEvidenceMatrix
    from nautilus_ctp_adapter.diagnostics.truth_merge_models import CtpTdTruthMergeSnapshot
    from nautilus_ctp_adapter.diagnostics.truth_merge_policy import (
        build_td_merged_evidence_matrix,
        evaluate_merged_reconciliation_policy,
    )

    class Account:
        balance = 1000.0
        available = 100.0
        margin = 900.0

    class AccountSnapshot:
        account = Account()

    class PositionSnapshot:
        completed = True
        timed_out = False
        position_count = 3

    snapshot = CtpTdTruthMergeSnapshot(
        order_truth=CtpTdOrderTruthEvidenceMatrix(
            evidence_version="td-order-truth-evidence-v1",
            captured_at_utc="2026-04-02T08:14:00Z",
            account_id="redacted-account",
            disposition="boundary_required",
            observed_callback_count=2,
            historical_callback_count=1,
            delayed_callback_count=0,
            current_session_callback_count=0,
            first_historical_order_id="historical-order",
            first_current_session_order_id=None,
            manual_review_codes=(),
            boundary_codes=("historical_callbacks_present",),
            evidence_only_codes=("no_current_session_callbacks",),
        ),
        positions=PositionSnapshot(),
        account=AccountSnapshot(),
    )

    result = evaluate_merged_reconciliation_policy(snapshot)
    evidence = build_td_merged_evidence_matrix(result)

    assert result.disposition == "manual_review_required"
    assert result.available_ratio == 0.1
    assert result.margin_ratio == 0.9
    assert [finding.code for finding in result.findings] == [
        "historical_callbacks_present",
        "available_ratio_warn",
        "margin_ratio_warn",
        "no_current_session_callbacks",
    ]
    assert evidence.account_id == "redacted-account"
    assert evidence.position_count == 3
    assert evidence.manual_review_codes == ("available_ratio_warn", "margin_ratio_warn")
    assert evidence.boundary_codes == ("historical_callbacks_present",)
    assert evidence.evidence_only_codes == ("no_current_session_callbacks",)


def test_diagnostics_owner_evaluates_live_ops_policy_without_adapter_state() -> None:
    from nautilus_ctp_adapter.diagnostics.live_ops_models import CtpLiveOpsSnapshotSummary
    from nautilus_ctp_adapter.diagnostics.live_ops_policy import (
        build_live_ops_evidence_matrix,
        evaluate_live_ops_summary,
    )

    summary = CtpLiveOpsSnapshotSummary(
        baseline="live-ops-snapshot-v1",
        account_id=None,
        symbol="rb2610",
        startup_disposition="rebuild_required",
        md_disposition="restore_required",
        td_disposition="boundary_required",
        reconciliation_disposition="evidence_only",
        startup_shared_flow_reuse_allowed=False,
        startup_session_rotated=True,
        md_restore_succeeded=False,
        position_count=73,
        observed_callback_count=9,
        historical_callback_count=9,
        current_session_callback_count=0,
        available_ratio=0.5,
        margin_ratio=0.2,
        manual_review_codes=("available_ratio_warn",),
        rebuild_required_codes=("shared_flow_requires_isolated_rebuild",),
        restore_required_codes=("md_restore_failed",),
        boundary_codes=("historical_callbacks_present",),
        evidence_only_codes=("dominant_exposure_watch",),
    )

    result = evaluate_live_ops_summary(summary)
    evidence = build_live_ops_evidence_matrix(result)

    assert result.disposition == "manual_review_required"
    assert [finding.code for finding in result.findings] == [
        "missing_account_identity",
        "manual_review_codes_present",
        "startup_rebuild_required",
        "md_restore_attention_required",
        "td_boundary_required",
        "evidence_only_signals_present",
    ]
    assert evidence.account_id is None
    assert evidence.symbol == "rb2610"
    assert evidence.disposition == "manual_review_required"
    assert evidence.manual_review_codes == ("available_ratio_warn",)
    assert evidence.rebuild_required_codes == ("shared_flow_requires_isolated_rebuild",)
    assert evidence.restore_required_codes == ("md_restore_failed",)
    assert evidence.boundary_codes == ("historical_callbacks_present",)
    assert evidence.evidence_only_codes == ("dominant_exposure_watch",)


def test_diagnostics_owner_builds_evidence_matrix_payloads_without_cli_state() -> None:
    from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
        build_account_query_payload,
        build_instrument_query_payload,
        build_live_data_client_bootstrap_payload,
        build_marketdata_smoke_payload,
        build_md_login_smoke_payload,
        build_md_truth_evidence_matrix_payload,
        build_md_restore_policy_payload,
        build_md_startup_truth_payload,
        build_nautilus_engine_harness_payload,
        build_nautilus_live_smoke_payload,
        build_order_trade_query_config_invalid_payload,
        build_order_trade_query_config_missing_payload,
        build_order_trade_query_native_missing_payload,
        build_order_trade_query_payload,
        build_order_lifecycle_exception_payload,
        build_order_lifecycle_payload,
        build_query_adapter_payload,
        build_live_ops_evidence_matrix_payload,
        build_live_ops_policy_payload,
        build_live_ops_snapshot_payload,
        build_position_query_payload,
        build_reconciliation_evidence_payload,
        build_reconciliation_policy_payload,
        build_reconciliation_snapshot_payload,
        build_repo_debug_smoke_payload,
        build_session_rebuild_policy_payload,
        build_td_historical_callback_boundary_payload,
        build_td_login_smoke_payload,
        build_startup_truth_evidence_matrix_payload,
        build_td_merged_reconciliation_policy_payload,
        build_td_merged_evidence_matrix_payload,
        build_td_order_truth_payload,
        build_td_order_truth_evidence_matrix_payload,
        build_td_startup_truth_payload,
        build_td_truth_merge_snapshot_payload,
        classify_account_query_failure,
        classify_instrument_query_failure,
        classify_live_data_client_bootstrap_failure,
        classify_marketdata_smoke_failure,
        classify_md_login_smoke_failure,
        classify_md_restore_policy_failure,
        classify_md_startup_truth_failure,
        classify_nautilus_engine_harness_success,
        classify_nautilus_live_smoke_failure,
        classify_order_trade_query_failure,
        classify_order_lifecycle_success,
        classify_query_adapter_failure,
        classify_live_ops_evidence_matrix_failure,
        classify_live_ops_summary_failure,
        classify_md_truth_evidence_matrix_failure,
        classify_position_query_failure,
        classify_reconciliation_evidence_failure,
        classify_reconciliation_policy_failure,
        classify_reconciliation_snapshot_failure,
        classify_repo_debug_smoke_failure,
        classify_session_rebuild_policy_failure,
        classify_td_historical_callback_boundary_failure,
        classify_td_login_smoke_failure,
        classify_startup_truth_evidence_matrix_failure,
        classify_td_merged_reconciliation_policy_failure,
        classify_td_merged_evidence_matrix_failure,
        classify_td_order_truth_failure,
        classify_td_order_truth_evidence_matrix_failure,
        classify_td_startup_truth_failure,
        classify_td_truth_merge_snapshot_failure,
        instrument_matches_requested_symbol,
    )
    from nautilus_ctp_adapter.diagnostics.live_ops_models import (
        CtpLiveOpsEvidenceMatrix,
        CtpLiveOpsPolicyResult,
        CtpLiveOpsSnapshotSummary,
    )
    from nautilus_ctp_adapter.diagnostics.md_models import (
        CtpMdRestorePolicyFinding,
        CtpMdRestorePolicyResult,
        CtpMdRestoreResult,
        CtpMdStartupTruthEvidence,
        CtpMdTruthEvidenceMatrix,
    )
    from nautilus_ctp_adapter.diagnostics.reconciliation_models import (
        CtpReconciliationEvidence,
        CtpReconciliationPolicyFinding,
        CtpReconciliationPolicyResult,
        CtpReconciliationSummary,
        CtpReconciliationSymbolExposure,
    )
    from nautilus_ctp_adapter.diagnostics.startup_models import (
        CtpSessionRebuildFinding,
        CtpSessionRebuildPolicyResult,
        CtpTdStartupTruthEvidence,
    )
    from nautilus_ctp_adapter.diagnostics.td_models import CtpTdOrderTruthEvidenceMatrix
    from nautilus_ctp_adapter.diagnostics.truth_merge_models import (
        CtpTdMergedReconciliationFinding,
        CtpTdMergedReconciliationPolicyResult,
        CtpTdTruthMergeSnapshot,
    )

    md_evidence = CtpMdTruthEvidenceMatrix(
        evidence_version="md-truth-evidence-v1",
        captured_at_utc="2026-04-02T08:01:00Z",
        account_id="redacted-account",
        symbol="rb2610",
        disposition="evidence_only",
        startup_ready=True,
        restore_triggered=True,
        restore_succeeded=True,
        startup_flow_path="startup",
        restored_flow_path="restored",
        startup_first_tick_ts_epoch_us=100,
        restored_first_tick_ts_epoch_us=200,
        manual_review_codes=(),
        restore_required_codes=(),
        evidence_only_codes=("restore_resubscribe_triggered",),
    )
    td_evidence = CtpTdOrderTruthEvidenceMatrix(
        evidence_version="td-order-truth-evidence-v1",
        captured_at_utc="2026-04-02T08:10:00Z",
        account_id=None,
        disposition="boundary_required",
        observed_callback_count=2,
        historical_callback_count=1,
        delayed_callback_count=0,
        current_session_callback_count=1,
        first_historical_order_id="historical-order",
        first_current_session_order_id="current-order",
        manual_review_codes=(),
        boundary_codes=("historical_callbacks_present",),
        evidence_only_codes=("current_session_callbacks_present",),
    )

    md_payload = build_md_truth_evidence_matrix_payload(
        md_evidence,
        flow_mode="explicit_override",
        session_label="isolated-flow",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )
    td_payload = build_td_order_truth_evidence_matrix_payload(
        td_evidence,
        flow_mode="default",
        session_label="default",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )

    assert classify_md_truth_evidence_matrix_failure(md_evidence) is None
    assert md_payload["baseline"] == "md-truth-evidence-matrix-v1"
    assert md_payload["success"] is True
    assert md_payload["evidence_only_codes"] == ["restore_resubscribe_triggered"]

    assert classify_td_order_truth_evidence_matrix_failure(td_evidence) == "account_id_missing"
    assert td_payload["baseline"] == "td-order-truth-evidence-matrix-v1"
    assert td_payload["success"] is False
    assert td_payload["failure_reason"] == "account_id_missing"
    assert td_payload["boundary_codes"] == ["historical_callbacks_present"]

    class StartupEvidence:
        evidence_version = "startup-truth-evidence-v1"
        captured_at_utc = "2026-04-02T08:11:00Z"
        account_id = "redacted-account"
        disposition = "rebuild_required"
        shared_flow_reuse_allowed = False
        session_rotated = True
        max_order_ref_reset = True
        shared_flow_path = "shared"
        isolated_flow_path = "isolated"
        shared_session_id = 1
        isolated_session_id = 2
        shared_max_order_ref = 20
        isolated_max_order_ref = 1
        shared_disconnect_count = 0
        isolated_disconnect_count = 0
        manual_review_codes = ()
        rebuild_required_codes = ("shared_flow_requires_isolated_rebuild",)
        evidence_only_codes = ("isolated_flow_verified",)

    class MergedEvidence:
        evidence_version = "td-merged-evidence-v1"
        captured_at_utc = "2026-04-02T08:12:00Z"
        account_id = "redacted-account"
        disposition = "boundary_required"
        position_count = -1
        observed_callback_count = 9
        historical_callback_count = 1
        current_session_callback_count = 8
        available_ratio = 0.8
        margin_ratio = 0.2
        manual_review_codes = ()
        boundary_codes = ("historical_callbacks_present",)
        evidence_only_codes = ()

    startup_payload = build_startup_truth_evidence_matrix_payload(
        StartupEvidence(),
        flow_mode="explicit_override",
        session_label="isolated-flow",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )
    merged_payload = build_td_merged_evidence_matrix_payload(
        MergedEvidence(),
        flow_path="flow",
        flow_mode="explicit_override",
        session_label="flow",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )

    assert classify_startup_truth_evidence_matrix_failure(StartupEvidence()) is None
    assert startup_payload["baseline"] == "td-startup-truth-evidence-matrix-v1"
    assert startup_payload["success"] is True
    assert startup_payload["rebuild_required_codes"] == ["shared_flow_requires_isolated_rebuild"]

    assert classify_td_merged_evidence_matrix_failure(MergedEvidence()) == "position_count_invalid"
    assert merged_payload["baseline"] == "td-merged-evidence-matrix-v1"
    assert merged_payload["success"] is False
    assert merged_payload["failure_reason"] == "position_count_invalid"

    live_summary = CtpLiveOpsSnapshotSummary(
        baseline="live-ops-snapshot-v1",
        account_id="redacted-account",
        symbol="rb2610",
        startup_disposition="clear",
        md_disposition="clear",
        td_disposition="clear",
        reconciliation_disposition="clear",
        startup_shared_flow_reuse_allowed=True,
        startup_session_rotated=False,
        md_restore_succeeded=True,
        position_count=1,
        observed_callback_count=1,
        historical_callback_count=0,
        current_session_callback_count=1,
        available_ratio=0.5,
        margin_ratio=0.2,
        manual_review_codes=(),
        rebuild_required_codes=(),
        restore_required_codes=(),
        boundary_codes=(),
        evidence_only_codes=(),
    )
    live_result = CtpLiveOpsPolicyResult(
        summary=live_summary,
        disposition="clear",
        findings=(),
    )
    live_evidence = CtpLiveOpsEvidenceMatrix(
        evidence_version="live-ops-evidence-v1",
        account_id=None,
        symbol="rb2610",
        disposition="clear",
        startup_disposition="clear",
        md_disposition="clear",
        td_disposition="clear",
        reconciliation_disposition="clear",
        startup_shared_flow_reuse_allowed=True,
        startup_session_rotated=False,
        md_restore_succeeded=True,
        position_count=1,
        observed_callback_count=1,
        historical_callback_count=0,
        current_session_callback_count=1,
        available_ratio=0.5,
        margin_ratio=0.2,
        manual_review_codes=(),
        rebuild_required_codes=(),
        restore_required_codes=(),
        boundary_codes=(),
        evidence_only_codes=(),
    )

    assert classify_live_ops_summary_failure(live_summary, "clear") is None
    assert classify_live_ops_evidence_matrix_failure(live_evidence) == "account_id_missing"
    assert build_live_ops_policy_payload(
        live_result,
        flow_mode="default",
        session_label="default",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "live-ops-policy-v1"
    assert build_live_ops_evidence_matrix_payload(
        live_evidence,
        flow_mode="default",
        session_label="default",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["failure_reason"] == "account_id_missing"

    class LiveSnapshot:
        startup_truth = StartupEvidence()
        md_truth = md_evidence
        td_truth = MergedEvidence()
        reconciliation = type(
            "ReconciliationEvidence",
            (),
            {
                "account_id": "redacted-account",
                "disposition": "clear",
                "requires_manual_review": False,
                "finding_count": 0,
                "position_line_count": 1,
                "symbol_count": 1,
                "gross_position_qty": 1,
                "available_ratio": 0.5,
                "margin_ratio": 0.2,
                "manual_review_codes": (),
                "evidence_only_codes": (),
            },
        )()

    assert build_live_ops_snapshot_payload(
        snapshot=LiveSnapshot(),
        summary=live_summary,
        policy_result=live_result,
        flow_mode="default",
        session_label="default",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "live-ops-snapshot-v1"

    class PositionsSnapshot:
        request_id = "positions-request"
        query_code = 0
        completed = True
        timed_out = False
        no_positions = False
        position_count = 1

    class AccountValue:
        account_id = "redacted-account"
        balance = 1000.0
        available = 500.0
        margin = 200.0
        commission = 1.0
        close_profit = 2.0
        position_profit = 3.0

    class AccountSnapshot:
        request_id = "account-request"
        query_code = 0
        completed = True
        timed_out = False
        account = AccountValue()

    class QuerySnapshot:
        positions = PositionsSnapshot()
        account = AccountSnapshot()

    class ReconciliationSnapshot:
        query_snapshot = QuerySnapshot()

    reconciliation_summary = CtpReconciliationSummary(
        position_request_id="positions-request",
        account_request_id="account-request",
        account_id="redacted-account",
        position_line_count=1,
        symbol_count=1,
        total_long_qty=1,
        total_short_qty=0,
        gross_position_qty=1,
        total_position_cost=100.0,
        account_balance=1000.0,
        account_available=500.0,
        account_margin=200.0,
        available_ratio=0.5,
        margin_ratio=0.2,
        dominant_exposure_symbol="rb2610",
        dominant_exposure_exchange="SHFE",
        dominant_exposure_abs_net_qty=1,
        exposures=(
            CtpReconciliationSymbolExposure(
                venue_symbol="rb2610",
                exchange_id="SHFE",
                long_qty=1,
                short_qty=0,
                gross_qty=1,
                net_qty=1,
                abs_net_qty=1,
                position_cost=100.0,
            ),
        ),
    )
    reconciliation_result = CtpReconciliationPolicyResult(
        summary=reconciliation_summary,
        disposition="evidence_only",
        requires_manual_review=False,
        findings=(
            CtpReconciliationPolicyFinding(
                code="dominant_exposure_watch",
                severity="info",
                action="evidence_only",
                metric="dominant_exposure_abs_net_qty",
                metric_value=1,
                threshold=1,
                message="Synthetic evidence-only finding.",
            ),
        ),
    )
    reconciliation_evidence = CtpReconciliationEvidence(
        evidence_version="reconciliation-evidence-v1",
        captured_at_utc="2026-04-02T08:13:00Z",
        account_id=None,
        disposition="evidence_only",
        requires_manual_review=False,
        finding_count=1,
        manual_review_codes=(),
        evidence_only_codes=("dominant_exposure_watch",),
        position_line_count=1,
        symbol_count=1,
        gross_position_qty=1,
        available_ratio=0.5,
        margin_ratio=0.2,
        dominant_exposure_symbol="rb2610",
        dominant_exposure_abs_net_qty=1,
        top_exposures=reconciliation_summary.exposures,
    )

    assert classify_reconciliation_snapshot_failure(
        ReconciliationSnapshot(),
        reconciliation_summary,
    ) is None
    assert classify_reconciliation_policy_failure(reconciliation_result) is None
    assert classify_reconciliation_evidence_failure(reconciliation_evidence) == "account_id_missing"
    assert build_reconciliation_snapshot_payload(
        snapshot=ReconciliationSnapshot(),
        summary=reconciliation_summary,
        policy_result=reconciliation_result,
        session_label="default",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "reconciliation-snapshot-v1"
    assert build_reconciliation_policy_payload(
        reconciliation_result,
        session_label="default",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "reconciliation-policy-v1"
    assert build_reconciliation_evidence_payload(
        reconciliation_evidence,
        session_label="default",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["failure_reason"] == "account_id_missing"

    td_startup = CtpTdStartupTruthEvidence(
        flow_path="td-startup",
        flow_mode="explicit_override",
        ready=True,
        login_success=True,
        settlement_code=0,
        front_id=1,
        session_id=2,
        max_order_ref=3,
        disconnect_count=0,
        disconnect_reasons=(),
    )
    session_rebuild = CtpSessionRebuildPolicyResult(
        shared_truth=td_startup,
        isolated_truth=td_startup,
        disposition="evidence_only",
        shared_flow_reuse_allowed=False,
        session_rotated=False,
        max_order_ref_reset=True,
        findings=(
            CtpSessionRebuildFinding(
                code="synthetic_finding",
                severity="info",
                action="evidence_only",
                metric="synthetic",
                metric_value=1,
                threshold=1,
                message="Synthetic finding.",
            ),
        ),
    )
    md_restore = CtpMdRestorePolicyResult(
        startup_truth=CtpMdStartupTruthEvidence(
            flow_path="startup",
            flow_mode="explicit_override",
            selected_symbols=("rb2610",),
            ready=True,
            login_success=True,
            login_error_id=0,
            subscribe_code=0,
            first_tick_symbol="rb2610",
            first_tick_last=1.0,
            first_tick_bid=0.9,
            first_tick_ask=1.1,
            first_tick_ts_epoch_us=100,
            disconnect_count=0,
            disconnect_reasons=(),
        ),
        restored_truth=CtpMdStartupTruthEvidence(
            flow_path="restored",
            flow_mode="explicit_override",
            selected_symbols=("rb2610",),
            ready=True,
            login_success=True,
            login_error_id=0,
            subscribe_code=0,
            first_tick_symbol="rb2610",
            first_tick_last=1.2,
            first_tick_bid=1.1,
            first_tick_ask=1.3,
            first_tick_ts_epoch_us=200,
            disconnect_count=0,
            disconnect_reasons=(),
        ),
        restore_result=CtpMdRestoreResult(triggered=True, restored_symbols=("rb2610",)),
        disposition="evidence_only",
        restore_succeeded=True,
        findings=(
            CtpMdRestorePolicyFinding(
                code="restore_resubscribe_triggered",
                severity="info",
                action="evidence_only",
                metric="restore_triggered",
                metric_value=True,
                threshold=True,
                message="Synthetic restore finding.",
            ),
        ),
    )
    td_merge_snapshot = CtpTdTruthMergeSnapshot(
        order_truth=td_evidence,
        positions=PositionsSnapshot(),
        account=AccountSnapshot(),
    )
    td_merged_policy = CtpTdMergedReconciliationPolicyResult(
        snapshot=td_merge_snapshot,
        disposition="boundary_required",
        available_ratio=0.5,
        margin_ratio=0.2,
        findings=(
            CtpTdMergedReconciliationFinding(
                code="synthetic_boundary",
                severity="warn",
                action="boundary_required",
                metric="synthetic",
                metric_value=1,
                threshold=0,
                message="Synthetic boundary.",
            ),
        ),
    )

    assert classify_td_startup_truth_failure(td_startup) is None
    assert classify_session_rebuild_policy_failure(session_rebuild) is None
    assert classify_md_restore_policy_failure(md_restore) is None
    assert classify_td_truth_merge_snapshot_failure(td_merge_snapshot) == "order_truth_account_missing"
    assert classify_td_merged_reconciliation_policy_failure(td_merged_policy) is None
    assert build_td_startup_truth_payload(
        td_startup,
        flow_mode="explicit_override",
        session_label="td-startup",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "td-startup-truth-v1"
    assert build_session_rebuild_policy_payload(
        session_rebuild,
        flow_mode="explicit_override",
        session_label="session-rebuild",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "td-session-rebuild-policy-v1"
    assert build_md_restore_policy_payload(
        md_restore,
        flow_mode="explicit_override",
        session_label="md-restore",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "md-restore-policy-v1"
    assert build_td_truth_merge_snapshot_payload(
        td_merge_snapshot,
        flow_path="flow",
        flow_mode="explicit_override",
        session_label="td-merge",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["failure_reason"] == "order_truth_account_missing"
    assert build_td_merged_reconciliation_policy_payload(
        td_merged_policy,
        flow_path="flow",
        flow_mode="explicit_override",
        session_label="td-merged-policy",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "td-merged-reconciliation-policy-v1"

    class ProductKind:
        value = "FUTURE"

    class Instrument:
        venue_symbol = "rb2610"
        display_symbol = "rb2610.SHFE"
        underlying = "rb"
        contract_month = "2610"
        product_kind = ProductKind()
        price_tick = 1.0
        volume_multiple = 10

    class InstrumentResult:
        request_id = "instrument-request"
        loaded = True
        instrument_count = 1
        instruments = (Instrument(),)

    assert instrument_matches_requested_symbol(
        requested_symbol="rb2610",
        venue_symbol="rb2610",
        display_symbol="rb2610.SHFE",
    )
    assert classify_query_adapter_failure(
        snapshot=QuerySnapshot(),
        instrument_result=InstrumentResult(),
        requested_instrument_symbol="rb2610",
        order_truth_result=None,
        order_trade_snapshot_result=None,
        reconciliation_policy=None,
        merged_policy_result=None,
    ) is None
    query_payload = build_query_adapter_payload(
        snapshot=QuerySnapshot(),
        flow_path="flow",
        flow_mode="explicit_override",
        session_label="query",
        instrument_result=InstrumentResult(),
        requested_instrument_symbol="rb2610",
        account_id="redacted-account",
        order_truth_result=None,
        order_trade_snapshot_result=None,
        reconciliation_summary=reconciliation_summary,
        reconciliation_policy=reconciliation_result,
        reconciliation_evidence=reconciliation_evidence,
        merged_policy_result=td_merged_policy,
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )
    assert query_payload["baseline"] == "nautilus-query-adapter-v1"
    assert query_payload["success"] is True
    assert query_payload["instrument"]["matched_symbols"] == ["rb2610.SHFE"]
    assert query_payload["reconciliation"]["account_id"] == "redacted-account"
    assert query_payload["merged_policy"]["disposition"] == "boundary_required"
    assert classify_instrument_query_failure(InstrumentResult(), "rb2610") is None
    assert build_instrument_query_payload(
        InstrumentResult(),
        requested_symbol="rb2610",
        flow_path="flow",
        flow_mode="explicit_override",
        session_label="instrument",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "instrument-query-smoke-v1"

    class TdSmoke:
        login_success = True
        settlement_code = 0

    class ExecutionBootstrap:
        td_smoke = TdSmoke()

    class Bootstrap:
        ready = True
        execution_bootstrap = ExecutionBootstrap()

    class AccountQueryResult:
        query_request_id = "account-request"
        query_code = 0
        completed = True
        timed_out = False
        account = AccountValue()
        bootstrap = Bootstrap()
        disconnects = ()

    class PositionRecord:
        venue_symbol = "rb2610"
        exchange_id = "SHFE"
        direction = "LONG"
        position_qty = 1
        yd_position_qty = 0
        td_position_qty = 1
        position_cost = 100.0

    class PositionQueryResult:
        query_request_id = "positions-request"
        query_code = 0
        completed = True
        timed_out = False
        no_positions = False
        position_count = 1
        positions = (PositionRecord(),)
        bootstrap = Bootstrap()
        disconnects = ()

    assert classify_account_query_failure(AccountQueryResult()) is None
    assert build_account_query_payload(
        AccountQueryResult(),
        flow_path="flow",
        flow_mode="explicit_override",
        session_label="account",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["account"]["account_id"] == "redacted-account"
    assert classify_position_query_failure(PositionQueryResult()) is None
    assert build_position_query_payload(
        PositionQueryResult(),
        flow_path="flow",
        flow_mode="explicit_override",
        session_label="positions",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["positions"][0]["venue_symbol"] == "rb2610"

    class ObservedCallback:
        order_id = "order-1"
        order_ref = "1"
        front_id = 1
        session_id = 2
        is_trade = False
        ts_epoch_us = 100
        status = "accepted"

    class TdOrderTruth:
        flow_path = "td-order"
        ready = True
        login_success = True
        settlement_code = 0
        disconnect_count = 0
        disconnect_reasons = ()
        observed_callback_count = 1
        observed_order_event_count = 1
        observed_trade_event_count = 0
        no_callbacks_observed = False
        first_order_id = "order-1"
        first_order_ref = "1"
        first_session_id = 2
        first_front_id = 1
        first_is_trade = False
        observed_callbacks = (ObservedCallback(),)

    assert classify_td_order_truth_failure(TdOrderTruth()) is None
    assert build_td_order_truth_payload(
        TdOrderTruth(),
        flow_mode="explicit_override",
        session_label="td-order",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["observed_callbacks"][0]["order_id"] == "order-1"

    class BoundaryBaseline:
        ready = True
        observed_callback_count = 1
        login_front_id = 1
        login_session_id = 2
        login_max_order_ref = "3"

    class HistoricalBoundary:
        baseline = BoundaryBaseline()
        disposition = "evidence_only"
        historical_callback_count = 0
        delayed_callback_count = 0
        current_session_callback_count = 1
        first_historical_order_id = None
        first_current_session_order_id = "order-1"
        findings = ()

    assert classify_td_historical_callback_boundary_failure(HistoricalBoundary()) is None
    assert build_td_historical_callback_boundary_payload(
        HistoricalBoundary(),
        flow_mode="explicit_override",
        session_label="td-boundary",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "td-historical-callback-boundary-v1"
    assert classify_md_startup_truth_failure(md_restore.startup_truth) is None
    assert build_md_startup_truth_payload(
        md_restore.startup_truth,
        flow_mode="explicit_override",
        session_label="md-startup",
        export={"written": False},
        bridge_commands=(),
        bridge_events=(),
    )["baseline"] == "md-startup-truth-v1"

    class BridgeKind:
        value = "tick"

    class BridgeEvent:
        kind = BridgeKind()
        venue_symbol = "rb2610"

    class MdLoginSmoke:
        init_code = 0
        login_request_code = 0
        subscribe_code = 0
        login_success = True
        login_error_id = 0
        login_error_message = ""
        first_tick_symbol = "rb2610"
        first_tick_last = 1.0
        first_tick_bid = 0.9
        first_tick_ask = 1.1
        first_tick_ts_epoch_us = 100

    assert classify_md_login_smoke_failure(MdLoginSmoke()) is None
    assert build_md_login_smoke_payload(
        MdLoginSmoke(),
        flow_path="md-login",
        flow_mode="explicit_override",
        session_label="md-login",
        instruments=("rb2610",),
        instrument_override=True,
        md_front_override={"enabled": False, "raw_value_recorded": False},
        md_login_override={"applied": False, "raw_values_recorded": False},
        runtime_pack_override={"enabled": False, "raw_value_recorded": False},
        export={"written": False},
        bridge_events=(BridgeEvent(),),
    )["bridge_tick_symbol"] == "rb2610"

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 1
        session_id = 2
        max_order_ref = "3"

    assert classify_td_login_smoke_failure(LoginResponse(), 0) is None
    assert build_td_login_smoke_payload(
        login=LoginResponse(),
        settlement_code=0,
        init_code=0,
        authenticate_code=0,
        login_code=0,
        flow_path="td-login",
        flow_mode="explicit_override",
        session_label="td-login",
        disconnects=(),
        export={"written": False},
    )["baseline"] == "td-login-smoke-v1"

    class BootstrapState:
        started = True
        connect_request_id = 1
        subscribe_request_ids = (2,)

    class EventBatch:
        events = (BridgeEvent(),)
        should_restore = False

    class MarketdataResult:
        instrument_request_id = "instrument-request"
        instrument_loaded = True
        source_instrument_count = 1
        selected_symbols = ("rb2610",)
        bootstrap_state = BootstrapState()
        md_smoke = MdLoginSmoke()
        event_batch = EventBatch()

    assert classify_marketdata_smoke_failure(MarketdataResult(), "rb2610") is None
    assert build_marketdata_smoke_payload(
        MarketdataResult(),
        requested_symbol="rb2610",
        flow_path="marketdata",
        flow_mode="explicit_override",
        session_label="marketdata",
        export={"written": False},
        bridge_events=(BridgeEvent(),),
    )["baseline"] == "marketdata-smoke-v1"

    class CommandKind:
        value = "subscribe"

    class BootstrapCommand:
        kind = CommandKind()
        venue_symbol = "rb2610"

    class LoadResult:
        request_id = "instrument-request"
        loaded = True
        instrument_count = 1
        instruments = (Instrument(),)

    class BootstrapResult:
        selected_symbols = ("rb2610",)
        bootstrap_state = BootstrapState()

    assert classify_live_data_client_bootstrap_failure(
        load_result=LoadResult(),
        bootstrap_result=BootstrapResult(),
        requested_symbol="rb2610",
    ) is None
    assert build_live_data_client_bootstrap_payload(
        load_result=LoadResult(),
        bootstrap_result=BootstrapResult(),
        requested_symbol="rb2610",
        flow_path="bootstrap",
        flow_mode="explicit_override",
        session_label="bootstrap",
        export={"written": False},
        bootstrap_commands=(BootstrapCommand(),),
        instrument_events=(BridgeEvent(),),
    )["bootstrap_subscribe_symbols"] == ["rb2610"]

    class TdLiveSmoke:
        init_code = 0
        authenticate_code = 0
        login_code = 0
        settlement_code = 0
        login_success = True
        login_error_id = 0
        front_id = 1
        session_id = 2
        max_order_ref = "3"
        disconnects = ()

    class TdLoginEventKind:
        value = "login_succeeded"

    class TdLoginEvent:
        kind = TdLoginEventKind()
        venue_symbol = None
        payload = {"channel": "td"}

    class SettlementEventKind:
        value = "settlement_confirmed"

    class SettlementEvent:
        kind = SettlementEventKind()
        venue_symbol = None
        payload = {}

    assert classify_nautilus_live_smoke_failure(
        bootstrap=BootstrapState(),
        md_result=MdLoginSmoke(),
        td_result=TdLiveSmoke(),
        configured_instruments=("rb2610",),
    ) is None
    nautilus_payload = build_nautilus_live_smoke_payload(
        bootstrap=BootstrapState(),
        md_result=MdLoginSmoke(),
        td_result=TdLiveSmoke(),
        configured_instruments=("rb2610",),
        bridge_events=(BridgeEvent(), TdLoginEvent(), SettlementEvent()),
    )
    assert nautilus_payload["baseline"] == "nautilus-live-smoke-v1"
    assert nautilus_payload["bridge_td_login_seen"] is True
    assert nautilus_payload["bridge_settlement_seen"] is True
    assert classify_order_trade_query_failure(
        ready=True,
        query_order_code=0,
        query_trade_code=0,
    ) is None
    order_trade_payload = build_order_trade_query_payload(
        captured_at_utc="2026-04-02T08:14:00Z",
        account_id="acct.ctp.paper.19053",
        display_alias="19053",
        config_ref="owner://nautilus_ctp_adapter/cfgs/local/ctp.openctp.tts.7x24.local.json",
        native_dll_ref="D:/Nautilus/_worktrees/r1-hb-contract/nautilus_ctp_adapter/rust/target/release/ctp_native.dll",
        native_dll_checksum="sha256:synthetic",
        flow_path="td-query-flow",
        login=LoginResponse(),
        settlement_code=0,
        ready=True,
        init_code=0,
        authenticate_code=0,
        login_code=0,
        query_order_code=0,
        query_trade_code=0,
        order_is_last=True,
        trade_is_last=True,
        order_callback_observed=True,
        trade_callback_observed=True,
        disconnects=(1001,),
        orders=({"callback_source": "OnRspQryOrder", "response_is_last": True},),
        trades=({"callback_source": "OnRspQryTrade", "response_is_last": True},),
    )
    assert order_trade_payload["schema"] == "account-console.openctp-order-trade-query.v1"
    assert order_trade_payload["success"] is True
    assert order_trade_payload["readonly_api_calls"] == ["ReqQryOrder", "ReqQryTrade"]
    assert order_trade_payload["order_send_called"] is False
    assert order_trade_payload["raw_secret_values_recorded"] is False
    assert order_trade_payload["raw_broker_endpoint_recorded"] is False
    failure_payload = build_order_trade_query_config_missing_payload(
        captured_at_utc="2026-04-02T08:14:00Z",
        config_ref="owner://missing",
    )
    assert failure_payload["success"] is False
    assert failure_payload["order_action_sent"] is False
    assert build_order_trade_query_native_missing_payload(
        captured_at_utc="2026-04-02T08:14:00Z",
        native_dll_ref="owner://missing-native",
    )["failure_stage"] == "native"
    assert build_order_trade_query_config_invalid_payload(
        captured_at_utc="2026-04-02T08:14:00Z",
        config_ref="owner://invalid",
        missing_fields=("broker_id",),
    )["missing_fields"] == ["broker_id"]
    repo_debug_snapshot = {
        "probe_scope": "repo_only_debug_bootstrap",
        "td_probe_mode": "public_pyo3_scaffold_before_c3",
        "formal_live_td_entrypoint": "python scripts/ctp_nautilus_live_smoke.py --config <path>",
        "formal_live_td_path": "execution_client.run_live_td_readiness_smoke -> native.td_ctypes -> ctp_native.dll",
        "runtime_package_file": "D:/repo/src/ctp_runtime/__init__.py",
        "runtime_native_module_file": "D:/repo/src/ctp_runtime/_ctp_runtime.pyd",
        "has_internal_md_live_session": True,
        "scaffold_not_implemented": -9000,
        "invalid_handle": -9001,
        "md_init_code": -9000,
        "md_login_code": -9000,
        "md_subscribe_code": -9000,
        "td_init_code": -9000,
        "td_authenticate_code": -9000,
        "td_login_code": -9000,
        "md_init_after_dispose_code": -9001,
    }
    assert classify_repo_debug_smoke_failure(repo_debug_snapshot) is None
    assert build_repo_debug_smoke_payload(repo_debug_snapshot)["baseline"] == "repo-debug-smoke-v1"
    mismatch_snapshot = dict(repo_debug_snapshot)
    mismatch_snapshot["td_login_code"] = -42
    assert classify_repo_debug_smoke_failure(mismatch_snapshot) == "scaffold_contract_mismatch"

    class OrderLifecycleKind:
        value = "submit_order"

    class OrderLifecycleCommand:
        kind = OrderLifecycleKind()
        payload = {"client_order_id": "order-smoke-1"}

    class ExecEventKind:
        value = "order"

    class ExecEvent:
        kind = ExecEventKind()
        client_order_id = "order-smoke-1"
        venue_symbol = "c2609.DCE"
        message = "accepted"
        payload = {
            "native_order_id": "native-order",
            "native_order_ref": "1",
            "status": "ACCEPTED",
            "trade_volume": 0,
            "leaves_qty": 1,
            "match_reason": "client_order_id",
        }

    class LifecycleBootstrapState:
        connect_request_id = 1

    class LifecycleExecutionBootstrap:
        bootstrap_state = LifecycleBootstrapState()

    class LifecycleIdentity:
        front_id = 1
        session_id = 2
        max_order_ref = "3"

    class LifecycleBootstrap:
        ready = True
        execution_bootstrap = LifecycleExecutionBootstrap()
        td_session_identity = LifecycleIdentity()

    class LifecycleSubmit:
        error = None
        order_ref = "1"
        command = OrderLifecycleCommand()

    class LifecycleMatched:
        python_client_order_id = "order-smoke-1"
        native_order_id = "native-order"
        native_order_ref = "1"
        venue_symbol = "c2609.DCE"
        front_id = 1
        session_id = 2
        status = "ACCEPTED"
        is_trade = False
        trade_volume = 0
        leaves_qty = 1
        match_reason = "client_order_id"

    class LifecycleResult:
        dry_run = True
        live_send_armed = False
        bootstrap = LifecycleBootstrap()
        mapped_submit = LifecycleSubmit()
        matched_execs = (LifecycleMatched(),)

    lifecycle_payload = build_order_lifecycle_payload(
        result=LifecycleResult(),
        live_send_requested=False,
        commands=(OrderLifecycleCommand(),),
        events=(ExecEvent(),),
    )
    assert lifecycle_payload["baseline"] == "nautilus-order-lifecycle-smoke-v1"
    assert lifecycle_payload["matched_exec_count"] == 1
    assert lifecycle_payload["exec_events"][0]["native_order_ref"] == "1"
    assert classify_order_lifecycle_success(LifecycleResult(), matched_exec_count=1) is True
    exception_payload = build_order_lifecycle_exception_payload(
        dry_run=True,
        live_send_requested=False,
        td_session_identity=LifecycleIdentity(),
        error="synthetic",
        commands=(OrderLifecycleCommand(),),
        events=(ExecEvent(),),
    )
    assert exception_payload["error"] == "synthetic"
    assert classify_nautilus_engine_harness_success(
        accepted_count=1,
        canceled_count=1,
        rejected_count=1,
        fill_count=1,
        position_count=1,
        account_state_reported=True,
        account_id_redacted=True,
        script_only_smoke=False,
    ) is True
    engine_payload = build_nautilus_engine_harness_payload(
        run_id="engine-harness",
        instrument_ids=("c2609.DCE",),
        order_statuses=("ACCEPTED", "CANCELED", "REJECTED"),
        order_report_count=3,
        fill_report_count=1,
        position_report_count=1,
        account_state_reported=True,
        account_id_redacted=True,
    )
    assert engine_payload["baseline"] == "ctp-nautilus-engine-harness-v1"
    assert engine_payload["paper_send_armed"] is False
    assert engine_payload["script_only_smoke"] is False
    assert engine_payload["success"] is True

    class EmptyInstrumentResult:
        request_id = "instrument-request"
        loaded = True
        instrument_count = 0
        instruments = ()

    assert classify_query_adapter_failure(
        snapshot=QuerySnapshot(),
        instrument_result=EmptyInstrumentResult(),
        requested_instrument_symbol="rb2610",
        order_truth_result=None,
        order_trade_snapshot_result=None,
        reconciliation_policy=None,
        merged_policy_result=None,
    ) == "instrument_missing"


def test_evidence_matrix_cli_payloads_delegate_to_diagnostics_owner() -> None:
    script_root = PROJECT_ROOT / "scripts"

    for relative, owner_function in (
        (
            "ctp_md_truth_evidence_matrix_smoke.py",
            "build_md_truth_evidence_matrix_payload",
        ),
        (
            "ctp_td_order_truth_evidence_matrix_smoke.py",
            "build_td_order_truth_evidence_matrix_payload",
        ),
        (
            "ctp_startup_truth_evidence_matrix_smoke.py",
            "build_startup_truth_evidence_matrix_payload",
        ),
        (
            "ctp_td_merged_evidence_matrix_smoke.py",
            "build_td_merged_evidence_matrix_payload",
        ),
        (
            "ctp_live_ops_snapshot_smoke.py",
            "build_live_ops_snapshot_payload",
        ),
        (
            "ctp_live_ops_policy_smoke.py",
            "build_live_ops_policy_payload",
        ),
        (
            "ctp_live_ops_evidence_matrix_smoke.py",
            "build_live_ops_evidence_matrix_payload",
        ),
        (
            "ctp_reconciliation_snapshot_smoke.py",
            "build_reconciliation_snapshot_payload",
        ),
        (
            "ctp_reconciliation_policy_smoke.py",
            "build_reconciliation_policy_payload",
        ),
        (
            "ctp_reconciliation_evidence_smoke.py",
            "build_reconciliation_evidence_payload",
        ),
        (
            "ctp_startup_truth_smoke.py",
            "build_td_startup_truth_payload",
        ),
        (
            "ctp_session_rebuild_policy_smoke.py",
            "build_session_rebuild_policy_payload",
        ),
        (
            "ctp_md_restore_policy_smoke.py",
            "build_md_restore_policy_payload",
        ),
        (
            "ctp_td_truth_merge_snapshot_smoke.py",
            "build_td_truth_merge_snapshot_payload",
        ),
        (
            "ctp_td_merged_reconciliation_policy_smoke.py",
            "build_td_merged_reconciliation_policy_payload",
        ),
        (
            "ctp_query_adapter_smoke.py",
            "build_query_adapter_payload",
        ),
        (
            "ctp_instrument_query_smoke.py",
            "build_instrument_query_payload",
        ),
        (
            "ctp_account_query_smoke.py",
            "build_account_query_payload",
        ),
        (
            "ctp_position_query_smoke.py",
            "build_position_query_payload",
        ),
        (
            "ctp_td_order_truth_smoke.py",
            "build_td_order_truth_payload",
        ),
        (
            "ctp_td_historical_callback_boundary_smoke.py",
            "build_td_historical_callback_boundary_payload",
        ),
        (
            "ctp_md_startup_truth_smoke.py",
            "build_md_startup_truth_payload",
        ),
        (
            "ctp_md_login_smoke.py",
            "build_md_login_smoke_payload",
        ),
        (
            "ctp_td_login_smoke.py",
            "build_td_login_smoke_payload",
        ),
        (
            "ctp_marketdata_smoke.py",
            "build_marketdata_smoke_payload",
        ),
        (
            "ctp_live_data_client_bootstrap_smoke.py",
            "build_live_data_client_bootstrap_payload",
        ),
        (
            "ctp_nautilus_live_smoke.py",
            "build_nautilus_live_smoke_payload",
        ),
        (
            "ctp_order_trade_query_smoke.py",
            "build_order_trade_query_payload",
        ),
        (
            "ctp_repo_debug_smoke.py",
            "build_repo_debug_smoke_payload",
        ),
        (
            "ctp_order_lifecycle_smoke.py",
            "build_order_lifecycle_payload",
        ),
        (
            "ctp_nautilus_engine_harness.py",
            "build_nautilus_engine_harness_payload",
        ),
        (
            "ctp_p077_market_freshness_probe.py",
            "run_probe_with_watchdog",
        ),
        (
            "ctp_paper_session_preflight.py",
            "build_preflight_summary",
        ),
        (
            "ctp_paper_readonly_snapshot.py",
            "populate_connected_snapshot_payload",
        ),
        (
            "ctp_paper_recovery_idempotency.py",
            "build_reconnect_disposition",
        ),
        (
            "ctp_controlled_reconnect_harness.py",
            "build_controlled_reconnect_evidence",
        ),
        (
            "ctp_guarded_paper_cancel_loop.py",
            "build_native_cancel_login_failed_payload",
        ),
        (
            "ctp_guarded_paper_order_loop.py",
            "finalize_order_lifecycle_payload",
        ),
    ):
        text = (script_root / relative).read_text(encoding="utf-8")
        assert owner_function in text
        if relative == "ctp_p077_market_freshness_probe.py":
            assert "from nautilus_ctp_adapter.diagnostics.p077_market_freshness import" in text
            assert "def market_freshness_issues" not in text
            assert "def build_market_freshness_artifact" not in text
        if relative == "ctp_paper_session_preflight.py":
            assert "from nautilus_ctp_adapter.diagnostics.paper_session_preflight import" in text
            assert "def paper_config_issues" not in text
            assert "def build_preflight_summary" not in text
        if relative == "ctp_paper_readonly_snapshot.py":
            assert "from nautilus_ctp_adapter.diagnostics.paper_readonly_snapshot import" in text
            assert "def classify_positions_disposition" not in text
            assert "def classify_account_disposition" not in text
            assert "def position_contract_issues" not in text
            assert "def build_config_only_snapshot" not in text
        if relative == "ctp_paper_recovery_idempotency.py":
            assert "from nautilus_ctp_adapter.diagnostics.paper_recovery_idempotency import" in text
            assert "def classify_checkpoint_resume" not in text
            assert "def build_reconnect_disposition" not in text
            assert "def build_resource_blocker_payload" not in text
            assert "def classify_historical_residue" not in text
        if relative == "ctp_controlled_reconnect_harness.py":
            assert "from nautilus_ctp_adapter.diagnostics.paper_recovery_idempotency import" in text
            assert "def build_controlled_reconnect_evidence" not in text
        if relative == "ctp_guarded_paper_cancel_loop.py":
            assert "from nautilus_ctp_adapter.diagnostics.guarded_paper_cancel import" in text
            assert "def build_cancel_contract" not in text
            assert "def validate_cancel_command_contract" not in text
            assert "def classify_cancel_events" not in text
            assert "def _event_value" not in text
        if relative == "ctp_guarded_paper_order_loop.py":
            assert "from nautilus_ctp_adapter.diagnostics.guarded_paper_order import" in text
            assert "def build_callback_source_observability" not in text
            assert "def finalize_order_lifecycle_payload" not in text
            assert '"order_lifecycle_not_ready"' not in text
            assert '"armed_lifecycle_timeout"' not in text
        assert '"account_id_missing"' not in text
        assert '"account_balance_missing"' not in text
        assert '"account_incomplete"' not in text
        assert '"account_query_failed"' not in text
        assert '"account_query_timed_out"' not in text
        assert '"account_snapshot_incomplete"' not in text
        assert '"account_timed_out"' not in text
        assert '"account_missing"' not in text
        assert '"bootstrap_not_ready"' not in text
        assert '"bootstrap_not_started"' not in text
        assert '"connect_request_missing"' not in text
        assert '"config_invalid"' not in text
        assert '"config_missing"' not in text
        assert '"first_tick_missing"' not in text
        assert '"first_tick_stale"' not in text
        assert '"finding_count_missing"' not in text
        assert '"findings_missing"' not in text
        assert '"instrument_missing"' not in text
        assert '"instrument_query_incomplete"' not in text
        assert '"instrument_symbol_mismatch"' not in text
        assert '"instrument_not_loaded"' not in text
        assert '"internal_md_live_session_missing"' not in text
        assert '"isolated_bootstrap_not_ready"' not in text
        assert '"md_bootstrap_not_started"' not in text
        assert '"md_first_tick_missing"' not in text
        assert '"md_login_failed"' not in text
        assert '"md_subscribe_failed"' not in text
        assert '"login_failed"' not in text
        assert '"login_response_missing"' not in text
        assert '"merged_policy_manual_review_required"' not in text
        assert '"native_dll_missing"' not in text
        if relative != "ctp_guarded_paper_order_loop.py":
            assert '"paper_send_armed"' not in text
        assert '"order_trade_snapshot_manual_review_required"' not in text
        assert '"order_truth_manual_review_required"' not in text
        assert '"order_truth_account_missing"' not in text
        assert '"position_count_invalid"' not in text
        assert '"position_query_failed"' not in text
        assert '"position_query_timed_out"' not in text
        assert '"position_snapshot_incomplete"' not in text
        assert '"positions_incomplete"' not in text
        assert '"positions_query_failed"' not in text
        assert '"positions_timed_out"' not in text
        assert '"restore_not_succeeded"' not in text
        assert '"restore_not_triggered"' not in text
        assert '"restored_tick_missing"' not in text
        assert '"reconciliation_manual_review_required"' not in text
        assert '"query_not_ready"' not in text
        assert '"scaffold_contract_mismatch"' not in text
        assert '"script_only_smoke"' not in text
        assert '"settlement_not_confirmed"' not in text
        assert '"shared_bootstrap_not_ready"' not in text
        assert '"startup_not_ready"' not in text
        assert '"subscribe_failed"' not in text
        assert '"subscribe_requests_missing"' not in text
        assert '"symbol_missing"' not in text
        assert '"symbol_not_selected"' not in text
        assert '"td_login_failed"' not in text
        assert '"td_settlement_not_confirmed"' not in text
        assert '"unexpected_tick_symbol"' not in text
        assert '"unexpected_disposition"' not in text


def test_ctp_runtime_import_shim_delegates_native_bootstrap_to_owner() -> None:
    shim_text = (PROJECT_ROOT / "src" / "ctp_runtime" / "__init__.py").read_text(encoding="utf-8")
    owner_text = (
        PROJECT_ROOT
        / "src"
        / "nautilus_ctp_adapter"
        / "native"
        / "pyo3_runtime.py"
    ).read_text(encoding="utf-8")

    assert "bootstrap_pyo3_runtime_import" in shim_text
    for token in (
        "candidate_native_paths",
        "add_windows_dll_directories",
        "preload_runtime_vendor_dlls",
        "explicit_runtime_pack_bin_from_env",
        "runtime_pack_strict_from_env",
        "sys.platform",
    ):
        assert token not in shim_text

    assert "def bootstrap_pyo3_runtime_import" in owner_text
    assert "candidate_native_paths" in owner_text
    assert "preload_runtime_vendor_dlls" in owner_text
