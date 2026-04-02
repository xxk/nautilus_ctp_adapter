# Nautilus CTP Adapter Mainline Topic Roadmap

**创建日期**：2026-04-01
**最后更新**：2026-04-02
**状态**：进行中
**进度**：Topic 1 / 5
**topic-id**：nautilus-ctp-adapter-mainline
**用途**：作为 `nautilus_ctp_adapter` 的总 roadmap，按多个 topic 推进“使用真实 CTP 账户、集中适配 Nautilus”的正式开发计划。

---

## 一、长期目标

1. 使用真实 CTP 期货账户完成 Nautilus 实盘接入，而不是停留在示例或诊断脚本层。
2. 让仓内维护的 `ctpnative`、共享 runtime、Nautilus adapter 三层边界稳定可维护。
3. 先打通行情，再打通交易，再补齐运营与对账闭环。

## 二、真实账户统一安全边界

以下规则自 2026-04-02 起视为 `025292` 实盘账户的仓内统一 guardrails，后续任何 execution change、smoke、诊断脚本或人工调试都不得越过：

1. 调试下单只允许 `c2609`。
2. 单笔报单数量上限为 `1` 手。
3. 调试期净持仓上限按 `5` 手处理。
4. 任意 1 分钟窗口内报单次数不得超过 `10` 次。
5. 调试默认只能使用一档价格下单：`BUY -> ask1`，`SELL -> bid1`。
6. 在 Topic 4 的 execution guardrails 生效前，不允许把任何“真发单能力”接进 Nautilus 主线。

说明：用户原话中出现“持仓最大 5 收”，当前按“`5` 手”冻结；若后续用户明确不是 `5` 手，则必须先更新本节与 Topic 4 guardrails，再推进 execution 实现。

## 三、主线推进原则

1. 一次只推进一个 implementation topic；只有当前 topic 达到 topic 级出口条件，下一 topic 才能进入 `in_progress`。
2. 每个 topic 都必须具备 4 个最小元素：topic README、child change 队列、topic 级验收、明确的 next action。
3. 除非 topic README 明确声明 anchor change 例外，否则同一 topic 内同时只允许一个 child change 处于 `in_progress`。
4. 每个 child change 完成后，必须先回填 `plan.md`、`acceptance.md`、`ai_constraints.md` 和 topic queue 状态，再继续下一个 child change。
5. 若下一 topic 的 README 不存在，AI 不能直接跳 topic 实现；必须先创建 topic README，再创建该 topic 的首个 child change。

## 四、Topic 顺序

| Topic | 状态 | 核心目标 | 说明 |
| --- | --- | --- | --- |
| Topic 1: `ctp-live-connectivity` | 进行中 | 真实账户连通、MD/TD 基础登录、`rb2610` 行情与最小 smoke 入口 | 当前第一优先级 topic |
| Topic 2: `nautilus-instrument-provider` | 未开始 | 合约查询、符号映射、InstrumentProvider 正式落地 | 解决 Nautilus 识别 CTP 合约的问题 |
| Topic 3: `nautilus-live-marketdata` | 未开始 | LiveDataClient、订阅恢复、批量事件出桥、Nautilus 数据侧 smoke | 把 Topic 1 的行情链路接进正式 Nautilus adapter |
| Topic 4: `nautilus-live-execution` | 未开始 | TD auth/login、下单/撤单、订单状态机、LiveExecutionClient | 从“能连”升级到“能交易” |
| Topic 5: `live-ops-and-reconciliation` | 未开始 | 启动对账、失败诊断、重连、运维脚本与实盘验收矩阵 | 补齐实盘长期可运维性 |

## 五、Topic 切换门槛

| Topic | 进入条件 | 退出条件 | 下一 topic 可继承的稳定产物 |
| --- | --- | --- | --- |
| `ctp-live-connectivity` | 仓库具备 live config 样例、native pack 来源和最小 smoke 方向 | `rb2610` live 连通证据、主线路径、TD readiness 和 Nautilus smoke 基线都已留证 | live config contract、native ownership、MD/TD readiness、smoke baseline |
| `nautilus-instrument-provider` | Topic 1 完成，主线 live/bootstrap 口径已冻结 | 合约查询、符号归一化和 InstrumentProvider 最小闭环成立 | instrument query contract、symbol mapping、provider bootstrap |
| `nautilus-live-marketdata` | Topic 2 完成，InstrumentProvider 可稳定提供合约定义 | LiveDataClient 与订阅恢复路径成立，行情事件可稳定出桥 | marketdata runtime contract、subscription restore、Nautilus data smoke |
| `nautilus-live-execution` | Topic 3 完成，Topic 1 的 TD readiness 已收敛 | TD 主线登录、下单撤单和订单状态机形成最小闭环 | execution runtime contract、order lifecycle smoke |
| `live-ops-and-reconciliation` | Topic 4 完成，仓库具备最小 live trading 路径 | 启动、恢复、审计、对账和运营 runbook 收敛 | ops smoke、recovery policy、reconciliation baseline |

