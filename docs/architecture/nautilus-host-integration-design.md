# Nautilus Host Integration Interface Design 宿主集成接口设计

**更新日期**：2026-04-13
**状态**：已冻结 / Frozen
**change-id**：20260413__nautilus-host-integration__adapter-interface-design

> 本文档是 CTP adapter 集成到 Nautilus TradingNode 的正式接口设计。C2/C3/C4/C5 的实现以本文档为准。

---

## 一、设计原则 / Design Principles

1. **包装，不重写**：新的 Nautilus adapter 类内部持有现有 `CtpDataClient` / `CtpExecutionClient`，复用已有的 bootstrap、subscription、callback、order lifecycle 逻辑。
2. **最小实现优先**：只实现 CTP 能力范围内的方法，其他方法显式 raise `NotImplementedError`（Nautilus 基类默认行为）。
3. **保持 standalone 兼容**：现有 `CtpDataClient` / `CtpExecutionClient` 及 smoke 脚本保持独立可用。
4. **Async 桥接清晰**：CTP 的 sync callback 通过 `loop.call_soon_threadsafe()` 安全注入 asyncio event loop。
5. **Config 继承 Nautilus 体系**：使用 `frozen=True` 的 `NautilusConfig` 子类，与 `TradingNodeConfig` 无缝集成。

---

## 二、类层次设计 / Class Hierarchy

```text
nautilus_trader.live.data_client.LiveMarketDataClient
  └── CtpLiveDataClient                              ← NEW
        ├── 内部持有 CtpDataClient（复用 bootstrap/subscription/callback）
        ├── 内部持有 CtpMdLiveSession（PyO3 bridge）
        ├── 内部持有 CtpLiveInstrumentProvider（Nautilus 兼容）
        └── 实现 _connect/_disconnect/_subscribe_quote_ticks 等

nautilus_trader.live.execution_client.LiveExecutionClient
  └── CtpLiveExecutionClient                         ← NEW
        ├── 内部持有 CtpExecutionClient（复用 bootstrap/order/query/reconciliation）
        ├── 内部持有 CtpTdLiveSession（PyO3 bridge）
        └── 实现 _connect/_submit_order/_cancel_order/generate_*_reports 等

nautilus_trader.common.providers.InstrumentProvider
  └── CtpLiveInstrumentProvider                      ← NEW
        └── 内部持有 CtpInstrumentProvider + CtpTdLiveSession

nautilus_trader.live.factories.LiveDataClientFactory
  └── CtpLiveDataClientFactory                       ← NEW
        └── create() → CtpLiveDataClient

nautilus_trader.live.factories.LiveExecClientFactory
  └── CtpLiveExecClientFactory                       ← NEW
        └── create() → CtpLiveExecutionClient
```

---

## 三、DataClient 方法映射 / DataClient Method Mapping

### 3.1 基类：`LiveMarketDataClient`

`__init__` 签名（Nautilus 上游）：

```python
def __init__(
    self,
    loop: asyncio.AbstractEventLoop,
    client_id: ClientId,
    venue: Venue | None,
    msgbus: MessageBus,
    cache: Cache,
    clock: LiveClock,
    instrument_provider: InstrumentProvider,
    config: NautilusConfig | None = None,
) -> None
```

### 3.2 `CtpLiveDataClient.__init__` 设计

```python
class CtpLiveDataClient(LiveMarketDataClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        instrument_provider: CtpLiveInstrumentProvider,
        config: CtpDataClientConfig,
    ) -> None:
        super().__init__(
            loop=loop,
            client_id=ClientId("CTP"),
            venue=Venue("CTP"),
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=instrument_provider,
            config=config,
        )
        self._inner = CtpDataClient(config.to_adapter_config(), CtpRuntimeBridge())
        self._md_session: CtpMdLiveSession | None = None
```

### 3.3 方法映射表

