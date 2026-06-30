# Nautilus Marketdata Smoke Baseline Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline`

## 一、正式 smoke 入口

当前 Topic 3 的正式 marketdata smoke 入口已经固定为：

```powershell
python scripts/ctp_marketdata_smoke.py --config <path> --symbol rb2610
```

该脚本走的是仓内正式主线：

```text
live instrument query
  -> LiveDataClient bootstrap
  -> repo-owned c wrapper MD login
  -> first live tick
```

## 二、代码落点

1. `/D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_marketdata_smoke.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/data_client.py`

## 三、真实验证

执行：

```powershell
python -m pytest
python -m pip install -e .
python scripts/ctp_marketdata_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --symbol rb2610
```

结果摘要：

```json
{
  "baseline": "nautilus-marketdata-smoke-v1",
  "instrument_loaded": true,
  "source_instrument_count": 43,
  "selected_symbols": ["rb2610"],
  "bootstrap_started": true,
  "connect_request_id": "md-connect-1",
  "subscribe_request_ids": ["md-subscribe-2"],
  "md": {
    "login_success": true,
    "first_tick_symbol": "rb2610",
    "first_tick_last": 3132.0
  },
  "marketdata_batch_event_kinds": ["login_succeeded", "tick"],
  "marketdata_batch_should_restore": false,
  "bridge_event_kinds": ["login_succeeded", "tick"],
  "bridge_tick_symbol": "rb2610"
}
```

原始输出留存在：

1. `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline/marketdata_smoke_20260402.log`

## 四、Topic 3 关闭结论

当前 Topic 3 已具备：

1. 稳定的 marketdata runtime event contract
2. 稳定的 `LiveDataClient` bootstrap path
3. 稳定的 restore / batching contract
4. 可重复通过的 `rb2610` 正式 marketdata smoke baseline
