# TD Order Truth Baseline Evidence

**change-id**：`20260403__td-order-truth-and-reconciliation__td-order-truth-baseline`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_td_order_truth_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --observation-grace-seconds 1.5
```

## 验收结果摘要

1. 真实 `td order truth smoke` 返回 `0`。
2. live 输出包含：
   `baseline=td-order-truth-v1`
   `ready=true`
   `login_success=true`
   `settlement_code=0`
3. 当前真实 observation 结果为：
   `observed_callback_count=9`
   `observed_order_event_count=8`
   `observed_trade_event_count=1`
   `no_callbacks_observed=false`
4. 首个真实 callback 结构化字段为：
   `first_order_id=49456082`
   `first_order_ref=20850`
   `first_session_id=0`
   `first_front_id=0`
   `first_is_trade=false`

## 关键结论

1. 当前仓内已经有正式的 `TD order truth baseline` 自动输出层。
2. 真实 `025292` 的 live 结果已经证明：TD login 后可在只读观察窗口中收到真实 order/trade callback truth。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [td_order_truth_20260402.log](./td_order_truth_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
