---
change-id: "20260403__live-ops-truth-snapshot__live-ops-snapshot-baseline"
dependencies:
  hard_blocking:
    - id: "20260403__td-position-account-truth-merge__merged-evidence-matrix"
      reason: "需要先完成 merged truth evidence，才能把 startup/md/td/reconciliation 收进统一 ops snapshot"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Live Ops Snapshot Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、`src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：live-ops-truth-snapshot
**change-id**：20260403__live-ops-truth-snapshot__live-ops-snapshot-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 收口 startup truth、MD truth、TD merged truth 与 reconciliation 的统一只读 snapshot。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读，不引入真实交易动作。

## 二、实施结果

1. 已新增 `ops_snapshot.py`，落成 `CtpLiveOpsSnapshotAdapter`、`CtpLiveOpsSnapshot` 与 `CtpLiveOpsSnapshotSummary`。
2. 已新增真实 live 入口 `scripts/ctp_live_ops_snapshot_smoke.py`。
3. 已用真实账户 `025292` 跑通 live ops snapshot smoke，并收集 raw log 与 evidence 文档。

