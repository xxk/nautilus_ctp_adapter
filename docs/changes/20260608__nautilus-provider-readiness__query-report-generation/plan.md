---
change-id: "20260608__nautilus-provider-readiness__query-report-generation"
dependencies:
  hard_blocking:
    - id: "20260608__nautilus-provider-readiness__execution-event-reporting"
      reason: "query report generation depends on provider-backed report identity"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Nautilus Provider Readiness Phase 4 Query Report Generation 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/nautilus_execution.py`、`tests/test_nautilus_integration.py`、P002 proposal docs
**topic-id**：nautilus-live-execution
**execution_order**：5
**change-id**：20260608__nautilus-provider-readiness__query-report-generation
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 推进 P002 Phase 4：把 CTP query truth 翻译为 Nautilus-facing position/account evidence。
2. Position query row 必须生成 `PositionStatusReport`。
3. Account query row 必须生成 `AccountState`，包含 balance/free/margin。
4. Query lifecycle truth 仍归 runtime/query adapter；Nautilus wrapper 只做翻译。

## 二、任务清单

| 步骤 | 任务 | 修改文件 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | position row -> `PositionStatusReport` | `nautilus_execution.py`、tests | focused pytest | 已完成 |
| P2 | account row -> `AccountState` | `nautilus_execution.py`、tests | focused pytest | 已完成 |
| P3 | 回写 P002 Phase 4 状态 | proposal docs | docs gates | 已完成 |

## 三、验证动作

```powershell
python -m pytest tests/test_nautilus_integration.py -k "CtpNautilusExecutionReports" -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness
```

## 四、完成定义

1. Known fake CTP position row produces `PositionStatusReport`.
2. Known fake CTP account row produces `AccountState`.
3. Account state keeps CNY total/free/locked/margin values.
4. Wrapper does not create a second query lifecycle state machine.
