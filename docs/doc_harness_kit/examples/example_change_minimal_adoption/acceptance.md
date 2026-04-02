# 最小接入 5 步 / Minimal 5-Step Adoption 验收方案 / Acceptance Plan

**状态**：⬜ 待执行
**日期**：2026-03-27
**change-id**：20260327__harness-adoption__minimal-5step-adoption
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md

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

scenarios:
  A1: { exec: false, result: null, blocking: true }
  A2: { exec: false, result: null, blocking: true }
  A3: { exec: false, result: null, blocking: true }
  A4: { exec: false, result: null, blocking: true }
  A5: { exec: false, result: null, blocking: true }
```
<!-- AI-STATUS-END -->

## 一、验收目标

1. 证明目标项目已完成 `Doc Harness Kit` 的最小接入 5 步。
2. 证明当前 change 本身已经作为第一个真实试点 change 跑通。

---

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

## 四、场景看板

| # | 场景 | 执行 | 结论 | 阻塞 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | kit 目录已落地 | ⬜ | ⬜ | 是 | |
| A2 | 入口地图已建立 | ⬜ | ⬜ | 是 | |
| A3 | change 模板落点已建立 | ⬜ | ⬜ | 是 | |
| A4 | 真实验证入口已替换 | ⬜ | ⬜ | 是 | |
| A5 | 当前 change 已作为第一个真实试点 change 跑通 | ⬜ | ⬜ | 是 | |

---

## 五、验收场景

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | kit 目录已落地 | 查看 `docs/doc_harness_kit/` | 目录与关键文档存在 | `README.md` 可打开 | 只复制了零散文件 | |
| A2 | 入口地图已建立 | 阅读入口地图与导航索引 | AI 可定位正式入口 | 入口地图存在且能指向正式入口 | 仍需靠聊天补充入口 | |
| A3 | change 模板落点已建立 | 检查 `docs/changes/` | 可创建真实 change bundle | 模板目录存在 | 只有 kit，没有真实落点 | |
| A4 | 真实验证入口已替换 | 执行目标项目最小验证命令 | 命令存在且可执行 | 退出码=0 或文档明确可替换路径 | 仍保留示例仓命令占位 | |
| A5 | 当前 change 已作为第一个真实试点 change 跑通 | 检查当前 change 的 evidence 回填 | 这次 change 本身就是第一笔试点留证 | evidence 完整且结论可追溯 | 还要另开一笔试点才能算通过 | |

---

## 六、出口条件

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ⬜ | A1-A5 全通过 | |
| E2 | 失败口径明确 | ⬜ | 任一步失败时能指出缺哪一步 | |
| E3 | 必跑验证已执行 | ⬜ | A4 至少执行一次真实命令验证 | |
| E4 | 关键证据已留存 | ⬜ | A1-A5 均有 evidence | |

---

## 七、关键说明

这份 change 的设计目的，就是让它在目标项目里同时承担两件事：

1. 完成最小接入 5 步
2. 作为第一个真实试点 change

所以，**是的，只要这份 change 在目标项目里真实执行并留证，它本身就可以算完成这张清单。**
