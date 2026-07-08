# Risk Preflight Expansion Evidence 2026-06-08

## Scope

Change: `20260608__openctp-tts-simulation-provider__risk-preflight-expansion`

This evidence proves the guarded OpenCTP TTS simulation order loop emits redacted account/position risk facts and blocks unsafe commands before native submit mapping.

## Positive Dry Run

Command:

```bash
python scripts/ctp_guarded_paper_order_loop.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/post_cleanup_snapshot_c2609.json --instrument c2609 --side BUY --quantity 1 --limit-price 2300 --client-order-id risk-dry-run-c2609 --timeout-seconds 5 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/risk_dry_run_c2609.json
```

Result:

- `success=true`
- `risk_preflight.accepted=true`
- account metrics emitted as presence-only redacted facts
- c2609 risk facts: `long_qty=1`, `short_qty=2`, `net_position=-1`
- `order_lifecycle.dry_run=true`, `live_send_armed=false`

Evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/risk_dry_run_c2609.json`

## Negative Guardrail Block

Command:

```bash
python scripts/ctp_guarded_paper_order_loop.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/risk_blocked_guardrails.local.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/post_cleanup_snapshot_c2609.json --instrument c2609 --side SELL --quantity 2 --limit-price 2300 --client-order-id risk-dup-budget --timeout-seconds 5 --arm-paper-send --submit-count-last-minute 1 --session-send-count 1 --session-send-budget 1 --seen-client-order-id risk-dup-budget --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/blocked_guardrails_combo.json
```

Result:

- `success=false`
- `failure_reason=risk_preflight_rejected`
- `blocker_type=paper-safety`
- `mapped_submit=null`
- `order_lifecycle=null`
- typed issues: `kill_switch_closed`, `instrument_not_allowed`, `max_order_qty_exceeded`, `max_net_position_exceeded`, `frequency_cap_exceeded`, `session_send_budget_exceeded`, `duplicate_client_order_id`

Evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/blocked_guardrails_combo.json`

## Missing External Metrics Block

Command:

```bash
python scripts/ctp_guarded_paper_order_loop.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/missing_account_metrics_snapshot.json --instrument c2609 --side BUY --quantity 1 --limit-price 2300 --client-order-id risk-missing-metrics --timeout-seconds 5 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/blocked_missing_account_metrics.json
```

Result:

- `success=false`
- `failure_reason=risk_preflight_rejected`
- typed issues: `account_identity_unavailable`, `account_available_metric_unavailable`, `account_margin_metric_unavailable`
- `native_send_allowed=false`
- no fake pass when account metrics are unavailable

Evidence:

- `output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/blocked_missing_account_metrics.json`

## Test Evidence

```bash
python -m pytest tests/test_guarded_paper_order_loop.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Result: `29 passed`
