# Post-order Reconciliation Evidence - 2026-06-08

## Scope

- Proposal: `p004-openctp-tts-simulation-provider-completeness`
- Change: `20260608__openctp-tts-simulation-provider__post-order-reconciliation`
- Account profile: `openctp-tts-7x24-simulation`
- Evidence class: `openctp-tts-7x24-simulation`
- Formal trading: not used

## Repo Contract Evidence

Commands:

```powershell
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Result: `107 passed`.

Covered contracts:

- Reconciliation rejects same-run post snapshots as stale.
- Reconciliation rejects account fingerprint mismatch.
- Filled order reconciliation compares target symbol/direction position delta with fill volume.
- Rejected and cancelled order reconciliation require no unexpected position delta.
- Accepted/pending and timeout states are typed and require follow-up instead of being guessed as filled/rejected.
- Duplicate fills are deduplicated; CTP ASCII status `53` is classified as cancelled.
- Native exec `error_msg` is preserved in runtime payload for reject classification.

## Filled Evidence

Source: c2609 close from previous child change, reconciled here with the new helper.

- Pre snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_c2609.json`
- Post snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_c2609_after_stdout_fix.json`
- Reconciliation: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_close_armed_c2609_short1.json`
- Intent: `BUY CLOSE 1 @ 2350`
- Lifecycle: `filled`, `fill_volume=1`
- Verdict: `filled_reconciled`
- Target: `c2609 SHORT`, position delta `-1`, expected delta `-1`

## Rejected Evidence

- Pre snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/pre_reject2_snapshot_c2609.json`
- Order evidence: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reject2_order_c2609_sell_999999.json`
- Post snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/post_reject2_snapshot_c2609.json`
- Reconciliation: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_rejected_c2609_sell_999999.json`
- Intent: `SELL OPEN 1 @ 999999`
- Lifecycle: `rejected`, `fill_volume=0`
- Verdict: `rejected_reconciled`
- Target: `c2609 SHORT`, position delta `0`, expected delta `0`

## Cancelled Evidence

- Pre snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/pre_reject_snapshot_TEST.json`
- Order evidence: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reject_order_TEST_sell_999999.json`
- Post snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/post_reject_snapshot_TEST.json`
- Reconciliation: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_cancelled_TEST_sell_999999.json`
- Intent: `SELL OPEN 1 @ 999999`
- Lifecycle: `cancelled`, `fill_volume=0`, `leaves_qty=0`
- Verdict: `cancelled_reconciled`
- Target: `TEST SHORT`, position delta `0`, expected delta `0`

## Pending / Timeout-style Evidence

- Pre snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/pre_reject_snapshot_c2609.json`
- Order evidence: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reject_order_c2609_sell_999999.json`
- Post snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/post_reject_snapshot_c2609.json`
- Reconciliation: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_pending_c2609_sell_999999.json`
- Lifecycle: `accepted`, `fill_volume=0`, `leaves_qty=1`
- Verdict: `accepted_pending_no_delta`, `requires_followup=true`
- Cleanup: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/cleanup_cancel_pending_c2609_ref2.json`
- Cleanup snapshot: `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/post_cleanup_snapshot_c2609.json`

## Residual State

Latest cleanup snapshot:

- `c2609 LONG position_qty=1`
- `c2609 SHORT position_qty=2`
- `rb2609 LONG position_qty=1`
- `rb2609 LONG position_qty=4`
- `zn2610 LONG position_qty=2`
- Order/trade truth in the cleanup snapshot reports no current-session order/trade events.

## Caveats

- The first c2609 high-price order was classified as pending because the runtime event did not yet preserve native `error_msg` in payload. That root cause was fixed and verified before collecting the rejected c2609 evidence.
- The pending c2609 order cleanup returned native cancel code `0` but no callback within the cancel script. A post-cleanup snapshot was collected and no current-session order/trade events were observed.
