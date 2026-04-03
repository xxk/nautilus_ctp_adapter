# Live Ops And Reconciliation Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：Topic 5 / 5
**topic-id**：live-ops-and-reconciliation
**用途**：在行情与交易主线完成后，收口 live 启动、恢复、诊断、审计和对账规则，让 `nautilus_ctp_adapter` 具备长期可运行性。

---

## 一、主题目标

1. 冻结 live 启动 runbook、故障恢复和证据收集口径。
2. 建立 adapter 级别的审计、对账和失败诊断最小基线。
3. 让最终 mainline 完成条件不再只停留在“能连、能下单”，而是可运维。

## 二、进入条件

1. `nautilus-live-execution` 已完成。
2. 仓库已有最小 marketdata 与 execution smoke 入口。

## 三、Topic 级出口条件

1. live 启动与恢复 runbook 已冻结。
2. reconnection、recovery、audit、reconciliation 最小规则已留证。
3. 正式 failure triage 路径明确，诊断输出格式稳定。
4. mainline roadmap 可以被标记为初版 completed。

## 四、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260402__live-ops-and-reconciliation__live-startup-runbook` | 冻结 live 启动配置、入口与 runbook | ✅ 已完成 |
| C2 | `20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy` | 冻结恢复、重连和 flow/state 处理规则 | ✅ 已完成 |
| C3 | `20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline` | 建立审计与对账最小基线 | ✅ 已完成 |
| C4 | `20260402__live-ops-and-reconciliation__operational-evidence-matrix` | 收口长期运维验收矩阵 | ✅ 已完成 |

## 五、AI-TASK-QUEUE

**当前状态**：已完成；Topic 5 已达到 topic 级出口条件。

- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`
- [x] 完成 `C2`
- [x] 完成 `C3`
- [x] 完成 `C4`
- [x] 回写 mainline roadmap 为 completed

**当前 first action**：无；等待后续新一轮 roadmap 扩展。

**激活规则**：Topic 4 已 completed；当前 topic 已进入 `in_progress`。

## 六、Mainline 收尾条件

1. 上游 topic 的稳定产物都已接住。
2. live 运行、恢复、审计和对账都有正式口径。
3. `nautilus-ctp-adapter-mainline` README 可标记为 completed。
