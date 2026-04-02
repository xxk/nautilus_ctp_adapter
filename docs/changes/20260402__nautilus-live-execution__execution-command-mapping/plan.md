---
change-id: "20260402__nautilus-live-execution__execution-command-mapping"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-execution__td-mainline-login-bootstrap"
      reason: "需要先继承正式 TD bootstrap 主线"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Execution Command Mapping 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、当前 change 三件套
**topic-id**：nautilus-live-execution
**change-id**：20260402__nautilus-live-execution__execution-command-mapping
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结下单撤单命令映射。
2. 明确 `order_ref / front_id / session_id / error_id` 在 execution 侧的稳定表达。
3. 为后续 `LiveExecutionClient` 和 order lifecycle smoke 提供正式 contract。

## 二、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 submit/cancel 中间模型 | topic C2 | execution client/tests | 稳定 mapping DTO | `python -m pytest` | architecture doc | 后续不再漂移 | 已完成 |
| P2 | 固化 identity 与错误表达 | acceptance | execution client/tests/docs | 稳定 identity/error shape | `python -m pytest` | topic README | C3/C4 可复用 | 已完成 |
| P3 | 回写 topic 队列与状态 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 4 可继续推 C3 | 已完成 |

## 三、完成结论

1. execution 侧已有稳定的 submit/cancel mapping contract。
2. `order_ref / front_id / session_id / error_id` 的表达已冻结。
3. Topic 4 的下一个 implementation change 可以直接进入 `LiveExecutionClient` bootstrap。
