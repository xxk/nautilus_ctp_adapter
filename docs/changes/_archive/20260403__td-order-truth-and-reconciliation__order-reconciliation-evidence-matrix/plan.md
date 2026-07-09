---
change-id: "20260403__td-order-truth-and-reconciliation__order-reconciliation-evidence-matrix"
dependencies:
  hard_blocking:
    - id: "20260403__td-order-truth-and-reconciliation__historical-callback-boundary-policy"
      reason: "需要先完成 boundary policy，才能收口 order truth/reconciliation 的正式 evidence matrix"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Order Reconciliation Evidence Matrix 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、必要时 `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：td-order-truth-and-reconciliation
**change-id**：20260403__td-order-truth-and-reconciliation__order-reconciliation-evidence-matrix
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 收口 order truth/reconciliation 的正式 evidence matrix。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 二、实施结果

1. 已在 `execution_client.py` 中落成 `CtpTdOrderTruthEvidenceMatrix` 与 `capture_td_order_truth_evidence_matrix_mainline(...)`。
2. 已新增真实 live 入口 `scripts/ctp_td_order_truth_evidence_matrix_smoke.py`。
3. 已用真实账户 `025292` 跑通只读 evidence matrix smoke，并收集 raw log 与 evidence 文档。
