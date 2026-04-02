# TD Order Truth And Reconciliation Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：C1-C3 completed
**topic-id**：td-order-truth-and-reconciliation
**用途**：在 MD/TD startup truth 与只读查询基线已经稳定的前提下，继续冻结真实订单回报真相、历史回报边界和只读 reconciliation 证据口径。

---

## 一、为什么这个 topic 现在应该继续

当前仓内已经有：

1. TD startup truth / session rebuild / evidence matrix
2. MD startup truth / restore policy / evidence matrix
3. 真实 `025292` 的 position/account/reconciliation 只读基线

但还缺：

1. 真实 order/trade callback 真相与历史回报边界
2. 跨 session 的 order/trade truth 证据
3. 面向 Nautilus 的 order reconciliation 只读 evidence

## 二、主题目标

1. 建立 TD order/trade truth 的正式 live evidence 入口。
2. 冻结历史回报、延迟回报与当前 session 真相的边界。
3. 收口 order reconciliation 的只读 evidence matrix。
4. 保持只读，不新增真实交易动作。

## 三、实盘边界

本 topic 继续使用真实账户 `025292`，但只允许：

1. `TD login/settlement/query/order-callback truth` 级别的只读 smoke
2. 相关 order truth、trade truth、reconciliation evidence

不允许：

1. 新增真实下单、撤单、改单
2. 用 test/mock/fake 结果充当验收证据

## 四、进入条件

1. [md-startup-truth-and-restore](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/md-startup-truth-and-restore/README.md) 已完成。
2. 仓内已有真实 live startup/restore evidence 和只读 reconciliation baseline。

## 五、Topic 级出口条件

1. TD order truth contract 已冻结。
2. 历史回报与当前 session 真相边界已有正式 policy。
3. order reconciliation evidence matrix 已有真实 live smoke 证据。
4. real-only evidence 口径在本 topic 内持续保持。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260403__td-order-truth-and-reconciliation__td-order-truth-baseline` | 冻结真实 order/trade callback truth 的只读 baseline | ✅ 已完成 |
| C2 | `20260403__td-order-truth-and-reconciliation__historical-callback-boundary-policy` | 冻结历史回报与当前 session 边界 | ✅ 已完成 |
| C3 | `20260403__td-order-truth-and-reconciliation__order-reconciliation-evidence-matrix` | 收口 order truth/reconciliation 的正式 evidence 矩阵 | ✅ 已完成 |

## 七、AI-TASK-QUEUE

**当前状态**：已完成；`C1/C2/C3` 全部收口。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 推进 `C2`
- [x] 推进 `C3`

**当前结论**：本 topic 已通过真实 `025292` live smoke 完成 order truth baseline、historical boundary policy 与 evidence matrix 的闭环。
