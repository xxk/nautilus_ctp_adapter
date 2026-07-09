# TD Truth Merge Snapshot Evidence

**change-id**：`20260403__td-position-account-truth-merge__td-truth-merge-snapshot`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_td_truth_merge_snapshot_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --observation-grace-seconds 1.5 --completion-grace-seconds 1.0
```

## 验收结果摘要

1. 真实 `td truth merge snapshot smoke` 返回 `0`。
2. live 输出包含：
   `baseline=td-truth-merge-snapshot-v1`
   `account_id=025292`
   `order_truth_disposition=boundary_required`
3. 当前真实 merged snapshot 结果为：
   `observed_callback_count=9`
   `historical_callback_count=9`
   `position_count=73`
   `positions_completed=true`
   `account_query_code=0`
   `account_present=true`

## 关键结论

1. 当前仓内已经有正式的 `TD truth merge snapshot` 自动输出层。
2. 真实 `025292` 的 live 结果已经证明：order/trade truth、position snapshot、account snapshot 可以在同一条只读主线上合并成统一 truth 视图。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [td_truth_merge_snapshot_20260402.log](./td_truth_merge_snapshot_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
