# Scripts

Put smoke tests, local diagnostics, and one-off bootstrap helpers here.

Current planned entrypoints:

1. `python scripts/sync_ctp_native.py`
2. `python scripts/ctp_md_login_smoke.py --config <path>`
3. `python scripts/ctp_td_login_smoke.py --config <path>`
4. `python scripts/ctp_nautilus_live_smoke.py --config <path>`
5. `python scripts/ctp_instrument_query_smoke.py --config <path> --symbol <symbol>`
6. `python scripts/ctp_live_data_client_bootstrap_smoke.py --config <path> --symbol <symbol>`
7. `python scripts/ctp_marketdata_smoke.py --config <path> --symbol <symbol>`
8. `python scripts/ctp_order_lifecycle_smoke.py --config <path> --instrument c2609 --quantity 1 --limit-price <price>`
9. `python scripts/check_topic_docs.py`
10. `python scripts/check_rust_gate.py`
10a. `python scripts/check_runtime_performance_gate.py --events 5000 --limit 1000 --min-events-per-sec 1000`
11. `python scripts/ctp_reconciliation_snapshot_smoke.py --config <path>`
12. `python scripts/ctp_reconciliation_policy_smoke.py --config <path>`
13. `python scripts/ctp_reconciliation_evidence_smoke.py --config <path>`
14. `python scripts/ctp_startup_truth_smoke.py --config <path>`
15. `python scripts/ctp_session_rebuild_policy_smoke.py --config <path>`
16. `python scripts/ctp_startup_truth_evidence_matrix_smoke.py --config <path>`
17. `python scripts/ctp_md_startup_truth_smoke.py --config <path>`
18. `python scripts/ctp_md_restore_policy_smoke.py --config <path>`
19. `python scripts/ctp_md_truth_evidence_matrix_smoke.py --config <path>`
20. `python scripts/ctp_td_order_truth_smoke.py --config <path>`
21. `python scripts/ctp_td_historical_callback_boundary_smoke.py --config <path>`
22. `python scripts/ctp_td_order_truth_evidence_matrix_smoke.py --config <path>`
23. `python scripts/ctp_td_truth_merge_snapshot_smoke.py --config <path>`
24. `python scripts/ctp_td_merged_reconciliation_policy_smoke.py --config <path>`
25. `python scripts/ctp_td_merged_evidence_matrix_smoke.py --config <path>`
26. `python scripts/ctp_live_ops_snapshot_smoke.py --config <path>`
27. `python scripts/ctp_live_ops_policy_smoke.py --config <path>`
28. `python scripts/ctp_live_ops_evidence_matrix_smoke.py --config <path>`

Offhours query aggregation note:

1. `python scripts/ctp_query_adapter_smoke.py --config <path> --include-reconciliation` now aggregates `position / account / reconciliation` in one read-only run.
2. Add `--include-order-truth` when the same offhours run also needs historical callback boundary truth.
3. Add `--include-order-trade-snapshot` when the same offhours run also needs a separate read-only `ORDER / TRADE` snapshot summary instead of only callback-boundary policy.
4. Add `--include-merged-policy` when the same offhours run also needs merged truth/reconciliation disposition from `truth_merge_adapter`.
5. Add `--instrument-symbol <symbol>` when the same offhours run also needs instrument lookup.
6. Add `--flow-path <dir>` when the same offhours run must force all optional lanes onto one shared TD flow path.
7. Add `--session-label <label>` when the same offhours run should stamp one human-readable session name into payload and evidence naming.
8. Add `--evidence-root output/debug/<subdir>` when the same run should auto-write evidence to `<evidence-root>/<session-label>/aggregated_query.json` without hardcoding a full file path.
9. Add `--output-json output/debug/<subdir>/aggregated_query.json` when the same run should emit reusable evidence to one explicit file path instead of session-root naming.
10. `--output-json` and `--evidence-root` are mutually exclusive because they describe two different export-target modes.
11. If `--session-label` is omitted, the current default is stable and predictable: `shared-flow` for default shared flow, `isolated-flow` for explicit `--flow-path` runs.
12. `order_truth_manual_review_required` means the extra order-truth lane did not reach a trustworthy read-only baseline, even if position/account snapshots themselves completed.
13. `order_trade_snapshot_manual_review_required` means the separate `ORDER / TRADE` snapshot lane could not be trusted as a read-only summary.
14. The order/trade snapshot lane now freezes `no_order_events / no_trade_events / historical_residue_*` semantics without implying that offhours code should send live orders.
15. `reconciliation_manual_review_required` means the shared query snapshot completed, but the reconciliation lane still requires operator review.
16. `merged_policy_manual_review_required` means the merged truth/reconciliation lane still requires operator review, even though the base query snapshot itself completed.

