# Evidence: Repo-Only Operator Playbook

**change-id**: `20260410__live-session-order-query-hardening__session-evidence-and-operator-playbook`
**captured-at**: 2026-06-08 Asia/Shanghai
**account-profile**: `repo-only`

## Commands

```powershell
python scripts/check_topic_docs.py --root .
python scripts/check_topic_governance.py --root .
python scripts/check_harness.py
```

## Observed Results

```text
SUMMARY topics=18 failures=0
TOPIC_GOVERNANCE_CHECK_OK: index=docs/topics/README.md topics=18 active_topic=无 active_change=无
HARNESS_CHECK_OK
```

## Covered Assertions

1. `docs/topics/live-session-order-query-hardening.md` contains an Operator Decision Playbook separating repo-only, OpenCTP paper, formal-trading, and real `c2609` live-send paths.
2. `docs/README.md` contains an Operator Entry Matrix with the same account-layer boundaries.
3. `scripts/README.md` contains an Operator decision note and keeps `ctp_order_lifecycle_smoke.py --live-send` gated behind TD preflight, trade window, and guardrails.
4. C2 and C8 live evidence gaps remain visible as blockers; the playbook does not fake live pass evidence.
5. A no-op/offhours handoff can still use repo-only aggregation and evidence export without relying on chat context.

## Limits

This closes the operator playbook/documentation surface only. It does not close real `c2609` live-send evidence or OpenCTP paper TCP/live-smoke evidence.
