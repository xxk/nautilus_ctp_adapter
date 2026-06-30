# A3 Merged Reconciliation Policy 证据 / Evidence

**日期**：2026-04-10
**状态**：❌ blocked（真实执行，含本地桥接修复）
**对应场景**：A3 Success 3: merged reconciliation policy 给出结构化 disposition

## 执行前修复

1. 首次执行暴露本地 PyO3 桥接 bug：运行时 `CtpTdLiveSession` 缺少 `set_exec_callback`。
2. 已修复 `rust/ctp_py/src/lib.rs` 中 TD 回调方法误挂到 `CtpMdLiveSession` 的问题，并重建 editable install。
3. 修复后确认 `CtpTdLiveSession` 已恢复 `set_exec_callback`、`set_instrument_callback`、`set_position_callback`、`set_account_callback` 四个 TD callback contract。

## 执行命令

```powershell
C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe scripts/ctp_td_merged_reconciliation_policy_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0 --observation-grace-seconds 1.5
```

## 输出结果

```json
{"baseline": "td-merged-reconciliation-policy-v1", "success": false, "failure_reason": "account_missing", "account_id": "025292", "disposition": "manual_review_required", "position_count": 0, "observed_callback_count": 0, "historical_callback_count": 0, "current_session_callback_count": 0, "available_ratio": null, "margin_ratio": null, "findings": [{"code": "missing_account_snapshot", "severity": "critical", "action": "manual_review_required", "metric": "account_present", "metric_value": "false", "threshold": "true", "message": "Merged truth snapshot is missing account state and cannot be trusted."}, {"code": "position_snapshot_incomplete", "severity": "critical", "action": "manual_review_required", "metric": "positions_completed", "metric_value": "False", "threshold": "true", "message": "Position snapshot did not complete cleanly in the merged truth window."}, {"code": "missing_available_ratio", "severity": "warn", "action": "manual_review_required", "metric": "available_ratio", "metric_value": null, "threshold": "computed", "message": "Available ratio could not be computed from the merged account snapshot."}, {"code": "missing_margin_ratio", "severity": "warn", "action": "manual_review_required", "metric": "margin_ratio", "metric_value": null, "threshold": "computed", "message": "Margin ratio could not be computed from the merged account snapshot."}, {"code": "no_current_session_callbacks", "severity": "info", "action": "evidence_only", "metric": "current_session_callback_count", "metric_value": 0, "threshold": "> 0 optional", "message": "No callbacks were classified as belonging to the current TD session truth."}], "bridge_command_kinds": ["connect", "connect", "connect"], "bridge_event_kinds": ["login_failed", "login_failed", "login_failed"]}
```

## 结论

1. A3 已不再被本地桥接缺陷阻塞，merged policy 路径现在能真正执行并给出结构化 `disposition` 与 `findings`。
2. 当前真实结果是 `manual_review_required`，根因仍是 `login_failed` 后缺少 account snapshot，而不是 merged policy 本身无结论。
3. 本轮新增的代码修复已把 A3 从“接口错误”推进到“真实 live blocker”。