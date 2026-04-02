# Marketdata Runtime Event Contract Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-marketdata__marketdata-runtime-event-contract`

## 一、冻结后的事件 contract

当前冻结的 marketdata 事件 contract 包含三类：

1. `LOGIN_SUCCEEDED / LOGIN_FAILED`
2. `TICK`
3. `DISCONNECTED`

## 二、冻结后的 payload 结构

### 1. Login payload

```text
CtpMdLoginEventPayload
  - channel
  - success
  - front_id
  - session_id
  - max_order_ref
  - error_id
  - error_message
```

### 2. Tick payload

```text
CtpMdTickEventPayload
  - channel
  - venue_symbol
  - last
  - bid
  - ask
  - ts_epoch_us
```

### 3. Disconnect payload

```text
CtpMdDisconnectEventPayload
  - channel
  - reason
```

## 三、Bridge 语义

当前冻结的 data-side 语义：

1. `CtpDataClient` 会把 marketdata 事件同时写入：
   - shared `runtime_bridge`
   - `data_client` 自己的 marketdata deque
2. 后续 `LiveDataClient` 应优先消费：

```text
data_client.drain_marketdata_events()
```

而不是直接假设全局 bridge 里只有 marketdata 事件。

## 四、代码落点

1. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/data_client.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

## 五、验证结果

执行：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `30 passed`
2. editable install 成功