Offhours evidence naming note:

1. `ctp_query_adapter_smoke.py` now supports `--session-label`, `--evidence-root`, and `--output-json` as the canonical offhours export surface.
2. `ctp_instrument_query_smoke.py`, `ctp_position_query_smoke.py`, and `ctp_account_query_smoke.py` now reuse the same naming/export contract, and each also accepts `--flow-path` so isolated-flow leaf evidence can land under the same session namespace as the aggregate entrypoints.
3. `ctp_reconciliation_snapshot_smoke.py` now supports the same `--session-label`, `--evidence-root`, and `--output-json` contract for snapshot-only runs.
4. `ctp_td_truth_merge_snapshot_smoke.py` now supports the same naming/export contract, and combines it with `--flow-path` so isolated TD flow sessions can still produce stable evidence paths.
5. `ctp_reconciliation_policy_smoke.py` and `ctp_reconciliation_evidence_smoke.py` now reuse the same `--session-label`, `--evidence-root`, and `--output-json` surface for reconciliation-only policy/evidence runs.
6. `ctp_td_merged_reconciliation_policy_smoke.py` and `ctp_td_merged_evidence_matrix_smoke.py` now reuse the same naming/export contract, and combine it with `--flow-path` so merged TD truth sessions can still emit stable isolated-flow evidence paths.
7. `ctp_live_ops_snapshot_smoke.py` now supports the same naming/export contract, and derives `flow_mode` from the effective snapshot flow override so higher-level live ops evidence can reuse the same session namespace.
8. `ctp_live_ops_policy_smoke.py` and `ctp_live_ops_evidence_matrix_smoke.py` now reuse the same `--session-label`, `--evidence-root`, and `--output-json` surface, so the whole live-ops stack can land under one stable session namespace.
9. `ctp_startup_truth_smoke.py`, `ctp_startup_truth_evidence_matrix_smoke.py`, and `ctp_session_rebuild_policy_smoke.py` now reuse the same naming/export contract; the two shared-vs-isolated comparison scripts derive `session_label` from the effective isolated/shared flow override and emit stable session-root evidence paths.
10. `ctp_td_login_smoke.py` now also reuses the same `--flow-path`, `--session-label`, `--evidence-root`, and `--output-json` surface, so the remaining TD login-only leaf entrypoint no longer emits one-off evidence naming.
11. `ctp_td_order_truth_smoke.py`, `ctp_td_order_truth_evidence_matrix_smoke.py`, and `ctp_td_historical_callback_boundary_smoke.py` now reuse the same naming/export contract, and combine it with `--flow-path` so TD callback-truth and boundary evidence can share the same isolated-flow namespace as the rest of the offhours stack.
12. `ctp_md_startup_truth_smoke.py`, `ctp_md_restore_policy_smoke.py`, and `ctp_md_truth_evidence_matrix_smoke.py` now reuse the same naming/export contract, and combine it with `--flow-path` so MD startup/restore evidence can land under the same stable session namespace as the TD and live-ops stacks.
13. `ctp_md_login_smoke.py`, `ctp_live_data_client_bootstrap_smoke.py`, and `ctp_marketdata_smoke.py` now also reuse the same `--flow-path`, `--session-label`, `--evidence-root`, and `--output-json` surface, so the remaining MD diagnostics-only leaf entrypoints no longer emit one-off evidence naming.
14. The shared default label is deterministic: `shared-flow` when no explicit flow path is provided, `isolated-flow` when an explicit flow path is used.
15. `--output-json` and `--evidence-root` remain mutually exclusive across these offhours scripts.

## Repo-Only Bootstrap And Debug

