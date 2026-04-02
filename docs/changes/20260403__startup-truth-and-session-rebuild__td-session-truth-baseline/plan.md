---
change-id: "20260403__startup-truth-and-session-rebuild__td-session-truth-baseline"
dependencies:
  hard_blocking:
    - id: "20260403__full-reconciliation-automation__automated-reconciliation-evidence"
      reason: "需要先继承上一轮完成的 live evidence 治理口径"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# TD Session Truth Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-03
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`scripts/`、`docs/`
**topic-id**：startup-truth-and-session-rebuild
**change-id**：20260403__startup-truth-and-session-rebuild__td-session-truth-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 TD startup truth 的正式 contract。
2. 建立真实 `025292` 的 live startup truth smoke 与 evidence。
3. 明确 flow path、session identity、disconnect 记录的基础口径。
4. 保持只读，不使用 test/mock/fake 作为验收证据。

## 二、实现摘要

1. 新增 `src/nautilus_ctp_adapter/adapters/ctp/startup_truth.py`，冻结 `CtpTdStartupTruthEvidence` 与 `CtpStartupTruthAdapter`。
2. 在 `factory.py` 与 `adapters/ctp/__init__.py` 挂出正式 startup truth 入口。
3. 新增真实 live 入口 `scripts/ctp_startup_truth_smoke.py`。
4. 在 `tests/test_smoke_import.py` 补齐 factory 共享关系与 startup truth contract 回归。

## 三、验收结果

1. 真实 `025292` startup truth smoke 已通过。
2. 2026-04-03 实测 `flow_mode=default_shared_flow`、`ready=true`、`login_success=true`、`settlement_code=0`、`front_id=11`、`session_id=386081387`。
3. 当前仓内已经具备正式 TD startup truth live baseline。

## 四、验收说明

1. 本 change 的验收证据只认真实 live smoke 与原始 log。
2. `python -m pytest` 与 `python scripts/check_topic_docs.py` 仅作为 supporting validation，不作为验收证据。
