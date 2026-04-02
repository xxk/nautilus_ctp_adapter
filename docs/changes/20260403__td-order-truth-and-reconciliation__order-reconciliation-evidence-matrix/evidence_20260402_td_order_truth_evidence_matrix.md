# TD Order Truth Evidence Matrix Evidence

**change-id**：`20260403__td-order-truth-and-reconciliation__order-reconciliation-evidence-matrix`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_td_order_truth_evidence_matrix_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --observation-grace-seconds 1.5
```

## 验收结果摘要

1. 真实 `td order truth evidence matrix smoke` 返回 `0`。
2. live 输出包含：
   `evidence_version=td-order-truth-evidence-v1`
   `account_id=025292`
   `disposition=boundary_required`
3. 当前真实 evidence 结果为：
   `observed_callback_count=9`
   `historical_callback_count=9`
   `delayed_callback_count=0`
   `current_session_callback_count=0`
4. 当前 live code buckets 为：
   `manual_review_codes=[]`
   `boundary_codes=["historical_callbacks_present"]`
   `evidence_only_codes=[]`

## 关键结论

1. 当前仓内已经有正式的 `TD order truth evidence matrix` 自动输出层。
2. 真实 `025292` 的 live 结果已经证明：本轮 order/trade callback 真相应全部按历史 callback 边界处理，而不是当前 session 真相。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [td_order_truth_evidence_matrix_20260402.log](./td_order_truth_evidence_matrix_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
