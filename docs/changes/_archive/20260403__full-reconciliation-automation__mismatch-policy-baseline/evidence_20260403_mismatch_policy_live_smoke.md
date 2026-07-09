# Mismatch Policy Baseline Evidence

**change-id**：`20260403__full-reconciliation-automation__mismatch-policy-baseline`  
**date**：2026-04-03

## 验收命令

```powershell
python scripts/ctp_reconciliation_policy_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 验收结果摘要

1. 真实 `reconciliation policy smoke` 返回 0。
2. live 输出包含：
   `disposition=manual_review_required`
   `account_id=025292`
   `available_ratio=0.213524`
   `margin_ratio=0.781359`
   `dominant_exposure_symbol=m2605-P-3000`
   `dominant_exposure_abs_net_qty=10`
3. 当前 live findings 为：
   `available_ratio_warn -> manual_review_required`
   `margin_ratio_warn -> manual_review_required`
   `dominant_exposure_watch -> evidence_only`

## 关键结论

1. mismatch policy baseline 已经把“只记 evidence”和“必须人工介入”区分成正式 machine-readable 结果。
2. 当前真实账户 `025292` 的 live summary 依据本轮基线规则，需要人工复核。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [reconciliation_policy_smoke_20260403.log](./reconciliation_policy_smoke_20260403.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
