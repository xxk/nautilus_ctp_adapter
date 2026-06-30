# Hot-Path Owner Inventory / Cutover Boundary 设计

**状态**：completed
**日期**：2026-05-29
**范围**：P001 Phase 2 owner inventory
**关联 plan**：./plan.md

## 一、正式 owner 规则

Phase 2 冻结以下长期 owner 规则：

1. Runtime truth、runtime state、query lifecycle、market stream lifecycle、order lifecycle 和 performance-sensitive buffering 的目标 owner 是 Rust/native runtime。
2. Python adapter 的正式 owner 是 Nautilus host integration：config、factory、provider/client shell、host object translation、operator-facing smoke orchestration。
3. Python-side runtime modules may exist only as transitional placeholders or focused guards until equivalent Rust/native owner exists.
4. No new Python adapter code may become the owner of callback parsing, raw CTP state machine, order lifecycle truth, query completion truth, or per-event hot loop.

## 二、Hot-Path Owner Inventory

| Hot path | Current source evidence | Current owner class | Target owner | Migration boundary |
| --- | --- | --- | --- | --- |
| Adapter-facing command ingress | `src/nautilus_ctp_adapter/runtime/bridge.py`; `rust/ctp_runtime_core/src/native.rs` | shared boundary already batch-shaped | Rust/native runtime + PyO3 bridge | keep `submit_command(command)` stable |
| Adapter-facing event egress | `src/nautilus_ctp_adapter/runtime/bridge.py`; `rust/ctp_runtime_core/src/native.rs` | shared boundary already batch-shaped | Rust/native runtime + PyO3 bridge | keep `drain_events(limit)` stable |
| Query lifecycle | `src/nautilus_ctp_adapter/runtime/query.py`; `instrument_provider.py`; `execution_client.py` query smokes | transitional Python runtime placeholder plus host smoke orchestration | Rust/native query module | Python may submit query commands and translate loaded results, but query completion truth must move native-side |
| Market data subscription and tick flow | `runtime/market.py`; `adapters/ctp/data_client.py` | transitional Python subscription set plus host bootstrap | Rust/native market module | Python may choose requested symbols and package drained events; raw tick callback flow must not become Python-owned |
| Trading / order lifecycle | `runtime/trading.py`; `adapters/ctp/execution_client.py` | transitional Python state guard plus host guardrails | Rust/native trading module | Python may map Nautilus intents and enforce guardrails; order lifecycle truth must move native-side |
| Session/login/reconnect/settlement | `runtime/session.py`; PyO3 live sessions | mixed transitional state and live bridge | Rust/native session module | Python may orchestrate smoke/bootstrap, but runtime session truth belongs native-side |
| Managed bridge / ctypes helper residue | `src/nautilus_ctp_adapter/native/`; historical smoke docs | compatibility/debug helper | non-mainline helper only | no new production ownership; retirement handled by active vendor-bridge change |

## 三、Allowed Temporary Python Items

These items may remain while cutover proceeds:

1. `CtpRuntimeBridge` as placeholder and focused test surface.
2. `CtpQueryRuntime`, `CtpMarketRuntime`, `CtpTradingRuntime`, `CtpSessionRuntime` as transitional state mirrors and guard evidence.
3. `CtpInstrumentProvider`, `CtpDataClient`, `CtpExecutionClient` as Nautilus integration shells.
4. Adapter-local packaging helpers such as `drain_marketdata_event_batch(limit)`.
5. Smoke orchestration code that proves live path readiness without becoming runtime truth.

## 四、Must-Move / Must-Not-Grow Items

| Category | Rule |
| --- | --- |
| raw callback parsing | must move native/Rust; Python callback handlers are temporary event push / smoke adapters only |
| query completion truth | must move native/Rust; Python completion helpers cannot become long-term truth |
| order lifecycle state machine | must move native/Rust; Python aliases and debug mapping cannot become final execution truth |
| market tick hot loop | must move native/Rust; Python per-tick crossing cannot be default mainline |
| fallback / compat bridge | must not grow; existing helper status remains bounded by active vendor-bridge closeout |

## 五、Phase Boundaries

1. Phase 2 completes when this inventory and migration boundary are frozen.
2. Phase 2 does not prove all hot paths have already moved.
3. Phase 3 owns the thin Python host glue contract lock.
4. Phase 4 owns benchmark gate and daemon trigger policy.

## 六、Guard Evidence

Current focused guard surfaces:

1. `python -m pytest tests/test_smoke_import.py::test_runtime_bridge_submit_and_drain_contract -q`
2. `python -m pytest tests/test_smoke_import.py -k "query_runtime or market_runtime or trading_runtime or bootstrap" -q`
3. `python scripts/check_rust_gate.py`
4. proposal and change docs gates
