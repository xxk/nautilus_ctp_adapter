---
change-id: "20260403__md-startup-truth-and-restore__md-startup-truth-baseline"
dependencies:
  hard_blocking:
    - id: "20260403__startup-truth-and-session-rebuild__startup-truth-evidence-matrix"
      reason: "需要先完成 TD startup truth/evidence matrix，确保 MD topic 延续同样的 real-only 证据治理"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# MD Startup Truth Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、必要时 `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：md-startup-truth-and-restore
**change-id**：20260403__md-startup-truth-and-restore__md-startup-truth-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 收口 MD login、subscribe、first tick 的正式 startup truth baseline。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 二、实施结果

1. 已在 `data_client.py` 中落成 `CtpMdStartupTruthEvidence` 与 `capture_md_startup_truth_mainline(...)`。
2. 已新增真实 live 入口 `scripts/ctp_md_startup_truth_smoke.py`。
3. 已用真实账户 `025292` 跑通 `rb2610` live smoke，并收集 raw log 与 evidence 文档。
