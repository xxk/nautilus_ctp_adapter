# Subscription Restore And Batching Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-marketdata__subscription-restore-and-batching`

## 一、冻结后的规则

当前 `LiveDataClient` 的 marketdata restore / batching 规则固定为：

1. `CtpDataClient` 持有 `active_subscription_symbols` 作为恢复来源。
2. `drain_marketdata_event_batch(limit)` 返回稳定的 `CtpMdEventBatch`。
3. 只要 batch 中包含 `DISCONNECTED`，且当前仍有 active subscriptions，则 `should_restore = true`。
4. 真正的恢复动作通过 `restore_market_data_subscriptions()` 触发。
5. 当前恢复入口会重发：
   - 1 条 `CONNECT`
   - N 条 `SUBSCRIBE_MARKET_DATA`

## 二、冻结后的输出模型

```text
CtpMdEventBatch
  - events
  - contains_disconnect
  - should_restore

CtpMdRestoreResult
  - triggered
  - restored_symbols
  - bootstrap_state
```

## 三、代码落点

1. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/data_client.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

## 四、验证结果

执行：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `35 passed`
2. editable install 成功

## 五、与后续 change 的边界

这笔 change 已完成：

1. 恢复前置状态模型
2. restore 触发条件
3. batch drain 稳定 contract

这笔 change 不完成：

1. 正式 live marketdata smoke baseline
2. `rb2610` 的 topic 级正式行情证据
