---
change-id: "20260608__openctp-tts-simulation-provider__post-order-reconciliation"
dependencies:
  hard_blocking:
    - docs/proposals/p004-openctp-tts-simulation-provider-completeness/
  soft_dependency:
    - docs/proposals/p003-ctp-live-trading-provider-readiness/
  blocked_by: []
---

# OpenCTP TTS Simulation Post-order Reconciliation 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`scripts/`, `tests/`, `src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：openctp-tts-simulation-provider
**execution_order**：3
**change-id**：20260608__openctp-tts-simulation-provider__post-order-reconciliation
**关联 acceptance**：./acceptance.md

## 一、需求简述

让每笔 simulation order 自动产出 pre/post account、position、order、trade snapshot，并给出 fill/reject/cancel/timeout 的 reconciliation verdict。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-simulation-provider.post-order-reconciliation
- capability_name: OpenCTP TTS Simulation Post-order Reconciliation
- long_term_target: docs/architecture/openctp-tts-simulation-provider-completeness.md
- secondary_targets: docs/proposals/p004-openctp-tts-simulation-provider-completeness/acceptance.md
- decision_target: docs/proposals/p004-openctp-tts-simulation-provider-completeness/
- affects_long_term_rules: 是
- change_type: 纯实现 + 验证确认
```

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 扩展 guarded order 支持 post snapshot | P4-A6/P4-A7 | `scripts/` | JSON verdict | focused pytest | evidence | pre/post linked by run id | 已完成 |
| P2 | 拒绝 stale/partial/mismatched snapshot | P4-F6 | `tests/` | negative tests | pytest | 无 | unsafe evidence blocked | 已完成 |
| P3 | 采集 filled/rejected/cancelled reconciliation evidence | P4-A6/P4-A7 | 本 change | evidence | simulation command | P004 acceptance | lifecycle explained | 已完成 |

## 九、验证动作

```bash
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py -q
python scripts/check_change_docs.py --root .
```

## 十、进度记录

- 2026-06-08：进入执行；重点补齐 symbol/direction 级别的 pre/post position delta、lifecycle disposition 对账、stale/partial/account mismatch 阻断和真实 TTS evidence。
- 2026-06-08：完成 target symbol/direction reconciliation、same-run stale/account mismatch/partial/delta mismatch guards、CTP status `53` cancelled classification、native `error_msg` payload preservation，以及 filled/rejected/cancelled/pending TTS evidence。
