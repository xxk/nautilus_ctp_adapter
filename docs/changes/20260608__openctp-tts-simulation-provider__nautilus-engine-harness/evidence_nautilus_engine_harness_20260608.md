# Nautilus Engine Harness Evidence 2026-06-08

## Scope

Change: `20260608__openctp-tts-simulation-provider__nautilus-engine-harness`

The harness proves P004 provider completeness is not closed with script-only native smoke. It uses the Nautilus-facing provider entrypoint `CtpLiveExecutionClient`, CTP provider metadata, and Nautilus report APIs.

## Command

```bash
python scripts/ctp_nautilus_engine_harness.py --run-id p004-nautilus-engine-harness --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/nautilus-engine-harness/engine_harness_provider_reports.json
```

Result:

- `success=true`
- `provider_entrypoint=CtpLiveExecutionClient`
- `script_only_smoke=false`
- `paper_send_armed=false`
- instrument provider loaded `c2609.DCE`
- order statuses: `ACCEPTED`, `CANCELED`, `REJECTED`
- fill reports: `1`
- duplicate fill ignored: `true`
- position reports: `1`
- account state reported: `true`
- account id redacted: `true`

Evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/nautilus-engine-harness/engine_harness_provider_reports.json`

## Provider Fix

The child change fixed CTP cancel callback projection in `nautilus_execution.py`: CTP status `5`/`53` now maps to Nautilus `OrderStatus.CANCELED` before `leaves_qty=0` can be interpreted as a fill.

## Test Evidence

```bash
python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Focused evidence includes:

- cancel callback maps to `OrderStatus.CANCELED`
- minimal engine harness uses provider entrypoint and emits accepted/canceled/rejected/fill/account/position reports
- duplicate fill callback is idempotent
