# MD Truth Evidence Matrix Evidence

**change-id**：`20260403__md-startup-truth-and-restore__md-truth-evidence-matrix`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_md_truth_evidence_matrix_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## 验收结果摘要

1. 真实 `md truth evidence matrix smoke` 返回 `0`。
2. live 输出包含：
   `evidence_version=md-truth-evidence-v1`
   `account_id=025292`
   `symbol=rb2610`
   `disposition=evidence_only`
   `restore_triggered=true`
   `restore_succeeded=true`
3. 当前 live code buckets 为：
   `manual_review_codes=[]`
   `restore_required_codes=[]`
   `evidence_only_codes=["restore_resubscribe_triggered"]`

## 关键结论

1. 当前仓内已经有正式的 `MD truth evidence matrix` 自动输出层。
2. 真实 `025292` 的 live 结果已经证明：`rb2610` 的 startup/restore 真相可以稳定收口成 machine-readable evidence。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [md_truth_evidence_matrix_20260402.log](./md_truth_evidence_matrix_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
