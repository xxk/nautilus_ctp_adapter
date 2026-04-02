---
change-id: "20260403__full-reconciliation-automation__live-reconciliation-summary-smoke"
dependencies:
  hard_blocking:
    - id: "20260403__full-reconciliation-automation__reconciliation-snapshot-contract"
      reason: "需要先继承 reconciliation snapshot contract"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Live Reconciliation Summary Smoke 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、必要时 `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：full-reconciliation-automation
**change-id**：20260403__full-reconciliation-automation__live-reconciliation-summary-smoke
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把 reconciliation summary smoke 变成正式的 live evidence 入口。
2. 明确 summary 字段、排序口径和 diagnostics 留证。
3. 保持只读。

## 二、实现摘要

1. 在 `src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py` 增加 `gross_qty`、`abs_net_qty` 和 dominant exposure 聚合字段。
2. 在 `scripts/ctp_reconciliation_snapshot_smoke.py` 输出更稳定的 live summary 字段和排序后的 `top_exposures`。
3. 在 `tests/test_smoke_import.py` 锁住 summary 排序和 dominant exposure 口径。
4. 使用真实账户 `025292` 重新运行 summary smoke，并把原始输出落到当前 change bundle。

## 三、验收结果

1. 真实 `live reconciliation summary smoke` 已通过。
2. 2026-04-02 实测 `account_id=025292`、`gross_position_qty=183`、`available_ratio=0.214403`、`margin_ratio=0.780486`。
3. 当前 `dominant_exposure_symbol` 为 `m2605-P-3000`，`dominant_exposure_abs_net_qty=10`。

## 四、验收说明

1. 本 change 的验收证据只认真实 live smoke 与原始 log。
2. `python -m pytest` 与 `python scripts/check_topic_docs.py` 仅作为 supporting validation，不作为验收证据。
