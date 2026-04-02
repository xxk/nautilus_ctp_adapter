# Manual `c2609` One-Lot Runbook

**日期**：2026-04-02  
**用途**：固定 `c2609 / 1手 / 低价 / IOC` 的人工执行前检查与留证流程，用最小风险验证真实下单链路且尽量不保留挂单。  
**适用账户**：`025292`

## 一、范围与边界

本 runbook 只用于：

1. 人工执行前的最后检查
2. dry-run 预演
3. 证据留存

本 runbook 不包含：

1. 未经双重安全门的真实下单命令
2. 长时间保留挂单的测试方式

## 一点五、双重安全门

即使未来允许人工做 live smoke，也必须同时满足：

1. 配置里显式设置 `ExecutionGuardrails.AllowLiveOrderSmoke = true`
2. CLI 显式传入 `--live-send`

缺任何一个，都只能 dry-run。

## 二、固定边界

1. 只允许合约：`c2609`
2. 数量：`1` 手
3. 价格模式：`manual_low_price`
4. 账户：`025292`
5. 任意 1 分钟窗口内不得超过 `10` 次报单
6. `TimeInForce`：`IOC`

## 三、人工执行前必须先跑的 dry-run

```powershell
python scripts/ctp_order_lifecycle_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --instrument c2609 --quantity 1 --limit-price <LOWER_LIMIT_PRICE> --time-in-force IOC
```

## 四、dry-run 通过标准

终端输出的 JSON 中至少应满足：

1. `"dry_run": true`
2. `"bootstrap_ready": true`
3. `"mapped_submit_error": null`
4. `"command_kinds"` 包含 `connect` 和 `submit_order`
5. `"submit_payload"` 中：
   - `channel = "td"`
   - `quantity = "1"`
   - `side` 与人工计划一致
   - `time_in_force = "IOC"`
   - `order_ref / front_id / session_id` 均存在

`2026-04-02` 的已执行低价示例：`c2609 = 2241.0`

说明：当前仓内 Python 行情边界只能直接拿到 `last/bid/ask`，还没有直接暴露 `LowerLimitPrice`。因此像 `2241.0` 这样的测试价格，当前仍应视为“人工冻结的低价”，而不是脚本可自动推导的跌停价。

## 五、人工执行前留证

建议留证顺序：

1. 保存 dry-run 原始终端输出
2. 记录计划合约、方向、数量、人工确认价格
3. 记录当时一档行情截图或终端摘录
4. 记录当时测试低价来源与数值
4. 记录执行前本分钟内已报单次数
5. 记录执行人、执行时间、执行原因

## 六、人工执行后最小回填项

1. 实际发单时间
2. 实际下单价格
3. `client_order_id`
4. `order_ref`
5. 若有回报：
   - `front_id`
   - `session_id`
   - 订单状态
   - 是否形成净成交
   - 若查询仓位，记录 `c2609` 净仓位结果

## 七、当前仓库状态

当前仓库已经具备：

1. `TdOrderSend` / `TdOrderAction` ABI 认知
2. `TdOnExecCallback` -> `ORDER / TRADE` event contract
3. execution dry-run baseline

当前仓库已具备受双重安全门约束的真实发单命令；`2026-04-02` 起推荐使用 `IOC + 人工冻结低价` 做最小风险 smoke。

补充：正式 `order lifecycle smoke` 现已默认使用每次唯一的 TD flow 目录，避免复用旧 session artifact 干扰当前回报判定。

补充：当前 `TdOnExecCallback` 不仅不会稳定回显 Python 侧的 `client_order_id/mapped order_ref`，还会在登录阶段先回放历史 exec 事件。因此人工留证时必须同时记录：

1. native 回报里的 `order_ref`、`status`
2. 该回报是否属于发送后新增事件，而不是登录阶段历史回放
