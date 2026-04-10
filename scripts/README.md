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

## Repo-Only Bootstrap And Debug

1. `python scripts/ctp_repo_debug_smoke.py` is the repo-only debug entry for a fresh clone after `python -m pip install -e .`.
2. It verifies `_ctp_runtime` import, public scaffold return codes, and internal `CtpMdLiveSession` symbol availability without `vendor/ctp/bin` or `cfgs/local`.
3. If you also want to run the repository tests on a fresh machine, install `python -m pip install -e ".[dev]"` first so `pytest` is present.
4. Live smoke scripts remain separate and still require a local vendor runtime pack plus a local config file.
5. `python scripts/check_rust_gate.py` automatically prepends `vendor/ctp/bin/` to `PATH` when that local pack exists, so cargo-side tests can resolve `thost*_se.dll` without manual PATH edits.
6. A live-ready vendor bridge build additionally requires a full SDK under `vendor/ctp/sdk/` or a matching `CTP_VENDOR_SDK_ROOT` / `CTP_SDK_ROOT` override.
7. The runtime pack and SDK payload remain local/private inputs; the Git repository only carries the code and runbooks that describe the layout.

## Formal Baseline

The formal Nautilus-facing live smoke baseline is:

1. `python scripts/ctp_nautilus_live_smoke.py --config <path>`
2. It must be the default live smoke entrypoint reused by later topics.
3. The MD-only and TD-only scripts remain diagnostics helpers.

## Topic 5 Startup Layering

Topic 5 adopts the following startup layering:

1. Mainline startup entrypoint: `python scripts/ctp_nautilus_live_smoke.py --config <path>`
2. Marketdata and execution smoke scripts are frozen sub-entrypoints, not replacements for the mainline startup result.
3. `ctp_md_login_smoke.py`, `ctp_td_login_smoke.py`, `ctp_instrument_query_smoke.py`, and `ctp_live_data_client_bootstrap_smoke.py` remain diagnostics-only.

See [live_startup_runbook.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/live_startup_runbook.md).

## Legacy Note

`scripts/ctp_live_smoke_host/` is legacy verification residue only.

1. It is not the current mainline.
2. Do not extend it for new work.
3. New smoke and adapter work must prefer the repository-owned local C wrapper path.
