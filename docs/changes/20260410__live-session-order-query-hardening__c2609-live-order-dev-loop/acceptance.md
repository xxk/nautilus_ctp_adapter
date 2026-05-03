# C2609 Live Order Dev Loop 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-10
**范围**：trade-window preflight、`c2609` 一手 live-send、guardrail reject 与最小 order/trade evidence
**change-id**：20260410__live-session-order-query-hardening__c2609-live-order-dev-loop
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

1. 冻结交易时段真实开发的最小闭环。
2. 证明 preflight、live-send、guardrail reject 三条路径能清楚区分。
3. 为后续 operator playbook 提供真实交易证据。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `ctp_td_order_truth_smoke.py` preflight。
2. `ctp_order_lifecycle_smoke.py` 的单笔 live-send。
3. guardrail violation 的本地拒绝。
4. cancel/fill 或预期失败的结构化证据。

### 不覆盖（Out of Scope）

1. 多合约、多手数、多订单并发。
2. 自动化交易策略。
3. vendor-bridge SDK/live DLL 的私有输入补齐。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| vendor-bridge ready | 环境 | 是 | 是 | ⬜ | 由 sibling handoff change 解锁 |
| 本地 real-account live config 已准备好 | 配置 | 是 | 是 | ⬜ | 使用忽略目录 `cfgs/local/` |
| 当前为交易时段 | 市场窗口 | 否 | 是 | ⬜ | A1/A2 必需 |
| 当前净持仓未突破 `5` 手上限 | 风控 | 否 | 是 | ⬜ | live-send 前必须确认 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. A2 只有在 A1 通过后才允许执行。
2. guardrail 拒绝必须发生在触达 TD 前。
3. test 只能锁定 contract/function，不替代真实交易时段证据。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: trade-window preflight ready | `python scripts/ctp_td_order_truth_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20` | TD readiness 与 order truth 可用 | `ready=true`、`login_success=true` | ready/login 无法判定 | `./evidence_a1_trade_window_preflight.md` |
| A2 | Success 2: `c2609` 一手 live-send 走通 | `python scripts/ctp_order_lifecycle_smoke.py ... --instrument c2609 --quantity 1 --live-send` | submit/cancel/fill 至少一种结果可留证 | `live_send_armed=true` 且有清晰 order/trade 结果 | live-send 与失败原因不可区分 | `./evidence_a2_live_send.md` |
| A3 | Success 3: trade-window evidence 可复盘 | 汇总 A1/A2 产物 | operator 能复盘 session outcome | evidence 路径与字段稳定 | 证据散落或字段不稳定 | `./evidence_a3_trade_window_summary.md` |
| A4 | Failure 1: offhours 不允许误发 live-send | 在非交易时段尝试 `--live-send` | 被 runbook 或脚本明确阻断 | 阻断语义清楚 | 误用被写成模糊连接错误 | `./evidence_a4_offhours_live_send_block.md` |
| A5 | Failure 2: guardrail violation 本地拒绝 | 错误 symbol/qty/position 前置验证 | 在本地被拒绝 | 输出明确 violation | 请求仍触达 TD | `./evidence_a5_guardrail_violation.md` |
| A6 | Boundary 1: cancel/fill 缺一不等于不可复盘 | live order loop 的边界场景 | 允许以结构化“部分完成”留证 | evidence 可复盘当前阶段 | 只能二元成功/失败 | `./evidence_a6_partial_trade_loop.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | trade-window preflight | `./evidence_a1_trade_window_preflight.md` | A1 |
| 2 | live-send result | `./evidence_a2_live_send.md` | A2 |
| 3 | trade-window summary | `./evidence_a3_trade_window_summary.md` | A3 |
| 4 | offhours block | `./evidence_a4_offhours_live_send_block.md` | A4 |
| 5 | guardrail violation | `./evidence_a5_guardrail_violation.md` | A5 |
| 6 | partial loop boundary | `./evidence_a6_partial_trade_loop.md` | A6 |

## 七、未通过处理 / On Failure

1. 回到 `plan.md` 只修当前最小交易路径缺口。
2. 不得为获得“通过”而放宽 guardrails。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | 待执行 | trade-window preflight | `python scripts/ctp_td_order_truth_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20` | ready/login 成功 | vendor bridge、交易窗口 | `./evidence_a1_trade_window_preflight.md` |
| R2 | A2 | 待执行 | 单笔 live-send | `python scripts/ctp_order_lifecycle_smoke.py ... --live-send` | `live_send_armed=true` 且结果可留证 | vendor bridge、交易窗口、仓位上限 | `./evidence_a2_live_send.md` |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Governance 锁定 | `python scripts/check_topic_docs.py` | topic frontier 不漂移 |
| Function 锁定 | `python -m pytest` | 仅锁定 order lifecycle / preflight contract |

## 十一、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：2026-04-10
- **执行人**：—
- **建议**：暂不建议宣告通过
- **说明**：vendor-bridge ready 前，本 change 只作为 Autopilot 的下一批正式执行面，不应误判为可立即开跑。