# Position Account Query Baseline Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：100%
**topic-id**：position-account-query-baseline
**domain**：nautilus_adapter
**用途**：使用真实账户 `025292` 的只读查询能力，把持仓与资金查询从“native 能力预留”推进成正式 smoke、正式证据链和 Nautilus 可消费的查询基线。

---

## 一、为什么这个 topic 应该优先

当前主线已经完成：

1. live bootstrap
2. instrument
3. marketdata
4. execution
5. ops/recovery/audit baseline

但还有一个明显功能缺口没有完成成正式主线能力：

1. `TdQryPosition`
2. `TdQryAccount`

这两条能力现在只停留在：

1. runtime command/event 已定义
2. native manifest 已登记 export
3. 还没有正式 smoke、正式 evidence、正式 adapter 口径

所以这个 topic 的价值是：

1. 它能直接补齐当前最实际的功能空白
2. 它只需要 `025292` 的只读查询，不需要新增实盘交易风险
3. 它会直接提升后续完整自动对账能力

## 二、主题目标

1. 把 `position` 与 `account` 查询做成正式仓内主线能力。
2. 建立只读 query smoke 和正式 evidence。
3. 给 Nautilus 侧提供稳定的 position/account query contract。
4. 为后续完整 reconciliation automation 打下基础。

## 三、实盘边界

本 topic 使用真实账户 `025292`，但只允许做只读查询：

1. 允许 `TdQryPosition`
2. 允许 `TdQryAccount`
3. 允许与这些查询相关的 evidence/smoke
4. 不新增新的发单、撤单、改单行为

说明：

1. Topic 4 已冻结的 execution guardrails 继续有效
2. 本 topic 不以“新增真实交易动作”为目标

## 四、进入条件

1. [nautilus-ctp-adapter-mainline](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-ctp-adapter-mainline.md) 已完成初版收口。
2. Topic 5 已明确 position/account 仍属于人工复核空白区。

## 五、Topic 级出口条件

1. `position query smoke` 已建立。
2. `account query smoke` 已建立。
3. position/account 已有结构化 evidence。
4. Nautilus 侧已具备稳定的 query contract。
5. Topic 5 里“position/account 仅人工复核”的口径可以被缩小或替换。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260403__position-account-query-baseline__runtime-query-contract` | 冻结 `QUERY_POSITIONS / QUERY_ACCOUNT` 与 `POSITION / ACCOUNT` 的正式 runtime contract | ✅ 已完成 |
| C2 | `20260403__position-account-query-baseline__position-query-smoke` | 建立真实 `025292` 持仓查询 smoke 与 evidence | ✅ 已完成 |
| C3 | `20260403__position-account-query-baseline__account-query-smoke` | 建立真实 `025292` 资金查询 smoke 与 evidence | ✅ 已完成 |
| C4 | `20260403__position-account-query-baseline__nautilus-query-adapter-baseline` | 把 position/account query 接成 Nautilus 可消费的最小 adapter baseline | ✅ 已完成 |

## 七、AI-TASK-QUEUE

**当前状态**：已完成；`C1/C2/C3/C4` 全部收口。

- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 完成 `C2`
- [x] 完成 `C3`
- [x] 完成 `C4`
- [ ] 回写新的 post-mainline 主线或扩展 roadmap

**当前 first action**：暂无；等待下一轮 post-mainline topic

## 八、成功信号

1. 能通过正式入口拿到 `POSITION` 快照
2. 能通过正式入口拿到 `ACCOUNT` 快照
3. evidence 中能区分“无持仓/无变动”和“查询失败”
4. query 结果能作为后续 reconciliation 自动化的可信输入

## 十、Topic Closure

1. 真实账户 `025292` 的 `position/account` 只读查询已经建立正式 smoke 和 evidence。
2. `CtpQueryAdapter` 已提供最小 Nautilus-facing snapshot baseline，不再停留在 native 能力预留阶段。
3. 后续如果继续推进，应新开更上层的 reconciliation / startup truth topic，而不是在本 topic 内继续堆叠。

## 九、与现有 completed mainline 的关系

这个 topic 不是对当前 mainline 的回滚，而是下一轮功能增强 topic。

它最自然的承接关系是：

1. 继承 Topic 5 的 audit/reconciliation baseline
2. 把其中“持仓/资金仍需人工复核”的部分推进成正式自动化 query baseline
