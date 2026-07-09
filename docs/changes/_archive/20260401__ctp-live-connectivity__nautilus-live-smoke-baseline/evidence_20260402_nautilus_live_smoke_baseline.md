# Nautilus Live Smoke Baseline Evidence

**日期**：2026-04-02  
**change-id**：`20260401__ctp-live-connectivity__nautilus-live-smoke-baseline`

## 一、正式入口

本 change 冻结的正式 smoke 入口是：

```powershell
python scripts\ctp_nautilus_live_smoke.py --config <path>
```

这条入口必须满足：

1. 只走本仓维护的本地 `c wrapper`
2. 通过 Nautilus-facing adapter factory 建栈
3. 统一输出单个 JSON 结果
4. 同时覆盖 `MD tick`、`TD readiness`、`runtime bridge events`

## 二、实测命令

```powershell
python scripts\ctp_nautilus_live_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --md-timeout-seconds 20 --td-timeout-seconds 20
```

## 三、关键结果

```json
{
  "baseline": "nautilus-live-smoke-v1",
  "bootstrap_started": true,
  "connect_request_id": "md-connect-1",
  "subscribe_request_ids": ["md-subscribe-2"],
  "md": {
    "login_success": true,
    "login_error_id": 0,
    "first_tick_symbol": "rb2610",
    "first_tick_last": 3131.0
  },
  "td": {
    "authenticate_code": 0,
    "login_success": true,
    "login_error_id": 0,
    "settlement_code": 0
  },
  "bridge_event_kinds": ["login_succeeded", "tick", "login_succeeded", "settlement_confirmed"],
  "bridge_tick_symbol": "rb2610",
  "bridge_td_login_seen": true,
  "bridge_settlement_seen": true
}
```

## 四、成功信号

正式 baseline 的通过口径冻结为：

1. `bootstrap_started = true`
2. `md.login_success = true`
3. `md.first_tick_symbol` 命中订阅列表
4. `td.login_success = true`
5. `td.settlement_code = 0`
6. `bridge_td_login_seen = true`
7. `bridge_settlement_seen = true`

## 五、边界说明

1. 这是 Topic 1 的正式 live smoke baseline，不是完整的 Nautilus `LiveDataClient` 或 `LiveExecutionClient` 实现。
2. `scripts/ctp_md_login_smoke.py` 与 `scripts/ctp_td_login_smoke.py` 仍可保留为 diagnostics，但不再承担“正式 baseline”角色。
3. 后续 Topic 2/3/4 若需要活体验证，应优先复用这条入口，而不是重新定义新的 smoke 口径。
