# TD Startup Truth Evidence

**change-id**：`20260403__startup-truth-and-session-rebuild__td-session-truth-baseline`  
**date**：2026-04-03

## 验收命令

```powershell
python scripts/ctp_startup_truth_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## 验收结果摘要

1. 真实 `td startup truth smoke` 返回 0。
2. live 输出包含：
   `flow_path=D:\Nautilus\nautilus_ctp_adapter\var\td_flow_smoke`
   `flow_mode=default_shared_flow`
   `ready=true`
   `login_success=true`
   `settlement_code=0`
   `front_id=11`
   `session_id=386081387`
   `max_order_ref=1`
3. `bridge_event_kinds` 为 `login_succeeded -> settlement_confirmed`。

## 关键结论

1. 当前仓内已经有正式的 TD startup truth live baseline，可稳定产出 flow path、session identity 和 settlement truth。
2. 当前默认 TD startup truth 使用共享 flow 目录 `var/td_flow_smoke`。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [td_startup_truth_20260403.log](./td_startup_truth_20260403.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
