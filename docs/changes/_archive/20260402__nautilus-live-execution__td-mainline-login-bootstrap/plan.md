---
change-id: "20260402__nautilus-live-execution__td-mainline-login-bootstrap"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-execution__real-account-debug-guardrails"
      reason: "需要先继承正式 guardrails"
      expected_status: completed
  soft_dependency:
    - id: "20260401__ctp-live-connectivity__td-auth-and-login-readiness"
      reason: "复用已验证的 TD readiness 结论"
      expected_status: completed
  blocked_by: []
---

# TD Mainline Login Bootstrap 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、当前 change 三件套
**topic-id**：nautilus-live-execution
**change-id**：20260402__nautilus-live-execution__td-mainline-login-bootstrap
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把 Topic 1 的 TD readiness 收口到正式 execution bootstrap 主线。
2. 让 `LiveExecutionClient` 不再只剩 smoke residue。
3. 为后续 command mapping 和 order lifecycle 铺出稳定登录入口。

## 二、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立 execution bootstrap 主线 | topic C1 | execution client/tests | 可提交 TD connect/login bootstrap | `python -m pytest` | topic README | execution client 不再只是 readiness smoke | 已完成 |
| P2 | 冻结 bootstrap 输出模型 | acceptance | execution client/docs/tests | 稳定 login shape | `python -m pytest` | architecture doc | C2/C3 可复用 | 已完成 |
| P3 | 回写 topic 队列与状态 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 4 可继续推 C2 | 已完成 |

## 三、完成结论

1. `CtpExecutionClient` 已具备正式 execution bootstrap 主线，不再只是 readiness smoke residue。
2. `CtpTdBootstrapState` 与 `CtpExecutionBootstrapResult` 已冻结成稳定 contract。
3. Topic 4 的下一个 implementation change 可以直接进入 command mapping。
