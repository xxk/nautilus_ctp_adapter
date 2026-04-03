# Nautilus Live Execution Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：Topic 4 / 5
**topic-id**：nautilus-live-execution
**用途**：在行情与合约定义稳定后，收敛 TD 主线登录、下单撤单和订单生命周期，把 CTP 交易能力正式接入 Nautilus `LiveExecutionClient`。

---

## 一、主题目标

1. 把 Topic 1 中的 TD readiness 结论升级为正式 execution 主线。
2. 建立 `submit / cancel / order update / trade fill` 的最小执行闭环。
3. 冻结 `LiveExecutionClient` 的 smoke 入口和最小成功信号。

## 二、实盘调试 Guardrails

`025292` 是实盘账户，所以本 topic 必须先继承 mainline guardrails，再允许任何真正触达 TD 的实现继续往前：

1. 调试下单只允许 `c2609`。
2. 单笔报单数量最多 `1` 手。
3. 调试净持仓上限按 `5` 手处理。
4. 任意 1 分钟窗口内报单次数不得超过 `10` 次。
5. 调试默认只能使用一档价格下单：`BUY -> ask1`，`SELL -> bid1`。
6. Guardrails 未在配置模型、执行预检和 smoke 入口同时生效前，不允许宣称 execution 主线 ready。

说明：用户原话中的“5 收”当前按“5 手”冻结；若后续用户明确不是 `5` 手，必须先修本 topic 和对应 child change，再继续执行实现。

## 三、进入条件

1. `nautilus-live-marketdata` 已完成。
2. `ctp-live-connectivity` 中的 TD readiness 已给出明确可执行口径。

## 四、Topic 级出口条件

1. TD 主线登录已脱离临时诊断路径。
2. 最小下单撤单链路和订单状态机可在 guardrails 生效前提下复现并留证。
3. Nautilus `LiveExecutionClient` 具备可验证的正式 smoke。
4. 后续运维与对账 topic 可以建立在稳定 execution contract 上。

## 五、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C0 | `20260402__nautilus-live-execution__real-account-debug-guardrails` | 冻结 `025292` 实盘账户的调试下单边界，并先落配置与预检入口 | ✅ 已完成 |
| C1 | `20260402__nautilus-live-execution__td-mainline-login-bootstrap` | 把 TD readiness 收口到正式 execution 主线 | ✅ 已完成 |
| C2 | `20260402__nautilus-live-execution__execution-command-mapping` | 冻结下单撤单命令映射、order ref 与错误语义 | ✅ 已完成 |
| C3 | `20260402__nautilus-live-execution__live-execution-client-bootstrap` | 建立最小 `LiveExecutionClient` | ✅ 已完成 |
| C4 | `20260402__nautilus-live-execution__order-lifecycle-smoke-baseline` | 冻结 execution smoke 与证据格式 | ✅ 已完成 |

## 六、AI-TASK-QUEUE

**当前状态**：已完成；Topic 5 已接管当前活动 topic。

- [x] 创建 `C0` child change bundle
- [x] 完成 `C0`
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 完成 `C2`
- [x] 完成 `C3`
- [x] 完成 `C4`
- [x] 回写 mainline roadmap 与 Topic 5 进入条件

**当前 first action**：无；等待 Topic 5 按 `C1` 继续推进。

**激活规则**：Topic 3 已 completed；当前 topic 已进入 `in_progress`。

## 七、交接给下一 Topic 的稳定产物

1. real-account debug guardrails
2. TD mainline login contract
3. execution command mapping
4. `LiveExecutionClient` bootstrap path
5. order lifecycle smoke baseline

## 八、当前已冻结结论

1. `025292` 的 execution guardrails 已冻结
2. execution 侧已具备正式 TD bootstrap 主线
3. execution 侧已具备稳定的 submit/cancel command mapping contract
4. execution 侧已具备最小 `LiveExecutionClient` bootstrap path
5. Topic 4 已达到 topic 级出口条件，并已完成向 Topic 5 的治理交接。

## 九、完成说明

1. Topic 4 的 dry-run execution smoke baseline 已成立。
2. `TdOrderSend/TdOrderAction` 与 `TdOnExecCallback` 的仓内 ABI 已摸清并落到代码。
3. 真实 order lifecycle smoke 已通过；当前正式脚本默认使用唯一 TD flow 目录，并已稳定识别本次 `c2609` live send 的新增回报。
4. 主线 topic 切换、入口索引与 Topic 5 首个 child change 已创建完成。
