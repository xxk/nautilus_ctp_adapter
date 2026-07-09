---
change-id: "20260608__ctp-paper-provider-readiness__guarded-paper-order-loop"
dependencies:
  hard_blocking:
    - id: "20260608__ctp-paper-provider-readiness__paper-session-preflight"
      reason: "guarded paper order loop depends on paper session preflight"
      expected_status: completed
    - id: "20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot"
      reason: "guarded order loop depends on pre-order snapshot and reconciliation input"
      expected_status: completed
  soft_dependency:
    - id: "p003-ctp-live-trading-provider-readiness"
      reason: "P003 owns the paper-first capability readiness scope"
      expected_status: completed
  blocked_by: []
---

# CTP Paper Provider Readiness Phase 3 Guarded Paper Order Loop 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：OpenCTP paper guarded order submit/cancel/fill/reject/timeout and reconciliation
**topic-id**：live-session-order-query-hardening
**execution_order**：3
**change-id**：20260608__ctp-paper-provider-readiness__guarded-paper-order-loop
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 继续使用 `openctp-paper`，不推进 formal-trading / Live。
2. 在 paper 账号上补齐最小 guarded order loop：preflight、submit、cancel/fill/reject/timeout、callback report、post-trade reconciliation。
3. Paper order 也默认关闭，必须 explicit arm、paper profile、trade window、instrument、qty、net position、rate limit、kill switch 全部通过。
4. 所有输出 redacted，不暴露账号或 secret。

## 二、待开发功能列表

| 步骤 | 功能 | 修改文件 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | 盘点现有 order lifecycle smoke、guardrails 和 execution report mapping | `scripts/ctp_order_lifecycle_smoke.py`, `src/nautilus_ctp_adapter/adapters/ctp/` | source review | 已完成 |
| P2 | 新增或扩展 guarded paper order command，默认 dry-run/request-only | `scripts/ctp_guarded_paper_order_loop.py` | command/help + negative tests | 已完成 |
| P3 | 补 preflight tests：explicit arm、paper profile、trade window、qty、net-position、rate、kill-switch | `tests/test_guarded_paper_order_loop.py` | focused pytest | 已完成 |
| P4 | 接入 submit/cancel/fill/reject/timeout typed lifecycle evidence | `scripts/`, `src/` | focused pytest + paper evidence | 已完成 |
| P5 | 接入 Phase 2 pre/post snapshot reconciliation | `scripts/ctp_guarded_paper_order_loop.py` | snapshot diff evidence | 已完成 |
| P6 | 运行 paper order loop 或记录 typed paper-resource blocker | ignored local config + evidence root | paper evidence | 已完成 |
| P7 | 回填 P003 Phase 3 acceptance 和 change evidence | docs | docs gates | 已完成 |

## 三、验证动作

```powershell
python scripts/check_rust_gate.py
python -m pytest tests/test_nautilus_integration.py -q
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness
```

## 四、完成定义

1. Paper order loop 无 explicit arm 不会触发 native order send。
2. Guarded paper one-hand lifecycle result 被分类为 dry-run preflight / submit/cancel/fill/reject/timeout / typed blocker 中的一种。
3. Pre/post snapshot reconciliation contract 可复核；本次无真实 paper send，因此 post-order snapshot 作为 successor paper-send evidence 保留。
4. 当前 change 不调用 formal-trading / Live。
