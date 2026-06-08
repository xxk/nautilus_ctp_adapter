# Post-order Reconciliation 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-06-08
**范围**：simulation post-order reconciliation
**change-id**：20260608__openctp-tts-simulation-provider__post-order-reconciliation
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/openctp-tts-simulation-provider-completeness.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 21:26"
concluded_by: "codex"
exit_conditions: { E1_success_scenarios: passed, E2_failure_scenarios: passed, E3_verification_cmds: passed, E4_evidence_collected: passed, E5_real_acceptance_only: passed, E6_minimum_scenarios: passed }
scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: true }
  A7: { exec: true, result: passed, blocking: true }
  A8: { exec: true, result: passed, blocking: true }
  A9: { exec: true, result: passed, blocking: true }
  A10: { exec: true, result: passed, blocking: true }
  A11: { exec: true, result: passed, blocking: false }
  A12: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | filled/rejected/cancelled/pending reconciliation evidence recorded |
| AI 建议宣告通过 | 是 | cleanup caveat recorded |

## 一、验收目标 / Goals

证明 simulation order 的最终状态可由 post-order snapshot 对账解释。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Filled reconciliation | simulation filled order | delta matches fill | position/order/trade explain fill | delta mismatch | 本 change evidence |
| A2 | Rejected reconciliation | rejected order evidence | no fill delta | reject reason typed | marked filled | 本 change evidence |
| A3 | Cancelled reconciliation | cancelled order evidence | no or partial delta typed | cancel final state | ambiguous lifecycle | 本 change evidence |
| A4 | Stale snapshot rejected | negative test | blocked | stale run id detected | accepted | test output |
| A5 | Account mismatch rejected | negative test | blocked | fingerprint mismatch typed | accepted | test output |
| A6 | Partial fill reconciliation | simulated partial fill or synthetic callback contract test | filled qty, leaves qty and position delta agree | partial state typed | full fill assumed | test/evidence |
| A7 | Timeout reconciliation | no final order callback within timeout | post snapshot and lifecycle verdict both recorded | timeout is typed, not pass/fail guess | timeout treated as fill/reject | 本 change evidence |
| A8 | Trade callback duplicate handling | duplicate trade callback test | one fill counted | duplicate count recorded | duplicate fill counted | test output |
| A9 | Order/trade query consistency | post snapshot order/trade query | callback and query agree or mismatch typed | query status explains final state | query ignored | 本 change evidence |
| A10 | Evidence schema and redaction | evidence review | run id/scenario id/profile/evidence class present; secrets absent | row can close | raw secret or missing id | 本 change evidence |
| A11 | Resource blocker carry-forward | front/query unavailable | typed blocker with next action | no fake pass | blocker hidden | 本 change evidence |
| A12 | P003 regression | focused tests | pass | no regression | baseline broken | command output |

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| Post-order evidence | `docs/changes/20260608__openctp-tts-simulation-provider__post-order-reconciliation/evidence_post_order_reconciliation_20260608.md` | A1-A12 evidence recorded |
| Filled reconciliation | `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_close_armed_c2609_short1.json` | `filled_reconciled`, c2609 SHORT delta `-1` |
| Rejected reconciliation | `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_rejected_c2609_sell_999999.json` | `rejected_reconciled`, no position delta |
| Cancelled reconciliation | `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_cancelled_TEST_sell_999999.json` | `cancelled_reconciled`, no position delta |
| Pending reconciliation | `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/reconcile_pending_c2609_sell_999999.json` | `accepted_pending_no_delta`, `requires_followup=true` |
| Cleanup cancel | `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/cleanup_cancel_pending_c2609_ref2.json` | native cancel code `0`; no callback observed |
| Cleanup snapshot | `output/reports/p004-openctp-tts-simulation-provider-completeness/post-order-reconciliation/post_cleanup_snapshot_c2609.json` | no current-session order/trade events observed |
| Focused verification | `python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider` | `107 passed` |

## Verdict

Passed. Simulation order outcomes now have target symbol/direction reconciliation verdicts for filled, rejected, cancelled and accepted-pending states. Stale same-run snapshots, account mismatch, partial snapshots and position delta mismatches are blocked by tests.

Caveat: one c2609 high-price order was initially typed as pending before native `error_msg` was added to runtime payload. It was cancelled for cleanup; the repeat c2609 high-price evidence is typed as `rejected_reconciled`.
