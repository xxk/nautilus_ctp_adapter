# 统一运行入口 / Unified Run Entrypoint 开发计划

**状态**：draft
**进度**：0%
**日期**：2026-03-27
**范围**：`scripts/`、`docs/architecture/`、`docs/changes/20260327__project-entry__unified-run-entrypoint/`
**topic-id**：project-entry
**change-id**：20260327__project-entry__unified-run-entrypoint
**关联 acceptance**：./acceptance.md

> 这是跨项目示例文件。复制到目标项目后，必须替换 `topic-id`、`change-id`、目录边界、正式入口与验证命令。
> AI 阅读入口：先读 acceptance.md 的验收目标与禁止行为，再读本文的任务清单与完成定义，最后按 sibling `ai_constraints.md` 推进。

---

## 一、需求简述

当前项目存在多个历史运行入口，导致人和 AI 都容易在错误入口上继续叠代码。

本次明确交付：

1. 选定一个正式运行入口
2. 保留必要的兼容入口说明或过渡行为
3. 更新导航与入口文档

本次明确不做：

1. 不重写全部历史脚本
2. 不在本轮处理部署自动化
3. 不引入新的运行模式

验收信号：正式入口可执行，兼容入口行为明确，文档能指向唯一正式入口。

---

## 二、能力映射 / Capability Mapping

```text
- capability_id: project-entry
- capability_name: 运行入口治理 / Entrypoint Governance
- long_term_target: docs/architecture/正式入口与兼容入口清单.md
- secondary_targets: docs/architecture/AI开发导航总览.md
- decision_target: 无
- affects_long_term_rules: 是
- change_type: 修改规则
```

---

## 三、AI 执行约束

1. 允许修改：入口文档、导航文档、正式入口脚本、兼容入口说明。
2. 禁止修改：与入口无关的业务逻辑、部署脚本、数据库逻辑。
3. 正式入口应只有一个，兼容入口只能做过渡，不得继续承载真实实现。
4. AI 开始前必须先确认当前项目“哪个入口才是正式入口”，若不清楚，先补文档再编码。
5. 改完后必须执行至少一个正式入口命令验证，以及一个兼容入口行为验证。

---

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 确认正式入口与兼容入口 | A1 / A2 | `docs/architecture/正式入口与兼容入口清单.md` | 入口口径 | 对照现状检查 | `long_term_target` | 唯一正式入口已明确 | 未开始 |
| P2 | 收口入口实现落点 | A1 | `scripts/run.py` 或目标项目正式入口 | 统一入口实现 | `python <正式入口> --help` | `long_term_target` | 正式入口可执行 | 未开始 |
| P3 | 处理兼容入口 | A2 | 兼容脚本或兼容说明 | 兼容策略 | `python <兼容入口> --help` 或显式失败验证 | `long_term_target` | 兼容入口行为明确 | 未开始 |
| P4 | 更新导航文档 | A3 | `docs/architecture/AI开发导航总览.md` | 导航回链 | 文档检查 | `secondary_targets` | 导航已指向正式入口 | 未开始 |
| P5 | 执行验收并留证 | E1-E4 | 当前 change bundle | 验收记录 | 见 acceptance.md | 当前 change | 证据完整可追溯 | 未开始 |

---

## 五、完成定义

### 开发完成

1. 正式入口已明确并可执行
2. 兼容入口行为已定义
3. 导航文档已更新
4. 当前 change 已具备进入验收的前提

### 交付完成

1. acceptance.md 中阻塞场景全部通过
2. 证据路径已回填
3. 长期入口文档已完成回写

---

## 六、长期规则增量摘要 / Long-Term Rule Delta Summary

```text
### 新增规则
- 项目必须只有一个正式运行入口。

### 修改规则
- 兼容入口不得继续承载真实实现，只能承担过渡或显式失败提示。

### 废弃规则
- 多个并行入口同时作为正式入口的口径。
```
