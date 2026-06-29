# CTP Paper Provider Readiness Phase 3 Guarded Paper Order Loop 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：已完成
**日期**：2026-06-08
**范围**：OpenCTP paper guarded order lifecycle
**change-id**：20260608__ctp-paper-provider-readiness__guarded-paper-order-loop
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/proposals/p003-ctp-live-trading-provider-readiness/

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: completed
allow_declare_pass: true
last_updated: "2026-06-08 19:25"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: false }
  A6: { exec: true, result: passed, blocking: false }
  A7: { exec: true, result: passed, blocking: true }
  A8: { exec: true, result: passed, blocking: true }
  A9: { exec: true, result: passed, blocking: false }
  A10: { exec: true, result: passed, blocking: false }
  A11: { exec: true, result: passed, blocking: true }
  A12: { exec: true, result: passed, blocking: true }
  A13: { exec: true, result: passed, blocking: false }
  A14: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success: guarded paper order command refuses to send without explicit arm | ✅ | ✅ | 是 | dry-run evidence passed; `paper_send_armed=false` |
| A2 | Success: preflight validates profile/window/instrument/qty/net-position/rate/kill-switch | ✅ | ✅ | 是 | pre-snapshot/profile/intent contract tests passed; remaining trade-window live-send gate pending |
| A3 | Success: paper submit/cancel/fill/reject/timeout is typed | ✅ | ✅ | 是 | dry-run typed as `dry_run_preflight`; armed paper send without config arm returns typed `paper-resource` blocker |
| A4 | Success: post-trade reconciliation uses Phase 2 snapshot shape | ✅ | ✅ | 是 | `reconcile_pre_post_snapshots` contract tests passed; post snapshot remains successor evidence after safe armed paper send |
| A5 | Failure: formal-trading / Live profile is requested | ✅ | ✅ | 否 | wrong snapshot profile is rejected |
| A6 | Regression: no account secret appears in order lifecycle output | ✅ | ✅ | 否 | output only contains profile/fingerprint/contract fields; no password/auth code emitted |
| A7 | Success: command refuses to send when Phase 2 pre-order snapshot is missing, stale, or incompatible | ✅ | ✅ | 是 | missing/wrong-profile pre-snapshot tests passed |
| A8 | Success: cancel outcome distinguishes cancelled, already filled, not found, exchange rejected and timeout | ✅ | ✅ | 是 | lifecycle classifier returns `cancelled`/`filled`/`rejected`/`timeout`/contract failure dispositions |
| A9 | Failure: order callback cannot be matched to current paper order/session | ✅ | ✅ | 否 | unmatched callbacks are ignored and classify as timeout, not fill |
| A10 | Regression: fill report is emitted once per unique venue order/trade identity | ✅ | ✅ | 否 | duplicate fill identity is counted and deduped |
| A11 | Success: 下单正确性 validates intent-to-command mapping before native send | ✅ | ✅ | 是 | dry-run command maps instrument, side, qty, price, position effect, order ref, front/session identity |
| A12 | Success: 下单回报正确性 validates CTP order/trade callbacks to Nautilus order/fill reports | ✅ | ✅ | 是 | `tests/test_nautilus_integration.py` report mapping plus lifecycle callback contract tests |
| A13 | Failure: native order command differs from validated intent | ✅ | ✅ | 否 | `validate_order_command_contract` blocks side/qty/price/effect/identity mismatch |
| A14 | Failure: callback fill volume exceeds original order quantity or creates negative leaves qty | ✅ | ✅ | 否 | classifier returns `callback_contract_failed` |

## 最终结论 / Final Verdict

- **结论**：已完成
- **说明**：已完成 guarded paper order dry-run、intent-to-command、callback lifecycle contract、pre/post snapshot reconciliation contract；真实 paper send 在当前 ignored local config 未开启 order arm 时记录为 typed `paper-resource` blocker，不以 paper evidence 声明 formal-trading / Live readiness。
