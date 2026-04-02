---
change-id: "20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-marketdata__subscription-restore-and-batching"
      reason: "需要先继承已冻结的 restore / batching contract"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Nautilus Marketdata Smoke Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、当前 change 三件套
**topic-id**：nautilus-live-marketdata
**change-id**：20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 Topic 3 的正式行情 smoke 入口。
2. 证明 `rb2610` 可经当前 `LiveDataClient` 主线重复收取真实行情。
3. 为 Topic 4 提供稳定的数据侧前置验证命令。

## 二、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立正式 marketdata smoke 入口 | topic C4 | scripts/data client/docs | 可重复执行的 smoke 脚本 | live smoke | topic README | 正式入口清楚 | 已完成 |
| P2 | 冻结证据格式 | acceptance | 当前 change 三件套 | 可交接证据 | 文档检查 | docs index | Topic 4 可复用 | 已完成 |
| P3 | 回写 topic 队列与状态 | governance | 当前 change 三件套 / topic README | 可关闭 Topic 3 | 文档检查 | mainline roadmap | Topic 4 可进入 | 已完成 |

## 三、完成结论

1. `ctp_marketdata_smoke.py` 已成为 Topic 3 的正式 smoke 入口。
2. `rb2610` 已通过当前 `LiveDataClient` 主线收到真实 tick。
3. Topic 3 已达到 topic 级出口条件，可进入 Topic 4。
