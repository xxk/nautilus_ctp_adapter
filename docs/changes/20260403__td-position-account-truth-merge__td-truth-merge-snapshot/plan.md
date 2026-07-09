---
change-id: "20260403__td-position-account-truth-merge__td-truth-merge-snapshot"
dependencies:
  hard_blocking:
    - id: "20260403__td-order-truth-and-reconciliation__order-reconciliation-evidence-matrix"
      reason: "需要先完成 TD order truth evidence，才能把 callback truth 与 query baseline 合并成统一 snapshot"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# TD Truth Merge Snapshot 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、必要时 `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：td-position-account-truth-merge
**change-id**：20260403__td-position-account-truth-merge__td-truth-merge-snapshot
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 收口 order/trade/position/account 的只读 truth merge snapshot。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 二、实施结果

1. 已新增 `truth_merge.py`，落成 `CtpTruthMergeAdapter` 与 `CtpTdTruthMergeSnapshot`。
2. 已新增真实 live 入口 `scripts/ctp_td_truth_merge_snapshot_smoke.py`。
3. 已用真实账户 `025292` 跑通 merged snapshot smoke，并收集 raw log 与 evidence 文档。
