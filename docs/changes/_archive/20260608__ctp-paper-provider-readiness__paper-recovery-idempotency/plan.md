---
change-id: "20260608__ctp-paper-provider-readiness__paper-recovery-idempotency"
dependencies:
  hard_blocking:
    - id: "20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot"
      reason: "recovery/idempotency depends on truth snapshot disposition"
      expected_status: completed
    - id: "20260608__ctp-paper-provider-readiness__guarded-paper-order-loop"
      reason: "recovery/idempotency depends on paper order lifecycle evidence shape"
      expected_status: completed
  soft_dependency:
    - id: "p003-ctp-live-trading-provider-readiness"
      reason: "P003 owns the paper-first capability readiness scope"
      expected_status: completed
  blocked_by: []
---

# CTP Paper Provider Readiness Phase 4 Paper Recovery And Idempotency 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：OpenCTP paper reconnect/resubscribe/duplicate callback/historical residue/backpressure semantics
**topic-id**：live-session-order-query-hardening
**execution_order**：4
**change-id**：20260608__ctp-paper-provider-readiness__paper-recovery-idempotency
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 继续使用 `openctp-paper`，不推进 formal-trading / Live。
2. 补齐 paper/repo-only recovery matrix：断点恢复、MD/TD reconnect、resubscribe、duplicate callback、historical residue、timeout retry、callback backpressure。
3. 确保重复 order/trade callback 不生成重复 order/fill report。
4. 历史残留不被归类为当前 session fill。

## 二、待开发功能列表

| 步骤 | 功能 | 修改文件 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | 盘点 existing session rebuild/historical callback/reconciliation smokes | `scripts/ctp_*session*_smoke.py`, `scripts/ctp_td_historical_callback_boundary_smoke.py` | source review | 已完成 |
| P2 | 补 duplicate callback / idempotent report repo-only tests | `tests/` | focused pytest | 已完成 |
| P3 | 补 historical residue disposition tests | `tests/` | focused pytest | 已完成 |
| P4 | 设计 paper reconnect/resubscribe rehearsal command 或 typed blocker shape | `scripts/` | command/help test | 已完成 |
| P5 | 记录 callback queue/backpressure/timeout disposition | `scripts/ctp_paper_recovery_idempotency.py` | focused pytest | 已完成 |
| P6 | 补断点 resume checkpoint / evidence append / partial snapshot negative path | `scripts/`, `tests/` | focused pytest | 已完成 |
| P7 | 运行 paper recovery rehearsal 或记录 typed paper-resource blocker | ignored local config + evidence root | paper evidence | 已完成 |
| P8 | 回填 P003 Phase 4 acceptance 和 change evidence | docs | docs gates | 已完成 |

## 三、验证动作

```powershell
python -m pytest tests/test_nautilus_integration.py -q
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness
```

## 四、完成定义

1. Duplicate order/trade callbacks are idempotent。
2. Historical residue is not classified as current session fill。
3. Reconnect/resubscribe disposition can be judged pass/fail/blocker。
4. Breakpoint resume keeps run identity, attempt history, and partial evidence disposition。
5. 当前 change 不调用 formal-trading / Live。