1. `python scripts/ctp_repo_debug_smoke.py` is the repo-only debug entry for a fresh clone after `python -m pip install -e .`.
2. It verifies `_ctp_runtime` import, public scaffold return codes, and internal `CtpMdLiveSession` symbol availability without `vendor/ctp/bin` or `cfgs/local`.
3. If you also want to run the repository tests on a fresh machine, install `python -m pip install -e ".[dev]"` first so `pytest` is present.
4. Live smoke scripts remain separate and still require a local vendor runtime pack plus a local config file.
5. `python scripts/check_rust_gate.py` automatically prepends `vendor/ctp/bin/` to `PATH` when that local pack exists, so cargo-side tests can resolve `thost*_se.dll` without manual PATH edits.
6. A live-ready vendor bridge build additionally requires a full SDK under `vendor/ctp/sdk/` or a matching `CTP_VENDOR_SDK_ROOT` / `CTP_SDK_ROOT` override.
7. The runtime pack and SDK payload remain local/private inputs; the Git repository only carries the code and runbooks that describe the layout.

## Runtime Performance Gate

1. `python scripts/check_runtime_performance_gate.py --events 5000 --limit 1000 --min-events-per-sec 1000` is the P001 repo-local lower-bound performance gate for runtime bridge batch draining.
2. The default report path is `output/reports/p001-ADR001-native-first-runtime-rollout/runtime_performance_gate.json`.
3. This gate is not live performance evidence and cannot approve external daemon mode.
4. External daemon remains future-proposal-only unless a formal benchmark proves the in-process batch bridge is the bottleneck.

## Vendor Bridge Readiness / SDK Handoff

1. `python scripts/check_rust_gate.py` is the only preflight gate for vendor-bridge readiness.
2. The gate reports three operator-facing classes together: runtime pack presence, SDK probe roots, and the two follow-up entrypoints.
3. `python scripts/ctp_repo_debug_smoke.py` is a repo-only bootstrap probe for the public PyO3 scaffold contract.
4. `python scripts/ctp_nautilus_live_smoke.py --config <path>` is the only formal live readiness verdict.
5. `vendor/ctp/bin/` with `pack_kind=compat` is necessary for local runtime resolution, but it is not sufficient to declare live-ready vendor bridge.
6. `CTP_SDK_SCAN_ROOTS` can be used as a semicolon-separated fallback when the SDK is not under `vendor/ctp/sdk/` and no explicit `CTP_VENDOR_SDK_ROOT` / `CTP_SDK_ROOT` is set.
7. Broad-root scans intentionally skip system temp subtrees so stale pytest placeholder SDKs do not produce a false `ctp_vendor_bridge-ready` verdict.
8. If the gate still prints `ctp_vendor_bridge-scaffold-only sdk-not-found`, stop tuning auth/front/credential and switch to the SDK/live-DLL handoff lane.

Important: `python scripts/ctp_repo_debug_smoke.py` is not the formal TD readiness verdict.
It intentionally exercises the public PyO3 scaffold `CtpTdSession`, so TD `-9000` is expected there until C3.
Use `python scripts/ctp_nautilus_live_smoke.py --config <path>` when you need the actual live TD readiness result.

## Formal Baseline

The formal Nautilus-facing live smoke baseline is:

1. `python scripts/ctp_nautilus_live_smoke.py --config <path>`
2. It must be the default live smoke entrypoint reused by later topics.
3. The MD-only and TD-only scripts remain diagnostics helpers.

## Topic 5 Startup Layering

Topic 5 adopts the following startup layering:

1. Mainline startup entrypoint: `python scripts/ctp_nautilus_live_smoke.py --config <path>`
2. Marketdata and execution smoke scripts are frozen sub-entrypoints, not replacements for the mainline startup result.
3. `ctp_md_login_smoke.py`, `ctp_td_login_smoke.py`, `ctp_instrument_query_smoke.py`, `ctp_live_data_client_bootstrap_smoke.py`, and `ctp_marketdata_smoke.py` remain diagnostics-only.

See [live_startup_runbook.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/live_startup_runbook.md).

## Legacy Note

`scripts/ctp_live_smoke_host/` is legacy verification residue only.

1. It is not the current mainline.
2. Do not extend it for new work.
3. New smoke and adapter work must prefer the repository-owned local C wrapper path.