## 六、为什么 Topic 1 必须先做

第一个 topic 必须先解决“真实账户是否可被仓内 runtime 和 adapter 目标路径稳定接住”。

如果 Topic 1 没完成，后面 Topic 2-5 都会陷入两个问题：

1. 我们不知道真实账户登录参数、前置地址、授权链路到底能不能在本仓稳定复现。
2. 我们无法判断后续 InstrumentProvider、LiveDataClient、LiveExecutionClient 的问题，究竟是适配器问题，还是底层 live 连通本身没站稳。

所以 Topic 1 的定位不是“做最终功能”，而是“冻结真实连通与 smoke 基线”。

## 七、Autopilot 执行契约

要让 Codex 或其他代理一次性顺着 mainline 推进，必须按下面顺序执行：

1. 先从当前 `in_progress` topic 开始，不允许跳过当前 topic 直接实现后续 topic。
2. 在当前 topic 内优先读取 topic README，再读取当前 active child change 的 `acceptance.md`、`plan.md`、`ai_constraints.md`。
3. 若当前 topic README 声明了 anchor change，允许该 anchor change 在 topic 结束前保持 `in_progress`；除此之外一次只推进一个 implementation change。
4. 每完成一个 child change，必须先更新 child change 三件套与 topic queue，再选择该 topic 的下一个 `not_started` change。
5. 当前 topic 全部 child change 完成后，必须先把 topic README 标记为 completed，并明确下一个 topic 的 first child change，再进入下一 topic。

真实阻塞只允许是下面四类：

1. 缺本机或远端权限，导致正式验证命令无法执行。
2. 缺 live 依赖或目标前置不可达，且仓内不存在可替代的验证口径。
3. 当前 child change 的 `plan.md`、`acceptance.md`、`ai_constraints.md` 互相冲突，无法从仓库事实消解。
4. topic 级出口条件无法判定，导致 AI 无法判断“完成”与“未完成”。

## 八、允许并行的预备工作

默认没有可以并行实现的 implementation topic；主线实现仍按 Topic 1 -> 5 串行推进。

当前唯一建议并行给 Codex 的，是不会消耗不稳定运行时结论的 prework：

1. `Topic 4 / C0`：`20260402__nautilus-live-execution__real-account-debug-guardrails`
   这是安全规则、配置表达和 precheck 入口，不依赖 Topic 2/3 的实现完成，可先做。
2. `Topic 2` 的 docs-only 预备工作
   仅允许预创建 child change bundle、冻结 acceptance 骨架、整理映射规则输入；不允许提前写 `InstrumentProvider` 正式实现。
3. `Topic 3` 和 `Topic 5` 当前不建议并行
   它们直接依赖上游稳定产物，提前实现会把不稳定假设固化进代码。

## 九、Topic 级总验收

1. Nautilus 方向的 CTP 适配开发顺序被拆成多个 topic，并且 topic 边界清楚、不重叠。
2. Topic 1 完成后，仓库应具备真实账户 live bootstrap 基线。
3. Topic 3 完成后，Nautilus 应能稳定接收真实行情。
4. Topic 4 完成后，Nautilus 应能在 guardrails 生效前提下完成最小实盘交易链路。
5. Topic 5 完成后，仓库应具备实盘运行、诊断、对账与收口能力。

## 十、Topic Roadmap Index

1. [ctp-live-connectivity](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md)
2. [nautilus-instrument-provider](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md)
3. [nautilus-live-marketdata](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md)
4. [nautilus-live-execution](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-execution/README.md)
5. [live-ops-and-reconciliation](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md)

## 十一、AI-TASK-QUEUE

**当前活动 Topic**：`ctp-live-connectivity`

- [x] `docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md`
- [ ] `docs/changes_topic/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md`
- [ ] `docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md`
- [ ] `docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-execution/README.md`
- [ ] `docs/changes_topic/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md`

**当前 next action**：按 `ctp-live-connectivity` README 中声明的 child-change 顺序完成 Topic 1；Topic 1 关闭前不得切到 Topic 2。

## 十二、不在本层解决的内容

1. 单个 child change 的详细任务分解。
2. 单次 smoke 的原始日志。
3. 具体代码改动清单。
4. 单轮失败留证与补丁说明。

## 十三、相关文档

1. [CTP live connectivity roadmap](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md)
2. [Platform-neutral CTP runtime](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md)
3. [Rust / Python adapter split](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md)
4. [Runtime performance guidelines](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md)
