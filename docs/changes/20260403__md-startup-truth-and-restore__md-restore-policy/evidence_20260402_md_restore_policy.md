# MD Restore Policy Evidence

**change-id**：`20260403__md-startup-truth-and-restore__md-restore-policy`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_md_restore_policy_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## 验收结果摘要

1. 真实 `md restore policy smoke` 返回 `0`。
2. live 输出包含：
   `baseline=md-restore-policy-v1`
   `disposition=evidence_only`
   `restore_triggered=true`
   `restore_succeeded=true`
3. 当前 live 结果已经证明：
   `restored_first_tick_ts_epoch_us > startup_first_tick_ts_epoch_us`
   也就是 restore 成功依赖恢复后的新 tick，而不是仅凭重连或旧缓存痕迹。

## 关键结论

1. 当前仓内已经有正式的 `MD restore policy` baseline。
2. 真实 `025292` 的 live 结果已经证明：`rb2610` 的 restore 成功必须以恢复后的新 tick 为准。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [md_restore_policy_20260402.log](./md_restore_policy_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
