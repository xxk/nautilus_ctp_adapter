---
change-id: "20260608__nautilus-provider-readiness__live-ops-evidence-readiness"
dependencies:
  hard_blocking:
    - id: "20260608__nautilus-provider-readiness__marketdata-provider-live-loop"
      reason: "paper evidence readiness depends on provider-backed marketdata baseline"
      expected_status: completed
    - id: "20260608__nautilus-provider-readiness__execution-event-reporting"
      reason: "paper evidence readiness depends on execution report identity"
      expected_status: completed
  soft_dependency:
    - id: "20260607__openctp-tts__test-baseline"
      reason: "C8 supplies the OpenCTP paper account baseline"
      expected_status: completed
  blocked_by: []
---

# Nautilus Provider Readiness Phase 5 Live Ops Evidence Readiness 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：P002 proposal docs、OpenCTP C8 runbook/evidence boundary
**topic-id**：live-session-order-query-hardening
**execution_order**：6
**change-id**：20260608__nautilus-provider-readiness__live-ops-evidence-readiness
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 推进 P002 Phase 5：固定 OpenCTP paper evidence readiness 与 formal-trading final evidence 分层。
2. 复用 C8 的 OpenCTP paper baseline，不重复托管账号或 SDK。
3. 保持 `.env` / `cfgs/local/` / downloaded TTS runtime ignored。
4. formal-trading 仍是上线前最终证据，不阻塞 P002 daily development closeout。

## 二、任务清单

| 步骤 | 任务 | 修改文件 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | 将 C8 OpenCTP paper baseline 映射到 P002 Phase 5 | P002 docs | proposal docs gate | 已完成 |
| P2 | 明确 formal-trading final-only 边界 | P002 docs / topic docs | docs gates | 已完成 |
| P3 | 回填 P002 closeout 状态 | P002 docs | proposal docs gate | 已完成 |

## 三、验证动作

```powershell
python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
```

## 四、完成定义

1. P002 Phase 5 可复用 C8 paper account evidence。
2. formal-trading final evidence 不被 paper evidence 替代。
3. Operator 可从 docs 判断 paper vs formal account profile。
4. Proposal closeout 不再等待 repo-local repairable work。
