# Order Lifecycle Smoke Baseline Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-execution__order-lifecycle-smoke-baseline`

## 一、当前已冻结的 execution smoke 入口

当前 Topic 4 的正式 execution smoke 入口已经存在：

```powershell
python scripts/ctp_order_lifecycle_smoke.py --config <path> --instrument c2609 --quantity 1 --limit-price <price> --time-in-force IOC
```

## 二、dry-run baseline 结果

执行：

```powershell
python scripts/ctp_order_lifecycle_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --instrument c2609 --quantity 1 --limit-price 2241.0 --time-in-force IOC
```

结果摘要：

```json
{
  "baseline": "nautilus-order-lifecycle-smoke-v1",
  "dry_run": true,
  "bootstrap_ready": true,
  "connect_request_id": "td-connect-1",
  "mapped_submit_error": null,
  "mapped_submit_order_ref": 2,
  "command_kinds": ["connect", "submit_order"],
  "submit_payload": {
    "time_in_force": "IOC"
  },
  "event_kinds": ["login_succeeded", "settlement_confirmed"]
}
```

## 三、当前 session 的 `c2609` 行情探针结果

为避免完全盲发，先通过本仓 `CtpMdApi` 只读订阅取得 `c2609` 的实时一档：

```json
{
  "symbol": "c2609",
  "last_price": 2378.0,
  "bid_price_1": 2377.0,
  "ask_price_1": 2378.0
}
```

说明：本仓当前 `NativeTickView` 还没有暴露 `LowerLimitPrice/UpperLimitPrice`，因此 `2241.0` 仍是本次 smoke 使用的人工冻结价格，而不是由当前 Python 行情边界直接算出。

## 四、真实 `IOC + 跌停价` smoke 结果

本次真实验证不是直接改本地 JSON，而是在 Python 进程内临时打开以下 guardrails：

1. `enabled = true`
2. `allowed_instruments = ["c2609"]`
3. `max_order_qty = 1`
4. `max_net_position = 5`
5. `max_submit_per_minute = 10`
6. `price_mode = "best_level_1"`
7. `allow_live_order_smoke = true`

真实验证参数固定为：

1. `instrument = c2609`
2. `side = BUY`
3. `quantity = 1`
4. `limit_price = 2241.0`
5. `time_in_force = IOC`

其中一轮带回报留证的结果摘要如下：

```json
{
  "command_kinds": ["connect", "submit_order"],
  "events": [
    {
      "kind": "order",
      "client_order_id": "   141370591",
      "venue_symbol": "c2609",
      "order_ref": "       24332",
      "status": "51"
    },
    {
      "kind": "order",
      "client_order_id": "   141370591",
      "venue_symbol": "c2609",
      "order_ref": "       24332",
      "status": "53"
    }
  ]
}
```

这说明两件事已经成立：

1. `TdOrderSend` 已经真的发出了 `c2609` 买单。
2. 当前仓内确实能收到属于 `c2609` 的 native `ORDER` 回报。

## 五、当前自动判定 blocker（旧结论）

本次实测同时暴露了当前 smoke 自动化还没有完全闭环的原因：

1. Python 侧预分配的 `client_order_id = order-smoke-live-*` 没有在 native 回报里原样返回。
2. Python 侧 `mapped_submit_order_ref = 2` 也没有在 native 回报里原样返回；native 回报里的 `order_ref` 是服务器侧生成的 `24332`。
3. 因此 `live order send did not produce matching exec callback within timeout` 当前仍可能误报失败。

换句话说，旧 blocker 已经不是“单子能不能发出去”，而是“如何把本次发单与 native 回报可靠关联起来”。

## 六、2026-04-02 后续推进结果

本次继续推进后，仓内已经新增两项能力：

1. `execution_client.py` 会把 fake/native-drift 场景下匹配到的回报冻结为 `matched_execs`
2. `scripts/ctp_order_lifecycle_smoke.py` 在成功和失败两条路径都会输出结构化 `exec_events`

对应仓内验证：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `49 passed`
2. editable install 成功

## 七、本次真实 live smoke 新证据

执行正式入口：

```powershell
python scripts/ctp_order_lifecycle_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --instrument c2609 --quantity 1 --limit-price 2241.0 --time-in-force IOC --client-order-id order-smoke-ioc-20260402-3 --live-send
```

结果摘要：

