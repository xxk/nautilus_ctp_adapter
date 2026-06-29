# Real Reconnect Evidence 2026-06-08

## Scope

Change: `20260608__openctp-tts-simulation-provider__real-reconnect-evidence`

This change freezes the reconnect rehearsal command and records the current limitation: this environment can verify deterministic reconnect/idempotency semantics, but cannot safely force a real OpenCTP public 7x24 simulation front disconnect. The real disconnect evidence is therefore recorded as a typed `paper-resource` blocker rather than a fake pass.

## Rehearsal Command

Help evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/reconnect_rehearsal_help.txt`

Primary command shape:

```bash
python scripts/ctp_paper_recovery_idempotency.py --run-id p004-real-reconnect-rehearsal --attempt 1 --md-symbol c2609 --md-symbol zn2610 --md-symbol c2609 --evidence-root output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/rehearsal-manifest --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/reconnect_rehearsal_pass.json
```

Result:

- `success=true`
- `recovery.reconnects[0].resubscribed_symbols=["c2609","zn2610"]`
- `recovery.reconnects[0].resubscribe_counts={"c2609":1,"zn2610":1}`
- `recovery.reconnects[1].guardrails_preserved=true`
- `recovery.query_recovery.disposition=query_ready`
- `recovery.idempotency.disposition=historical_residue_isolated`

Evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/reconnect_rehearsal_pass.json`
- `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/rehearsal-manifest/manifest.json`

## In-Flight Order Conservative Blocker

Command:

```bash
python scripts/ctp_paper_recovery_idempotency.py --run-id p004-real-reconnect-inflight --attempt 1 --md-symbol c2609 --in-flight-client-order-id p004-inflight-order --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/inflight_order_conservative_blocker.json
```

Result:

- `success=false`
- `recovery.disposition=typed_blocker`
- `recovery.in_flight_order.disposition=conservative_blocker`
- issue: `in_flight_order_requires_manual_reconciliation`

Evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/inflight_order_conservative_blocker.json`

## Real Disconnect Resource Blocker

OpenCTP status page check:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/openctp_simenv_status_20260608.json`
- HTTP status: `200`
- status page contained `openctp-7x24`

Typed blocker command:

```bash
python scripts/ctp_paper_recovery_idempotency.py --run-id p004-real-reconnect-resource-blocker --attempt 1 --md-symbol c2609 --md-symbol zn2610 --resource-blocker-code forced_front_disconnect_unavailable --resource-blocker-detail "OpenCTP public 7x24 simulation front is externally operated; this run cannot force a real front disconnect without operator/network intervention, so real reconnect is typed as paper-resource blocker instead of fake pass." --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/forced_disconnect_resource_blocker.json
```

Result:

- `success=false`
- `status=blocked`
- `blocker_type=paper-resource`
- issue: `forced_front_disconnect_unavailable`
- no real reconnect pass is declared

Evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/forced_disconnect_resource_blocker.json`

## Test Evidence

```bash
python -m pytest tests/test_paper_recovery_idempotency.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Result: `8 passed`

## External Condition To Unblock

One of these must be available to collect true real reconnect pass evidence:

1. An operator-controlled way to restart or disconnect the OpenCTP TTS 7x24 MD/TD front for this account.
2. Permission to perform a controlled local network interruption against only this test process/front and then verify relogin/resubscribe.
3. A dedicated simulation front or broker paper environment where forced disconnect/reconnect is allowed.
