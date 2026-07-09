---
change-id: "20260608__openctp-tts-simulation-provider__close-position-semantics"
dependencies:
  hard_blocking:
    - docs/proposals/p004-openctp-tts-simulation-provider-completeness/
  soft_dependency:
    - docs/changes/20260608__openctp-tts-simulation-provider__cancel-lifecycle/
  blocked_by: []
---

# OpenCTP TTS Simulation Close Position Semantics 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`scripts/`, `src/nautilus_ctp_adapter/adapters/ctp/`, `tests/`
**topic-id**：openctp-tts-simulation-provider
**execution_order**：2
**change-id**：20260608__openctp-tts-simulation-provider__close-position-semantics
**关联 acceptance**：./acceptance.md

## 一、需求简述

补齐 `CLOSE`、`CLOSETODAY`、`CLOSEYESTERDAY` 的 provider 语义，确保 SHFE/INE 今昨仓规则不被静默折叠。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-simulation-provider.close-position-semantics
- capability_name: OpenCTP TTS Simulation Close Position Semantics
- long_term_target: docs/architecture/openctp-tts-simulation-provider-completeness.md
- secondary_targets: docs/proposals/p004-openctp-tts-simulation-provider-completeness/acceptance.md
- decision_target: docs/proposals/p004-openctp-tts-simulation-provider-completeness/
- affects_long_term_rules: 是
- change_type: 纯实现 + 验证确认
```

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 识别 close candidate position | P4-A4 | `scripts/`, `src/` | close preflight | focused pytest | evidence | long/short/td/yd split clear | 已完成 |
| P2 | 冻结 CTP position effect mapping | P4-A5/P4-F5 | `src/`, `tests/` | mapping tests | `pytest tests/test_nautilus_integration.py -q` | 无 | SHFE/INE split explicit | 已完成 |
| P3 | 采集 simulation close evidence 或 typed blocker | P4-A5/P4-F4 | 本 change | evidence | simulation command | P004 acceptance | close result typed | 已完成 |

## 九、验证动作

```bash
python -m pytest tests/test_nautilus_integration.py -q
python scripts/check_change_docs.py --root .
```

## 十、进度记录

- 2026-06-08：进入执行；目标是先用 contract tests 锁定 close candidate、CTP offset mapping、无仓/超量/过期快照阻断，再采集 TTS 7x24 simulation evidence 或 typed blocker。
- 2026-06-08：完成 close candidate helper、`CLOSE/CLOSETODAY/CLOSEYESTERDAY` offset mapping、snapshot run id freshness、direction filter、DCE generic close、SHFE close-yesterday dry-run、insufficient/stale blockers，以及 c2609 armed close post-snapshot reconciliation。stdout exporter blocker 已修复并覆盖测试。
