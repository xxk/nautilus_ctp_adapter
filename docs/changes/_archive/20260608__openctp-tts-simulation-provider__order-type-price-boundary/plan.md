---
change-id: "20260608__openctp-tts-simulation-provider__order-type-price-boundary"
dependencies:
  hard_blocking:
    - docs/proposals/p004-openctp-tts-simulation-provider-completeness/
  soft_dependency: []
  blocked_by: []
---

# OpenCTP TTS Simulation Order Type And Price Boundary 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`scripts/`, `src/nautilus_ctp_adapter/adapters/ctp/`, `tests/`
**topic-id**：openctp-tts-simulation-provider
**execution_order**：4
**change-id**：20260608__openctp-tts-simulation-provider__order-type-price-boundary
**关联 acceptance**：./acceptance.md

## 一、需求简述

覆盖 limit、FAK/FOK、tick 规整、涨跌停和不可交易合约阻断，禁止 unsupported order type 静默降级。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-simulation-provider.order-type-price-boundary
- capability_name: OpenCTP TTS Simulation Order Type And Price Boundary
- long_term_target: docs/architecture/openctp-tts-simulation-provider-completeness.md
- secondary_targets: docs/proposals/p004-openctp-tts-simulation-provider-completeness/acceptance.md
- decision_target: docs/proposals/p004-openctp-tts-simulation-provider-completeness/
- affects_long_term_rules: 是
- change_type: 纯实现 + 验证确认
```

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 order type mapping | P4-A8/P4-F7 | `src/`, `tests/` | mapping tests | pytest | 无 | no silent downgrade | 已完成 |
| P2 | 增加 tick/limit/trading status preflight | P4-A9/P4-F8 | `scripts/`, `src` | preflight verdict | pytest | evidence | unsafe price blocked | 已完成 |
| P3 | 采集 simulation evidence 或 blocker | P4-A8/P4-A9 | 本 change | evidence | simulation command | P004 acceptance | native payload typed | 已完成 |

## 九、验证动作

```bash
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_nautilus_integration.py -q
python scripts/check_change_docs.py --root .
```

## 十、进度记录

- 2026-06-08：进入执行；先补 FAK/FOK/unsupported order type contract，再补 snapshot instrument metadata 驱动的 tick、price、quantity preflight。
- 2026-06-08：完成 FAK/FOK native mapping、unsupported order type/TIF fail-fast、snapshot metadata tick/price/quantity preflight，以及 LIMIT/FAK/FOK dry-run 和 off-tick/zero-price/invalid-quantity/missing-metadata/unsupported-type blockers。
