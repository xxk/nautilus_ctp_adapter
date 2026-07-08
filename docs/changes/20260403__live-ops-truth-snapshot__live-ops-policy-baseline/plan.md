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

**状态**：blocked
**进度**：65%
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

## 三、当前进展

1. `ops_snapshot.py` 已新增 `CtpLiveOpsPolicyFinding`、`CtpLiveOpsPolicyResult` 与 `CtpLiveOpsEvidenceMatrix`。
2. 已新增脚本入口：
   `scripts/ctp_live_ops_policy_smoke.py`
   `scripts/ctp_live_ops_evidence_matrix_smoke.py`
3. 已完成本地 supporting validation，但真实 `025292` live smoke 在本轮重跑中出现大规模断线噪声，导致 startup/md/td/query 真相同时退化，当前不应宣告通过。

## 四、当前 blocker

1. 当前真实链路出现 `TD Front Disconnected: 4097` 高密度重复断线。
2. 在这轮重跑里，`live_ops_snapshot` 本身也退化成：
   `startup_disposition=manual_review_required`
   `md_disposition=manual_review_required`
   `td_disposition=manual_review_required`
   `position_count=0`
3. 因此 `C2` 当前只能宣告“代码与脚本已落地，真实验收待稳定重跑”，不能把本轮失败重跑当成通过证据。
