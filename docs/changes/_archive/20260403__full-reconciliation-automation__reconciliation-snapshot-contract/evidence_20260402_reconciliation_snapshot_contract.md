# Reconciliation Snapshot Contract Evidence

**change-id**：`20260403__full-reconciliation-automation__reconciliation-snapshot-contract`  
**date**：2026-04-02

## 验证命令

```powershell
python scripts/check_topic_docs.py
python -m pytest
python scripts/ctp_reconciliation_snapshot_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 结果摘要

1. `python scripts/check_topic_docs.py` 返回：`SUMMARY topics=9 failures=0`
2. `python -m pytest` 返回：`60 passed`
3. 真实 `reconciliation snapshot smoke` 返回：
   `account_id=025292`
   `position_line_count=73`
   `symbol_count=73`
   `gross_position_qty=183`
   `available_ratio=0.21403`
   `margin_ratio=0.780857`

## 关键结论

1. `query_adapter` 之上已经建立了正式只读 reconciliation contract：`snapshot -> summary -> symbol exposure`。
2. `reconciliation_adapter` 复用了现有 `query_adapter` 和 shared `runtime_bridge`，没有再造第二条 query 主线。
3. 真实账户 `025292` 的只读结果已经能被收口成稳定的 summary 指标，用作后续 mismatch policy 的输入。
4. 当前输出仍然只是 reconciliation baseline，不等于完整自动对账已完成。

## 原始证据

1. [reconciliation_snapshot_smoke_20260402.log](./reconciliation_snapshot_smoke_20260402.log)
