# Session Evidence 与 Operator Playbook 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-10
**范围**：session-window operator 决策树、evidence matrix、docs/scripts 双导航
**change-id**：20260410__live-session-order-query-hardening__session-evidence-and-operator-playbook
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-04-10 00:00"
concluded_by: ""

exit_conditions:
  E1_success_scenarios: pending
  E2_failure_scenarios: pending
  E3_verification_cmds: pending
  E4_evidence_collected: pending
  E5_real_acceptance_only: pending
  E6_minimum_scenarios: pending

scenarios:
  A1: { exec: false, result: null, blocking: true }
  A2: { exec: false, result: null, blocking: true }
  A3: { exec: false, result: null, blocking: true }
  A4: { exec: false, result: null, blocking: true }
  A5: { exec: false, result: null, blocking: true }
  A6: { exec: false, result: null, blocking: false }
```
<!-- AI-STATUS-END -->

## 一、验收目标 / Goals

1. 让 operator 可直接根据当前时段、gate 结果和 blocker 决定下一步。
2. 让 evidence 能按 change/session 快速定位。
3. 让 docs 层的入口说明与 scripts 层的入口说明保持一致。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. topic README 中的决策树与 child change 队列。
2. `docs/README.md` 的 current delivery / operator 导航。
3. `scripts/README.md` 的入口分层与 verdict 说明。
4. sibling change evidence 的引用与索引。

### 不覆盖（Out of Scope）

1. 新的脚本能力开发。
2. 私有 SDK/live DLL 输入补齐。
3. 真实交易执行本身。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| sibling changes 已存在正式 bundle | 文档 | 是 | 是 | ⬜ | 至少包含 C1/C3/C2/U1 |
| `python scripts/check_topic_docs.py` 可执行 | 治理 | 是 | 是 | ⬜ | 必跑 |
| `python scripts/check_topic_governance.py --root .` 可执行 | 治理 | 是 | 是 | ⬜ | 必跑 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 不得用聊天里的临时说明替代 playbook 文档。
2. 必须引用真实 sibling change 路径，不能写虚构 evidence。
3. test 只能辅助治理验证，不替代文档可执行性。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: operator 能选择正确入口 | 阅读 topic/docs/scripts 导航 | 能判断该跑哪个 gate/smoke/change | 决策树清晰 | 仍需聊天问入口 | `./evidence_a1_operator_routing.md` |
| A2 | Success 2: evidence 能按路径索引 | 根据 docs 索引打开 sibling evidence | 能快速定位相关证据 | evidence 索引完整 | 证据仍散落不可查 | `./evidence_a2_evidence_index.md` |
| A3 | Success 3: gate/blocker/ready 术语一致 | 对照 topic/docs/scripts 三处文案 | ready/blocker 含义一致 | 三处术语无冲突 | 同一名词多种含义 | `./evidence_a3_terminology_alignment.md` |
| A4 | Failure 1: 缺 sibling evidence 时明确指出缺口 | 故意检查未完成 sibling | playbook 不会假装已齐全 | 缺口可见 | 文档暗示已完成但找不到证据 | `./evidence_a4_missing_evidence_gap.md` |
| A5 | Failure 2: blocked topic/change 不会被误排成 active next | 检查 queue 与 current state | blocked 不会被当成 ready-next | queue 状态一致 | blocked/queued 混淆 | `./evidence_a5_queue_state_consistency.md` |
| A6 | Boundary 1: no-op day 也能完成 operator handoff | 无新 live evidence 的一天 | 仍能依据既有 gate + queue 做决策 | playbook 支持 no-op handoff | 没有新运行就无法交接 | `./evidence_a6_noop_handoff.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | operator routing | `./evidence_a1_operator_routing.md` | A1 |
| 2 | evidence index | `./evidence_a2_evidence_index.md` | A2 |
| 3 | terminology alignment | `./evidence_a3_terminology_alignment.md` | A3 |
| 4 | missing evidence gap | `./evidence_a4_missing_evidence_gap.md` | A4 |
| 5 | queue state consistency | `./evidence_a5_queue_state_consistency.md` | A5 |
| 6 | noop handoff | `./evidence_a6_noop_handoff.md` | A6 |

## 七、未通过处理 / On Failure

1. 回到 `plan.md` 只修导航、索引或术语冲突。
2. 不得为了“通过”而隐藏 blocked/缺证据状态。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | 待执行 | 三层导航可直接用 | 文档 walk-through | operator 能独立决策 | sibling evidence 未齐全 | `./evidence_a1_operator_routing.md` |
| R2 | A2 | 待执行 | sibling evidence 已索引 | 文档 walk-through | evidence 可按路径定位 | sibling changes 未完成 | `./evidence_a2_evidence_index.md` |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Governance 锁定 | `python scripts/check_topic_docs.py` | topic queue 与状态投影一致 |
| Governance 锁定 | `python scripts/check_topic_governance.py --root .` | change bundle 与 queue 对齐 |

## 十一、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：2026-04-10
- **执行人**：—
- **建议**：暂不建议宣告通过
- **说明**：当前 change 只规划 operator playbook 收口，不代表 sibling evidences 已自动具备。