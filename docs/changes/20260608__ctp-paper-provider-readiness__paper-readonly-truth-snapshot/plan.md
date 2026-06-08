---
change-id: "20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot"
dependencies:
  hard_blocking:
    - id: "20260608__ctp-paper-provider-readiness__paper-session-preflight"
      reason: "read-only snapshot depends on redacted OpenCTP paper session preflight"
      expected_status: completed
  soft_dependency:
    - id: "p003-ctp-live-trading-provider-readiness"
      reason: "P003 owns the paper-first capability readiness scope"
      expected_status: planned
  blocked_by: []
---

# CTP Paper Provider Readiness Phase 2 Paper Read-only Truth Snapshot 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：OpenCTP paper read-only account/position/order/trade/instrument truth snapshot
**topic-id**：live-session-order-query-hardening
**execution_order**：2
**change-id**：20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 继续使用 `openctp-paper`，不推进 formal-trading / Live。
2. 在 paper 账号上建立只读 truth snapshot：account、position、order、trade、instrument。
3. 输出 redacted JSON summary，支持 pre-order / post-order reconciliation 复用。
4. 区分 valid empty、no-position、timeout、login failed、query failed，不把空结果当异常。

## 二、待开发功能列表

| 步骤 | 功能 | 修改文件 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | 盘点现有 query smoke 和 runtime query adapter 输出 | `scripts/ctp_*query*_smoke.py`, `src/nautilus_ctp_adapter/runtime/` | source review | 已完成 |
| P2 | 新增或扩展 paper read-only snapshot command，统一输出 account/position/order/trade/instrument JSON | `scripts/ctp_paper_readonly_snapshot.py` | command/help test | 已完成 |
| P3 | 补 repo-only tests：empty/no-position/timeout/login-failed disposition | `tests/test_paper_readonly_snapshot.py` | focused pytest | 已完成 |
| P4 | 将 snapshot 输出接入 P002/P003 report/reconciliation evidence shape | `scripts/ctp_paper_readonly_snapshot.py` | focused pytest + paper smoke | 已完成 |
| P5 | 运行 OpenCTP paper read-only snapshot 或记录 typed paper-resource blocker | ignored local config + evidence root | paper evidence | 已完成 |
| P6 | 回填 P003 Phase 2 acceptance 和 change evidence | docs | docs gates | 已完成 |

## 三、验证动作

```powershell
python -m pytest tests/test_nautilus_integration.py -q
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness
```

可选 paper evidence，只有本地 ignored config 和 OpenCTP front 可用时运行 successor command。

## 四、完成定义

1. Paper read-only snapshot 可输出 redacted pass/fail/blocker JSON。
2. account/position/order/trade/instrument 至少有可判定 disposition。
3. valid empty、timeout、login/query failure 被区分。
4. 输出可被 Phase 3 guarded paper order loop 作为 pre/post reconciliation 输入。
