# Full Reconciliation Automation Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：100%
**topic-id**：full-reconciliation-automation
**domain**：nautilus_adapter
**用途**：在真实账户 `025292` 的只读基础上，把 position/account query baseline 推进成更正式的 reconciliation snapshot、差异判断和自动 evidence 主线。

---

## 一、为什么这个 topic 现在应该继续

`position-account-query-baseline` 已经完成：

1. `TdQryPosition`
2. `TdQryAccount`
3. `query_adapter` 最小统一入口

但距离“更完整自动对账”还差一层明确 contract：

1. 缺统一 reconciliation snapshot 视图
2. 缺汇总指标和 symbol exposure 口径
3. 缺 mismatch 分类和 evidence 结构
4. 缺面向运维的正式 reconciliation smoke

## 二、主题目标

1. 冻结 reconciliation snapshot 与 summary contract。
2. 建立真实 `025292` 的 reconciliation smoke。
3. 为后续 mismatch policy 和自动 evidence 打基础。
4. 保持只读，不新增真实交易动作。

## 三、实盘边界

本 topic 继续使用真实账户 `025292`，但只允许：

1. `TdQryPosition`
2. `TdQryAccount`
3. 基于查询结果的汇总、对账、evidence

不允许：

1. 新增真实下单、撤单、改单
2. 把“汇总快照”宣告成“完整自动对账”已完成

## 四、进入条件

1. [position-account-query-baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/position-account-query-baseline.md) 已完成。
2. `query_adapter` 已能通过真实账户拿到 position/account 统一快照。

## 五、Topic 级出口条件

1. reconciliation snapshot contract 已冻结。
2. reconciliation smoke 已建立并留证。
3. mismatch policy 已具备正式 child change 落点。
4. 自动 evidence 口径已能复用到后续 topic。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260403__full-reconciliation-automation__reconciliation-snapshot-contract` | 冻结 reconciliation snapshot、summary 和 symbol exposure contract | ✅ 已完成 |
| C2 | `20260403__full-reconciliation-automation__live-reconciliation-summary-smoke` | 建立真实 `025292` 的 reconciliation summary smoke 与 evidence | ✅ 已完成 |
| C3 | `20260403__full-reconciliation-automation__mismatch-policy-baseline` | 冻结 mismatch 分类、升级口径和 evidence 字段 | ✅ 已完成 |
| C4 | `20260403__full-reconciliation-automation__automated-reconciliation-evidence` | 建立正式自动 evidence 输出 | ✅ 已完成 |

## 七、AI-TASK-QUEUE

**当前状态**：已完成；`C1/C2/C3/C4` 全部收口。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 推进 `C2`
- [x] 完成 `C4`
- [ ] 回写下一轮更完整 startup/reconciliation roadmap

**当前 first action**：暂无；等待下一轮 topic

## 八、成功信号

1. 能通过正式入口得到统一 reconciliation summary
2. symbol exposure 口径稳定
3. account 可用资金 / 保证金比率有稳定输出
4. 后续 mismatch policy 不必重新发明输入模型

## 九、Topic Closure

1. 当前仓内已经有 `query baseline -> summary -> mismatch policy -> automated evidence` 的完整只读链路。
2. 真实 `025292` 的 live smoke 已经分别验证了 summary、policy 和 evidence 输出。
3. 所有 child change 的验收证据都已明确约束为真实 live smoke，不使用 test/mock/fake 结果宣告通过。
