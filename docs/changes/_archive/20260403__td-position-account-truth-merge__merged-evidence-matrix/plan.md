---
change-id: "20260403__td-position-account-truth-merge__merged-evidence-matrix"
dependencies:
  hard_blocking:
    - id: "20260403__td-position-account-truth-merge__merged-reconciliation-policy"
      reason: "需要先完成 merged reconciliation policy，才能把结果收口成 evidence matrix"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Merged Evidence Matrix 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、`src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：td-position-account-truth-merge
**change-id**：20260403__td-position-account-truth-merge__merged-evidence-matrix
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把 merged truth 与 merged policy 收口成稳定 evidence matrix。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读，不引入真实交易动作。

## 二、实施结果

1. 已在 `truth_merge.py` 中新增 `CtpTdMergedEvidenceMatrix`。
2. 已新增真实 live 入口 `scripts/ctp_td_merged_evidence_matrix_smoke.py`。
3. 已用真实账户 `025292` 跑通 merged evidence matrix smoke，并收集 raw log 与 evidence 文档。

