# 最小接入 5 步 / Minimal 5-Step Adoption 开发计划

**状态**：draft
**进度**：0%
**日期**：2026-03-27
**范围**：目标项目的 `docs/`、入口地图、`docs/changes/` 模板落点、验证入口文档
**topic-id**：harness-adoption
**change-id**：20260327__harness-adoption__minimal-5step-adoption
**关联 acceptance**：./acceptance.md

> 这是跨项目示例文件。复制到目标项目后，必须替换 `topic-id`、`change-id`、路径、入口名和验证命令。
> AI 阅读入口：先读 acceptance.md 的验收目标与失败口径，再读本文的任务清单与完成定义，最后按 sibling `ai_constraints.md` 推进。

---

## 一、需求简述

当前目标不是实现业务功能，而是让目标项目完成 `Doc Harness Kit` 的最小接入闭环。

本次明确交付：

1. `Doc Harness Kit` 已复制到目标项目
2. 目标项目已建立入口地图
3. 目标项目已建立 change 模板落点
4. 目标项目已替换真实验证入口
5. 当前 change 自身成为第一个真实试点 change

本次明确不做：

1. 不补完整守卫脚本实现
2. 不强推 Full 档治理
3. 不在本轮引入远端高风险链路改造

验收信号：目标项目已完成最小接入 5 步，并且当前 change 留证完整、可追溯。

---

## 二、能力映射 / Capability Mapping

```text
- capability_id: harness-minimal-adoption
- capability_name: 最小接入闭环 / Minimal Harness Adoption
- long_term_target: docs/doc_harness_kit/跨项目最小接入5步法_Minimal 5-Step Adoption.md
- secondary_targets: docs/doc_harness_kit/adoption_guide.md
- decision_target: 无
- affects_long_term_rules: 是
- change_type: 新增规则
```

---

## 三、AI 执行约束

1. 允许修改：目标项目中的入口地图、导航文档、`docs/changes/` 模板落点、接入验证文档、当前 change bundle。
2. 禁止修改：与接入无关的业务逻辑、远端部署脚本、数据库结构。
3. 必须先建立入口和模板落点，再讨论“是否接入完成”。
4. 必须把验证命令替换为目标项目真实存在的入口，禁止保留示例仓命令占位。
5. 必须把当前 change 自身当成第一个真实试点 change，而不是另起一笔匿名试点。

---

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 复制并落地 kit 目录 | A1 | `docs/doc_harness_kit/` | 套件骨架 | 目录检查 | `long_term_target` | 目标项目可打开 kit 入口 | 未开始 |
| P2 | 建立入口地图与正式导航 | A2 | 入口地图文件、导航索引 | 正式入口说明 | 文档检查 | `secondary_targets` | AI 可定位正式入口 | 未开始 |
| P3 | 建立 change 模板落点 | A3 | `docs/changes/` | 模板落点 | 目录检查 | `secondary_targets` | 可创建真实 change bundle | 未开始 |
| P4 | 替换真实验证入口 | A4 | 验证说明文档 | 项目真实命令 | 执行最小命令验证 | `secondary_targets` | 至少一个验证入口真实可用 | 未开始 |
| P5 | 执行当前 change 并留证 | E1-E4 | 当前 change bundle | evidence 与结论 | 见 acceptance.md | 当前 change | 本 change 成为第一个真实试点 change | 未开始 |

---

## 五、完成定义

### 开发完成

1. 目标项目已具备 kit 目录、入口地图、change 模板落点和真实验证入口。
2. 当前 change 已具备进入验收的前提。

### 交付完成

1. acceptance.md 中阻塞场景全部通过。
2. 当前 change 被确认为第一个真实试点 change。
3. 证据路径已回填。
