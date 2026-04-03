---
change-id: "20260402__live-ops-and-reconciliation__live-startup-runbook"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-execution__order-lifecycle-smoke-baseline"
      reason: "需要先继承 Topic 4 已冻结的 execution smoke 与 guardrails 结论"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Live Startup Runbook 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`docs/`、`scripts/`、`cfgs/`
**topic-id**：live-ops-and-reconciliation
**change-id**：20260402__live-ops-and-reconciliation__live-startup-runbook
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 `nautilus_ctp_adapter` 的 live 启动 runbook。
2. 明确正式 live 启动依赖哪些配置、脚本和验证入口。
3. 区分正式主线入口、诊断脚本和人工确认步骤。
4. 用真实仓内入口与证据判断“runbook 可执行”。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ops.live_startup_runbook
- capability_name: Live Startup Runbook
- long_term_target: D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md
- secondary_targets: D:/Nautilus/nautilus_ctp_adapter/docs/README.md; D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改 `docs/`、`scripts/README.md`、必要的 runbook 文档。
2. 不修改 `src/nautilus_ctp_adapter/adapters/ctp/`、`src/nautilus_ctp_adapter/runtime/`、`rust/` 下的业务实现，除非 runbook 明确暴露出入口错误。
3. Topic 5 的正式入口应建立在 Topic 1-4 已冻结的 smoke 和 guardrails 之上。
4. AI 开始前必须阅读 Topic 5 README、当前 `acceptance.md` 与本文件。
5. 改完后至少执行 `python scripts/check_topic_docs.py` 与 `python -m pytest`。

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 live 启动入口与依赖清单 | capability:ops.live_startup_runbook | `docs/` `scripts/README.md` | 正式 runbook 草案 | `python scripts/check_topic_docs.py` | Topic 5 README | runbook 列出正式入口、配置与 guardrails | 已完成 |
| P2 | 区分正式入口与诊断入口 | capability:ops.live_startup_runbook | `docs/` | 入口分层说明 | `python -m pytest` | Topic 5 README | 不再混淆 mainline 与 diagnostics | 已完成 |
| P3 | 留存 runbook 验证证据 | capability:ops.live_startup_runbook | 当前 change bundle | evidence | `python -m pytest` | 当前 change bundle | evidence 与 acceptance 可支持宣告通过 | 已完成 |

## 五、长期规则增量摘要 / Long-Term Rule Delta Summary

本 change 新增：Topic 5 的 live 启动正式 runbook 口径。
