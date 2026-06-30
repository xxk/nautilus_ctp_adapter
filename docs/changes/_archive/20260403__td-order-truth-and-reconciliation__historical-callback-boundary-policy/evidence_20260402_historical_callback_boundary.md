# Historical Callback Boundary Policy Evidence

**change-id**：`20260403__td-order-truth-and-reconciliation__historical-callback-boundary-policy`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_td_historical_callback_boundary_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --observation-grace-seconds 1.5
```

## 验收结果摘要

1. 真实 `historical callback boundary smoke` 返回 `0`。
2. live 输出包含：
   `baseline=td-historical-callback-boundary-v1`
   `disposition=boundary_required`
   `observed_callback_count=9`
3. 当前真实边界结果为：
   `login_front_id=11`
   `login_session_id=594882991`
   `login_max_order_ref=1`
   `historical_callback_count=9`
   `delayed_callback_count=0`
   `current_session_callback_count=0`
4. 当前 live findings 为：
   `historical_callbacks_present -> boundary_required`

## 关键结论

1. 当前仓内已经有正式的 `historical callback boundary policy` baseline。
2. 真实 `025292` 的 live 结果已经证明：本轮观测到的 `9` 条 callback 全都不属于当前 session 真相，必须作为历史 callback 对待。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [historical_callback_boundary_20260402.log](./historical_callback_boundary_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
