# Startup Truth Evidence Matrix Evidence

**change-id**：`20260403__startup-truth-and-session-rebuild__startup-truth-evidence-matrix`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_startup_truth_evidence_matrix_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## 验收结果摘要

1. 真实 `startup truth evidence matrix smoke` 返回 `0`。
2. live 输出包含：
   `evidence_version=startup-truth-evidence-v1`
   `account_id=025292`
   `disposition=rebuild_required`
   `shared_flow_reuse_allowed=false`
   `session_rotated=true`
   `max_order_ref_reset=true`
3. 当前 live code buckets 为：
   `rebuild_required_codes=["shared_flow_requires_isolated_rebuild"]`
   `evidence_only_codes=["isolated_flow_verified", "fresh_session_identity_observed", "max_order_ref_reinitialized"]`

## 关键结论

1. 当前仓内已经有正式的 `startup truth evidence matrix` 自动输出层。
2. 真实 `025292` 的 live 结果继续证明：共享 `td_flow_smoke` 不能被当作 rebuild-safe session truth，隔离 flow 才能提供新的 startup/session 真相。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [startup_truth_evidence_matrix_20260403.log](./startup_truth_evidence_matrix_20260403.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
python -m pip install -e .
```
