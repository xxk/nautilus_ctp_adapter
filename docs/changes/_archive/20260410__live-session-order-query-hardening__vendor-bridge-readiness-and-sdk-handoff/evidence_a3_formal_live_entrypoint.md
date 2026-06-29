# Formal Live Entry 证据 / Evidence A3

**更新日期**：2026-04-11
**状态**：已执行
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**场景**：A3 Success 3 - formal live smoke 明确是唯一结果面

## 执行命令 / Command

```bash
python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/ctp.live.025292.local.json
```

## 运行结果 / Runtime Result

```json
{
  "baseline": "nautilus-live-smoke-v1",
  "success": false,
  "failure_reason": "md_login_failed",
  "bootstrap_started": true,
  "connect_request_id": "md-connect-1",
  "subscribe_request_ids": ["md-subscribe-2"],
  "md": {
    "init_code": -9000,
    "login_request_code": -9000,
    "subscribe_code": -1,
    "login_success": false,
    "login_error_id": -9000,
    "first_tick_symbol": null
  },
  "td": {
    "init_code": -9000,
    "authenticate_code": -9000,
    "login_code": -9000,
    "settlement_code": -1,
    "login_success": false,
    "login_error_id": -9000
  },
  "bridge_event_kinds": ["login_failed", "login_failed"],
  "bridge_td_login_seen": false,
  "bridge_settlement_seen": false
}
```

## 引用一致性 / Reference Consistency

1. [scripts/README.md](/D:/Nautilus/nautilus_ctp_adapter/scripts/README.md) 已明确写明 `python scripts/ctp_nautilus_live_smoke.py --config <path>` 是唯一 formal live readiness verdict。
2. [docs/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/README.md) 已把 formal TD readiness verdict 固定到同一入口。
3. [docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/live_startup_runbook.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/live_startup_runbook.md) 与 [docs/changes/20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook/runbook.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook/runbook.md) 都继续引用同一 formal live 入口。

## 结论 / Verdict

1. A3 通过的含义是“唯一结果面与失败语义已冻结”，不是“当前机器已 ready”。
2. 本次实跑证明 formal live smoke 可以稳定给出结构化 payload，并把当前机器状态明确归结为 `md_login_failed`，而不是散落在多个 competing entrypoint 之间。
3. 因此后续 operator 需要 live readiness 结论时，仍应只看 `ctp_nautilus_live_smoke.py`，不要把 repo-only probe 或 diagnostics leaf 当成正式 verdict。