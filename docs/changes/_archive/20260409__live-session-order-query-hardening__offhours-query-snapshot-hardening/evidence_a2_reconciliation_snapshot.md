# A2 Reconciliation Snapshot 证据 / Evidence

**日期**：2026-04-10
**状态**：❌ blocked（真实执行）
**对应场景**：A2 Success 2: reconciliation snapshot 走通

## 执行命令

```powershell
C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe scripts/ctp_reconciliation_snapshot_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 输出结果

```json
{"baseline": "reconciliation-snapshot-v1", "success": false, "failure_reason": "account_id_missing", "position_request_id": "", "account_request_id": "", "account_id": null, "position_line_count": 0, "symbol_count": 0, "total_long_qty": 0, "total_short_qty": 0, "gross_position_qty": 0, "total_position_cost": 0, "account_balance": null, "account_available": null, "account_margin": null, "available_ratio": null, "margin_ratio": null, "dominant_exposure_symbol": null, "dominant_exposure_exchange": null, "dominant_exposure_abs_net_qty": 0, "top_exposures": [], "bridge_command_kinds": ["connect", "connect"], "bridge_event_kinds": ["login_failed", "login_failed"]}
```

## 结论

1. reconciliation snapshot 也已进入真实登录路径。
2. 当前失败不是汇总逻辑崩溃，而是上游真实登录失败后没有可用 `account_id`。
3. A2 与 A1 指向同一个真实 blocker：当前 offhours 真实查询尚未拿到成功登录态。