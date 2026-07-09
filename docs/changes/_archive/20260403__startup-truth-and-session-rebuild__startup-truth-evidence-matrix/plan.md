---
change-id: "20260403__startup-truth-and-session-rebuild__startup-truth-evidence-matrix"
dependencies:
  hard_blocking:
    - id: "20260403__startup-truth-and-session-rebuild__session-rebuild-policy"
      reason: "需要先继承 session rebuild policy 的正式判定口径"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Startup Truth Evidence Matrix 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、必要时 `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：startup-truth-and-session-rebuild
**change-id**：20260403__startup-truth-and-session-rebuild__startup-truth-evidence-matrix
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 收口 startup truth 与 session rebuild 的正式 evidence 矩阵。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 二、实施结果

1. 已在 `startup_truth.py` 中落成 `CtpStartupTruthEvidenceMatrix` 与 `capture_evidence_matrix_mainline(...)`。
2. 已新增真实 live 入口 `scripts/ctp_startup_truth_evidence_matrix_smoke.py`。
3. 已用真实账户 `025292` 跑通 live smoke，并收集 raw log 与 evidence 文档。
