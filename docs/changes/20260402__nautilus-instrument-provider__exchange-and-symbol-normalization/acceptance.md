# Exchange And Symbol Normalization 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-02
**范围**：exchange and symbol normalization
**change-id**：20260402__nautilus-instrument-provider__exchange-and-symbol-normalization
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 10:58"
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

1. 证明 exchange / symbol / product kind 的归一化规则已经冻结。
2. 证明 `C3` 不需要再重新定义基础映射口径。

## 二、启动前提 / Entry Preconditions

1. `C1` 必须已完成。
2. 本 change 不负责完整 `InstrumentProvider`。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: exchange normalization 冻结 | 检查 helper / docs | 交易所口径稳定 | alias map 已明确冻结 | 交易所映射仍漂移 | `./evidence_20260402_exchange_and_symbol_normalization.md` |
| A2 | Success 2: symbol normalization 冻结 | 检查 helper / docs | symbol 口径稳定 | 大小写规则已集中冻结 | symbol 仍漂移 | `./evidence_20260402_exchange_and_symbol_normalization.md` |
| A3 | Success 3: product kind normalization 冻结 | 检查 helper / docs | product kind 口径稳定 | `1..7` 的最小映射已明确 | 仍模糊 | `./evidence_20260402_exchange_and_symbol_normalization.md` |
| A4 | Failure 1: 不越界实现完整 provider | 对照 scope | 范围保持在 normalization | 未提前实现完整 provider | 范围失控 | `./evidence_20260402_exchange_and_symbol_normalization.md` |
| A5 | Failure 2: 不重定义 query contract | 对照 C1 | 继承 C1 contract | 未重写 query contract | 重新发明 query 边界 | `./evidence_20260402_exchange_and_symbol_normalization.md` |
| A6 | Boundary 1: 可交接给 C3 | 对照 topic queue | C3 可直接接力 | topic queue 可切到 C3 | topic queue 模糊 | `./evidence_20260402_exchange_and_symbol_normalization.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 当前 change 输出证据 | `./evidence_20260402_exchange_and_symbol_normalization.md` | normalization rule 与验证结果 |
| 2 | 上游 query contract | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-instrument-provider__instrument-query-runtime-contract/evidence_20260402_instrument_query_runtime_contract.md` | 证明本 change 继承 C1 而不是重写 query boundary |

## 七、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：推进 `C3`，开始建立最小 InstrumentProvider bootstrap
- **说明**：本 change 只冻结 normalization rule，不代表真实 InstrumentProvider 已完成。
