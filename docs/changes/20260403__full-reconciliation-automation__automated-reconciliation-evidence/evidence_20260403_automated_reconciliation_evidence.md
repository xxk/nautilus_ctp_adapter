# Automated Reconciliation Evidence

**change-id**：`20260403__full-reconciliation-automation__automated-reconciliation-evidence`  
**date**：2026-04-03

## 验收命令

```powershell
python scripts/ctp_reconciliation_evidence_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 验收结果摘要

1. 真实 `automated reconciliation evidence smoke` 返回 0。
2. live 输出包含：
   `evidence_version=reconciliation-evidence-v1`
   `account_id=025292`
   `disposition=manual_review_required`
   `manual_review_codes=[available_ratio_warn, margin_ratio_warn]`
   `evidence_only_codes=[dominant_exposure_watch]`
   `finding_count=3`
3. `top_exposures` 已作为自动 evidence 的稳定输出保留下来。

## 关键结论

1. 当前仓内已经有正式、机器可读、只读的 automated reconciliation evidence 输出。
2. 真实账户 `025292` 的 live 结果已经能稳定收口成 `evidence_version + disposition + findings + top_exposures` 结构。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [automated_reconciliation_evidence_20260403.log](./automated_reconciliation_evidence_20260403.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
python -m pip install -e .
```