| # | Nautilus 抽象方法 | CTP 实现方式 | 优先级 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | `_connect()` | `self._inner.bootstrap_md_mainline()` → MD init + login | P0 必须 | 等待 login callback 后 resolve |
| 2 | `_disconnect()` | `self._inner` dispose / session release | P0 必须 | |
| 3 | `_subscribe_quote_ticks(cmd)` | `self._inner.subscribe_market_data(symbols)` | P0 必须 | CTP 每个 tick 包含 bid1/ask1/last |
| 4 | `_unsubscribe_quote_ticks(cmd)` | `self._inner.unsubscribe_market_data(symbols)` | P0 必须 | |
| 5 | `_subscribe_trade_ticks(cmd)` | 从 CTP tick 提取 last_price + volume delta | P1 可选 | CTP 不单独推送 trade，从 tick 中推算 |
| 6 | `_unsubscribe_trade_ticks(cmd)` | 停止 trade tick 推算 | P1 可选 | |
| 7 | `_subscribe_instrument(cmd)` | 从 `instrument_provider` 获取已加载的合约 | P0 必须 | |
| 8 | `_subscribe_instruments(cmd)` | 从 `instrument_provider` 获取全部合约 | P0 必须 | |
| 9 | `_request_instrument(req)` | `instrument_provider.load_async(id)` | P0 必须 | |
| 10 | `_request_instruments(req)` | `instrument_provider.load_all_async()` | P0 必须 | |
| 11 | `_subscribe_order_book_deltas(cmd)` | CTP 五档快照（非增量），需适配为 deltas | P2 未来 | CTP 只推送快照而非增量 |
| 12 | `_subscribe_order_book_depth(cmd)` | CTP 五档快照直接映射 | P2 未来 | |
| 13 | `_subscribe_bars(cmd)` | 不支持 | — | CTP 无原生 bar 推送 |
| 14 | `_subscribe_mark_prices(cmd)` | 不支持 | — | 期货无 mark price |
| 15 | `_subscribe_index_prices(cmd)` | 不支持 | — | |
| 16 | `_subscribe_funding_rates(cmd)` | 不支持 | — | 期货无 funding |
| 17 | `_subscribe_option_greeks(cmd)` | 不支持 | — | |
| 18 | `_subscribe_instrument_status(cmd)` | CTP 合约状态推送（未来） | P2 未来 | |
| 19 | `_subscribe_instrument_close(cmd)` | CTP 收盘价（结算价） | P2 未来 | |
| 20 | `_request_bars(req)` | 不支持 | — | CTP 无历史 bar 接口 |
| 21 | `_request_quote_ticks(req)` | 不支持 | — | CTP 无历史 tick 接口 |
| 22 | `_request_trade_ticks(req)` | 不支持 | — | |

### 3.4 Tick 转换设计

CTP 推送的 `NativeTickView` 包含：

```text
last_price, bid_price1, ask_price1, bid_volume1, ask_volume1,
volume, open_interest, update_time, update_millisec, ...
```

映射为 Nautilus `QuoteTick`：

```python
QuoteTick(
    instrument_id=instrument_id,
    bid_price=Price(tick.bid_price1, precision),
    ask_price=Price(tick.ask_price1, precision),
    bid_size=Quantity(tick.bid_volume1, 0),
    ask_size=Quantity(tick.ask_volume1, 0),
    ts_event=ctp_timestamp_to_unix_nanos(tick.update_time, tick.update_millisec),
    ts_init=clock.timestamp_ns(),
)
```

---

## 四、ExecutionClient 方法映射 / ExecutionClient Method Mapping

### 4.1 基类：`LiveExecutionClient`

`__init__` 签名（Nautilus 上游）：

```python
def __init__(
    self,
    loop: asyncio.AbstractEventLoop,
    client_id: ClientId,
    venue: Venue,
    oms_type: OmsType,
    instrument_provider: InstrumentProvider,
    account_type: AccountType,
    base_currency: Currency | None,
    msgbus: MessageBus,
    cache: Cache,
    clock: LiveClock,
    config: LiveExecClientConfig | None = None,
) -> None
```

### 4.2 `CtpLiveExecutionClient.__init__` 设计

