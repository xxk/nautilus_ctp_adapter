---
change-id: "20260608__openctp-tts-simulation-provider__nautilus-engine-harness"
dependencies:
  hard_blocking:
    - docs/proposals/p004-openctp-tts-simulation-provider-completeness/
  soft_dependency:
    - docs/proposals/p002-nautilus-provider-production-readiness/
  blocked_by: []
---

# OpenCTP TTS Simulation Nautilus Engine Harness 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`scripts/`, `tests/`, `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：openctp-tts-simulation-provider
**execution_order**：7
**change-id**：20260608__openctp-tts-simulation-provider__nautilus-engine-harness
**关联 acceptance**：./acceptance.md

## 一、需求简述

补齐通过 Nautilus command path 触发 CTP provider submit/cancel/report 的最小 engine harness，避免 script-only smoke 代替 provider evidence。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-simulation-provider.nautilus-engine-harness
- capability_name: OpenCTP TTS Simulation Nautilus Engine Harness
- long_term_target: docs/architecture/openctp-tts-simulation-provider-completeness.md
- secondary_targets: docs/proposals/p004-openctp-tts-simulation-provider-completeness/acceptance.md
- decision_target: docs/proposals/p004-openctp-tts-simulation-provider-completeness/
- affects_long_term_rules: 是
- change_type: 纯实现 + 验证确认
```

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 定义 minimal engine harness entrypoint | P4-A13/P4-F13 | `scripts/`, `tests/` | command/tests | pytest | runbook | uses provider entrypoint | 完成 |
| P2 | 通过 engine command submit order | P4-A13 | `scripts/` | evidence | simulation command | P004 acceptance | provider reports emitted | 完成 |
| P3 | 通过 engine command cancel/classify cancel | P4-A14 | `scripts/` | evidence | simulation command | P004 acceptance | cancel report emitted/typed | 完成 |

## 九、验证动作

```bash
python -m pytest tests/test_nautilus_integration.py -q
python scripts/check_change_docs.py --root .
```
