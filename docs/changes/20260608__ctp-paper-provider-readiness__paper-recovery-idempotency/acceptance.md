# CTP Paper Provider Readiness Phase 4 Paper Recovery And Idempotency 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：已完成
**日期**：2026-06-08
**范围**：OpenCTP paper recovery and idempotency semantics
**change-id**：20260608__ctp-paper-provider-readiness__paper-recovery-idempotency
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/proposals/p003-ctp-live-trading-provider-readiness/

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: completed
allow_declare_pass: true
last_updated: "2026-06-08 19:35"
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
  A13: { exec: true, result: passed, blocking: true }
  A14: { exec: true, result: passed, blocking: true }
  A15: { exec: true, result: passed, blocking: false }
  A16: { exec: true, result: passed, blocking: false }
  A17: { exec: true, result: passed, blocking: false }
  A18: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success: duplicate order/trade callbacks are idempotent | ✅ | ✅ | 是 | `tests/test_paper_recovery_idempotency.py` |
| A2 | Success: historical residue is not current session fill | ✅ | ✅ | 是 | historical callbacks isolated from current reports |
| A3 | Success: reconnect/resubscribe disposition is typed | ✅ | ✅ | 是 | `paper-recovery-idempotency.json` |
| A4 | Success: timeout/backpressure disposition is visible | ✅ | ✅ | 是 | retry budget / typed blocker fields covered |
| A5 | Failure: formal-trading / Live profile is requested | ✅ | ✅ | 否 | checkpoint profile mismatch fails |
| A6 | Regression: no account secret appears in recovery evidence | ✅ | ✅ | 否 | evidence contains profile/run id only, no secret fields |
| A7 | Success: MD reconnect preserves or rebuilds the subscribed paper symbol set | ✅ | ✅ | 是 | duplicate `rb2610` resubscribes once |
| A8 | Success: TD reconnect preserves account profile, guardrails and explicit-arm state | ✅ | ✅ | 是 | `paper_send_armed=false` preserved |
| A9 | Failure: recovery rehearsal cannot force disconnect in current environment | ✅ | ✅ | 否 | deterministic repo-only simulation used; paper uncontrollable disconnect remains typed fallback |
| A10 | Regression: retry/backoff budget is recorded and bounded | ✅ | ✅ | 否 | max attempts failure covered |
| A11 | Success: 断点恢复 resumes from saved run id/checkpoint without duplicating completed steps | ✅ | ✅ | 是 | checkpoint resume test |
| A12 | Success: 断点恢复 appends to the same evidence root with monotonic attempt numbers | ✅ | ✅ | 是 | attempt manifest test |
| A13 | Success: MD 网络断线后 reconnect replays login and resubscribe only once per active symbol | ✅ | ✅ | 是 | reconnect disposition test |
| A14 | Success: TD 网络断线后 reconnect replays login/settlement readiness and keeps order-send disarmed | ✅ | ✅ | 是 | reconnect disposition test |
| A15 | Failure: resume checkpoint account profile differs from current `openctp-paper` profile | ✅ | ✅ | 否 | `checkpoint_contract_failed` |
| A16 | Failure: reconnect receives duplicate historical callbacks after TD recovery | ✅ | ✅ | 否 | duplicate historical input deduped |
| A17 | Regression: reconnect loop cannot spin forever | ✅ | ✅ | 否 | retry budget exhausted becomes typed blocker |
| A18 | Regression: partial snapshot from interrupted run is not accepted as complete pre-order evidence | ✅ | ✅ | 否 | covered by Phase 3 pre-snapshot partial rejection |

## 断点 / 重连验收设计

> 本节补充 Phase 4 的恢复类验收。`断点` 指命令或进程在已生成部分 evidence 后中断，后续重新执行需要从 checkpoint/evidence manifest 继续；`重连` 指 MD/TD front 或 session 断开后，adapter 需要重新建立 session 并恢复订阅/查询/guardrail 状态。

### 断点恢复 / Checkpoint Resume

| ID | 验收点 | 通过信号 | Must fail if | 状态 |
| --- | --- | --- | --- | --- |
| BP-C1 | Run identity | 恢复时沿用原 `run_id`、`session_label`、`account_profile=openctp-paper` | 新 run 覆盖旧 evidence 或 profile 改变仍继续 | passed |
| BP-C2 | Step checkpoint | 已完成 step 标记为 completed，未完成 step 标记为 pending/retryable | partial step 被当作 completed | passed |
| BP-C3 | Evidence append | 同一 evidence root 下追加 attempt N+1，保留 attempt N | 重跑删除或覆盖上一轮 evidence | passed |
| BP-C4 | Idempotent replay | 重放 order/trade callback、snapshot row、instrument row 不产生重复 report | 相同 event identity 生成重复 fill/report | passed |
| BP-C5 | Resume blocker | checkpoint 缺失、损坏、profile 不匹配、schema version 不匹配时 typed blocker | checkpoint 解析失败变 traceback 或静默新建 | passed |

### 重连恢复 / Reconnect Recovery

| ID | 验收点 | 通过信号 | Must fail if | 状态 |
| --- | --- | --- | --- | --- |
| RC-MD1 | MD disconnect detection | disconnect reason、front、attempt、timestamp 进入 evidence | 断线只表现为 timeout，无明确 reason | passed |
| RC-MD2 | MD reconnect | reconnect 后 login success，并恢复原 paper subscribed symbols | 重连后订阅集合丢失或重复订阅无记录 | passed |
| RC-MD3 | TD disconnect detection | TD disconnect reason、front/session identity、attempt 进入 evidence | TD 断线后仍认为 session ready | passed |
| RC-TD1 | TD reconnect readiness | reconnect 后重新 login、settlement readiness 可判定 | settlement 未确认却进入 order/query ready | passed |
| RC-TD2 | Guardrail preservation | reconnect 后 `paper_send_armed=false`，account profile 和 guardrails 不被清空 | reconnect 自动武装 order send | passed |
| RC-TD3 | Historical residue boundary | reconnect 后收到历史 order/trade callback 时标为 historical/residue | 历史 callback 进入 current session fill/report | passed |
| RC-R1 | Retry budget | max attempts、backoff、elapsed ms 进入 evidence | 无限重连或 backoff 无上限 | passed |

### Evidence Shape

| 字段 | 要求 |
| --- | --- |
| `recovery.run_id` | 与断点前 run id 一致；新 run 必须显式标明 parent run |
| `recovery.attempt` | 从 1 单调递增；不得覆盖旧 attempt |
| `recovery.resume_from` | checkpoint path、last_completed_step、pending_steps |
| `recovery.disconnects[]` | channel、reason、front/session、observed_at、attempt |
| `recovery.reconnects[]` | channel、login_success、settlement_code、resubscribed_symbols、guardrails_preserved |
| `recovery.idempotency` | duplicate input count、deduped count、emitted report count |
| `recovery.disposition` | `passed`、`typed_blocker`、`manual_review_required` |

### Completion Rule

Phase 4 只有在 repo-only checkpoint/idempotency tests 通过，并且 OpenCTP paper reconnect rehearsal 产生 pass 或 typed `paper-resource` blocker 后，才能关闭。若无法主动制造网络断线，必须保留 repo-only deterministic disconnect simulation，并把 paper front 不可控写成 typed blocker，不能把未执行的 reconnect 当作通过。

## 最终结论 / Final Verdict

- **结论**：已完成
- **说明**：已完成 repo-only checkpoint、reconnect/resubscribe、guardrail preservation、historical residue 和 idempotency 验收；OpenCTP paper 主动断线演练保留为 typed fallback，不用未执行的真实断线冒充通过。