```json
{
  "dry_run": false,
  "live_send_requested": true,
  "error": "live order send did not produce matching exec callback within timeout",
  "command_kinds": ["connect", "submit_order"],
  "event_kinds": ["login_succeeded", "order", "order", "order", "trade", "order", "order", "order", "order", "order", "settlement_confirmed"],
  "exec_events": [
    {
      "venue_symbol": "ao2605P2700",
      "native_order_ref": "       20850",
      "match_reason": ""
    },
    {
      "venue_symbol": "ao2609P2800",
      "native_order_ref": "       23089",
      "match_reason": ""
    },
    {
      "venue_symbol": "c2609",
      "native_order_ref": "       24332",
      "match_reason": ""
    }
  ]
}
```

这批 `exec_events` 有两个关键特征：

1. 它们在登录阶段就已经被推送出来，包含多只非目标合约，说明当前 callback 通道会先回放历史 exec 事件。
2. 其中虽然仍然能看到 `c2609` 的旧 `ORDER` 回报，但没有一条被识别为“本次发送后新增”的新回报，因此当前 smoke 仍不能自动宣称 real order lifecycle 闭环成立。

## 八、根因定位与修复

继续排查后发现，当前正式脚本失败的关键原因不是 `TdOrderSend` 本身，而是 live smoke 长期复用同一个默认 TD flow 目录：

1. 共享 flow 目录会把旧 session artifact 带回当前会话。
2. 这会放大登录阶段历史 exec 回放对当前判定的干扰。
3. 修复方式是把真实 `order lifecycle smoke` 的默认 flow 目录改为每次唯一：

```text
output/debug/live_order_smoke_<time_ns>
```

对应代码落点：

1. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

新增 contract-lock：

1. `real order smoke must use a unique default flow directory to avoid reusing stale TD session artifacts`

## 九、修复后的正式 live smoke 结果

执行正式入口：

```powershell
python scripts/ctp_order_lifecycle_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --instrument c2609 --quantity 1 --limit-price 2241.0 --time-in-force IOC --client-order-id order-smoke-ioc-20260402-fix --live-send
```

结果摘要：

```json
{
  "dry_run": false,
  "live_send_requested": true,
  "live_send_armed": true,
  "bootstrap_ready": true,
  "matched_exec_count": 2,
  "matched_execs": [
    {
      "python_client_order_id": "order-smoke-ioc-20260402-fix",
      "native_order_id": "141370591",
      "native_order_ref": "24332",
      "venue_symbol": "c2609",
      "status": 51,
      "trade_volume": 0,
      "match_reason": "post_send_symbol_qty"
    },
    {
      "python_client_order_id": "order-smoke-ioc-20260402-fix",
      "native_order_id": "141370591",
      "native_order_ref": "24332",
      "venue_symbol": "c2609",
      "status": 53,
      "trade_volume": 0,
      "match_reason": "native_alias"
    }
  ],
  "command_kinds": ["connect", "submit_order"]
}
```

结论：

1. 正式脚本已经成功完成一次真实 `c2609 BUY 1 IOC @ 2241.0` smoke。
2. `matched_exec_count = 2` 证明本次发送后新增回报已被正式脚本识别。
3. 两条匹配回报都已回绑到本次 Python smoke `client_order_id`。
4. `trade_volume = 0`，当前验证停留在“发单能力成立且未成交”的安全口径。

## 十、当前新增的 lifecycle callback contract

仓内已冻结：

1. `TdOrderSend` ABI
2. `TdOrderAction` ABI
3. `TdSetCallback(TdOnExecCallback)` ABI
4. `NativeExec -> ORDER / TRADE runtime event` 映射

## 十一、当前 live-send 安全门

当前仓库已冻结双重安全门：

1. 配置必须显式开启 `ExecutionGuardrails.AllowLiveOrderSmoke = true`
2. 脚本必须显式传入 `--live-send`

缺任一条件，execution smoke 都只能停在 dry-run。

对应代码：

1. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/native/td_ctypes.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`
3. `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

## 十二、当前建议口径

当前更安全的真实验证口径仍然是：

1. `IOC + 人工冻结低价`
2. 单次只做 `1` 手
3. 先看 `command_kinds = ["connect", "submit_order"]`
4. 再看 `matched_exec_count > 0` 且 `exec_events` 中 `c2609` 已回绑到本次 `client_order_id`
5. 如需手工排障，优先确认 live smoke 是否落在唯一 flow 目录，而不是复用旧目录

当前这笔 change 已可标记为正式通过。

## 十三、人工执行 runbook

当前人工执行前检查与留证流程见：

1. `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-execution__order-lifecycle-smoke-baseline/manual_c2609_one_lot_runbook.md`
