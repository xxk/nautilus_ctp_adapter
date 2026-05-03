# Nautilus Host Integration Topic Roadmap

**topic-id**：nautilus-host-integration
**domain**：nautilus_adapter
**状态**：completed
**canonical_status**：completed
**创建日期**：2026-04-13
**最后更新**：2026-04-13

## 一、Topic 目标

将当前独立的 CTP adapter（`CtpDataClient`、`CtpExecutionClient`）正式集成为 Nautilus `TradingNode` 原生 adapter：

1. **DataClient**：继承 `LiveMarketDataClient`，实现 `_connect/_disconnect/_subscribe_quote_ticks` 等方法，把 CTP tick 通过 Nautilus EventBus 分发。
2. **ExecutionClient**：继承 `LiveExecutionClient`，实现 `_submit_order/_cancel_order` 与 report generation，把 CTP 回报映射为 Nautilus `OrderStatusReport`/`FillReport`。
3. **Factory**：实现 `LiveDataClientFactory`/`LiveExecClientFactory`，支持 `TradingNodeBuilder.add_data_client_factory()`。
4. **Config**：继承 `LiveDataClientConfig`/`LiveExecClientConfig`，统一 CTP 连接参数。
5. **End-to-End**：用 `TradingNode` 启动策略，接收 CTP 实时行情并执行交易指令。

## 二、前置条件

1. ✅ `rust-ctp-runtime-cutover` 已完成 — Rust-owned PyO3 bridge 已就绪。
2. ✅ `nautilus-live-marketdata` / `nautilus-live-execution` 已完成 — 独立 MD/TD smoke 已验证。
3. ✅ 现有 `CtpMdLiveSession` / `CtpTdLiveSession` PyO3 内部类可直接复用。
4. ⬜ Nautilus 上游基类稳定：`LiveMarketDataClient`、`LiveExecutionClient`、`LiveDataClientFactory`。

## 三、Nautilus Adapter 接口参考

| Nautilus 基类 | 文件位置 | 关键方法 |
| --- | --- | --- |
| `LiveMarketDataClient` | `nautilus_trader/live/data_client.py` | `_connect`, `_disconnect`, `_subscribe_quote_ticks`, `_unsubscribe_quote_ticks` |
| `LiveExecutionClient` | `nautilus_trader/live/execution_client.py` | `_connect`, `_disconnect`, `_submit_order`, `_cancel_order`, `_cancel_all_orders`, `generate_*_reports` |
| `LiveDataClientFactory` | `nautilus_trader/live/factories.py` | `create(loop, name, config, msgbus, cache, clock)` |
| `LiveExecClientFactory` | `nautilus_trader/live/factories.py` | `create(loop, name, config, msgbus, cache, clock)` |

参考实现：`nautilus_trader/adapters/interactive_brokers/`。

## 四、AI-TASK-QUEUE

| 顺序 | change-id | 标题 | 状态 | 依赖 |
| --- | --- | --- | --- | --- |
| C1 | `20260413__nautilus-host-integration__adapter-interface-design` | Nautilus Adapter Interface Design 接口设计冻结 | `completed` | — |
| C2 | `20260413__nautilus-host-integration__nautilus-live-data-client` | Nautilus Live Data Client 集成 | `completed` | C1 |
| C3 | `20260413__nautilus-host-integration__nautilus-live-execution-client` | Nautilus Live Execution Client 集成 | `not_started` | C1 |
| C4 | `20260413__nautilus-host-integration__factory-and-node-bootstrap` | Factory + TradingNode Bootstrap | `not_started` | C2, C3 |
| C5 | `20260413__nautilus-host-integration__e2e-strategy-smoke` | End-to-End Strategy Smoke 验证 | `not_started` | C4 |

## 五、完成定义

1. `TradingNode` 可以通过 `CtpLiveDataClientFactory` 和 `CtpLiveExecClientFactory` 创建 CTP adapter。
2. 策略可以在 `TradingNode` 内接收 CTP 实时 tick 并提交/取消订单。
3. 所有 child change 的 acceptance 通过。
4. 现有 standalone smoke 脚本继续可用，不被破坏。
