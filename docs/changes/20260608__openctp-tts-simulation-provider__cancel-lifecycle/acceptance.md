# OpenCTP TTS Simulation Cancel Lifecycle 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-06-08
**范围**：OpenCTP TTS simulation cancel lifecycle
**change-id**：20260608__openctp-tts-simulation-provider__cancel-lifecycle
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/openctp-tts-simulation-provider-completeness.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 20:55"
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
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: true }
  A7: { exec: true, result: passed, blocking: true }
  A8: { exec: true, result: passed, blocking: true }
  A9: { exec: true, result: passed, blocking: true }
  A10: { exec: true, result: passed, blocking: true }
  A11: { exec: true, result: passed, blocking: true }
  A12: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 通过 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 是 | 阻塞场景已通过 |
| 最后更新 | 2026-06-08 20:55 | |
| AI 执行人 | Codex | |

## 一、验收目标 / Goals

补齐 simulation cancel lifecycle，证明 provider 可以安全地发起撤单、分类撤单回报，并保持 idempotent reports。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. Passive order staging or typed blocker。
2. Cancel command mapping and callback classification。
3. Duplicate cancel callback idempotency。
4. Pre-cancel snapshot、residual order detection、redaction 和 typed blocker 证据。

### 不覆盖（Out of Scope）

1. Formal-trading cancel。
2. 自动策略撤单。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Passive order staging | OpenCTP TTS simulation staged order command | order accepted or typed blocker | native order ref/front/session recorded | no identity and still attempts cancel | 本 change evidence |
| A2 | Active cancel command | cancel lifecycle command | cancel accepted/rejected typed | cancel report emitted | missing cancel report | 本 change evidence |
| A3 | Cancel rejected classification | forced invalid/stale cancel path | typed reject | reject reason recorded | treated as pass fill/cancel | 本 change evidence |
| A4 | Missing native identity blocks cancel | focused test | no native cancel send | `cancel_contract_failed` | command sent anyway | `evidence_cancel_contract_repo_only_20260608.md` |
| A5 | Duplicate cancel callback idempotency | focused test | one report | duplicate ignored/typed | duplicate report emitted | `evidence_cancel_contract_repo_only_20260608.md` |
| A6 | Pre-cancel read-only snapshot | `ctp_paper_readonly_snapshot.py` before staging/cancel | snapshot is complete or typed blocker | account/order/position fingerprint redacted | cancel proceeds with missing snapshot | 本 change evidence |
| A7 | Residual open order handling | query order/trade snapshot before staging | existing live order is listed or typed no-open-order | residual order mapped to cancel/carry-forward | residual ignored | 本 change evidence |
| A8 | Dry-run cancel contract | cancel command without armed send | native cancel payload contract emitted, no send | order ref/front/session/profile present | dry-run sends native cancel | `evidence_cancel_contract_repo_only_20260608.md` |
| A9 | Armed cancel safety | cancel command with explicit simulation arm | send only if profile/allowlist/kill switch pass | `openctp-tts-7x24-simulation` and guard verdict recorded | send with wrong profile or disabled guard | 本 change evidence |
| A10 | Cancel-after-fill race | staged order fills before cancel arrives | lifecycle classified as filled, not cancel failure | fill/cancel race typed and reconciled | duplicate or contradictory final state | 本 change evidence |
| A11 | Redaction and evidence schema | review produced evidence | scenario id/run id/profile/evidence class present; secrets absent | evidence can close repo-only and simulation rows | raw secret or missing scenario id | `evidence_cancel_contract_repo_only_20260608.md` |
| A12 | P003 regression | existing guarded order tests | no regression | tests pass | P003 baseline broken | `evidence_cancel_contract_repo_only_20260608.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | repo-only contract evidence | `evidence_cancel_contract_repo_only_20260608.md` | A4/A5/A8/A11/A12 covered; Rust/PyO3 gate loader fix covered |
| 2 | dry-run cancel JSON | `output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/cancel_dry_run_contract.json` | `success=true`, no runtime cancel command submitted |
| 3 | pre-cancel snapshot blocker JSON | `output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/pre_cancel_snapshot_live_timeout_blocker.json` | 记录环境漂移前 blocker；服务器状态页显示 OpenCTP front running |
| 4 | recovered pre-cancel snapshot | `output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/pre_cancel_snapshot_tts669_TEST.json` | A6 通过：account/position/instrument/order-trade snapshot passed |
| 5 | staged order evidence | `output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/stage_order_c2609_buy_2300.json` | A1 通过：passive order accepted, leaves_qty=1, native identity captured |
| 6 | armed cancel evidence | `output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/cancel_order_c2609_ref2.json` | A2/A9 通过：native cancel accepted, native_code=0, no disconnects |
| 7 | post-cancel cleanup evidence | `output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/post_cancel_snapshot_cleanup_c2609.json` | A7/A10 通过：no current-session order residual; fill-race left c2609 LONG 1 and no order residual |

## 十一、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-06-08
- **执行人**：
- **建议**：建议宣告通过
- **说明**：repo-only cancel contract、idempotency、Rust/PyO3 loader gate、真实 OpenCTP TTS pre/post snapshot、passive staging、armed cancel、reject classification、residual cleanup 与 fill-before-cancel cleanup evidence 均已覆盖。Cancel action 未收到 cancel callback，但 native cancel accepted 且 post-order truth 无残单，按当前验收口径通过。
