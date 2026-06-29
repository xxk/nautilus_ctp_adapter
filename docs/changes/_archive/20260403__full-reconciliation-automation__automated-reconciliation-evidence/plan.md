---
change-id: "20260403__full-reconciliation-automation__automated-reconciliation-evidence"
dependencies:
  hard_blocking:
    - id: "20260403__full-reconciliation-automation__mismatch-policy-baseline"
      reason: "需要先继承 mismatch policy baseline 的正式判定口径"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Automated Reconciliation Evidence 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-03
**范围**：`scripts/`、`docs/`、必要时 `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：full-reconciliation-automation
**change-id**：20260403__full-reconciliation-automation__automated-reconciliation-evidence
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把 reconciliation summary + mismatch policy 输出收口成更稳定的自动 evidence 格式。
2. 保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 二、实现摘要

1. 在 `src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py` 新增 `CtpReconciliationEvidence` 以及 `build_evidence(...) / capture_evidence_mainline(...)`。
2. 新增正式 live 入口 `scripts/ctp_reconciliation_evidence_smoke.py`。
3. 在 `tests/test_smoke_import.py` 锁住 automated evidence 的回归契约。
4. 使用真实账户 `025292` 运行 automated evidence smoke，并把原始输出落到当前 change bundle。

## 三、验收结果

1. 真实 `automated reconciliation evidence smoke` 已通过。
2. 2026-04-03 实测 `disposition=manual_review_required`，`manual_review_codes=[available_ratio_warn, margin_ratio_warn]`，`evidence_only_codes=[dominant_exposure_watch]`。
3. 当前仓内已经具备正式、机器可读的 automated evidence 输出。

## 四、验收说明

1. 本 change 的验收证据只认真实 live smoke 与原始 log。
2. `python -m pytest`、`python scripts/check_topic_docs.py` 和 `python -m pip install -e .` 仅作为 supporting validation，不作为验收证据。
