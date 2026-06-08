# Evidence: Repo-Only Aggregated Query Export

**change-id**: `20260410__live-session-order-query-hardening__aggregated-query-evidence-export`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Commands

```powershell
python -m pytest tests/test_smoke_import.py -k "query_adapter_smoke and (aggregated_query or evidence_root or output_json or session_labeled_export or conflicting_output_json)" -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_query_adapter_smoke.py --help
```

## Observed Results

```text
3 passed, 209 deselected in 0.88s
```

`ctp_query_adapter_smoke.py --help` exposes the repo-only contract surface:

```text
--flow-path
--session-label
--evidence-root
--instrument-symbol
--include-reconciliation
--include-order-truth
--include-order-trade-snapshot
--include-merged-policy
--output-json
```

## Source Evidence

1. `scripts/ctp_query_adapter_smoke.py` aggregates position/account query snapshot and optional instrument, reconciliation, order truth, order/trade snapshot, and merged policy lanes.
2. The same script resolves export targets through `resolve_export_path()` with `aggregated_query.json` as the stable default file name.
3. `scripts/README.md` documents the offhours query aggregation note and offhours evidence naming note for operator reuse.

## Limits

This is repo-only contract evidence. It does not prove live TD connectivity, OpenCTP paper front reachability, or formal broker account readiness.
