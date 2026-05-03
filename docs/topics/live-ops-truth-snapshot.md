# Live Ops Truth Snapshot Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-10
**状态**：阻塞
**进度**：C2 blocked（live retry blocked by unstable disconnect storm）
**topic-id**：live-ops-truth-snapshot
**domain**：nautilus_adapter
**用途**：把已冻结的 startup truth、MD truth、TD merged truth 与 reconciliation evidence 收成单个只读 live ops truth 入口。

---

## 一、为什么这个 topic 现在应该继续

当前仓内已经有：

1. TD startup truth / session rebuild / evidence matrix
2. MD startup truth / restore / evidence matrix
3. TD position/account truth merge 与 merged evidence matrix
4. real-only acceptance governance

但还缺：

1. 单个只读 live ops snapshot 入口
2. 面向运维消费的统一 policy 口径
3. 更稳定的 live ops evidence matrix

## 二、主题目标

1. 建立只读 `live ops snapshot` 的正式 live evidence 入口。
2. 冻结面向运维消费的统一 live ops policy。
3. 收口 live ops evidence matrix。
4. 保持只读，不新增真实交易动作。

## 三、实盘边界

本 topic 继续使用真实账户 `025292`，但只允许：

1. `TD/MD login/query/callback observation` 级别的只读 smoke
2. 相关 truth merge、ops policy、ops evidence

不允许：

1. 新增真实下单、撤单、改单
2. 用 test/mock/fake 结果充当验收证据

## 四、进入条件

1. [td-position-account-truth-merge](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/td-position-account-truth-merge.md) 已完成。
2. 仓内已有真实 live 的 startup truth、MD truth、TD merged truth 与 reconciliation evidence。

## 五、Topic 级出口条件

1. live ops snapshot contract 已冻结。
2. live ops policy 已有正式 child change 落点。
3. live ops evidence matrix 已有真实 live smoke 证据。
4. real-only evidence 口径在本 topic 内持续保持。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260403__live-ops-truth-snapshot__live-ops-snapshot-baseline` | 冻结 startup/md/td/reconciliation 的统一只读 live ops snapshot | ✅ 已完成 |
| C2 | `20260403__live-ops-truth-snapshot__live-ops-policy-baseline` | 冻结 live ops snapshot 的统一 policy 与处置口径 | 🔄 进行中 |
| C3 | `20260403__live-ops-truth-snapshot__live-ops-evidence-matrix` | 收口 live ops 的正式 evidence matrix | ⬜ 待执行 |

## 七、AI-TASK-QUEUE

**当前状态**：阻塞；`C2` 受 disconnect storm 影响暂停。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [ ] 推进 `C2`
- [ ] 推进 `C3`

**当前 first action**：待外部 disconnect storm 收敛后，再继续稳定化并重跑 `20260403__live-ops-truth-snapshot__live-ops-policy-baseline` 的真实 live smoke
