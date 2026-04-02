# Instrument Query Runtime Contract 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-02
**范围**：instrument query runtime contract
**change-id**：20260402__nautilus-instrument-provider__instrument-query-runtime-contract
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-04-02 10:31"
concluded_by: ""

exit_conditions:
  E1_success_scenarios: pending
  E2_failure_scenarios: pending
  E3_verification_cmds: pending
  E4_evidence_collected: pending
  E5_real_acceptance_only: pending
  E6_minimum_scenarios: pending

scenarios:
  A1: { exec: false, result: null, blocking: true }
  A2: { exec: false, result: null, blocking: true }
  A3: { exec: false, result: null, blocking: true }
  A4: { exec: false, result: null, blocking: true }
  A5: { exec: false, result: null, blocking: true }
  A6: { exec: false, result: null, blocking: false }
```
<!-- AI-STATUS-END -->

## 一、验收目标 / Goals

1. 证明 instrument query 的 runtime / adapter contract 已冻结。
2. 证明后续 C2/C3 不需要再重新发明 query 边界。

## 二、启动前提 / Entry Preconditions

1. Topic 1 必须已完成。
2. 本 change 不负责完整 `InstrumentProvider`，只负责 query contract。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: query command contract 冻结 | 检查 runtime models / docs | 有稳定 query command 入口 | command 口径清楚 | command 仍漂移 | 当前 change |
| A2 | Success 2: query event contract 冻结 | 检查 runtime events / docs | 有稳定 query event 入口 | event 口径清楚 | event 仍漂移 | 当前 change |
| A3 | Success 3: adapter bootstrap 可复用 | 检查 adapter/query bootstrap | 后续 `InstrumentProvider` 可复用 | bootstrap 不再临时化 | 仍需重写 | 当前 change |
| A4 | Failure 1: 不越界实现完整 provider | 对照 scope | 范围保持在 query contract | 未提前做完 provider | 范围失控 | 当前 change |
| A5 | Failure 2: 不重定义 Topic 1 smoke | 对照 baseline | Topic 1 baseline 被复用 | 无新 live baseline | 出现 competing baseline | 当前 change |
| A6 | Boundary 1: 可交接给 C2 | 对照 topic queue | Topic 2 下一个 change 可直接接力 | 交接边界清楚 | topic queue 模糊 | 当前 change |
