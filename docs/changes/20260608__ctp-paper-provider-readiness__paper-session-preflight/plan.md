---
change-id: "20260608__ctp-paper-provider-readiness__paper-session-preflight"
dependencies:
  hard_blocking:
    - id: "20260607__openctp-tts__test-baseline"
      reason: "paper session preflight depends on the OpenCTP paper account baseline and runbook authority"
      expected_status: completed
    - id: "20260608__nautilus-provider-readiness__live-ops-evidence-readiness"
      reason: "paper capability work depends on P002 account/evidence boundary closeout"
      expected_status: completed
  soft_dependency:
    - id: "p003-ctp-live-trading-provider-readiness"
      reason: "P003 owns the paper-first capability readiness scope"
      expected_status: planned
  blocked_by: []
---

# CTP Paper Provider Readiness Phase 1 Paper Session Preflight 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：OpenCTP paper session preflight、redacted evidence、no-Live execution boundary
**topic-id**：live-session-order-query-hardening
**execution_order**：1
**change-id**：20260608__ctp-paper-provider-readiness__paper-session-preflight
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 继续使用 `openctp-paper` 账号 profile 作为当前开发环境，不推进 formal-trading / Live。
2. 固化 paper TD/MD login、settlement、trading day、front/session disposition 和 redacted evidence schema。
3. 让后续 paper read-only snapshot 与 guarded paper order loop 可以复用同一个 preflight 结果。
4. 缺账号、缺 SDK、缺 front、缺交易窗口时输出 typed paper-resource blocker，不泄露敏感信息。

## 二、任务清单

| 步骤 | 任务 | 修改文件 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- |
| P1 | 盘点现有 OpenCTP paper smoke/config helper 和 runbook 输出 | `scripts/`, `docs/changes/20260607__openctp-tts__test-baseline/` | source review | 已完成 |
| P2 | 设计或扩展 paper preflight command，输出 redacted JSON summary | `scripts/ctp_paper_session_preflight.py` | focused command/help test | 已完成 |
| P3 | 补 repo-only negative tests：missing config、wrong profile、secret redaction、no-Live guard | `tests/test_openctp_env_config.py` | focused pytest | 已完成 |
| P4 | 运行 paper session smoke 或记录 typed paper-resource blocker | ignored local config + evidence root | paper preflight evidence | 已完成 |
| P5 | 回填 acceptance、P003 Phase 1 状态和 runbook 使用说明 | change docs + P003 docs | docs gates | 已完成 |

## 三、验证动作

```powershell
python scripts/check_rust_gate.py
python -m pytest tests/test_openctp_env_config.py tests/test_nautilus_integration.py -q
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness
```

可选 paper smoke，只有本地 ignored config 和 OpenCTP front 可用时运行：

```powershell
python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --md-timeout-seconds 30 --td-timeout-seconds 30
```

## 四、完成定义

1. Paper preflight 能输出 redacted pass/fail/blocker summary。
2. P003 当前路径不要求 formal-trading / Live。
3. Missing paper dependency 走 typed blocker，不是 traceback 或伪 pass。
4. 后续 Phase 2/3 可以复用 preflight result 和 account profile boundary。
