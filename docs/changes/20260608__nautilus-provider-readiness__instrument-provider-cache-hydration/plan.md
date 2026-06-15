---
change-id: "20260608__nautilus-provider-readiness__instrument-provider-cache-hydration"
dependencies:
  hard_blocking: []
  soft_dependency:
    - id: "20260607__openctp-tts__test-baseline"
      reason: "OpenCTP paper live evidence is available for later L5 work, while Phase 1 repo-only provider/cache contract stays independent"
      expected_status: completed
  blocked_by: []
---

# Nautilus Provider Readiness Phase 1 InstrumentProvider Cache Hydration 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/nautilus_provider.py`、`nautilus_factories.py`、`tests/test_nautilus_integration.py`、P002 proposal docs
**topic-id**：nautilus-instrument-provider
**execution_order**：2
**change-id**：20260608__nautilus-provider-readiness__instrument-provider-cache-hydration
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 推进 P002 Phase 1：把 CTP factories 从空白 Nautilus `InstrumentProvider()` 切到 CTP-aware provider。
2. 让 data/exec factories 对同一 CTP account profile/config 共享同一个 provider 实例。
3. 给 provider 增加 CTP normalized metadata staging map，作为后续真实 Nautilus instrument/cache hydration 的前置 contract。
4. 本 change 不做 live OpenCTP 登录通过声明，不把 `openctp-paper` evidence 写成 `formal-trading` evidence。

## 二、能力映射 / Capability Mapping

```text
- capability_id: p002-instrument-provider-cache-hydration
- capability_name: P002 InstrumentProvider cache hydration
- long_term_target: docs/proposals/p002-nautilus-provider-production-readiness/
- secondary_targets: docs/changes/20260608__nautilus-provider-readiness__instrument-provider-cache-hydration/
- decision_target: docs/proposals/p002-nautilus-provider-production-readiness/phase-plan.md
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：CTP Nautilus provider/factory 代码、focused tests、当前 change bundle、P002 proposal 状态回写。
2. 禁止修改：`.env`、`cfgs/local/`、真实账号凭据、OpenCTP downloaded runtime、formal trading config。
3. 正式入口：repo-only tests first；OpenCTP live smoke 仅作为 L5 blocker/evidence，不是 Phase 1 repo-only 退出条件。
4. 账号 profile：本 change 默认 `repo-only`；若补 L5，只能使用 `openctp-paper`。
5. 必跑验证：`python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider`、`python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness`、`python scripts/check_change_docs.py --root .`。

## 四、背景与约束

P002 当前最大 Phase 1 缺口是 `nautilus_factories.py` 通过 module cache 共享 provider，但缓存对象仍是 Nautilus 基类 `InstrumentProvider()`。基类可存 instrument，但缺 CTP metadata 和 query/hydration contract，后续 data/exec 不能可靠证明它们共享 CTP-aware provider。

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 新增 CTP-aware Nautilus provider | C1/C4 | `nautilus_provider.py` | `CtpNautilusInstrumentProvider` | focused pytest | P002 Phase 1 | provider 可保存 normalized CTP metadata | 已完成 |
| P2 | Factory 切换到 CTP-aware provider | C1 | `nautilus_factories.py` | shared provider cache 不再返回基类 | focused pytest | P002 acceptance | 同 config data/exec 共享同一 CTP-aware provider | 已完成 |
| P3 | 补 repo-only contract tests | C1/C4/C12 | `tests/test_nautilus_integration.py` | provider type + metadata map tests | focused pytest | 当前 acceptance | 测试覆盖空白 provider 退化 | 已完成 |
| P4 | 真实 Nautilus Instrument/cache hydration | C2/C3 | `nautilus_provider.py`、`tests/test_nautilus_integration.py` | `FuturesContract` hydrate + incomplete metadata negative path | focused pytest | P002 Phase 1 | fake normalized futures instrument 进入 Nautilus provider/cache | 已完成 |

## 六、验证动作

```powershell
python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python -m pytest tests/test_smoke_import.py -k "all_nautilus_exports_importable or native_loader_keeps_windows_dll_directory_handles" -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness
python scripts/check_change_docs.py --root .
```

## 七、完成定义

### 开发完成

1. Factories return `CtpNautilusInstrumentProvider`, not blank `InstrumentProvider()`.
2. Same CTP instrument provider config returns the same provider instance.
3. Normalized CTP metadata can be stored and looked up by display symbol and venue symbol.

### 交付完成

1. P002 Phase 1 acceptance rows reflect current partial progress.
2. Current change acceptance/evidence records focused test output.
3. Remaining true Nautilus cache hydration is explicitly carried forward.

## 八、长期规则增量摘要 / Long-Term Rule Delta Summary

本次无长期规则增量；P002 仍是 proposal-local implementation slice。

## 九、回写与相关变更 / Write-back & Related Changes

1. 回写 P002 `phase-plan.md` Phase 1 progress。
2. 回写 P002 `acceptance.md` C1/C4/A5 current evidence。

## 十、阻塞项

1. OpenCTP paper baseline 已由 `20260607__openctp-tts__test-baseline` 完成；不阻塞本 repo-only Phase 1，也不等同于 formal-trading final evidence。
2. 后续 Phase 2 仍需 unknown-instrument tick diagnostics。

## 十一、进度记录

1. 2026-06-08：新增 `CtpNautilusInstrumentProvider`，factory cache 切换为 CTP-aware provider，focused tests 通过。
2. 2026-06-08：补齐 normalized CTP futures 到 Nautilus `FuturesContract` hydrate，以及 incomplete metadata negative path。
