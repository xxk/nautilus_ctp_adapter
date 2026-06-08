---
change-id: "20260608__openctp-tts-simulation-provider__real-reconnect-evidence"
dependencies:
  hard_blocking:
    - docs/proposals/p004-openctp-tts-simulation-provider-completeness/
  soft_dependency: []
  blocked_by: []
---

# OpenCTP TTS Simulation Real Reconnect Evidence 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-06-08
**范围**：`scripts/`, `tests/`, `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：openctp-tts-simulation-provider
**execution_order**：6
**change-id**：20260608__openctp-tts-simulation-provider__real-reconnect-evidence
**关联 acceptance**：./acceptance.md

## 一、需求简述

补齐真实 OpenCTP TTS simulation MD/TD reconnect、resubscribe、relogin、historical residue 隔离 evidence。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-simulation-provider.real-reconnect-evidence
- capability_name: OpenCTP TTS Simulation Real Reconnect Evidence
- long_term_target: docs/architecture/openctp-tts-simulation-provider-completeness.md
- secondary_targets: docs/proposals/p004-openctp-tts-simulation-provider-completeness/acceptance.md
- decision_target: docs/proposals/p004-openctp-tts-simulation-provider-completeness/
- affects_long_term_rules: 是
- change_type: 验证确认
```

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 reconnect rehearsal command | P4-A11/P4-A12 | `scripts/` | command | `--help`/pytest | runbook | command reusable | 完成 |
| P2 | 采集 MD resubscribe evidence | P4-A11 | 本 change | evidence | controlled proxy command | P004 acceptance | resubscribe once | 完成 |
| P3 | 采集 TD reconnect/disarm evidence | P4-A12/P4-F12 | 本 change | evidence | controlled proxy command | P004 acceptance | armed false after reconnect | 完成 |

## 十、阻塞解除记录

Controlled front proxy evidence generated `controlled_reconnect_pass.json`, proving process-scoped MD/TD disconnect, reconnect, resubscribe-once, TD readiness, query recovery and `paper_send_armed=false`.

受控 proxy 只影响本测试进程的 localhost relay，不要求控制或干扰 OpenCTP 公共 7x24 simulation front。

## 九、验证动作

```bash
python -m pytest tests/test_paper_recovery_idempotency.py -q
python -m pytest tests/test_controlled_front_proxy.py tests/test_paper_recovery_idempotency.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_change_docs.py --root .
```
