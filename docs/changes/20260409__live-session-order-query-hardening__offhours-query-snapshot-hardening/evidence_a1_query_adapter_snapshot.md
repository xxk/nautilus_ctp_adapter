# A1 Query Adapter Snapshot 证据 / Evidence

**日期**：2026-04-10
**状态**：❌ blocked（真实执行）
**对应场景**：A1 Success 1: query adapter 只读快照走通

## 执行命令

```powershell
C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 输出结果

```json
{"baseline": "nautilus-query-adapter-v1", "success": false, "failure_reason": "positions_query_failed", "positions": {"request_id": "", "query_code": -1, "completed": false, "timed_out": false, "no_positions": false, "position_count": 0}, "account": {"request_id": "", "query_code": -1, "completed": false, "timed_out": false, "account_id": null, "balance": null, "available": null}, "bridge_command_kinds": ["connect", "connect"], "bridge_event_kinds": ["login_failed", "login_failed"]}
```

## 结论

1. 当前 A1 已不再阻塞于 `vendor/ctp/bin` 缺 DLL。
2. query adapter 已进入真实登录路径，但 TD login 未成功，导致 `positions.query_code=-1`、`account.query_code=-1`。
3. 当前场景应收口为真实 `login_failed` blocker，而不是继续归因为 bootstrap pack 缺失。