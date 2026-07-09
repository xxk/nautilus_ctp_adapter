# Live Data Client Bootstrap Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-marketdata__live-data-client-bootstrap`

## 一、冻结后的主线路径

当前最小 `LiveDataClient` bootstrap 主线已经固定为：

```text
live instrument query
  -> normalized provider result
  -> select configured subscription symbols
  -> submit MD connect + subscribe commands
```

对应代码落点：

1. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/data_client.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py`
3. `/D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_live_data_client_bootstrap_smoke.py`

## 二、冻结后的输出模型

当前 `LiveDataClient` bootstrap 的稳定输出模型是：

```text
CtpLiveDataBootstrapResult
  - instrument_request_id
  - instrument_loaded
  - source_instrument_count
  - selected_symbols
  - bootstrap_state
```

其中 `bootstrap_state` 继续复用：

```text
CtpMdBootstrapState
  - started
  - connect_request_id
  - subscribe_request_ids
```

## 三、关键结论

1. live instrument query 对 `rb2610` 会返回一组 related instruments，而不是单一 futures 合约。
2. `LiveDataClient` bootstrap 不能直接把 provider result 全量订阅，否则会把相关期权链一起带进订阅。
3. 当前主线已经冻结为：优先按 `config.instruments` 从 provider result 中精确挑出要订阅的 symbol。
4. 若 `config.instruments` 在 provider result 中找不到，才退回到 provider result 自身的去重 symbol 列表。

## 四、真实验证

执行：

```powershell
python -m pytest
python -m pip install -e .
python scripts/ctp_live_data_client_bootstrap_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --symbol rb2610
```

结果摘要：

```json
{
  "instrument_loaded": true,
  "instrument_count": 43,
  "selected_symbols": ["rb2610"],
  "bootstrap_started": true,
  "connect_request_id": "md-connect-1",
  "subscribe_request_ids": ["md-subscribe-2"],
  "bootstrap_command_kinds": ["connect", "subscribe_market_data"],
  "bootstrap_subscribe_symbols": ["rb2610"]
}
```

原始输出留存在：

1. `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__live-data-client-bootstrap/live_data_client_bootstrap_smoke_20260402.log`

## 五、范围边界

这笔 change 只证明：

1. `LiveDataClient` 已经有正式 bootstrap 主线。
2. bootstrap 输出模型和 symbol 选择规则已经稳定。
3. Topic 3 的 `C3/C4` 可以直接复用这条路径。

这笔 change 不证明：

1. 订阅恢复策略已经完成
2. batching / 节流语义已经完成
3. 正式 marketdata smoke baseline 已冻结
