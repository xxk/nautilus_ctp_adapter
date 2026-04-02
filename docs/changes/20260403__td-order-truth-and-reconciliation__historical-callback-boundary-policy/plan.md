---
change-id: "20260403__td-order-truth-and-reconciliation__historical-callback-boundary-policy"
dependencies:
  hard_blocking:
    - id: "20260403__td-order-truth-and-reconciliation__td-order-truth-baseline"
      reason: "需要先固定真实 callback truth baseline，才能冻结历史回报与当前 session 的边界 policy"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Historical Callback Boundary Policy 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、必要时 `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：td-order-truth-and-reconciliation
**change-id**：20260403__td-order-truth-and-reconciliation__historical-callback-boundary-policy
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结历史回报、延迟回报与当前 session 真相的边界 policy。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 二、实施结果

1. 已在 `execution_client.py` 中落成 `CtpTdHistoricalCallbackBoundaryPolicyResult` 与 `capture_historical_callback_boundary_policy_mainline(...)`。
2. 已新增真实 live 入口 `scripts/ctp_td_historical_callback_boundary_smoke.py`。
3. 已用真实账户 `025292` 跑通只读 callback boundary smoke，并收集 raw log 与 evidence 文档。
