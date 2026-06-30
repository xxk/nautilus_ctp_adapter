---
change-id: "20260608__nautilus-provider-readiness__execution-event-reporting"
dependencies:
  hard_blocking:
    - id: "20260608__nautilus-provider-readiness__instrument-provider-cache-hydration"
      reason: "execution reports require provider-backed CTP instrument identity"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Nautilus Provider Readiness Phase 3 Execution Event Reporting 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/nautilus_execution.py`、`tests/test_nautilus_integration.py`、P002 proposal docs
**topic-id**：nautilus-live-execution
**execution_order**：4
**change-id**：20260608__nautilus-provider-readiness__execution-event-reporting
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 推进 P002 Phase 3：把 CTP TD order/trade callback payload 转成 Nautilus-facing report。
2. `generate_order_status_report(s)` 和 `generate_fill_reports` 不再对已知 fake CTP callback 返回空。
3. report identity 必须通过 CTP provider metadata 解析，不得重新发明 `.CTP` fallback。
4. 本 change 不武装 live-send，不把 OpenCTP paper evidence 写成 formal-trading evidence。

## 二、任务清单

| 步骤 | 任务 | 修改文件 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | order callback -> `OrderStatusReport` helper | `nautilus_execution.py`、tests | focused pytest | 已完成 |
| P2 | trade callback -> `FillReport` helper | `nautilus_execution.py`、tests | focused pytest | 已完成 |
| P3 | `CtpLiveExecutionClient` report API 返回缓存报告 | `nautilus_execution.py`、tests | focused pytest | 已完成 |
| P4 | 回写 P002 Phase 3 状态 | proposal docs | docs gates | 已完成 |

## 三、验证动作

```powershell
python -m pytest tests/test_nautilus_integration.py -k "CtpNautilusExecutionReports" -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness
```

## 四、完成定义

1. Known fake CTP order callback produces `OrderStatusReport`.
2. Known fake CTP trade callback produces `FillReport`.
3. Report APIs return cached CTP reports and can filter by instrument/order id.
4. Unknown/missing provider metadata stays non-reportable instead of fabricating identity.

## 五、进度记录

1. 2026-06-08：新增 CTP exec payload 到 Nautilus order/fill report 的转换 helpers。
2. 2026-06-08：`_handle_td_exec_event` 写入 report caches，`generate_*reports` 读取缓存。
