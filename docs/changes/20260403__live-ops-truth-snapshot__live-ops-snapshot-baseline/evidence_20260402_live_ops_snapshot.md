# Live Ops Snapshot Baseline Evidence

**change-id**：`20260403__live-ops-truth-snapshot__live-ops-snapshot-baseline`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_live_ops_snapshot_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --observation-grace-seconds 1.5 --completion-grace-seconds 1.0
```

## 验收结果摘要

1. 真实 `live ops snapshot smoke` 返回 `0`。
2. live 输出包含：
   `baseline=live-ops-snapshot-v1`
   `account_id=025292`
   `symbol=rb2610`
3. 当前真实 disposition 结果为：
   `startup_disposition=rebuild_required`
   `md_disposition=evidence_only`
   `td_disposition=manual_review_required`
   `reconciliation_disposition=manual_review_required`
4. 当前核心 live 指标为：
   `startup_shared_flow_reuse_allowed=false`
   `startup_session_rotated=true`
   `md_restore_succeeded=true`
   `position_count=73`
   `observed_callback_count=9`
   `historical_callback_count=9`
   `current_session_callback_count=0`
   `available_ratio=0.213352`
   `margin_ratio=0.781532`
5. 当前 code buckets 为：
   `manual_review_codes=["available_ratio_warn", "margin_ratio_warn"]`
   `rebuild_required_codes=["shared_flow_requires_isolated_rebuild"]`
   `restore_required_codes=[]`
   `boundary_codes=["historical_callbacks_present"]`
   `evidence_only_codes=["isolated_flow_verified", "fresh_session_identity_observed", "max_order_ref_reinitialized", "restore_resubscribe_triggered", "no_current_session_callbacks", "dominant_exposure_watch"]`

## 关键结论

1. 当前仓内已经有正式的 `live ops snapshot` 统一只读入口。
2. 真实 `025292` 的 live 结果已经证明：startup、MD、TD merged truth 与 reconciliation evidence 可以在同一条只读主线上被统一消费。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [live_ops_snapshot_smoke_20260402.log](./live_ops_snapshot_smoke_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest D:\Nautilus\nautilus_ctp_adapter\tests\test_smoke_import.py -q
```

