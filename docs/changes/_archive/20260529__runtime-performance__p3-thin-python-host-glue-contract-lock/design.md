# Thin Python Host Glue Contract Lock 设计

**状态**：completed
**日期**：2026-05-29
**范围**：P001 Phase 3 thin-shell contract
**关联 plan**：./plan.md

## 一、Contract Summary

Python adapter remains a valid Nautilus host integration shell. It is not a runtime owner.

## 二、Allowlist

| Allowed Python responsibility | Source examples | Boundary |
| --- | --- | --- |
| config and environment loading | `adapters/ctp/config.py` | may shape user-facing config, not runtime truth |
| factory / stack construction | `adapters/ctp/factory.py`; package entrypoints | may wire runtime bridge into host clients |
| instrument provider host integration | `instrument_provider.py` | may submit query commands and translate loaded records |
| market data client host integration | `data_client.py` | may build bootstrap commands and package drained MD event batches |
| execution client host integration | `execution_client.py` | may precheck guardrails, map host intents, and submit normalized commands |
| smoke orchestration | `scripts/ctp_*_smoke.py` | may prove local/live readiness, not define long-term runtime owner |
| adapter-local evidence projection | `docs/changes/**/acceptance.md` | may record evidence, not replace runtime truth |

## 三、Forbidden Runtime Logic

| Forbidden category | Rule |
| --- | --- |
| raw CTP callback parsing owner | must not become Python adapter truth |
| query lifecycle truth | must not remain Python long-term owner |
| order lifecycle state machine | must not become Python adapter owner |
| market tick hot loop | must not use Python per-event crossing as default mainline |
| second runtime API | must not bypass `submit_command` / `drain_events(limit)` |
| fallback / compat expansion | must not silently keep managed bridge / ctypes helper as production path |
| daemon shortcut | must not be enabled without Phase 4 benchmark gate and separate proposal |

## 四、Focused Guard Path

Current guard path:

1. `python -m pytest tests/test_smoke_import.py::test_runtime_bridge_submit_and_drain_contract -q`
2. `python -m pytest tests/test_smoke_import.py -k "instrument_provider or data_client or execution_client" -q`
3. `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout`
4. `python scripts/check_change_docs.py --root .`

These tests are not a substitute for live performance evidence. They lock the host-glue contract and prevent accidental boundary drift.

## 五、Change Handling Rule

Future changes that touch `src/nautilus_ctp_adapter/adapters/ctp/` must classify each new Python responsibility as:

1. `host_glue_allowed`
2. `transitional_placeholder_with_retirement_owner`
3. `forbidden_runtime_logic`

Anything in category 3 must fail review unless it is moved native-side or reframed into a separate accepted proposal.
