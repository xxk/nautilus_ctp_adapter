"""Check architecture owner/truth/retirement governance boundaries."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

ADR_PATH = Path("docs/adr/ADR004 Adapter Governance Owner Truth Retirement Boundary.md")
ARCH_PATH = Path("docs/architecture/adapter-governance-owner-truth-retirement.md")
ADR_INDEX_PATH = Path("docs/adr/README.md")
ARCH_INDEX_PATH = Path("docs/architecture/README.md")
AGENTS_PATH = Path("AGENTS.md")
HARNESS_PATH = Path("scripts/check_harness.py")
DIAGNOSTICS_PAYLOADS_PATH = Path("src/nautilus_ctp_adapter/diagnostics/evidence_payloads.py")
P077_MARKET_FRESHNESS_OWNER_PATH = Path(
    "src/nautilus_ctp_adapter/diagnostics/p077_market_freshness.py"
)
PAPER_SESSION_PREFLIGHT_OWNER_PATH = Path(
    "src/nautilus_ctp_adapter/diagnostics/paper_session_preflight.py"
)
PAPER_READONLY_SNAPSHOT_OWNER_PATH = Path(
    "src/nautilus_ctp_adapter/diagnostics/paper_readonly_snapshot.py"
)
PAPER_RECOVERY_IDEMPOTENCY_OWNER_PATH = Path(
    "src/nautilus_ctp_adapter/diagnostics/paper_recovery_idempotency.py"
)
GUARDED_PAPER_CANCEL_OWNER_PATH = Path(
    "src/nautilus_ctp_adapter/diagnostics/guarded_paper_cancel.py"
)
GUARDED_PAPER_ORDER_OWNER_PATH = Path(
    "src/nautilus_ctp_adapter/diagnostics/guarded_paper_order.py"
)
CTP_RUNTIME_IMPORT_SHIM_PATH = Path("src/ctp_runtime/__init__.py")
PYO3_RUNTIME_OWNER_PATH = Path("src/nautilus_ctp_adapter/native/pyo3_runtime.py")
ADAPTER_DIAGNOSTICS_MODEL_SHIMS = (
    Path("src/nautilus_ctp_adapter/adapters/ctp/data_client.py"),
    Path("src/nautilus_ctp_adapter/adapters/ctp/execution_client.py"),
    Path("src/nautilus_ctp_adapter/adapters/ctp/startup_truth.py"),
    Path("src/nautilus_ctp_adapter/adapters/ctp/truth_merge.py"),
    Path("src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py"),
    Path("src/nautilus_ctp_adapter/adapters/ctp/ops_snapshot.py"),
)
RECONCILIATION_ADAPTER_PATH = Path("src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py")
RECONCILIATION_POLICY_OWNER_PATH = Path(
    "src/nautilus_ctp_adapter/diagnostics/reconciliation_policy.py"
)
LIVE_OPS_ADAPTER_PATH = Path("src/nautilus_ctp_adapter/adapters/ctp/ops_snapshot.py")
LIVE_OPS_POLICY_OWNER_PATH = Path("src/nautilus_ctp_adapter/diagnostics/live_ops_policy.py")
STARTUP_ADAPTER_PATH = Path("src/nautilus_ctp_adapter/adapters/ctp/startup_truth.py")
STARTUP_POLICY_OWNER_PATH = Path("src/nautilus_ctp_adapter/diagnostics/startup_policy.py")
TRUTH_MERGE_ADAPTER_PATH = Path("src/nautilus_ctp_adapter/adapters/ctp/truth_merge.py")
TRUTH_MERGE_POLICY_OWNER_PATH = Path("src/nautilus_ctp_adapter/diagnostics/truth_merge_policy.py")

REQUIRED_OWNER_IDS = (
    "runtime_core",
    "native_loader",
    "nautilus_adapter_glue",
    "diagnostics",
    "cli_wrappers",
    "governance",
)

REQUIRED_TRUTH_IDS = (
    "runtime_behavior_truth",
    "native_loading_truth",
    "adapter_stack_truth",
    "formal_live_verdict_truth",
    "governance_truth",
    "evidence_artifact_truth",
)

REQUIRED_MARKERS = (
    "<!-- ARCH-GOV:OWNER-REGISTRY:v1 -->",
    "<!-- ARCH-GOV:TRUTH-SOURCE-MATRIX:v1 -->",
    "<!-- ARCH-GOV:FORK-PREVENTION:v1 -->",
    "<!-- ARCH-GOV:RETIREMENT-LEDGER:v1 -->",
)

REQUIRED_LEGACY_PATHS = (
    "src/nautilus_ctp_adapter/adapters/ctp/data_client.py",
    "src/nautilus_ctp_adapter/adapters/ctp/execution_client.py",
    "scripts/ctp_*.py",
    "src/ctp_runtime/__init__.py",
)
REQUIRED_RETIREMENT_STATUS = "guarded_transitional"

SCRIPT_PAYLOAD_OWNER_GUARDS = (
    (
        Path("scripts/ctp_md_truth_evidence_matrix_smoke.py"),
        "build_md_truth_evidence_matrix_payload",
    ),
    (
        Path("scripts/ctp_td_order_truth_evidence_matrix_smoke.py"),
        "build_td_order_truth_evidence_matrix_payload",
    ),
    (
        Path("scripts/ctp_startup_truth_evidence_matrix_smoke.py"),
        "build_startup_truth_evidence_matrix_payload",
    ),
    (
        Path("scripts/ctp_td_merged_evidence_matrix_smoke.py"),
        "build_td_merged_evidence_matrix_payload",
    ),
    (
        Path("scripts/ctp_live_ops_snapshot_smoke.py"),
        "build_live_ops_snapshot_payload",
    ),
    (
        Path("scripts/ctp_live_ops_policy_smoke.py"),
        "build_live_ops_policy_payload",
    ),
    (
        Path("scripts/ctp_live_ops_evidence_matrix_smoke.py"),
        "build_live_ops_evidence_matrix_payload",
    ),
    (
        Path("scripts/ctp_reconciliation_snapshot_smoke.py"),
        "build_reconciliation_snapshot_payload",
    ),
    (
        Path("scripts/ctp_reconciliation_policy_smoke.py"),
        "build_reconciliation_policy_payload",
    ),
    (
        Path("scripts/ctp_reconciliation_evidence_smoke.py"),
        "build_reconciliation_evidence_payload",
    ),
    (
        Path("scripts/ctp_startup_truth_smoke.py"),
        "build_td_startup_truth_payload",
    ),
    (
        Path("scripts/ctp_session_rebuild_policy_smoke.py"),
        "build_session_rebuild_policy_payload",
    ),
    (
        Path("scripts/ctp_md_restore_policy_smoke.py"),
        "build_md_restore_policy_payload",
    ),
    (
        Path("scripts/ctp_td_truth_merge_snapshot_smoke.py"),
        "build_td_truth_merge_snapshot_payload",
    ),
    (
        Path("scripts/ctp_td_merged_reconciliation_policy_smoke.py"),
        "build_td_merged_reconciliation_policy_payload",
    ),
    (
        Path("scripts/ctp_query_adapter_smoke.py"),
        "build_query_adapter_payload",
    ),
    (
        Path("scripts/ctp_instrument_query_smoke.py"),
        "build_instrument_query_payload",
    ),
    (
        Path("scripts/ctp_account_query_smoke.py"),
        "build_account_query_payload",
    ),
    (
        Path("scripts/ctp_position_query_smoke.py"),
        "build_position_query_payload",
    ),
    (
        Path("scripts/ctp_td_order_truth_smoke.py"),
        "build_td_order_truth_payload",
    ),
    (
        Path("scripts/ctp_td_historical_callback_boundary_smoke.py"),
        "build_td_historical_callback_boundary_payload",
    ),
    (
        Path("scripts/ctp_md_startup_truth_smoke.py"),
        "build_md_startup_truth_payload",
    ),
    (
        Path("scripts/ctp_md_login_smoke.py"),
        "build_md_login_smoke_payload",
    ),
    (
        Path("scripts/ctp_td_login_smoke.py"),
        "build_td_login_smoke_payload",
    ),
    (
        Path("scripts/ctp_marketdata_smoke.py"),
        "build_marketdata_smoke_payload",
    ),
    (
        Path("scripts/ctp_live_data_client_bootstrap_smoke.py"),
        "build_live_data_client_bootstrap_payload",
    ),
    (
        Path("scripts/ctp_nautilus_live_smoke.py"),
        "build_nautilus_live_smoke_payload",
    ),
    (
        Path("scripts/ctp_order_trade_query_smoke.py"),
        "build_order_trade_query_payload",
    ),
    (
        Path("scripts/ctp_repo_debug_smoke.py"),
        "build_repo_debug_smoke_payload",
    ),
    (
        Path("scripts/ctp_order_lifecycle_smoke.py"),
        "build_order_lifecycle_payload",
    ),
    (
        Path("scripts/ctp_nautilus_engine_harness.py"),
        "build_nautilus_engine_harness_payload",
    ),
    (
        Path("scripts/ctp_p077_market_freshness_probe.py"),
        "run_probe_with_watchdog",
    ),
    (
        Path("scripts/ctp_paper_session_preflight.py"),
        "build_preflight_summary",
    ),
    (
        Path("scripts/ctp_paper_readonly_snapshot.py"),
        "populate_connected_snapshot_payload",
    ),
    (
        Path("scripts/ctp_paper_recovery_idempotency.py"),
        "build_reconnect_disposition",
    ),
    (
        Path("scripts/ctp_controlled_reconnect_harness.py"),
        "build_controlled_reconnect_evidence",
    ),
    (
        Path("scripts/ctp_guarded_paper_cancel_loop.py"),
        "build_native_cancel_login_failed_payload",
    ),
    (
        Path("scripts/ctp_guarded_paper_order_loop.py"),
        "finalize_order_lifecycle_payload",
    ),
)

FORBIDDEN_SCRIPT_PAYLOAD_TOKENS = (
    '"account_id_missing"',
    '"account_balance_missing"',
    '"account_incomplete"',
    '"account_query_failed"',
    '"account_query_timed_out"',
    '"account_snapshot_incomplete"',
    '"account_timed_out"',
    '"account_missing"',
    '"bootstrap_not_ready"',
    '"bootstrap_not_started"',
    '"connect_request_missing"',
    '"config_invalid"',
    '"config_missing"',
    '"first_tick_missing"',
    '"first_tick_stale"',
    '"finding_count_missing"',
    '"findings_missing"',
    '"instrument_missing"',
    '"instrument_query_incomplete"',
    '"instrument_symbol_mismatch"',
    '"instrument_not_loaded"',
    '"internal_md_live_session_missing"',
    '"isolated_bootstrap_not_ready"',
    '"md_bootstrap_not_started"',
    '"md_first_tick_missing"',
    '"md_login_failed"',
    '"md_subscribe_failed"',
    '"login_failed"',
    '"login_response_missing"',
    '"merged_policy_manual_review_required"',
    '"native_dll_missing"',
    '"paper_send_armed"',
    '"order_trade_snapshot_manual_review_required"',
    '"order_truth_manual_review_required"',
    '"order_truth_account_missing"',
    '"position_count_invalid"',
    '"position_query_failed"',
    '"position_query_timed_out"',
    '"position_snapshot_incomplete"',
    '"positions_incomplete"',
    '"positions_query_failed"',
    '"positions_timed_out"',
    '"restore_not_succeeded"',
    '"restore_not_triggered"',
    '"restored_tick_missing"',
    '"reconciliation_manual_review_required"',
    '"query_not_ready"',
    '"scaffold_contract_mismatch"',
    '"script_only_smoke"',
    '"settlement_not_confirmed"',
    '"shared_bootstrap_not_ready"',
    '"startup_not_ready"',
    '"subscribe_failed"',
    '"subscribe_requests_missing"',
    '"symbol_missing"',
    '"symbol_not_selected"',
    '"td_login_failed"',
    '"td_settlement_not_confirmed"',
    '"unexpected_tick_symbol"',
    '"unexpected_disposition"',
)

FORBIDDEN_CTP_RUNTIME_SHIM_TOKENS = (
    "candidate_native_paths",
    "add_windows_dll_directories",
    "preload_runtime_vendor_dlls",
    "explicit_runtime_pack_bin_from_env",
    "runtime_pack_strict_from_env",
    "sys.platform",
)


def _read(root: Path, relative: Path) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _require_file(root: Path, relative: Path, errors: list[str]) -> str:
    path = root / relative
    if not path.exists():
        errors.append(f"{relative.as_posix()} does not exist")
        return ""
    return path.read_text(encoding="utf-8")


def _extract_table_rows(text: str, marker: str) -> list[str]:
    marker_index = text.find(marker)
    if marker_index < 0:
        return []
    tail = text[marker_index:].splitlines()[1:]
    rows: list[str] = []
    for line in tail:
        stripped = line.strip()
        if not stripped:
            if rows:
                break
            continue
        if stripped.startswith("## "):
            break
        if stripped.startswith("|"):
            rows.append(stripped)
    return rows


def _validate_table_contains(
    *,
    text: str,
    marker: str,
    required_values: tuple[str, ...],
    label: str,
    errors: list[str],
) -> None:
    rows = _extract_table_rows(text, marker)
    if len(rows) < 3:
        errors.append(f"{label} table under {marker} is missing or empty")
        return
    table_text = "\n".join(rows)
    for value in required_values:
        if value not in table_text:
            errors.append(f"{label} table missing `{value}`")


def _validate_retirement_rows(text: str, errors: list[str]) -> None:
    rows = _extract_table_rows(text, "<!-- ARCH-GOV:RETIREMENT-LEDGER:v1 -->")
    table_text = "\n".join(rows)
    for legacy_path in REQUIRED_LEGACY_PATHS:
        if legacy_path not in table_text:
            errors.append(f"retirement ledger missing `{legacy_path}`")

    data_rows = [
        row
        for row in rows
        if row.startswith("| `") and "---" not in row
    ]
    for row in data_rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) < 7:
            errors.append(f"retirement ledger row is malformed: {row}")
            continue
        legacy_path, _current_role, successor_owner, retirement_action, _compat, retirement_gate, status = cells[:7]
        for field_name, value in (
            ("legacy_path", legacy_path),
            ("successor_owner", successor_owner),
            ("retirement_action", retirement_action),
            ("retirement_gate", retirement_gate),
            ("status", status),
        ):
            if not value or value in {"`planned`", "planned"} and field_name != "status":
                errors.append(f"retirement ledger row for {legacy_path} has weak `{field_name}`")
        if "focused pytest" not in retirement_gate and "test" not in retirement_gate.lower():
            errors.append(f"retirement ledger row for {legacy_path} lacks executable test/gate wording")
        if REQUIRED_RETIREMENT_STATUS not in status:
            errors.append(
                f"retirement ledger row for {legacy_path} must record `{REQUIRED_RETIREMENT_STATUS}`"
            )


def _validate_script_payload_owner(root: Path, errors: list[str]) -> None:
    payload_owner_text = _require_file(root, DIAGNOSTICS_PAYLOADS_PATH, errors)
    p077_owner_text = _require_file(root, P077_MARKET_FRESHNESS_OWNER_PATH, errors)
    paper_preflight_owner_text = _require_file(root, PAPER_SESSION_PREFLIGHT_OWNER_PATH, errors)
    paper_readonly_owner_text = _require_file(root, PAPER_READONLY_SNAPSHOT_OWNER_PATH, errors)
    paper_recovery_owner_text = _require_file(root, PAPER_RECOVERY_IDEMPOTENCY_OWNER_PATH, errors)
    guarded_cancel_owner_text = _require_file(root, GUARDED_PAPER_CANCEL_OWNER_PATH, errors)
    guarded_order_owner_text = _require_file(root, GUARDED_PAPER_ORDER_OWNER_PATH, errors)
    if payload_owner_text:
        for token in (
            "classify_md_truth_evidence_matrix_failure",
            "classify_td_order_truth_evidence_matrix_failure",
            "classify_startup_truth_evidence_matrix_failure",
            "classify_td_merged_evidence_matrix_failure",
            "classify_live_ops_summary_failure",
            "classify_live_ops_evidence_matrix_failure",
            "classify_reconciliation_snapshot_failure",
            "classify_reconciliation_policy_failure",
            "classify_reconciliation_evidence_failure",
            "classify_td_startup_truth_failure",
            "classify_session_rebuild_policy_failure",
            "classify_md_restore_policy_failure",
            "classify_td_truth_merge_snapshot_failure",
            "classify_td_merged_reconciliation_policy_failure",
            "classify_query_adapter_failure",
            "classify_instrument_query_failure",
            "classify_account_query_failure",
            "classify_position_query_failure",
            "classify_td_order_truth_failure",
            "classify_td_historical_callback_boundary_failure",
            "classify_md_startup_truth_failure",
            "classify_md_login_smoke_failure",
            "classify_td_login_smoke_failure",
            "classify_marketdata_smoke_failure",
            "classify_live_data_client_bootstrap_failure",
            "classify_nautilus_live_smoke_failure",
            "classify_order_trade_query_failure",
            "classify_order_lifecycle_success",
            "classify_nautilus_engine_harness_success",
            "build_order_trade_query_failure_payload",
        ):
            if token not in payload_owner_text:
                errors.append(f"{DIAGNOSTICS_PAYLOADS_PATH.as_posix()} missing `{token}`")
    if p077_owner_text:
        for token in (
            "def build_market_freshness_artifact",
            "def build_typed_blocker_artifact",
            "def market_freshness_issues",
            "def run_probe_with_watchdog",
            "FORBIDDEN_TRUTH_SOURCES",
        ):
            if token not in p077_owner_text:
                errors.append(f"{P077_MARKET_FRESHNESS_OWNER_PATH.as_posix()} missing `{token}`")
    if paper_preflight_owner_text:
        for token in (
            "def build_preflight_summary",
            "def paper_config_issues",
            "def redacted_config_summary",
            "OPENCTP_TTS_7X24_PROFILE",
        ):
            if token not in paper_preflight_owner_text:
                errors.append(f"{PAPER_SESSION_PREFLIGHT_OWNER_PATH.as_posix()} missing `{token}`")
    if paper_readonly_owner_text:
        for token in (
            "def build_config_only_snapshot",
            "def populate_connected_snapshot_payload",
            "def classify_positions_disposition",
            "def classify_account_disposition",
            "OPENCTP_TTS_7X24_PROFILE",
        ):
            if token not in paper_readonly_owner_text:
                errors.append(f"{PAPER_READONLY_SNAPSHOT_OWNER_PATH.as_posix()} missing `{token}`")
    if paper_recovery_owner_text:
        for token in (
            "def classify_checkpoint_resume",
            "def build_reconnect_disposition",
            "def build_controlled_reconnect_evidence",
            "def build_resource_blocker_payload",
            "def classify_historical_residue",
            "OPENCTP_TTS_7X24_PROFILE",
        ):
            if token not in paper_recovery_owner_text:
                errors.append(f"{PAPER_RECOVERY_IDEMPOTENCY_OWNER_PATH.as_posix()} missing `{token}`")
    if guarded_cancel_owner_text:
        for token in (
            "def build_cancel_contract",
            "def validate_cancel_command_contract",
            "def classify_cancel_events",
            "def build_native_cancel_login_failed_payload",
            "def build_native_cancel_action_payload",
        ):
            if token not in guarded_cancel_owner_text:
                errors.append(f"{GUARDED_PAPER_CANCEL_OWNER_PATH.as_posix()} missing `{token}`")
    if guarded_order_owner_text:
        for token in (
            "def build_callback_source_observability",
            "def finalize_order_lifecycle_payload",
        ):
            if token not in guarded_order_owner_text:
                errors.append(f"{GUARDED_PAPER_ORDER_OWNER_PATH.as_posix()} missing `{token}`")

    for script_path, builder_name in SCRIPT_PAYLOAD_OWNER_GUARDS:
        script_text = _require_file(root, script_path, errors)
        if not script_text:
            continue
        if builder_name not in script_text:
            errors.append(f"{script_path.as_posix()} does not delegate payload shape to `{builder_name}`")
        if script_path == Path("scripts/ctp_p077_market_freshness_probe.py"):
            if "from nautilus_ctp_adapter.diagnostics.p077_market_freshness import" not in script_text:
                errors.append(
                    "scripts/ctp_p077_market_freshness_probe.py must re-export from "
                    "diagnostics.p077_market_freshness"
                )
            for forbidden in ("def market_freshness_issues", "def build_market_freshness_artifact"):
                if forbidden in script_text:
                    errors.append(
                        "scripts/ctp_p077_market_freshness_probe.py still owns P077 market freshness logic"
                    )
        if script_path == Path("scripts/ctp_paper_session_preflight.py"):
            if "from nautilus_ctp_adapter.diagnostics.paper_session_preflight import" not in script_text:
                errors.append(
                    "scripts/ctp_paper_session_preflight.py must re-export from "
                    "diagnostics.paper_session_preflight"
                )
            for forbidden in ("def paper_config_issues", "def build_preflight_summary"):
                if forbidden in script_text:
                    errors.append(
                        "scripts/ctp_paper_session_preflight.py still owns paper preflight logic"
                    )
        if script_path == Path("scripts/ctp_paper_readonly_snapshot.py"):
            if "from nautilus_ctp_adapter.diagnostics.paper_readonly_snapshot import" not in script_text:
                errors.append(
                    "scripts/ctp_paper_readonly_snapshot.py must delegate to "
                    "diagnostics.paper_readonly_snapshot"
                )
            for forbidden in (
                "def classify_positions_disposition",
                "def classify_account_disposition",
                "def position_contract_issues",
                "def build_config_only_snapshot",
            ):
                if forbidden in script_text:
                    errors.append(
                        "scripts/ctp_paper_readonly_snapshot.py still owns paper readonly snapshot logic"
                    )
        if script_path == Path("scripts/ctp_paper_recovery_idempotency.py"):
            if "from nautilus_ctp_adapter.diagnostics.paper_recovery_idempotency import" not in script_text:
                errors.append(
                    "scripts/ctp_paper_recovery_idempotency.py must delegate to "
                    "diagnostics.paper_recovery_idempotency"
                )
            for forbidden in (
                "def classify_checkpoint_resume",
                "def build_reconnect_disposition",
                "def build_resource_blocker_payload",
                "def classify_historical_residue",
            ):
                if forbidden in script_text:
                    errors.append(
                        "scripts/ctp_paper_recovery_idempotency.py still owns paper recovery logic"
                    )
        if script_path == Path("scripts/ctp_controlled_reconnect_harness.py"):
            if "from nautilus_ctp_adapter.diagnostics.paper_recovery_idempotency import" not in script_text:
                errors.append(
                    "scripts/ctp_controlled_reconnect_harness.py must delegate to "
                    "diagnostics.paper_recovery_idempotency"
                )
            if "def build_controlled_reconnect_evidence" in script_text:
                errors.append(
                    "scripts/ctp_controlled_reconnect_harness.py still owns controlled reconnect evidence logic"
                )
        if script_path == Path("scripts/ctp_guarded_paper_cancel_loop.py"):
            if "from nautilus_ctp_adapter.diagnostics.guarded_paper_cancel import" not in script_text:
                errors.append(
                    "scripts/ctp_guarded_paper_cancel_loop.py must delegate to "
                    "diagnostics.guarded_paper_cancel"
                )
            for forbidden in (
                "def build_cancel_contract",
                "def validate_cancel_command_contract",
                "def classify_cancel_events",
                "def _event_value",
            ):
                if forbidden in script_text:
                    errors.append(
                        "scripts/ctp_guarded_paper_cancel_loop.py still owns guarded cancel verdict logic"
                    )
        if script_path == Path("scripts/ctp_guarded_paper_order_loop.py"):
            if "from nautilus_ctp_adapter.diagnostics.guarded_paper_order import" not in script_text:
                errors.append(
                    "scripts/ctp_guarded_paper_order_loop.py must delegate to "
                    "diagnostics.guarded_paper_order"
                )
            for forbidden in (
                "def build_callback_source_observability",
                "def finalize_order_lifecycle_payload",
                '"order_lifecycle_not_ready"',
                '"armed_lifecycle_timeout"',
            ):
                if forbidden in script_text:
                    errors.append(
                        "scripts/ctp_guarded_paper_order_loop.py still owns guarded order lifecycle verdict logic"
                    )
        for token in FORBIDDEN_SCRIPT_PAYLOAD_TOKENS:
            if script_path == Path("scripts/ctp_guarded_paper_order_loop.py") and token == '"paper_send_armed"':
                continue
            if token in script_text:
                errors.append(
                    f"{script_path.as_posix()} still owns evidence failure token {token}; "
                    "move it to diagnostics/evidence_payloads.py"
                )


def _validate_native_bootstrap_owner(root: Path, errors: list[str]) -> None:
    shim_text = _require_file(root, CTP_RUNTIME_IMPORT_SHIM_PATH, errors)
    owner_text = _require_file(root, PYO3_RUNTIME_OWNER_PATH, errors)
    if shim_text:
        if "bootstrap_pyo3_runtime_import" not in shim_text:
            errors.append(
                f"{CTP_RUNTIME_IMPORT_SHIM_PATH.as_posix()} must delegate to "
                "native.pyo3_runtime.bootstrap_pyo3_runtime_import"
            )
        for token in FORBIDDEN_CTP_RUNTIME_SHIM_TOKENS:
            if token in shim_text:
                errors.append(
                    f"{CTP_RUNTIME_IMPORT_SHIM_PATH.as_posix()} still owns native loader token `{token}`"
                )
    if owner_text:
        for token in (
            "def bootstrap_pyo3_runtime_import",
            "candidate_native_paths",
            "preload_runtime_vendor_dlls",
        ):
            if token not in owner_text:
                errors.append(f"{PYO3_RUNTIME_OWNER_PATH.as_posix()} missing `{token}`")


def _validate_adapter_model_shims(root: Path, errors: list[str]) -> None:
    for path in ADAPTER_DIAGNOSTICS_MODEL_SHIMS:
        text = _require_file(root, path, errors)
        if not text:
            continue
        for token in ("from dataclasses import dataclass", "@dataclass"):
            if token in text:
                errors.append(
                    f"{path.as_posix()} still declares diagnostics dataclasses; "
                    "move model ownership to nautilus_ctp_adapter.diagnostics"
                )


def _validate_reconciliation_policy_owner(root: Path, errors: list[str]) -> None:
    adapter_text = _require_file(root, RECONCILIATION_ADAPTER_PATH, errors)
    owner_text = _require_file(root, RECONCILIATION_POLICY_OWNER_PATH, errors)
    if adapter_text:
        if "from nautilus_ctp_adapter.diagnostics import reconciliation_policy" not in adapter_text:
            errors.append(
                f"{RECONCILIATION_ADAPTER_PATH.as_posix()} must delegate policy/evidence shaping "
                "to diagnostics.reconciliation_policy"
            )
        for token in (
            "def _build_exposures",
            "def build_reconciliation_exposures",
            "def evaluate_reconciliation_summary",
            "def build_reconciliation_evidence",
        ):
            if token in adapter_text:
                errors.append(
                    f"{RECONCILIATION_ADAPTER_PATH.as_posix()} still owns reconciliation policy token `{token}`"
                )
    if owner_text:
        for token in (
            "def build_reconciliation_exposures",
            "def summarize_reconciliation_snapshot",
            "def evaluate_reconciliation_summary",
            "def build_reconciliation_evidence",
        ):
            if token not in owner_text:
                errors.append(f"{RECONCILIATION_POLICY_OWNER_PATH.as_posix()} missing `{token}`")


def _validate_live_ops_policy_owner(root: Path, errors: list[str]) -> None:
    adapter_text = _require_file(root, LIVE_OPS_ADAPTER_PATH, errors)
    owner_text = _require_file(root, LIVE_OPS_POLICY_OWNER_PATH, errors)
    if adapter_text:
        if "from nautilus_ctp_adapter.diagnostics import live_ops_policy" not in adapter_text:
            errors.append(
                f"{LIVE_OPS_ADAPTER_PATH.as_posix()} must delegate policy/evidence shaping "
                "to diagnostics.live_ops_policy"
            )
        for token in (
            "CtpLiveOpsPolicyFinding(",
            "code=\"missing_account_identity\"",
            "code=\"manual_review_codes_present\"",
            "evidence_version=\"live-ops-evidence-v1\"",
        ):
            if token in adapter_text:
                errors.append(
                    f"{LIVE_OPS_ADAPTER_PATH.as_posix()} still owns live-ops policy token `{token}`"
                )
    if owner_text:
        for token in (
            "def summarize_live_ops_snapshot",
            "def evaluate_live_ops_summary",
            "def build_live_ops_evidence_matrix",
            "CtpLiveOpsPolicyFinding(",
            "evidence_version=\"live-ops-evidence-v1\"",
        ):
            if token not in owner_text:
                errors.append(f"{LIVE_OPS_POLICY_OWNER_PATH.as_posix()} missing `{token}`")


def _validate_startup_policy_owner(root: Path, errors: list[str]) -> None:
    adapter_text = _require_file(root, STARTUP_ADAPTER_PATH, errors)
    owner_text = _require_file(root, STARTUP_POLICY_OWNER_PATH, errors)
    if adapter_text:
        if "from nautilus_ctp_adapter.diagnostics import startup_policy" not in adapter_text:
            errors.append(
                f"{STARTUP_ADAPTER_PATH.as_posix()} must delegate policy/evidence shaping "
                "to diagnostics.startup_policy"
            )
        for token in (
            "CtpSessionRebuildFinding(",
            "code=\"shared_startup_truth_unready\"",
            "code=\"shared_flow_requires_isolated_rebuild\"",
            "evidence_version=\"startup-truth-evidence-v1\"",
        ):
            if token in adapter_text:
                errors.append(
                    f"{STARTUP_ADAPTER_PATH.as_posix()} still owns startup policy token `{token}`"
                )
    if owner_text:
        for token in (
            "def evaluate_session_rebuild_policy",
            "def build_startup_truth_evidence_matrix",
            "CtpSessionRebuildFinding(",
            "evidence_version=\"startup-truth-evidence-v1\"",
        ):
            if token not in owner_text:
                errors.append(f"{STARTUP_POLICY_OWNER_PATH.as_posix()} missing `{token}`")


def _validate_truth_merge_policy_owner(root: Path, errors: list[str]) -> None:
    adapter_text = _require_file(root, TRUTH_MERGE_ADAPTER_PATH, errors)
    owner_text = _require_file(root, TRUTH_MERGE_POLICY_OWNER_PATH, errors)
    if adapter_text:
        if "from nautilus_ctp_adapter.diagnostics import truth_merge_policy" not in adapter_text:
            errors.append(
                f"{TRUTH_MERGE_ADAPTER_PATH.as_posix()} must delegate policy/evidence shaping "
                "to diagnostics.truth_merge_policy"
            )
        for token in (
            "CtpTdMergedReconciliationFinding(",
            "code=\"missing_account_snapshot\"",
            "code=\"historical_callbacks_present\"",
            "evidence_version=\"td-merged-evidence-v1\"",
        ):
            if token in adapter_text:
                errors.append(
                    f"{TRUTH_MERGE_ADAPTER_PATH.as_posix()} still owns truth-merge policy token `{token}`"
                )
    if owner_text:
        for token in (
            "def evaluate_merged_reconciliation_policy",
            "def build_td_merged_evidence_matrix",
            "CtpTdMergedReconciliationFinding(",
            "evidence_version=\"td-merged-evidence-v1\"",
        ):
            if token not in owner_text:
                errors.append(f"{TRUTH_MERGE_POLICY_OWNER_PATH.as_posix()} missing `{token}`")


def validate_architecture_governance(root: Path) -> list[str]:
    errors: list[str] = []
    adr_text = _require_file(root, ADR_PATH, errors)
    arch_text = _require_file(root, ARCH_PATH, errors)
    adr_index_text = _require_file(root, ADR_INDEX_PATH, errors)
    arch_index_text = _require_file(root, ARCH_INDEX_PATH, errors)
    agents_text = _require_file(root, AGENTS_PATH, errors)
    harness_text = _require_file(root, HARNESS_PATH, errors)

    if adr_text:
        for token in (
            "adr_id: \"ADR004\"",
            "decision_status: accepted",
            "Owner / Canonical Entry Impact",
            "Design Kernel / 设计内核",
            "Decision Coverage And Landing Matrix",
            "ADR-Level Acceptance Only",
            "Successor Change Boundary",
            "ADR Closeout Distillation",
            "retirement 4/4 guarded_transitional",
        ):
            if token not in adr_text:
                errors.append(f"{ADR_PATH.as_posix()} missing `{token}`")

    if "ADR004" not in adr_index_text:
        errors.append("docs/adr/README.md does not reference ADR004")
    if "adapter-governance-owner-truth-retirement.md" not in arch_index_text:
        errors.append("docs/architecture/README.md does not reference adapter governance boundary")
    if "python scripts/check_architecture_governance.py" not in agents_text:
        errors.append("AGENTS.md missing architecture governance verify command")
    if "validate_architecture_governance" not in harness_text:
        errors.append("scripts/check_harness.py does not aggregate architecture governance gate")

    if arch_text:
        for marker in REQUIRED_MARKERS:
            if marker not in arch_text:
                errors.append(f"{ARCH_PATH.as_posix()} missing marker {marker}")
        _validate_table_contains(
            text=arch_text,
            marker="<!-- ARCH-GOV:OWNER-REGISTRY:v1 -->",
            required_values=REQUIRED_OWNER_IDS,
            label="owner registry",
            errors=errors,
        )
        _validate_table_contains(
            text=arch_text,
            marker="<!-- ARCH-GOV:TRUTH-SOURCE-MATRIX:v1 -->",
            required_values=REQUIRED_TRUTH_IDS,
            label="truth-source matrix",
            errors=errors,
        )
        _validate_retirement_rows(arch_text, errors)
        if re.search(r"chat-only|stdout-only|second runtime|second native loader", arch_text, re.IGNORECASE) is None:
            errors.append("architecture governance doc lacks anti-fork / weak-evidence red-line wording")

    _validate_script_payload_owner(root, errors)
    _validate_native_bootstrap_owner(root, errors)
    _validate_adapter_model_shims(root, errors)
    _validate_reconciliation_policy_owner(root, errors)
    _validate_live_ops_policy_owner(root, errors)
    _validate_startup_policy_owner(root, errors)
    _validate_truth_merge_policy_owner(root, errors)

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="check_architecture_governance")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_architecture_governance(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ARCH_GOV_FAILED: {error}")
        print(f"ARCH_GOV_CHECK_FAIL: {len(errors)} issues")
        return 1
    print("ARCH_GOV_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
