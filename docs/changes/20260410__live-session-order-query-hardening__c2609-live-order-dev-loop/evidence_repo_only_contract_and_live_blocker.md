# Evidence: Repo-Only Contract And Live Blocker

**change-id**: `20260410__live-session-order-query-hardening__c2609-live-order-dev-loop`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Commands

```powershell
python -m pytest tests/test_smoke_import.py -k "order_lifecycle_live_send or execution_precheck_enforces_real_account_guardrails or execution_client_rejects_submit_mapping_when_guardrails_fail" -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_order_lifecycle_smoke.py --help
python scripts/ctp_td_order_truth_smoke.py --help
```

## Observed Results

```text
8 passed, 204 deselected in 1.17s
```

`ctp_order_lifecycle_smoke.py --help` exposes the live-send command surface:

```text
--instrument
--quantity
--limit-price
--time-in-force
--live-send
```

`ctp_td_order_truth_smoke.py --help` exposes the preflight/evidence surface:

```text
--flow-path
--session-label
--evidence-root
--output-json
```

## Covered Repo-Only Assertions

1. Live order smoke requires explicit config arm before native order send.
2. Guardrail rejects remain local for invalid instrument/quantity/position preconditions.
3. Live-send contract remains locked to the guarded `c2609` path in focused tests.
4. Callback matching and partial live-loop boundary behavior remain structured.

## External Blocker

Formal A1/A2 live-send acceptance requires a formal-trading reachable TD front, active trade window, local live config, and known net position below the `5`-lot cap. The OpenCTP paper baseline in `20260607__openctp-tts__test-baseline` is available for simulation development, but it cannot truthfully declare real-account `c2609` live-send pass.
