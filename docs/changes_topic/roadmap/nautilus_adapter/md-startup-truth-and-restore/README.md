# MD Startup Truth And Restore Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：C1-C3 completed
**topic-id**：md-startup-truth-and-restore
**用途**：在 TD startup truth 已冻结的基础上，继续冻结 MD startup truth、订阅恢复与 restore evidence 的正式口径。

---

## 一、为什么这个 topic 现在应该继续

当前仓内已经有：

1. `rb2610` 的正式 marketdata baseline
2. TD startup truth / session rebuild / evidence matrix
3. real-only acceptance governance

但还缺：

1. MD startup truth 的正式 evidence baseline
2. MD restore 后“新 tick 才算恢复成功”的稳定证据层
3. flow / subscription restore 的正式 matrix

## 二、主题目标

1. 建立 MD startup truth 的正式 live evidence 入口。
2. 冻结 restore 成功必须以恢复后的新 tick 为准的证据口径。
3. 收口 MD restore evidence matrix。
4. 保持只读，不新增真实交易动作。

## 三、实盘边界

本 topic 继续使用真实账户 `025292`，但只允许：

1. `MD login/subscribe/restore` 级别的只读 smoke
2. 相关 startup truth、restore truth、evidence matrix

不允许：

1. 新增真实下单、撤单、改单
2. 用 test/mock/fake 结果充当验收证据

## 四、进入条件

1. [startup-truth-and-session-rebuild](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/startup-truth-and-session-rebuild/README.md) 已完成。
2. 仓内已有正式 `rb2610` marketdata baseline 与 TD startup truth evidence。

## 五、Topic 级出口条件

1. MD startup truth contract 已冻结。
2. MD restore policy 已有正式 child change 落点。
3. MD evidence matrix 已有真实 live smoke 证据。
4. real-only evidence 口径在本 topic 内持续保持。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260403__md-startup-truth-and-restore__md-startup-truth-baseline` | 冻结 MD login、subscription、first tick 的 startup truth baseline | ✅ 已完成 |
| C2 | `20260403__md-startup-truth-and-restore__md-restore-policy` | 冻结 restore 成功判定与订阅恢复边界 | ✅ 已完成 |
| C3 | `20260403__md-startup-truth-and-restore__md-truth-evidence-matrix` | 收口 MD startup/restore 的正式 evidence 矩阵 | ✅ 已完成 |

## 七、AI-TASK-QUEUE

**当前状态**：已完成；`C1/C2/C3` 全部收口。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 推进 `C2`
- [x] 推进 `C3`

**当前结论**：本 topic 已通过真实 `025292` + `rb2610` live smoke 完成 MD startup truth、restore policy 与 evidence matrix 的闭环。
