# 最小接入 5 步 / Minimal 5-Step Adoption 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-03-27
**范围**：kit 落地、入口地图、模板落点、真实验证入口、首个试点 change 闭环
**change-id**：20260327__harness-adoption__minimal-5step-adoption
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/doc_harness_kit/跨项目最小接入5步法_Minimal 5-Step Adoption.md

> 这是跨项目示例文件。复制到目标项目后，必须替换路径、正式入口和验证命令。

---

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-03-27 HH:MM"
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

## 一、验收目标

1. 证明目标项目已完成 `Doc Harness Kit` 的最小接入 5 步。
2. 证明当前 change 本身已经作为第一个真实试点 change 跑通。

---

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ⬜ 待执行 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 否 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-03-27 HH:MM | |
| AI 执行人 | — | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ⬜ | 阻塞成功场景全部 ✅ | |
| E2 | 关键失败场景符合预期 | ⬜ | 阻塞失败场景全部 ✅ | |
| E3 | 必跑验证命令已完成 | ⬜ | `plan.md` 中声明的必跑命令已执行 | |
| E4 | 关键证据已留存 | ⬜ | 当前 change bundle 中存在证据路径 | |
| E5 | 正式验收不依赖 test、mock、fake | ⬜ | 只接受真实入口、真实环境、真实产物与真实证据；test/mock/fake 只能作为补充锁定证据 | |
| E6 | 正式场景数不少于 5 且至少 1 个 failure | ⬜ | 少于 5 个或没有 failure 场景时必须存在明确豁免说明 | |

## 二、验收范围

### 覆盖（In Scope）

1. kit 目录落地
2. 入口地图与正式导航
3. change 模板落点
4. 真实验证入口替换
5. 当前 change 自身的 evidence 闭环

### 不覆盖（Out of Scope）

1. Full 档治理增强
2. 完整守卫脚本实现
3. 远端高风险部署链路

---

## 三、前置条件

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| 目标项目允许创建文档和模板目录 | 环境 | 是 | 是 | ⬜ | |
| 目标项目存在至少一个可确认的正式入口 | 文档 | 否 | 是 | ⬜ | |
| 目标项目存在至少一个可执行验证命令 | 工具 | 否 | 是 | ⬜ | |

---

## 三点五、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 任务级边界与必跑验证，以 sibling `plan.md` 为准。
2. test、mock、fake 只能作为 contract/function 锁定证据，不能充当正式验收证据。
3. 正式验收场景不得少于 5 个，且至少要有 1 个 failure 场景。

---

## 四、场景看板

| # | 场景 | 执行 | 结论 | 阻塞 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | kit 目录已落地 | ⬜ | ⬜ | 是 | |
| A2 | 入口地图已建立 | ⬜ | ⬜ | 是 | |
| A3 | change 模板落点已建立 | ⬜ | ⬜ | 是 | |
| A4 | 真实验证入口已替换 | ⬜ | ⬜ | 是 | |
| A5 | 当前 change 已作为第一个真实试点 change 跑通 | ⬜ | ⬜ | 是 | |
| A6 | 至少一个失败口径已明确 | ⬜ | ⬜ | 否 | |

---

## 五、验收场景

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | kit 目录已落地 | 查看 `docs/doc_harness_kit/` | 目录与关键文档存在 | `README.md` 可打开 | 只复制了零散文件 | |
| A2 | 入口地图已建立 | 阅读入口地图与导航索引 | AI 可定位正式入口 | 入口地图存在且能指向正式入口 | 仍需靠聊天补充入口 | |
| A3 | change 模板落点已建立 | 检查 `docs/changes/` | 可创建真实 change bundle | 模板目录存在 | 只有 kit，没有真实落点 | |
| A4 | 真实验证入口已替换 | 执行目标项目最小验证命令 | 命令存在且可执行 | 退出码=0 或文档明确可替换路径 | 仍保留示例仓命令占位 | |
| A5 | 当前 change 已作为第一个真实试点 change 跑通 | 检查当前 change 的 evidence 回填 | 这次 change 本身就是第一笔试点留证 | evidence 完整且结论可追溯 | 还要另开一笔试点才能算通过 | |
| A6 | Failure 1: 示例命令未替换时不得宣告通过 | 对照当前 acceptance 与目标项目命令 | 保持 pending 或明确失败 | 不会把示例仓命令占位误写成真实接入成功 | 仍保留示例命令却宣告通过 | |

---

## 六、未通过处理 / On Failure

1. 回退到 `plan.md` 重新制定修复计划。
2. 不得覆盖已通过的历史证据。

## 七、豁免说明 / Scenario Waiver

少于 5 个正式场景，或没有 failure 场景时，必须填写本节；否则可删除。

## 八、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A4 | 未执行 | 跑目标项目真实最小验证命令 | `<target-project-real-command>` | 命令可执行且结果可观察 | 目标项目命令待替换 | |

## 九、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Contract 锁定 | | |
| Function 锁定 | | |

## 十、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：
- **执行人**：
- **建议**：暂不建议宣告通过
- **说明**：

## 十一、关键说明

这份 change 的设计目的，就是让它在目标项目里同时承担两件事：

1. 完成最小接入 5 步
2. 作为第一个真实试点 change

所以，**是的，只要这份 change 在目标项目里真实执行并留证，它本身就可以算完成这张清单。**
