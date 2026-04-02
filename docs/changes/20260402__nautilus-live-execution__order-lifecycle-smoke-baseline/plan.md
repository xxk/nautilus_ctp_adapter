---
change-id: "20260402__nautilus-live-execution__order-lifecycle-smoke-baseline"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-execution__live-execution-client-bootstrap"
      reason: "需要先继承最小 LiveExecutionClient 主线"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Order Lifecycle Smoke Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、当前 change 三件套
**topic-id**：nautilus-live-execution
**change-id**：20260402__nautilus-live-execution__order-lifecycle-smoke-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 Topic 4 的正式 execution smoke 入口。
2. 明确 order lifecycle baseline 的最小成功信号。
3. 在 guardrails 前提下完成一次真实 `IOC + 跌停价` 下单验证，并确认不形成净持仓。

## 二、当前进展

1. dry-run 正式入口已经稳定，且能输出结构化 `matched_execs / exec_events` 证据。
2. fake/native-drift 场景下，仓内已能把 native `ORDER / TRADE` 回报回绑到 Python 侧 smoke `client_order_id`。
3. 真实 live smoke 默认改为唯一 TD flow 目录后，正式脚本已能稳定匹配 `c2609` 的发送后回报，当前 change 已达到出口条件。
