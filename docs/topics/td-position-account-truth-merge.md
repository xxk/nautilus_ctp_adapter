# TD Position Account Truth Merge Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：C1-C3 completed
**topic-id**：td-position-account-truth-merge
**domain**：nautilus_adapter
**用途**：把真实 TD callback truth 与 position/account query baseline 合并，形成更完整的只读 reconciliation 真相层。

---

## 一、为什么这个 topic 现在应该继续

当前仓内已经有：

1. position/account query baseline
2. reconciliation summary / evidence
3. TD order truth baseline / historical boundary / evidence matrix

但还缺：

1. order/trade truth 与 position/account query 的统一视角
2. 只读 session 内 truth merge contract
3. 更完整的 position/account/order reconciliation evidence

## 二、主题目标

1. 建立 TD truth merge snapshot 的正式 live evidence 入口。
2. 冻结 order/trade/position/account 的统一真相视图。
3. 收口更完整的 reconciliation evidence matrix。
4. 保持只读，不新增真实交易动作。

## 三、实盘边界

本 topic 继续使用真实账户 `025292`，但只允许：

1. `TD login/settlement/query/callback observation` 级别的只读 smoke
2. 相关 truth merge、reconciliation evidence

不允许：

1. 新增真实下单、撤单、改单
2. 用 test/mock/fake 结果充当验收证据

## 四、进入条件

1. [td-order-truth-and-reconciliation](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/td-order-truth-and-reconciliation.md) 已完成。
2. 仓内已有真实 live order truth evidence 与 position/account query baseline。

## 五、Topic 级出口条件

1. TD truth merge contract 已冻结。
2. merged reconciliation policy 已有正式 child change 落点。
3. merged evidence matrix 已有真实 live smoke 证据。
4. real-only evidence 口径在本 topic 内持续保持。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260403__td-position-account-truth-merge__td-truth-merge-snapshot` | 冻结 order/trade/position/account 的只读 truth merge snapshot | ✅ 已完成 |
| C2 | `20260403__td-position-account-truth-merge__merged-reconciliation-policy` | 冻结 merged truth 的 reconciliation policy | ✅ 已完成 |
| C3 | `20260403__td-position-account-truth-merge__merged-evidence-matrix` | 收口 merged truth 的正式 evidence matrix | ✅ 已完成 |

## 七、AI-TASK-QUEUE

**当前状态**：已完成；`C1/C2/C3` 全部收口。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 推进 `C2`
- [x] 推进 `C3`

**当前结论**：本 topic 已通过真实 `025292` live smoke 完成 TD merged truth snapshot、merged reconciliation policy 与 merged evidence matrix 的闭环。
