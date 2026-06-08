# Evidence: Repo-Only Order Trade Snapshot

**change-id**: `20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Commands

```powershell
python -m pytest tests/test_smoke_import.py -k "order_trade_snapshot or td_order_truth or historical_callback_boundary" -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_query_adapter_smoke.py --help
```

## Observed Results

```text
17 passed, 195 deselected in 0.97s
```

`ctp_query_adapter_smoke.py --help` exposes:

```text
--include-order-trade-snapshot
--include-order-truth
--include-merged-policy
--evidence-root
--output-json
```

## Covered Assertions

1. Order/trade snapshot is a read-only lane, separate from live-send.
2. Historical callback residue remains distinct from current snapshot semantics.
3. Empty order/trade results are boundary/evidence-only semantics, not implicit failures.
4. Query/session/identity failure paths remain explicit.
5. `scripts/README.md` documents `no_order_events / no_trade_events / historical_residue_*` semantics for operators.

## Limits

This is repo-only contract evidence. It does not prove live TD query connectivity or a real account snapshot.
