# <变更名称> 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：YYYY-MM-DD
**范围**：[影响目录/模块]
**change-id**：{{change-id}}
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：[长期文档主归宿或 无]

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "YYYY-MM-DD HH:MM"
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

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ⬜ 待执行 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 否 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | YYYY-MM-DD HH:MM | |
| AI 执行人 | — | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ⬜ | 阻塞成功场景全部 ✅ | |
| E2 | 关键失败场景符合预期 | ⬜ | 阻塞失败场景全部 ✅ | |
| E3 | 必跑验证命令已完成 | ⬜ | `plan.md` 中声明的必跑命令已执行 | |
| E4 | 关键证据已留存 | ⬜ | 当前 change bundle 中存在证据路径 | |
| E5 | 正式验收不依赖 mock 或 test | ⬜ | 只接受真实入口、真实环境、真实产物与真实证据 | |
| E6 | 正式场景数不少于 6 个 | ⬜ | 少于 6 个时必须存在明确豁免说明 | |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: 主路径成功 | ⬜ | ⬜ | 是 | |
| A2 | Success 2: 次主路径成功 | ⬜ | ⬜ | 是 | |
| A3 | Success 3: 关键变体成功 | ⬜ | ⬜ | 是 | |
| A4 | Failure 1: 关键失败路径 | ⬜ | ⬜ | 是 | |
| A5 | Failure 2: 另一类失败路径 | ⬜ | ⬜ | 是 | |
| A6 | Boundary 1: 边界场景 | ⬜ | ⬜ | 否 | |

## 一、验收目标 / Goals

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. …

### 不覆盖（Out of Scope）

1. …

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| [示例：目标环境可执行 Python] | 环境 | 是 | 是 | ⬜ | |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 任务级边界与必跑验证，以 sibling `plan.md` 为准。
2. `pytest`、`unittest`、`dotnet test` 等测试结果只能作为 contract/function 锁定证据，不能单独充当正式通过依据。
3. 默认至少 6 个正式场景；若少于 6 个，必须填写“豁免说明 / Scenario Waiver”。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 主路径成功 | | | | | |
| A2 | Success 2: 次主路径成功 | | | | | |
| A3 | Success 3: 关键变体成功 | | | | | |
| A4 | Failure 1: 关键失败路径 | | | | | |
| A5 | Failure 2: 另一类失败路径 | | | | | |
| A6 | Boundary 1: 边界场景 | | | | | |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | | | |

## 七、未通过处理 / On Failure

1. 回退到 `plan.md` 重新制定修复计划
2. 不得覆盖已通过的历史证据

## 八、豁免说明 / Scenario Waiver

少于 6 个正式场景时，必须填写本节；否则可删除。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | | | | | | |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Contract 锁定 | | |
| Function 锁定 | | |

## 十一、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：
- **执行人**：
- **建议**：暂不建议宣告通过 / 可宣告通过
- **说明**：
