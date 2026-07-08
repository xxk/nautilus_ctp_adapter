# Evidence: Repo-Only Provider Contract

**change-id**: `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Commands

```powershell
python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python -m pytest tests/test_smoke_import.py -k "all_nautilus_exports_importable or native_loader_keeps_windows_dll_directory_handles" -q --basetemp output/pytest-tmp -p no:cacheprovider
```

## Observed Results

```text
58 passed in 0.79s
1 passed, 211 deselected in 0.86s
```

## Covered Assertions

1. `get_ctp_instrument_provider()` returns `CtpNautilusInstrumentProvider`.
2. Same CTP provider config returns the same provider instance.
3. Different CTP provider configs return different provider instances.
4. Cache key remains `td_front:broker_id:user_id`.
5. Normalized CTP metadata can be looked up by display symbol and venue symbol.
6. Complete futures metadata hydrates a Nautilus `FuturesContract` into provider cache.
7. Incomplete metadata remains metadata-only and does not fabricate a partial Nautilus instrument.

## Limits

This is repo-only contract evidence. It does not prove OpenCTP paper connectivity,
formal broker readiness, or full Nautilus `Instrument` cache hydration.
