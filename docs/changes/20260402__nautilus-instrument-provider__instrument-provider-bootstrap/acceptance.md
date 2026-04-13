# Instrument Provider Bootstrap 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-02
**范围**：instrument provider bootstrap
**change-id**：20260402__nautilus-instrument-provider__instrument-provider-bootstrap
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-instrument-provider.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 11:12"
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

1. 证明 `InstrumentProvider` 已具备最小可用 bootstrap。
2. 证明 Topic 2 的 `C4` 可以在此基础上定义正式 smoke baseline。

## 二、启动前提 / Entry Preconditions

1. `C2` 必须已完成。
2. 本 change 不负责 instrument smoke baseline。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: provider bootstrap 成立 | 检查 provider load path | 有明确 load 入口 | provider 已具备 `bootstrap/load_result/load_all` 主线 | 仍是纯占位 | `./evidence_20260402_instrument_provider_bootstrap.md` |
| A2 | Success 2: provider 输出模型冻结 | 检查 provider output | 输出 shape 稳定 | `CtpInstrumentProviderLoadResult` 已冻结 | 输出仍漂移 | `./evidence_20260402_instrument_provider_bootstrap.md` |
| A3 | Success 3: Topic 3 可复用 | 对照 topic 目标 | marketdata topic 可复用 provider | provider 输出已可作为 Topic 3 输入 | 仍需重做 | `./evidence_20260402_instrument_provider_bootstrap.md` |
| A4 | Failure 1: 不越界做 smoke baseline | 对照 scope | 不提前完成 C4 | 本 change 未宣称正式 smoke baseline 已完成 | 范围失控 | `./evidence_20260402_instrument_provider_bootstrap.md` |
| A5 | Failure 2: 不重写 normalization | 对照 C2 | 继承 normalization helper | provider 直接复用 `C2` helper | 再次分叉 | `./evidence_20260402_instrument_provider_bootstrap.md` |
| A6 | Boundary 1: 可交接给 C4 | 对照 topic queue | C4 可直接接力 | topic queue 可切到 C4 | topic queue 模糊 | `./evidence_20260402_instrument_provider_bootstrap.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 当前 change 输出证据 | `./evidence_20260402_instrument_provider_bootstrap.md` | provider bootstrap 与输出模型 |
| 2 | 上游 normalization | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-instrument-provider__exchange-and-symbol-normalization/evidence_20260402_exchange_and_symbol_normalization.md` | 证明本 change 继承 `C2` |

## 七、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：推进 `C4`，定义并尽量打通 instrument smoke baseline
- **说明**：本 change 完成的是 provider bootstrap，不代表真实 instrument query 已 fully live。
