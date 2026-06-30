---
change-id: "20260608__openctp-tts-simulation-provider__risk-preflight-expansion"
dependencies:
  hard_blocking:
    - docs/proposals/p004-openctp-tts-simulation-provider-completeness/
  soft_dependency: []
  blocked_by: []
---

# OpenCTP TTS Simulation Risk Preflight Expansion 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`scripts/`, `src/nautilus_ctp_adapter/adapters/ctp/`, `tests/`
**topic-id**：openctp-tts-simulation-provider
**execution_order**：5
**change-id**：20260608__openctp-tts-simulation-provider__risk-preflight-expansion
**关联 acceptance**：./acceptance.md

## 一、需求简述

扩展资金、保证金、净持仓、重复 client order id、频率限制和 kill switch preflight。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-simulation-provider.risk-preflight-expansion
- capability_name: OpenCTP TTS Simulation Risk Preflight Expansion
- long_term_target: docs/architecture/openctp-tts-simulation-provider-completeness.md
- secondary_targets: docs/proposals/p004-openctp-tts-simulation-provider-completeness/acceptance.md
- decision_target: docs/proposals/p004-openctp-tts-simulation-provider-completeness/
- affects_long_term_rules: 是
- change_type: 纯实现 + 验证确认
```

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 读取 account/position risk facts | P4-A10 | `scripts/`, `src/` | risk input schema | pytest | evidence | facts redacted | 完成 |
| P2 | 实现 qty/net/funds/margin/frequency guards | P4-F9 | `src/`, `tests/` | guardrail verdict | pytest | 无 | no native send on fail | 完成 |
| P3 | 实现 duplicate client order id/kill switch guards | P4-F10/P4-F11 | `src/`, `tests/` | negative tests | pytest | 无 | blocked before mapping | 完成 |

## 九、验证动作

```bash
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py -q
python scripts/check_change_docs.py --root .
```
