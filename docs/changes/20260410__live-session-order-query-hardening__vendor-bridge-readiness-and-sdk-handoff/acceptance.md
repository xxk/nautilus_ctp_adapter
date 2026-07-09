# Vendor Bridge Readiness 与 SDK Handoff 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：🟨 进行中
**日期**：2026-04-10
**范围**：vendor-bridge readiness gate、formal live smoke、repo-only probe 与私有 SDK/live DLL handoff 口径
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: blocked-completed
allow_declare_pass: false
last_updated: "2026-04-13 00:00"
concluded_by: "autopilot"

exit_conditions:
  E1_success_scenarios: completed
  E2_failure_scenarios: completed
  E3_verification_cmds: completed
  E4_evidence_collected: completed
  E5_real_acceptance_only: completed
  E6_minimum_scenarios: completed

scenarios:
  A1: { exec: true, result: pass, blocking: true }
  A2: { exec: true, result: pass, blocking: true }
  A3: { exec: true, result: pass, blocking: true }
  A4: { exec: true, result: pass, blocking: true }
  A5: { exec: true, result: pass, blocking: true }
  A6: { exec: true, result: pass, blocking: false }
```
<!-- AI-STATUS-END -->

## 一、验收目标 / Goals

1. 冻结 vendor-bridge readiness 的正式判定口径。
2. 冻结私有 SDK/live DLL handoff 的输入清单与 blocking 说明。
3. 保证后续 C2 遇到 `sdk-not-found` 时会自动切回同一条 unblock 路线。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `check_rust_gate.py` 的 ready / scaffold-only / sdk-not-found 口径。
2. `ctp_nautilus_live_smoke.py` 的 formal live readiness 结果面。
3. `ctp_repo_debug_smoke.py` 的 repo-only probe 说明。
4. SDK/live DLL handoff checklist 与证据路径。

### 不覆盖（Out of Scope）

1. 把私有 SDK 或 live DLL 纳入 Git 仓库。
2. 直接完成真实 live order 开发。
3. 任何真实交易副作用。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| 当前 C3 blocker evidence 可访问 | 文档 | 是 | 是 | ☑ | 已复用 C3 query/export contract 与 gate blocker 语境 |
| `python scripts/check_rust_gate.py` 可执行 | 脚本 | 是 | 是 | ☑ | 2026-04-11 已复验并产出 A1/A4/A5 |
| `python scripts/check_topic_docs.py` 可执行 | 治理 | 是 | 是 | ☑ | frontier 切换到 U1 后已复验通过 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 正式通过不要求把私有 SDK/live DLL 提交进仓库。
2. 若私有输入缺失，必须给出 blocked 证据，不得把结论写成 ready。
3. test 只能锁定治理与 contract，不替代真实 readiness 判定。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: gate 能明确报告 vendor-bridge ready | `python scripts/check_rust_gate.py` | gate 明确输出 ready 或 scaffold-only | 输出存在稳定 ready/scaffold-only 口径 | 仍需靠人工读源码解释 | `./evidence_a1_gate_contract.md` |
| A2 | Success 2: repo-only probe 不再被误解为 live-ready | `python scripts/ctp_repo_debug_smoke.py` | probe 明确暴露 public scaffold 路径 | 输出中 repo-only / formal-live 路径清楚分离 | operator 仍会把 path A 当成 path B | `./evidence_a2_repo_probe_contract.md` |
| A3 | Success 3: formal live smoke 明确是唯一结果面 | `python scripts/ctp_nautilus_live_smoke.py --config <path>` | 入口与失败语义被固定 | docs/runbook 统一引用 formal live smoke | 仍有多个 competing verdict | `./evidence_a3_formal_live_entrypoint.md` |
| A4 | Failure 1: SDK 缺失时 blocker 明确 | 缺 SDK 条件下执行 gate | 明确得到 `sdk-not-found` 或等价 blocker | failure reason 可直接指向 SDK/live DLL 缺口 | 失败仍被误解释成 auth/front 问题 | `./evidence_a4_sdk_not_found.md` |
| A5 | Failure 2: compat runtime pack 不被误认成 live bridge | 仅存在 `vendor/ctp/bin` compat pack | gate 和 docs 明确说明“不等于 ready” | compat 与 live bridge 区分稳定 | 只因 DLL 在 `vendor/ctp/bin` 就误宣告 ready | `./evidence_a5_compat_not_ready.md` |
| A6 | Boundary 1: 没有私有输入时允许 blocked 交接 | review handoff checklist | blocked 结论仍可作为正式交接结果 | handoff checklist 完整、可复用 | 因缺私有输入而无限停在聊天里 | `./evidence_a6_blocked_handoff.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | Gate contract | `./evidence_a1_gate_contract.md` | readiness gate 口径 |
| 2 | Repo-only probe contract | `./evidence_a2_repo_probe_contract.md` | public scaffold 路径说明 |
| 3 | Formal live entrypoint | `./evidence_a3_formal_live_entrypoint.md` | formal live result 面 |
| 4 | SDK not found | `./evidence_a4_sdk_not_found.md` | 私有输入缺失 blocker |
| 5 | Compat not ready | `./evidence_a5_compat_not_ready.md` | compat pack 边界 |
| 6 | Blocked handoff | `./evidence_a6_blocked_handoff.md` | 无私有输入时的正式交接 |

## 七、未通过处理 / On Failure

1. 回到 `plan.md` 只修口径不一致或 handoff 缺口。
2. 不得把缺私有输入的 blocked 场景改写成通过。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | 已完成（scaffold-only 口径稳定） | 若后续拿到私有输入，再补 ready 分支对照 | `python scripts/check_rust_gate.py` | 输出语义稳定 | 私有输入可能缺失 | `./evidence_a1_gate_contract.md` |
| R2 | A2 | 已完成（repo-only 与 formal-live 已分离） | 无 | `python scripts/ctp_repo_debug_smoke.py` | path A / path B 分离清晰 | 无 | `./evidence_a2_repo_probe_contract.md` |
| R3 | A3 | 已完成（formal live 唯一结果面已固化） | 若后续拿到私有输入，再补 ready 分支对照 | `python scripts/ctp_nautilus_live_smoke.py --config <path>` | docs/runbook 一致 | 私有输入可能缺失 | `./evidence_a3_formal_live_entrypoint.md` |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Governance 锁定 | `python scripts/check_topic_docs.py` | topic queue 与状态不漂移 |
| Governance 锁定 | `python scripts/check_topic_governance.py --root .` | queue 与 bundle 对齐 |

## 十一、最终结论 / Final Verdict

- **结论**：🟨 blocked-completed（场景全 pass，等待外部输入解锁 C2）
- **日期**：2026-04-13
- **执行人**：autopilot
- **建议**：暂不建议宣告通过（需私有 SDK 解锁）
- **说明**：A1-A6 已全部有真实 evidence。P3 已完成：C2 解锁条件已冻结写入 topic README。E3 验证命令已全部执行。由于私有 SDK/live DLL 输入仍未补齐，本 change 正式结果保持 blocked-completed handoff。后续拿到私有输入后沿 gate → formal-live 路径直接进入 C2。