```python
class CtpLiveExecutionClient(LiveExecutionClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        instrument_provider: CtpLiveInstrumentProvider,
        config: CtpExecClientConfig,
    ) -> None:
        super().__init__(
            loop=loop,
            client_id=ClientId("CTP"),
            venue=Venue("CTP"),
            oms_type=OmsType.NETTING,       # CTP 使用净持仓模式
            instrument_provider=instrument_provider,
            account_type=AccountType.MARGIN,  # CTP 是保证金交易
            base_currency=Currency.from_str("CNY"),
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            config=config,
        )
        self._inner = CtpExecutionClient(config.to_adapter_config(), CtpRuntimeBridge())
        self._td_session: CtpTdLiveSession | None = None
```

### 4.3 方法映射表

| # | Nautilus 抽象方法 | CTP 实现方式 | 优先级 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | `_connect()` | `self._inner.bootstrap_td_mainline()` → TD init + authenticate + login + settlement confirm | P0 必须 | 4 步 handshake |
| 2 | `_disconnect()` | `self._inner` dispose / session release | P0 必须 | |
| 3 | `_submit_order(cmd)` | `self._inner.submit_order_intent()` → CTP `ReqOrderInsert` | P0 必须 | 需要 `generate_order_submitted()` |
| 4 | `_cancel_order(cmd)` | `self._inner.cancel_order()` → CTP `ReqOrderAction(delete)` | P0 必须 | |
| 5 | `_cancel_all_orders(cmd)` | 遍历 working orders 逐个调用 `_cancel_order` | P0 必须 | CTP 无批量 cancel API |
| 6 | `_submit_order_list(cmd)` | 依次调用 `_submit_order` | P1 可选 | CTP 无原生批量下单 |
| 7 | `_modify_order(cmd)` | CTP 不支持原生 modify；cancel + re-submit | P1 可选 | 需谨慎处理中间状态 |
| 8 | `_batch_cancel_orders(cmd)` | 逐个 cancel | P1 可选 | |
| 9 | `generate_order_status_report(inst_id, cl_order_id, venue_order_id)` | CTP `QryOrder` → match specific order | P0 必须 | Reconciliation 需要 |
| 10 | `generate_order_status_reports(inst_id, start, end, open_only)` | CTP `QryOrder` → filter by instrument | P0 必须 | |
| 11 | `generate_fill_reports(inst_id, venue_order_id, start, end)` | CTP `QryTrade` → filter by instrument | P0 必须 | |
| 12 | `generate_position_status_reports(inst_id, start, end)` | CTP `QryInvestorPosition` → filter | P0 必须 | |

### 4.4 Order Lifecycle 事件映射

CTP 回调 → Nautilus OrderEvent：

| CTP 回调 | Nautilus 事件 | 触发方法 |
| --- | --- | --- |
| `OnRtnOrder` (status=已提交) | `OrderSubmitted` | `self.generate_order_submitted()` |
| `OnRtnOrder` (status=已成交) | `OrderFilled` | `self.generate_order_filled()` |
| `OnRtnOrder` (status=已撤单) | `OrderCanceled` | `self.generate_order_canceled()` |
| `OnRtnOrder` (status=部分成交) | `OrderPartiallyFilled` | `self.generate_order_filled()` (partial) |
| `OnRtnTrade` | `OrderFilled` | `self.generate_order_filled()` |
| `OnErrRtnOrderInsert` | `OrderRejected` | `self.generate_order_rejected()` |
| `OnErrRtnOrderAction` | `OrderCancelRejected` | `self.generate_order_cancel_rejected()` |

### 4.5 CTP OMS 特性

- **OmsType**: `NETTING` — CTP 的净持仓模式
- **AccountType**: `MARGIN` — 保证金账户
- **Currency**: `CNY` — 人民币
- **CTP 不支持 modify order**：需要 cancel + resubmit 模拟；对于 P0 scope 不实现 `_modify_order()`

---

## 五、Config Schema 设计 / Config Schema

### 5.1 基类选择

Nautilus config 体系：

```text
NautilusConfig (frozen=True, msgspec.Struct)
  └── LiveDataClientConfig (frozen=True)
        ├── handle_revised_bars: bool = False
        ├── instrument_provider: InstrumentProviderConfig
        └── routing: RoutingConfig

  └── LiveExecClientConfig (frozen=True)
        ├── instrument_provider: InstrumentProviderConfig
        └── routing: RoutingConfig
```

### 5.2 `CtpDataClientConfig`

