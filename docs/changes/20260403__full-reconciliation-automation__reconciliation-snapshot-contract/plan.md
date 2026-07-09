---
change-id: "20260403__full-reconciliation-automation__reconciliation-snapshot-contract"
dependencies:
  hard_blocking:
    - id: "20260403__position-account-query-baseline__nautilus-query-adapter-baseline"
      reason: "需要先继承统一 query adapter baseline"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Reconciliation Snapshot Contract 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`scripts/`、`tests/`、`docs/`
**topic-id**：full-reconciliation-automation
**change-id**：20260403__full-reconciliation-automation__reconciliation-snapshot-contract
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 reconciliation snapshot / summary / symbol exposure 的正式 contract。
2. 给 Nautilus 侧提供一个比 `query_adapter` 更靠近“对账输入”的统一入口。
3. 建立正式 smoke 入口和 evidence。
4. 不新增任何真实交易动作。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp_reconciliation_snapshot
- capability_name: CTP Reconciliation Snapshot Baseline
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/full-reconciliation-automation.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/full-reconciliation-automation.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改 `src/nautilus_ctp_adapter/`、`scripts/`、`tests/`、`docs/`
2. 禁止新增真实下单、撤单、改单逻辑
3. 当前正式入口必须落在 `adapters/ctp/` 与 `scripts/`
4. AI 开始前必须阅读 `position-account-query-baseline` topic 和 `query_adapter.py`
5. 改完后必须执行 `python scripts/check_topic_docs.py`、`python -m pytest`

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 reconciliation snapshot / summary contract | capability:ctp_reconciliation_snapshot | `src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py` | dataclass 和 adapter 入口 | `python -m pytest` | topic README | contract 可单测 | 已完成 |
| P2 | 把 contract 接进 factory/export/script | capability:ctp_reconciliation_snapshot | `factory.py`、`__init__.py`、`scripts/ctp_reconciliation_snapshot_smoke.py` | 正式 smoke 入口 | `python -m pytest` | docs index | stack 可消费 | 已完成 |
| P3 | 用真实 `025292` 运行 smoke 留证 | A1 | `docs/changes/...` | evidence + raw log | smoke 命令 | acceptance | 真仓只读 evidence 成立 | 已完成 |

## 八、实现摘要

1. 新增 `src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py`，冻结 `CtpReconciliationSnapshot`、`CtpReconciliationSummary` 和 `CtpReconciliationSymbolExposure`。
2. 在 `factory.py` 和 `adapters/ctp/__init__.py` 挂出正式 adapter 入口。
3. 新增 `scripts/ctp_reconciliation_snapshot_smoke.py` 作为真实只读 smoke 入口。
4. 在 `tests/test_smoke_import.py` 补齐 factory 共享关系和 reconciliation summary 聚合回归测试。

## 九、验收结果

1. 真实 `025292` reconciliation snapshot smoke 已通过。
2. 2026-04-02 实测 `position_line_count=73`、`gross_position_qty=183`、`available_ratio=0.21403`、`margin_ratio=0.780857`。
3. 结果已写入 evidence 和原始 log。

## 十一、长期规则增量摘要 / Long-Term Rule Delta Summary

1. 新增一层正式 contract：`query_adapter` 之上允许定义只读 reconciliation snapshot / summary 入口。
2. 本次仍不宣告“完整自动对账”完成。
