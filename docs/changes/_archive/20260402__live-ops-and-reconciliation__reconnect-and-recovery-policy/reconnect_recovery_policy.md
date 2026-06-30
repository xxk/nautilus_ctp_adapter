# Reconnect And Recovery Policy

**日期**：2026-04-02  
**topic-id**：`live-ops-and-reconciliation`  
**change-id**：`20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy`

## 一、用途

这份 policy 用来冻结 `nautilus_ctp_adapter` 在 live 运行中的恢复口径。

它回答 4 个问题：

1. 哪些可以自动恢复
2. 哪些只允许有限重试
3. 哪些必须升级成人工介入
4. 恢复过程中哪些状态可以继承，哪些必须重建

## 二、恢复层级

恢复分 4 层看：

1. `MD channel`
2. `TD channel`
3. `runtime bridge state`
4. `flow directory / session artifact`

原则是：

1. 行情恢复优先自动化
2. 交易恢复优先保守化
3. 任何可能污染订单身份或 session 判定的状态，都不允许盲继承

## 三、MD 恢复策略

### 自动恢复

当前仓内已经冻结的 `MD` 恢复 contract 是：

1. `CtpDataClient` 持有 `active_subscription_symbols`
2. `drain_marketdata_event_batch()` 遇到 `DISCONNECTED` 会给出 `should_restore = true`
3. `restore_market_data_subscriptions()` 会重发：
   - 1 条 `CONNECT`
   - N 条 `SUBSCRIBE_MARKET_DATA`

这意味着 `MD` 的恢复策略是：

1. 允许自动重连
2. 允许自动重订阅
3. 恢复成功的判定必须回到“重新看到订阅合约 tick”

### 不允许宣告恢复成功的情况

下面这些情况不允许只因为重发了 `CONNECT/SUBSCRIBE` 就宣告恢复成功：

1. 只有 `DISCONNECTED` 事件，没有后续 `LOGIN_SUCCEEDED`
2. 只有 `LOGIN_SUCCEEDED`，但没有恢复后的目标合约 tick
3. 重连后订阅列表丢失或为空

### 人工介入边界

下面情况应升级为人工排查：

1. 连续自动 restore 后仍拿不到目标合约 tick
2. `MD front` 明显错误或配置漂移
3. loader / DLL 路径异常导致 `CtpMdApi` 无法创建

## 四、TD 恢复策略

### 自动恢复允许范围

`TD` 只允许做“bootstrap 级恢复”，不允许盲目把旧下单上下文自动续接。

允许自动恢复的步骤是：

1. 重新 `CONNECT`
2. 重新 `AUTHENTICATE`
3. 重新 `LOGIN`
4. 重新 `CONFIRM_SETTLEMENT`

恢复成功的最低信号是：

1. `login_success = true`
2. `settlement_code = 0`
3. runtime bridge 中重新看到 `LOGIN_SUCCEEDED` 和 `SETTLEMENT_CONFIRMED`

### 不允许自动继承的状态

下面这些状态不允许在 `TD` 断线后直接沿用：

1. 旧的 `front_id / session_id`
2. 旧的 `max_order_ref` 推导链
3. 旧的“当前发单正在等待回报”推断
4. 旧 flow 目录中的 session artifact

原因是：

1. `TD` 身份和订单关联高度依赖当前 session
2. 旧 artifact 会把历史 exec 回放混进当前会话
3. 这会让“当前这笔单是否真的收到了新增回报”产生误判

### 必须人工介入的情况

下面情况必须升级人工处理，不允许 AI 或脚本自行宣告恢复：

1. `authenticate_code != 0`
2. `login_success != true`
3. `settlement_code != 0`
4. 恢复后出现历史 exec 回放与当前订单回报无法区分
5. 需要判断真实订单状态、持仓状态或是否需要撤单

## 五、runtime bridge 恢复边界

runtime bridge 的恢复策略分两部分：

1. `MD` 侧事件流允许继续使用现有 bridge，并通过新事件覆盖旧状态
2. `TD` 侧只允许把新的 login / settlement / order / trade 事件继续推入 bridge，但不允许仅靠旧事件推断恢复成功

冻结规则：

1. bridge 是事件通道，不是 broker 真相来源
2. `MD` 恢复是否成功，必须看恢复后的新 tick
3. `TD` 恢复是否成功，必须看恢复后的新 `LOGIN_SUCCEEDED + SETTLEMENT_CONFIRMED`
4. 若要判断真实订单生命周期，必须只看“恢复后新增且可识别”的 exec 回报

## 六、flow directory 策略

### MD flow

当前 `MD` 默认 flow 目录是稳定目录：

1. `var/md_flow_smoke`

现阶段口径：

1. `MD` flow 允许稳定复用
2. 但恢复成功仍以“新 tick”判断，而不是以目录是否可用判断

### TD readiness flow

当前 `TD readiness` 默认 flow 目录也是稳定目录：

1. `var/td_flow_smoke`

它适用于：

1. readiness 诊断
2. login / settlement bootstrap

### live order flow

真实 `order lifecycle smoke` 已冻结为每次唯一 flow 目录：

1. `output/debug/live_order_smoke_<time_ns>`

这条规则必须保留，不能回退。  
原因是它直接防止：

1. 旧 session artifact 干扰当前会话
2. 历史 exec 回放污染本次发单回报判定

## 七、恢复顺序

统一恢复顺序如下：

1. 先判断故障落在 `MD`、`TD` 还是共同依赖层
2. 若仅 `MD` 异常：
   - 执行 `MD connect/login`
   - 恢复 active subscriptions
   - 等待目标合约 tick
3. 若 `TD` 异常：
   - 执行 `TD authenticate/login`
   - 重新确认 settlement
   - 丢弃旧 session 身份推断
   - 如需继续订单级验证，使用新的唯一 flow 目录
4. 若共同依赖层异常：
   - 先排 DLL/loader/config
   - 再重试 channel 级恢复

## 八、失败升级规则

### 可自动重试

1. 单次 `MD` disconnect 且仍保有订阅集
2. `TD` 重新 bootstrap 时的短暂网络波动，但未进入真实订单状态判断

### 必须停止并人工确认

1. 需要确认真实订单是否已报出、是否成交、是否需要撤单
2. session 身份与 native 回报关联出现歧义
3. 结算确认失败
4. auth/login 返回非零错误
5. 怀疑 flow 目录复用导致历史 artifact 污染当前判断

## 九、与后续 Topic 5 子阶段的关系

1. `C3 audit-and-reconciliation-baseline` 将继承本 policy 的“哪些状态不能盲信”
2. `C4 operational-evidence-matrix` 将继承本 policy 的失败升级与人工介入边界

## 十、当前冻结结论

1. `MD` 恢复默认允许自动 restore，但必须以恢复后的新 tick 判定成功
2. `TD` 恢复只允许 bootstrap 级重建，不允许盲继承旧 session 身份与订单推断
3. runtime bridge 只能当事件证据通道，不能替代 broker 真实状态
4. 真实 order lifecycle 验证必须继续使用唯一 flow 目录
