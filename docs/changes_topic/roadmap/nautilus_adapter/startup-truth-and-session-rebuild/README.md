# Startup Truth And Session Rebuild Topic Roadmap

**创建日期**：2026-04-03
**最后更新**：2026-04-02
**状态**：已完成
**进度**：C1-C3 completed
**topic-id**：startup-truth-and-session-rebuild
**用途**：在已完成的 live startup、recovery、reconciliation 基线之上，进一步冻结 startup truth、flow 目录归属和跨 session 真相恢复规则。

---

## 一、为什么这个 topic 现在应该继续

当前仓内已经有：

1. live startup runbook
2. reconnect / recovery policy
3. reconciliation summary / policy / automated evidence

但还缺一层更靠近运行真相的正式 contract：

1. 缺 TD startup truth 的结构化证据
2. 缺 flow 目录与 session identity 的正式归属
3. 缺“当前 session 真相”和“历史 artifact”之间的边界收口

## 二、主题目标

1. 建立 startup truth 的正式 live evidence 入口。
2. 冻结 flow 目录、session identity 和 disconnect 证据口径。
3. 收口 startup truth evidence matrix。
4. 保持只读，不新增真实交易动作。

## 三、实盘边界

本 topic 继续使用真实账户 `025292`，但只允许：

1. `TD authenticate/login/settlement` 级别的只读 bootstrap
2. 相关 startup truth、session truth、rebuild evidence

不允许：

1. 新增真实下单、撤单、改单
2. 用 test/mock/fake 结果充当验收证据

## 四、进入条件

1. [full-reconciliation-automation](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/full-reconciliation-automation/README.md) 已完成。
2. 仓内已有正式 TD bootstrap 和 reconciliation evidence 输出。

## 五、Topic 级出口条件

1. startup truth contract 已冻结。
2. session rebuild policy 已有正式 child change 落点。
3. startup truth evidence matrix 已落地。
4. real-only evidence 口径在本 topic 内持续保持。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260403__startup-truth-and-session-rebuild__td-session-truth-baseline` | 冻结 TD startup truth、flow path、session identity 的 live baseline | ✅ 已完成 |
| C2 | `20260403__startup-truth-and-session-rebuild__session-rebuild-policy` | 冻结跨 session rebuild 与 artifact 边界 | ✅ 已完成 |
| C3 | `20260403__startup-truth-and-session-rebuild__startup-truth-evidence-matrix` | 收口 startup truth 的正式 evidence 矩阵 | ✅ 已完成 |

## 七、AI-TASK-QUEUE

**当前状态**：已完成；`C1/C2/C3` 全部收口。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 推进 `C2`
- [x] 推进 `C3`

**当前结论**：本 topic 已通过真实 `025292` live smoke 完成 startup truth、session rebuild policy 与 evidence matrix 的闭环。
