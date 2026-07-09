# Instrument Smoke Baseline Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-instrument-provider__instrument-smoke-baseline`

## 一、正式入口

当前冻结的正式 instrument smoke 入口：

```powershell
python scripts\ctp_instrument_query_smoke.py --config <path> --symbol rb2610
```

## 二、实测命令

```powershell
python scripts\ctp_instrument_query_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --symbol rb2610 --timeout-seconds 20
```

## 三、关键结果

```json
{
  "request_id": "instrument-query-1",
  "loaded": true,
  "instrument_count": 43,
  "symbols": ["rb2610.SHFE", "..."],
  "first_instrument": {
    "display_symbol": "rb2610.SHFE",
    "underlying": "rb",
    "contract_month": "2610",
    "product_kind": "futures",
    "price_tick": 1.0,
    "volume_multiple": 10
  }
}
```

## 四、结论

1. 本仓本地 `c wrapper` 路径已经可以完成真实 instrument query。
2. `rb2610.SHFE` 合约定义可通过正式 smoke 入口重复取回。
3. 同一次 query 还返回了对应期权链，说明 Topic 2 的 provider/bootstrap 已经不再停留在单条模拟记录。
