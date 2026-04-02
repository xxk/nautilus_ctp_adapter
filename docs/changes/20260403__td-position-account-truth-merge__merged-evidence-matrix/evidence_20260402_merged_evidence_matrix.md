# Merged Evidence Matrix Evidence

**change-id**：`20260403__td-position-account-truth-merge__merged-evidence-matrix`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_td_merged_evidence_matrix_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --observation-grace-seconds 1.5 --completion-grace-seconds 1.0
```

## 验收结果摘要

1. 真实 `td merged evidence matrix smoke` 返回 `0`。
2. live 输出包含：
   `evidence_version=td-merged-evidence-v1`
   `account_id=025292`
   `disposition=manual_review_required`
3. 当前真实 merged evidence 结果为：
   `position_count=73`
   `observed_callback_count=9`
   `historical_callback_count=9`
   `current_session_callback_count=0`
4. 当前 live 指标为：
   `available_ratio=0.213352`
   `margin_ratio=0.781532`
5. 当前 live code buckets 为：
   `manual_review_codes=["available_ratio_warn", "margin_ratio_warn"]`
   `boundary_codes=["historical_callbacks_present"]`
   `evidence_only_codes=["no_current_session_callbacks"]`

## 关键结论

1. 当前仓内已经有正式的 `TD merged evidence matrix` 自动输出层。
2. 真实 `025292` 的 live 结果已经把 merged truth、policy 结果和 code buckets 收口成稳定 evidence，可直接用于后续只读运维结论。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [merged_evidence_matrix_20260402.log](./merged_evidence_matrix_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