```python
class CtpDataClientConfig(LiveDataClientConfig, frozen=True):
    """CTP market data client configuration."""
    md_front: str              # tcp://180.168.146.187:10131
    broker_id: str = ""        # 9999
    user_id: str = ""
    password: str = ""
    subscribe_symbols: list[str] = []
    instrument_provider: CtpInstrumentProviderConfig = CtpInstrumentProviderConfig()
```

### 5.3 `CtpExecClientConfig`

```python
class CtpExecClientConfig(LiveExecClientConfig, frozen=True):
    """CTP execution client configuration."""
    td_front: str              # tcp://180.168.146.187:10130
    broker_id: str = ""        # 9999
    user_id: str = ""
    password: str = ""
    app_id: str = ""           # simnow_client_test
    auth_code: str = ""        # 0000000000000000
    product_info: str = ""
    instrument_provider: CtpInstrumentProviderConfig = CtpInstrumentProviderConfig()
```

### 5.4 `CtpInstrumentProviderConfig`

```python
class CtpInstrumentProviderConfig(InstrumentProviderConfig, frozen=True):
    """Configuration for CTP instrument provider."""
    td_front: str = ""         # 复用 TD 前置查询合约
    broker_id: str = ""
    user_id: str = ""
    password: str = ""
    app_id: str = ""
    auth_code: str = ""
    load_contracts_on_start: bool = True
    contract_filter: list[str] = []   # 只加载指定合约
```

### 5.5 Config → 现有 `CtpAdapterConfig` 桥接

新的 Nautilus Config 类需要提供 `to_adapter_config()` 方法，将 Nautilus config 转换为现有 `CtpAdapterConfig` dataclass：

```python
def to_adapter_config(self) -> CtpAdapterConfig:
    return CtpAdapterConfig(
        broker_id=self.broker_id,
        user_id=self.user_id,
        password=self.password,
        md_front=self.md_front,
        # ...
    )
```

---

## 六、Factory 创建模式 / Factory Pattern

### 6.1 基类签名

```python
class LiveDataClientFactory:
    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config: LiveDataClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> LiveDataClient: ...

class LiveExecClientFactory:
    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config: LiveExecClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> LiveExecutionClient: ...
```

### 6.2 CTP Factory 实现

```python
class CtpLiveDataClientFactory(LiveDataClientFactory):
    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config: CtpDataClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> CtpLiveDataClient:
        # 1. 创建 InstrumentProvider（可能需要共享实例）
        provider = CtpLiveInstrumentProvider(config=config.instrument_provider)

        # 2. 创建 DataClient
        return CtpLiveDataClient(
            loop=loop,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=config,
        )


class CtpLiveExecClientFactory(LiveExecClientFactory):
    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config: CtpExecClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> CtpLiveExecutionClient:
        # 1. 获取或创建共享 InstrumentProvider
        provider = CtpLiveInstrumentProvider(config=config.instrument_provider)

        # 2. 创建 ExecutionClient
        return CtpLiveExecutionClient(
            loop=loop,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=config,
        )
```

### 6.3 TradingNode 注册

```python
from nautilus_trader.live.node import TradingNode

node = TradingNode(config=config)
node.add_data_client_factory("CTP", CtpLiveDataClientFactory)
node.add_exec_client_factory("CTP", CtpLiveExecClientFactory)
node.build()
node.run()
```

### 6.4 共享 InstrumentProvider 考虑

IB adapter 通过模块级缓存函数（`get_cached_ib_client()`, `get_cached_interactive_brokers_instrument_provider()`）确保 Data + Exec factory 共享同一个底层 client 和 provider。

CTP adapter 的类似方案：

```python
_CTP_PROVIDERS: dict[str, CtpLiveInstrumentProvider] = {}

def get_ctp_instrument_provider(
    config: CtpInstrumentProviderConfig,
) -> CtpLiveInstrumentProvider:
    key = f"{config.td_front}:{config.broker_id}:{config.user_id}"
    if key not in _CTP_PROVIDERS:
        _CTP_PROVIDERS[key] = CtpLiveInstrumentProvider(config=config)
    return _CTP_PROVIDERS[key]
```

---

## 七、Async 桥接方案 / Async Bridge Design

### 7.1 问题

