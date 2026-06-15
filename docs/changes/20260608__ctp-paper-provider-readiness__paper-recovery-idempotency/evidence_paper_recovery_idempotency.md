# Evidence: Paper Recovery And Idempotency

**change-id**：`20260608__ctp-paper-provider-readiness__paper-recovery-idempotency`
**日期**：2026-06-08
**account profile**：`openctp-paper`
**evidence class**：`paper-simulation`

## Commands

```powershell
python -m pytest tests/test_paper_recovery_idempotency.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_paper_recovery_idempotency.py --run-id paper-recovery-acceptance --attempt 1 --evidence-root output/reports/p003-ctp-live-trading-provider-readiness/paper-recovery-idempotency --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-recovery-idempotency.json
```

## Result

| Check | Result | Notes |
| --- | --- | --- |
| Focused tests | passed | 6 tests passed |
| Checkpoint resume | passed | run id preserved, attempt increments, profile/schema mismatch fails |
| Evidence append | passed | attempt files and manifest are appended under trusted report root |
| MD reconnect | passed | duplicate symbols resubscribe once |
| TD reconnect | passed | settlement ready and `paper_send_armed=false` preserved |
| Historical residue | passed | duplicate historical callback is deduped and not emitted as current fill |
| Retry budget | passed | max-attempt exhaustion is typed blocker |

## Evidence Paths

| Artifact | Path |
| --- | --- |
| Recovery summary | `output/reports/p003-ctp-live-trading-provider-readiness/paper-recovery-idempotency.json` |
| Attempt manifest | `output/reports/p003-ctp-live-trading-provider-readiness/paper-recovery-idempotency/manifest.json` |
| Attempt 1 | `output/reports/p003-ctp-live-trading-provider-readiness/paper-recovery-idempotency/attempt-001.json` |

## Boundary

This is deterministic repo-only recovery evidence for the OpenCTP paper profile. The current environment does not rely on forcibly breaking the external OpenCTP network session; if a future rehearsal can actively force front disconnects, it should append a paper-resource evidence attempt rather than replacing this repo-only baseline.
