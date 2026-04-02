---
change-id: "20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline"
dependencies:
  hard_blocking:
    - id: "20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy"
      reason: "需要先继承 Topic 5 已冻结的恢复边界与人工介入规则"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Audit And Reconciliation Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`docs/`、必要时 `scripts/`
**topic-id**：live-ops-and-reconciliation
**change-id**：20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结最小审计证据链和对账基线。
2. 明确市场数据、订单、成交、持仓、资金五类证据如何留存。
3. 规定“可自动判断的一致性”和“必须人工复核的不一致性”。
4. 给 Topic 5 最终 operational evidence matrix 提供基础结构。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ops.audit_and_reconciliation_baseline
- capability_name: Audit And Reconciliation Baseline
- long_term_target: D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md
- secondary_targets: D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- decision_target: D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 优先冻结规则和证据结构，不默认扩展 live 行为。
2. 不修改 Topic 1-4 已冻结的 mainline contract。
3. 改完后至少执行 `python scripts/check_topic_docs.py` 与 `python -m pytest`。

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结五类证据链结构 | capability:ops.audit_and_reconciliation_baseline | `docs/` | audit baseline 文档 | `python scripts/check_topic_docs.py` | Topic 5 README | 自动证据与人工复核边界明确 | 已完成 |
| P2 | 冻结最小自动对账规则 | capability:ops.audit_and_reconciliation_baseline | `docs/` | 自动判断 vs 人工复核清单 | `python -m pytest` | Topic 5 README | 不再把能力预留误写成已完成对账 | 已完成 |
| P3 | 留证并前推队列 | capability:ops.audit_and_reconciliation_baseline | 当前 change bundle | evidence + acceptance | `python -m pytest` | 当前 change bundle | 可支持切到 `C4` | 已完成 |
