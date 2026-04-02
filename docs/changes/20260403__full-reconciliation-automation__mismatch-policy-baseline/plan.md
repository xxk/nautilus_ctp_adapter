---
change-id: "20260403__full-reconciliation-automation__mismatch-policy-baseline"
dependencies:
  hard_blocking:
    - id: "20260403__full-reconciliation-automation__live-reconciliation-summary-smoke"
      reason: "需要先继承 live reconciliation summary smoke 的正式输出口径"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Mismatch Policy Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`docs/`、必要时 `scripts/`
**topic-id**：full-reconciliation-automation
**change-id**：20260403__full-reconciliation-automation__mismatch-policy-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 mismatch 分类、阈值和升级口径。
2. 明确哪些 summary 结果只记 evidence，哪些必须标红人工介入。
3. 保持只读。

## 二、实现摘要

1. 在 `src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py` 新增 `CtpReconciliationPolicyFinding`、`CtpReconciliationPolicyResult` 和 policy 评估逻辑。
2. 冻结了当前基线规则：
   `available_ratio < 0.25 -> manual_review_required`
   `margin_ratio > 0.75 -> manual_review_required`
   `dominant_exposure_abs_net_qty >= 10 -> evidence_only`
3. 新增正式 live 入口 `scripts/ctp_reconciliation_policy_smoke.py`。
4. 在 `tests/test_smoke_import.py` 锁住 mismatch policy 的回归契约。

## 三、验收结果

1. 真实 `025292` mismatch policy smoke 已通过。
2. 2026-04-03 实测 `disposition=manual_review_required`。
3. 当前 live findings 已能正式区分 `manual_review_required` 与 `evidence_only`。

## 四、验收说明

1. 本 change 的验收证据只认真实 live smoke 与原始 log。
2. `python -m pytest` 与 `python scripts/check_topic_docs.py` 仅作为 supporting validation，不作为验收证据。
