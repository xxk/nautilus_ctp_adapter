---
change-id: "20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy"
dependencies:
  hard_blocking:
    - id: "20260402__live-ops-and-reconciliation__live-startup-runbook"
      reason: "需要先继承 Topic 5 已冻结的 live 启动顺序与正式入口分层"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Reconnect And Recovery Policy 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`docs/`、必要时 `scripts/`
**topic-id**：live-ops-and-reconciliation
**change-id**：20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 live 运行中的重连、恢复与状态判定规则。
2. 明确 `MD`、`TD`、runtime bridge、flow 目录各自的恢复职责。
3. 建立“自动恢复”和“必须人工介入”的边界。
4. 给 Topic 5 后续 audit/reconciliation 提供稳定恢复口径。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ops.reconnect_and_recovery_policy
- capability_name: Reconnect And Recovery Policy
- long_term_target: D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md
- secondary_targets: D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- decision_target: D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许优先修改 `docs/`，必要时补充 diagnostics/runbook 文档。
2. 不修改 Topic 1-4 已冻结的业务 contract，除非当前恢复策略直接暴露入口设计错误。
3. 当前 change 先以“规则冻结与证据收口”为主，不默认扩展新的 live 交易行为。
4. 改完后至少执行 `python scripts/check_topic_docs.py` 与 `python -m pytest`。

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结重连边界 | capability:ops.reconnect_and_recovery_policy | `docs/` | MD/TD/runtime/flow 恢复职责说明 | `python scripts/check_topic_docs.py` | Topic 5 README | 自动恢复与人工介入边界清楚 | 已完成 |
| P2 | 冻结恢复时序 | capability:ops.reconnect_and_recovery_policy | `docs/` | 恢复顺序与失败升级口径 | `python -m pytest` | Topic 5 README | 失败分层与恢复顺序明确 | 已完成 |
| P3 | 留证并收口 | capability:ops.reconnect_and_recovery_policy | 当前 change bundle | evidence | `python -m pytest` | 当前 change bundle | acceptance 可判定 | 已完成 |
