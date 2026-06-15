# Evidence: Repo-Only Query Reports

**change-id**: `20260608__nautilus-provider-readiness__query-report-generation`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Command

```powershell
python -m pytest tests/test_nautilus_integration.py -k "CtpNautilusExecutionReports" -q --basetemp output/pytest-tmp -p no:cacheprovider
```

## Observed Result

```text
5 passed
```

## Covered Assertions

1. CTP position query row maps to `PositionStatusReport`.
2. CTP account query row maps to `AccountState`.
3. Account state carries CNY total/free/margin values.
4. Provider metadata is required before position report identity is emitted.
