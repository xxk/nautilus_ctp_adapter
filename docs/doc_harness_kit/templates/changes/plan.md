---
change-id: "{{change-id}}"
dependencies:
  hard_blocking: []
  soft_dependency: []
  blocked_by: []
---

# <变更名称> 开发计划

**状态**：draft
**进度**：0%
**日期**：YYYY-MM-DD
**范围**：[影响目录/模块]
**topic-id**：{{topic-id}}
**change-id**：{{change-id}}
**关联 acceptance**：./acceptance.md

> 默认采用 `plan.md + acceptance.md + ai_constraints.md` 三件套。若存在明显方案分叉、正式入口容易改错、或需要冻结长期接口与目录归属，可额外创建 sibling `design.md`。

## 一、需求简述

1. 本 change 要解决什么问题
2. 明确交付什么
3. 明确不做什么
4. 用什么真实信号判断“真的做成了”

## 二、能力映射 / Capability Mapping

```text
- capability_id: <稳定主题标识>
- capability_name: <中文主题 / English Topic>
- long_term_target: <长期文档路径或 无>
- secondary_targets: <次级回写目标或 无>
- decision_target: <README / architecture 路径或 无>
- affects_long_term_rules: 是 / 否
- change_type: 新增规则 / 修改规则 / 废弃规则 / 纯实现 / 验证确认
```

## 三、AI 执行约束

至少写清楚：

1. 允许修改哪些目录或文件
2. 禁止修改哪些目录或文件
3. 当前正式入口与主要实现落点
4. AI 开始前必须阅读的上下文文档
5. 改完后必须执行的验证命令

## 四、背景与约束（可选）

## 五、设计方案（可选）

## 六、阶段划分（可选）

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | <示例：冻结正式入口与配置口径> | <A1 / capability:xxx> | <文件路径> | <文档或实现> | <命令> | <长期文档路径或 无> | <通过信号> | 未开始 |

状态建议统一使用：`未开始`、`进行中`、`已完成`、`阻塞`。

## 八、任务说明（可选）

## 九、验证动作（可选）

## 十、完成定义（可选）

### 开发完成

1. 实现与文档修改完成
2. 最小验证已执行
3. 已具备进入正式验收的前提

### 交付完成

1. `acceptance.md` 中阻塞场景通过
2. 证据留存在当前 change bundle
3. 需要回写的长期文档已回写，或已记录暂不回写原因

## 十一、长期规则增量摘要 / Long-Term Rule Delta Summary

若 `change_type` 不是纯实现，可在此总结新增、修改或废弃的长期规则；否则显式写“本次无长期规则增量”。

## 十二、回写与相关变更 / Write-back & Related Changes

当 `long_term_target != 无` 时，收尾前必须说明：

1. 是否完成长期文档回写
2. 是否需要在长期文档底部登记 `Related Changes`

## 十三、阻塞项（可选）

## 十四、进度记录（可选）
