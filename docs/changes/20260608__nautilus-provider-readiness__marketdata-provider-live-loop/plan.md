---
change-id: "20260608__nautilus-provider-readiness__marketdata-provider-live-loop"
dependencies:
  hard_blocking:
    - id: "20260608__nautilus-provider-readiness__instrument-provider-cache-hydration"
      reason: "Marketdata tick resolution depends on CTP-aware provider metadata and hydrated Nautilus instruments"
      expected_status: completed
  soft_dependency:
    - id: "20260607__openctp-tts__test-baseline"
      reason: "OpenCTP paper baseline is available for later L5 provider evidence; repo-only tick/provider contract remains this change scope"
      expected_status: completed
  blocked_by: []
---

# Nautilus Provider Readiness Phase 2 Marketdata Provider Live Loop 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/nautilus_data.py`、`tests/test_nautilus_integration.py`、P002 proposal docs
**topic-id**：nautilus-live-marketdata
**execution_order**：3
**change-id**：20260608__nautilus-provider-readiness__marketdata-provider-live-loop
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 推进 P002 Phase 2：行情 tick path 必须使用 Phase 1 provider/cache resolution。
2. 消除 tick symbol 被硬编码到 `.CTP` venue 的行为。
3. 缺 provider metadata 或 cache instrument 时必须产生显式 unknown-instrument diagnostic，不得静默丢弃。
4. 本 change 不声明 OpenCTP live smoke pass。

## 二、能力映射 / Capability Mapping

```text
- capability_id: p002-marketdata-provider-live-loop
- capability_name: P002 Marketdata provider live loop
- long_term_target: docs/proposals/p002-nautilus-provider-production-readiness/
- secondary_targets: docs/topics/nautilus-live-marketdata.md
- decision_target: docs/proposals/p002-nautilus-provider-production-readiness/phase-plan.md
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：Nautilus data client tick resolution、focused tests、当前 change bundle、P002 docs。
2. 禁止修改：`.env`、`cfgs/local/`、live order guardrails、formal-trading config。
3. 当前账号 profile：repo-only；OpenCTP paper 仅作为 L5 blocker/evidence。
4. 必跑验证：`python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider`、proposal/change docs checks。

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Tick symbol 用 provider CTP metadata 解析 InstrumentId | C5 | `nautilus_data.py` | helper + callback path | focused pytest | P002 C5 | `rb2610` tick maps to `rb2610.SHFE` when metadata exists | 已完成 |
| P2 | Unknown instrument diagnostic | C5/C6 | `nautilus_data.py`、tests | typed/observable diagnostic | focused pytest | P002 C5/C6 | unknown symbol 不静默丢弃 | 已完成 |
| P3 | L5 OpenCTP paper smoke row | C6 | evidence only | typed blocker/pass | live smoke | P002 L5 | paper baseline 可复用，但本 change 不声明 L5 provider pass | 已移交 Phase 5 |

## 七、进度记录

1. 2026-06-08：新增 `resolve_ctp_tick_instrument_id()`，known tick symbol 可通过 CTP provider metadata 解析为 `rb2610.SHFE`；focused tests 通过。
2. 2026-06-08：新增 `resolve_ctp_tick_instrument()` 与 `provider_backed_subscription_symbols()`；missing metadata 不再伪造 `.CTP` instrument，未 hydrate metadata 返回 `instrument_not_hydrated` diagnostic。
3. 2026-06-08：OpenCTP paper 基线已由 C8 解除旧 TCP blocker；本 change 仍只关闭 repo-only Phase 2，L5 provider evidence 移交 P002 Phase 5。

## 五、验证动作

```powershell
python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness
python scripts/check_change_docs.py --root .
```

## 六、完成定义

1. Known CTP tick resolves through provider metadata/cache to the hydrated Nautilus instrument id.
2. Unknown tick path has focused negative evidence.
3. P002 C5/C6 rows are updated with repo-only or typed blocker evidence.