CTP callback 的调用链：

```text
CTP C++ SDK 线程
  → Rust callback trampoline (在 C++ 线程中)
  → PyO3 → Python callback function (仍在 C++ 线程中)
```

Nautilus 的 event handling 在 asyncio event loop 中。callback 在非 asyncio 线程中执行，直接操作 Nautilus 对象是不安全的。

### 7.2 解决方案

使用 `loop.call_soon_threadsafe()` 将 callback 安全调度到 asyncio event loop：

```python
# 在 CtpLiveDataClient 中
def _setup_callbacks(self):
    """注册 CTP → Nautilus 的 callback 桥接。"""
    self._md_session.set_tick_callback(self._on_ctp_tick)
    self._md_session.set_front_disconnected_callback(self._on_md_disconnect)

def _on_ctp_tick(self, tick_view):
    """在 CTP C++ 线程中被调用。"""
    # 只做最小工作：将 raw data 调度到 event loop
    self._loop.call_soon_threadsafe(self._handle_ctp_tick, tick_view)

def _handle_ctp_tick(self, tick_view):
    """在 asyncio event loop 中执行。安全操作 Nautilus 对象。"""
    instrument_id = self._resolve_instrument_id(tick_view.symbol)
    instrument = self._cache.instrument(instrument_id)
    if instrument is None:
        self._log.warning(f"Unknown instrument: {tick_view.symbol}")
        return

    quote_tick = QuoteTick(
        instrument_id=instrument_id,
        bid_price=Price(tick_view.bid_price1, instrument.price_precision),
        ask_price=Price(tick_view.ask_price1, instrument.price_precision),
        bid_size=Quantity(tick_view.bid_volume1, 0),
        ask_size=Quantity(tick_view.ask_volume1, 0),
        ts_event=self._parse_ctp_timestamp(tick_view),
        ts_init=self._clock.timestamp_ns(),
    )
    self._handle_quote_tick(quote_tick)
```

### 7.3 ExecutionClient 的 callback 桥接

```python
def _on_ctp_order_event(self, exec_view):
    """在 CTP C++ 线程中被调用。"""
    self._loop.call_soon_threadsafe(self._handle_ctp_order_event, exec_view)

def _handle_ctp_order_event(self, exec_view):
    """在 asyncio event loop 中执行。生成 Nautilus OrderEvent。"""
    # 根据 exec_view.status 映射到不同的 generate_order_* 方法
    ...
```

### 7.4 Connect/Disconnect 的 async 实现

`_connect()` 和 `_disconnect()` 是 coroutine，可以使用 `asyncio.Future` 等待 CTP callback：

```python
async def _connect(self):
    """Connect to CTP MD front."""
    self._login_future = self._loop.create_future()

    # 启动 CTP session（在当前线程）
    self._md_session = _create_md_live_session(flow_path)
    self._setup_callbacks()
    self._md_session.init(md_front)
    self._md_session.login(broker_id, user_id, password)

    # 等待 login callback 设置 future result
    await asyncio.wait_for(self._login_future, timeout=30.0)

def _on_md_login(self, login_response):
    """在 CTP 线程中被调用。"""
    self._loop.call_soon_threadsafe(
        self._login_future.set_result, login_response
    )
```

---

## 八、InstrumentProvider 对接 / InstrumentProvider Integration

### 8.1 方案

创建 `CtpLiveInstrumentProvider(InstrumentProvider)` 继承 Nautilus 基类，内部复用现有 `CtpInstrumentProvider` 和 `CtpTdLiveSession.query_instruments()`。

### 8.2 必须实现的方法

| Nautilus 方法 | CTP 实现 |
| --- | --- |
| `load_all_async(filters)` | `CtpTdLiveSession.query_instruments()` → 遍历结果 → `self.add(instrument)` |
| `load_ids_async(ids, filters)` | 从已加载数据中过滤 |
| `load_async(id, filters)` | 从已加载数据中查找 |

### 8.3 CTP 合约 → Nautilus Instrument 映射

CTP `InstrumentField` → Nautilus `FuturesContract`:

