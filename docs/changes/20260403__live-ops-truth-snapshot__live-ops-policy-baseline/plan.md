---
change-id: "20260403__live-ops-truth-snapshot__live-ops-policy-baseline"
dependencies:
  hard_blocking:
    - id: "20260403__live-ops-truth-snapshot__live-ops-snapshot-baseline"
      reason: "需要先完成 live ops snapshot baseline，才能冻结统一 policy"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Live Ops Policy Baseline 开发计划

**状态**：in_progress
**进度**：15%
**日期**：2026-04-02
**范围**：`scripts/`、`docs/`、`src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：live-ops-truth-snapshot
**change-id**：20260403__live-ops-truth-snapshot__live-ops-policy-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 在统一 `live ops snapshot` 上冻结运维处置 policy。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读，不引入真实交易动作。

## 二、当前计划

1. 定义 snapshot 级 `disposition` 归并规则。
2. 冻结 manual review / rebuild required / restore required / boundary required 的优先级。
3. 为后续 `live ops evidence matrix` 提供稳定 code bucket 输入。

