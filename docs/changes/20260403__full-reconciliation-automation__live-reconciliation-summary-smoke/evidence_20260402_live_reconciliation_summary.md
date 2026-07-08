# Live Reconciliation Summary Smoke Evidence

**change-id**：`20260403__full-reconciliation-automation__live-reconciliation-summary-smoke`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_reconciliation_snapshot_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 验收结果摘要

1. 真实 `live reconciliation summary smoke` 返回 0。
2. 输出包含：
   `account_id=025292`
   `position_line_count=73`
   `gross_position_qty=183`
   `available_ratio=0.214403`
   `margin_ratio=0.780486`
   `dominant_exposure_symbol=m2605-P-3000`
   `dominant_exposure_abs_net_qty=10`
3. `top_exposures` 已按 `abs_net_qty -> gross_qty -> position_cost` 优先级排序。

## 关键结论

1. 真实账户 `025292` 的只读 position/account 快照已经能稳定收口成 live reconciliation summary。
2. 当前 smoke 输出已经从“原始 query dump”提升成运维可读摘要，包含主导敞口、资金比例和 top exposures。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [live_reconciliation_summary_20260402.log](./live_reconciliation_summary_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
