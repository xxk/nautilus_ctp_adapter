# Audit And Reconciliation Baseline

**日期**：2026-04-02  
**topic-id**：`live-ops-and-reconciliation`  
**change-id**：`20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline`

## 一、用途

这份 baseline 用来冻结 `nautilus_ctp_adapter` 当前最小可用的审计与对账证据链。

它的目标不是假装“全部自动化都已经有了”，而是明确：

1. 哪些证据已经能由仓内正式入口自动产出
2. 哪些证据当前只有 native/export 能力，但还没有正式 smoke
3. 哪些一致性可以自动判断
4. 哪些差异必须人工复核

## 二、证据分类

当前统一分 5 类证据：

1. 市场数据证据
2. 订单证据
3. 成交证据
4. 持仓证据
5. 资金证据

## 三、当前正式自动化证据链

### 1. 市场数据证据

正式来源：

1. `python scripts/ctp_nautilus_live_smoke.py --config <path>`
2. `python scripts/ctp_marketdata_smoke.py --config <path> --symbol rb2610`

当前可稳定留存的字段包括：

1. `first_tick_symbol`
2. `first_tick_last / bid / ask`
3. `bridge_event_kinds`
4. `bridge_tick_symbol`

当前自动判断的一致性：

1. 订阅目标合约是否命中
2. 恢复后是否重新看到目标合约 tick
3. bridge 是否有 `tick` 事件

### 2. 订单证据

正式来源：

1. `python scripts/ctp_order_lifecycle_smoke.py --config <path> ...`

当前可稳定留存的字段包括：

1. `command_kinds`
2. `mapped_submit_order_ref`
3. `matched_exec_count`
4. `matched_execs[].native_order_id`
5. `matched_execs[].native_order_ref`
6. `matched_execs[].status`
7. `matched_execs[].match_reason`

当前自动判断的一致性：

1. 本次发送后是否产生了新增 `ORDER` 回报
2. native 回报是否已回绑到本次 Python `client_order_id`
3. 是否存在“发单成功但完全没有匹配回报”的异常

### 3. 成交证据

当前正式来源仍然沿用 order lifecycle smoke 的 `TRADE` 事件输出：

1. `exec_events[].trade_volume`
2. `matched_execs[].is_trade`
3. `matched_execs[].trade_volume`

当前自动判断的一致性：

1. 若 `TRADE` 事件出现，则其 `trade_volume` 必须大于 `0`
2. 若本次 smoke 目标是“仅验证发单且不成交”，则 `trade_volume = 0` 可以是成功口径

当前仓内已知事实：

1. 现有真实 `c2609` smoke 留证停留在“已发单、未成交”的安全口径
2. 所以“成交后仓位/资金联动是否正确”目前不能仅靠现有自动证据宣告通过

## 四、当前只有能力预留、尚未形成正式 smoke 的证据链

### 4. 持仓证据

仓内已有能力预留：

1. runtime command/event 已定义 `QUERY_POSITIONS` / `POSITION`
2. native manifest 已登记 `TdQryPosition`

但当前缺口是：

1. 还没有正式 `position query smoke`
2. 还没有结构化 `position snapshot evidence`
3. 还没有“下单/成交后如何对照持仓变化”的正式基线

因此当前规则是：

1. 持仓对账目前只能列为“人工复核项”
2. 不得把 native export 存在误写成“position reconciliation 已完成”

### 5. 资金证据

仓内已有能力预留：

1. runtime command/event 已定义 `QUERY_ACCOUNT` / `ACCOUNT`
2. native manifest 已登记 `TdQryAccount`

但当前缺口是：

1. 还没有正式 `account query smoke`
2. 还没有结构化 `account snapshot evidence`
3. 还没有“成交后资金变化如何自动核对”的正式基线

因此当前规则是：

1. 资金对账目前只能列为“人工复核项”
2. 不得把 manifest/export 当作正式验收通过证据

## 五、最小自动对账规则

当前允许自动判断的一致性，只限定在已经有正式证据链的部分：

1. `MD` 目标合约与实际 tick 一致
2. `TD` login + settlement 事件完整
3. order lifecycle 中“本次发送”和“本次新增回报”可关联
4. 若存在 `TRADE` 事件，则成交量字段必须自洽

## 六、必须人工复核的不一致性

下面这些差异当前必须人工处理：

1. 订单已发出，但是否最终成交、是否需要撤单
2. 持仓变化与预期是否一致
3. 资金变化与成交结果是否一致
4. 历史 exec 回放与当前订单回报之间的歧义
5. 任何需要跨 session 判断 broker 真相的场景

## 七、正式证据留存顺序

当前建议的审计留存顺序是：

1. 先留 mainline live smoke 证据
2. 再留 marketdata smoke 证据
3. 再留 execution order lifecycle smoke 证据
4. 若进入持仓/资金核查，则单独生成人工复核记录，不与自动 smoke 混写

## 八、当前最小结论

1. 市场数据、订单、成交三类证据已经有正式自动化入口
2. 持仓、资金两类证据当前只有能力预留，还没有正式 smoke 基线
3. 因此 Topic 5 的 audit/reconciliation 当前只能宣告“最小 baseline 已冻结”，不能宣告“完整自动对账已完成”

## 九、交给 C4 的直接输入

`operational-evidence-matrix` 必须直接继承这 3 条：

1. 证据链按五类分层
2. 自动证据与人工复核证据必须分开
3. 不得把 native export 的存在当成正式对账通过
