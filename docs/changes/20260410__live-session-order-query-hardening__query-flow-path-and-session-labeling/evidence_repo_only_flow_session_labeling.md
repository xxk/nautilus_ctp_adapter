# Evidence: Repo-Only Flow Session Labeling

**change-id**: `20260410__live-session-order-query-hardening__query-flow-path-and-session-labeling`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Command

```powershell
python -m pytest tests/test_smoke_import.py -k "flow_path or session_label or evidence_root or conflicting_export_targets or stable_default_label" -q --basetemp output/pytest-tmp -p no:cacheprovider
```

## Observed Result

```text
37 passed, 175 deselected in 0.93s
```

## Covered Assertions

1. Shared-flow default naming is stable.
2. Isolated flow can be selected through explicit flow path arguments.
3. Session labels are carried into evidence-root export paths.
4. `--output-json` and `--evidence-root` conflicts are rejected.
5. The unified contract is documented in `scripts/README.md` under offhours evidence naming.

## Limits

This is repo-only CLI/payload/naming evidence. It does not prove live TD/MD connectivity.
