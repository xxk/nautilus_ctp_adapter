# Nautilus Adapter Interface Design 设计文档 / Design Document

**change-id**：20260413__nautilus-host-integration__adapter-interface-design
**日期**：2026-04-13

> 本文件是设计预案。正式冻结版本已回写到 [`docs/architecture/nautilus-host-integration-design.md`](../../architecture/nautilus-host-integration-design.md)。
>
> **设计已冻结**：2026-04-13。后续 C2/C3/C4/C5 实现以冻结版为准。

## 一、设计原则

1. **包装，不重写**：新的 Nautilus adapter 类内部复用现有 `CtpDataClient` / `CtpExecutionClient`，不重复实现 CTP 通信逻辑。
2. **最小实现优先**：只实现 CTP 能力范围内的方法，其他方法显式标记 `not supported`。
3. **保持 standalone 兼容**：现有脚本（`ctp_nautilus_live_smoke.py`、`ctp_repo_debug_smoke.py`）继续可用。
4. **Async 桥接清晰**：CTP 的 sync callback 通过 `loop.call_soon_threadsafe()` 安全注入 asyncio event loop。

## 二、类层次设计

```text
nautilus_trader.live.data_client.LiveMarketDataClient
  └── CtpLiveDataClient
        ├── 内部持有 CtpDataClient（复用现有 bootstrap/subscription/callback 逻辑）
        ├── 内部持有 CtpMdLiveSession（PyO3 bridge）
        └── 实现 Nautilus 要求的 _connect/_disconnect/_subscribe_quote_ticks 等方法

nautilus_trader.live.execution_client.LiveExecutionClient
  └── CtpLiveExecutionClient
        ├── 内部持有 CtpExecutionClient（复用现有 bootstrap/order/query 逻辑）
        ├── 内部持有 CtpTdLiveSession（PyO3 bridge）
        └── 实现 Nautilus 要求的 _connect/_submit_order/_cancel_order 等方法

nautilus_trader.live.factories.LiveDataClientFactory
  └── CtpLiveDataClientFactory
        └── create() → CtpLiveDataClient

nautilus_trader.live.factories.LiveExecClientFactory
  └── CtpLiveExecClientFactory
        └── create() → CtpLiveExecutionClient
```

## 三、DataClient 方法映射（待冻结）

| Nautilus 方法 | CTP 实现 | 优先级 |
| --- | --- | --- |
| `_connect()` | MD init + login via `CtpMdLiveSession` | 必须 |
| `_disconnect()` | MD dispose via `CtpMdLiveSession` | 必须 |
| `_subscribe_quote_ticks()` | MD subscribe | 必须 |
| `_unsubscribe_quote_ticks()` | MD unsubscribe | 必须 |
| `_subscribe_trade_ticks()` | 从 CTP tick 中提取 last/volume | 可选 |
| `_subscribe_bars()` | 不支持（CTP 无原生 bar 推送） | 不实现 |
| `_subscribe_order_book_deltas()` | CTP 五档快照（非增量），需适配 | 未来 |
| `_request_instrument()` | 通过 InstrumentProvider | 必须 |
| `_request_instruments()` | 通过 InstrumentProvider 批量 | 必须 |

## 四、ExecutionClient 方法映射（待冻结）

| Nautilus 方法 | CTP 实现 | 优先级 |
| --- | --- | --- |
| `_connect()` | TD init + auth + login + settlement confirm | 必须 |
| `_disconnect()` | TD dispose | 必须 |
| `_submit_order()` | CTP order insert via `CtpTdLiveSession` | 必须 |
| `_cancel_order()` | CTP order action (delete) | 必须 |
| `_cancel_all_orders()` | 遍历 working orders 逐个 cancel | 必须 |
| `_modify_order()` | CTP 不支持原生 modify，cancel + re-submit | 可选 |
| `generate_order_status_report()` | CTP QryOrder | 必须 |
| `generate_order_status_reports()` | CTP QryOrder (all) | 必须 |
| `generate_fill_reports()` | CTP QryTrade | 必须 |
| `generate_position_status_reports()` | CTP QryPosition | 必须 |

## 五、Config Schema（待冻结）

```python
@dataclass
class CtpDataClientConfig(LiveDataClientConfig):
    md_front: str        # tcp://180.168.146.187:10131
    broker_id: str       # 9999
    user_id: str
    password: str
    subscribe_symbols: list[str] = field(default_factory=list)

@dataclass
class CtpExecClientConfig(LiveExecClientConfig):
    td_front: str        # tcp://180.168.146.187:10130
    broker_id: str
    user_id: str
    password: str
    app_id: str          # simnow_client_test
    auth_code: str       # 0000000000000000
```

## 六、Async 桥接方案（待冻结）

CTP callback 在 C++ 线程触发 → Rust callback trampoline → Python `callback(payload)` 在 C++ 线程执行。

需要安全注入 asyncio event loop：
```python
def _on_tick_callback(self, tick_view):
    # 在 C++ 线程中被调用
    self._loop.call_soon_threadsafe(self._handle_tick, tick_view)

def _handle_tick(self, tick_view):
    # 在 asyncio event loop 中执行
    quote_tick = self._convert_to_nautilus_quote_tick(tick_view)
    self._handle_quote_tick(quote_tick)  # Nautilus base class method
```

## 七、InstrumentProvider 对接（待冻结）

继承 Nautilus `InstrumentProvider` 基类，内部复用 `CtpInstrumentProvider` + `CtpTdLiveSession.query_instruments()`。

## 八、待决事项

1. [ ] CTP tick 映射到 `QuoteTick` 还是同时映射 `TradeTick`？
2. [ ] `InstrumentId` 格式：`rb2610.SHFE` 还是 `RB2610.SHFE`？
3. [ ] 单 TradingNode 是否允许同时接入多个 CTP 前置？
