# Evidence: Tick Provider Resolution

**change-id**: `20260608__nautilus-provider-readiness__marketdata-provider-live-loop`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Command

```powershell
python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

## Observed Result

```text
64 passed in 0.84s
```

## Covered Assertions

1. Hydrated CTP metadata for `rb2610.SHFE` is used to resolve a CTP tick symbol `rb2610`.
2. The resolved `InstrumentId` is `rb2610.SHFE`, not hardcoded `rb2610.CTP`.
3. Hydrated provider instruments are reused by tick resolution when cache lookup misses.
4. Missing CTP metadata returns `ctp_metadata_missing` and does not fabricate `rb2610.CTP`.
5. Metadata that cannot hydrate a Nautilus instrument returns `instrument_not_hydrated`.
6. Provider-backed subscription symbols filter unknown symbols before restore/resubscribe logic consumes the active symbol set.

## Limits

This evidence does not prove OpenCTP paper connectivity, first tick receipt, or
formal trading readiness.