```python
FuturesContract(
    instrument_id=InstrumentId(Symbol(instrument_id), Venue("CTP")),
    raw_symbol=Symbol(instrument_id),
    asset_class=AssetClass.COMMODITY,   # 或 INDEX / EQUITY
    currency=Currency.from_str("CNY"),
    price_precision=price_precision,     # 从 PriceTick 推导
    size_precision=0,                    # 整数手
    price_increment=Price(price_tick, price_precision),
    multiplier=Quantity(volume_multiple, 0),
    lot_size=Quantity(1, 0),
    # ... expiration, underlying 等
)
```

### 8.4 InstrumentId 命名规范

```text
格式: {合约代码}.CTP
示例: rb2610.CTP, IF2504.CTP, au2412.CTP
```

使用 CTP 原始大小写（不强制大写），Venue 统一为 `CTP`。

---

## 九、文件落点 / File Layout

```text
src/nautilus_ctp_adapter/adapters/ctp/
  ├── config.py              # 保留现有 CtpAdapterConfig
  ├── nautilus_config.py      # NEW: CtpDataClientConfig, CtpExecClientConfig
  ├── data_client.py          # 保留现有 CtpDataClient
  ├── nautilus_data.py         # NEW: CtpLiveDataClient(LiveMarketDataClient)
  ├── execution_client.py     # 保留现有 CtpExecutionClient
  ├── nautilus_execution.py    # NEW: CtpLiveExecutionClient(LiveExecutionClient)
  ├── nautilus_provider.py     # NEW: CtpLiveInstrumentProvider(InstrumentProvider)
  ├── nautilus_factories.py    # NEW: CtpLiveDataClientFactory, CtpLiveExecClientFactory
  ├── instrument_provider.py  # 保留现有 CtpInstrumentProvider
  ├── factory.py              # 保留现有 build_ctp_stack()
  └── ...                     # 保留现有文件
```

新文件使用 `nautilus_` 前缀，与现有 standalone 文件区分。

---

## 十、Standalone 兼容策略 / Standalone Compatibility

1. 现有 `CtpDataClient` / `CtpExecutionClient` 不修改签名和行为。
2. 现有 `build_ctp_stack()` 继续返回 standalone 组件。
3. 新增 `build_nautilus_ctp_stack()` 或通过 Factory 创建 Nautilus 兼容组件。
4. Smoke 脚本（`ctp_nautilus_live_smoke.py`、`ctp_repo_debug_smoke.py`）继续使用现有 standalone 路径。
5. 新增 `ctp_nautilus_node_smoke.py` 用于验证 TradingNode 集成。

---

## 十一、待决事项 / Open Questions

### 已决

1. **CTP tick 映射**：CTP tick 包含 bid/ask/last，优先映射为 `QuoteTick`（bid1/ask1）；`TradeTick` 作为 P1 可选实现（从 last_price + volume delta 推算）。
2. **InstrumentId 格式**：使用 CTP 原始大小写 + `.CTP` venue，如 `rb2610.CTP`。
3. **OmsType**：使用 `NETTING`（CTP 净持仓模式）。

### 待决（C2-C5 实施时解决）

1. 单 TradingNode 是否允许同时接入多个 CTP 前置？（当前设计支持，通过不同 ClientId 区分）
2. CTP 的 `position_effect`（开/平/平今/平昨）如何映射到 Nautilus？（可能需要自定义 `PositionEffect` 或在 submit_order 中注入）
3. CTP 的结算价 vs 最新价在 Nautilus 的表达？（可能需要 `InstrumentClose` subscription）

---

## 十二、实施顺序 / Implementation Sequence

本设计对应 topic `nautilus-host-integration` 的 5 个 child changes：

| # | Change | 依赖 | 范围 |
| --- | --- | --- | --- |
| C1 | adapter-interface-design（本文档） | — | 设计冻结 |
| C2 | data-client-implementation | C1 | `nautilus_data.py` + `nautilus_config.py` (Data 部分) |
| C3 | execution-client-implementation | C1, C2 | `nautilus_execution.py` + `nautilus_config.py` (Exec 部分) |
| C4 | factory-and-node-integration | C2, C3 | `nautilus_factories.py` + `nautilus_provider.py` + node smoke |
| C5 | strategy-smoke-test | C4 | 端到端策略 smoke test |
