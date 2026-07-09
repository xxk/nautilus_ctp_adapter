# Session Rebuild Policy Evidence

**change-id**：`20260403__startup-truth-and-session-rebuild__session-rebuild-policy`  
**date**：2026-04-03

## 验收命令

```powershell
python scripts/ctp_session_rebuild_policy_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## 验收结果摘要

1. 真实 `session rebuild policy smoke` 返回 0。
2. live 输出包含：
   `disposition=rebuild_required`
   `shared_flow_reuse_allowed=false`
   `session_rotated=true`
   `max_order_ref_reset=true`
3. 当前 live findings 为：
   `shared_flow_requires_isolated_rebuild -> rebuild_required`
   `isolated_flow_verified -> evidence_only`
   `fresh_session_identity_observed -> evidence_only`
   `max_order_ref_reinitialized -> evidence_only`

## 关键结论

1. 当前仓内已经有正式的 session rebuild policy baseline。
2. 真实 `025292` 的 live 结果已经证明：共享 `td_flow_smoke` 不应被当作 rebuild-safe truth，隔离 flow 才能提供新的 session truth。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [session_rebuild_policy_20260403.log](./session_rebuild_policy_20260403.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
