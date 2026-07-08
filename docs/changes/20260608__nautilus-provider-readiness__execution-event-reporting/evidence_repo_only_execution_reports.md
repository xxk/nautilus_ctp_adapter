# Evidence: Repo-Only Execution Reports

**change-id**: `20260608__nautilus-provider-readiness__execution-event-reporting`
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

1. CTP order callback payload maps to `OrderStatusReport`.
2. CTP trade callback payload maps to `FillReport`.
3. `generate_order_status_report(s)` and `generate_fill_reports` return cached CTP reports.
4. Report identity is provider-backed and does not fabricate `.CTP` instrument ids.
