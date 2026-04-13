# Instrument Query Runtime Contract 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-02
**范围**：instrument query runtime contract
**change-id**：20260402__nautilus-instrument-provider__instrument-query-runtime-contract
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-instrument-provider.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 10:44"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: pass
  E2_failure_scenarios: pass
  E3_verification_cmds: pass
  E4_evidence_collected: pass
  E5_real_acceptance_only: pass
  E6_minimum_scenarios: pass

scenarios:
  A1: { exec: true, result: pass, blocking: true }
  A2: { exec: true, result: pass, blocking: true }
  A3: { exec: true, result: pass, blocking: true }
  A4: { exec: true, result: pass, blocking: true }
  A5: { exec: true, result: pass, blocking: true }
  A6: { exec: true, result: pass, blocking: false }
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
| A1 | Success 1: query command contract 冻结 | 检查 runtime models / docs | 有稳定 query command 入口 | `QUERY_INSTRUMENTS` 已冻结并接入 shared bridge | command 仍漂移 | `./evidence_20260402_instrument_query_runtime_contract.md` |
| A2 | Success 2: query event contract 冻结 | 检查 runtime events / docs | 有稳定 query event 入口 | `INSTRUMENT` 与 `INSTRUMENT_END` 已冻结 | event 仍漂移 | `./evidence_20260402_instrument_query_runtime_contract.md` |
| A3 | Success 3: adapter bootstrap 可复用 | 检查 adapter/query bootstrap | 后续 `InstrumentProvider` 可复用 | `bootstrap_instrument_query_mainline()` 已存在且走 shared bridge | 仍需重写 | `./evidence_20260402_instrument_query_runtime_contract.md` |
| A4 | Failure 1: 不越界实现完整 provider | 对照 scope | 范围保持在 query contract | 未提前实现真实 provider/normalization | 范围失控 | `./evidence_20260402_instrument_query_runtime_contract.md` |
| A5 | Failure 2: 不重定义 Topic 1 smoke | 对照 baseline | Topic 1 baseline 被复用 | 未新增 competing live baseline | 出现 competing baseline | `./evidence_20260402_instrument_query_runtime_contract.md` |
| A6 | Boundary 1: 可交接给 C2 | 对照 topic queue | Topic 2 下一个 change 可直接接力 | query contract 已固定，topic queue 可切到 C2 | topic queue 模糊 | `./evidence_20260402_instrument_query_runtime_contract.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 当前 change 输出证据 | `./evidence_20260402_instrument_query_runtime_contract.md` | query contract、adapter bootstrap、验证结果 |
| 2 | 上游正式 baseline | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md` | 证明本 change 复用 Topic 1 baseline，而不是重造 live baseline |

## 七、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：推进 `C2`，开始冻结 exchange / symbol / product kind normalization
- **说明**：本 change 只冻结 query contract，不代表真实 instrument query 或 InstrumentProvider 已完成。
