---
change-id: "20260402__nautilus-live-marketdata__subscription-restore-and-batching"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-marketdata__live-data-client-bootstrap"
      reason: "需要先继承已冻结的 LiveDataClient bootstrap 主线"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Subscription Restore And Batching 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/data_client.py`、当前 change 三件套
**topic-id**：nautilus-live-marketdata
**change-id**：20260402__nautilus-live-marketdata__subscription-restore-and-batching
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 建立 `LiveDataClient` 的订阅恢复规则。
2. 收口 marketdata 事件批量 drain 语义。
3. 为 `C4` 的正式 marketdata smoke baseline 提供稳定入口。

## 二、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 明确订阅恢复状态模型 | topic C3 | data client/runtime docs | 可表达 active subscriptions | `python -m pytest` | topic README | 恢复前置状态清楚 | 已完成 |
| P2 | 冻结批量 drain 与恢复触发点 | acceptance | data client/tests/docs | 稳定 drain/restore contract | `python -m pytest` | architecture doc | C4 可复用 | 已完成 |
| P3 | 回写 topic 队列与状态 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 3 可继续推 C4 | 已完成 |

## 三、完成结论

1. `active_subscription_symbols` 已成为当前恢复入口的稳定状态源。
2. `CtpMdEventBatch` 和 `CtpMdRestoreResult` 已冻结成 C4 可复用的中间模型。
3. 当前恢复动作会复用 `C2` 已冻结的 bootstrap 主线，不另起新通道。
