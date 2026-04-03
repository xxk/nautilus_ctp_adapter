# Marketdata Runtime Event Contract 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-02
**范围**：marketdata runtime event contract
**change-id**：20260402__nautilus-live-marketdata__marketdata-runtime-event-contract
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 11:27"
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

1. 证明市场数据事件 contract 已冻结。
2. 证明 Topic 3 后续 change 不需要再重定义 tick / login / disconnect 事件语义。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: tick 事件 contract 冻结 | 检查 runtime/data glue | tick 口径稳定 | tick payload 已冻结为 `CtpMdTickEventPayload` | payload 仍漂移 | `./evidence_20260402_marketdata_runtime_event_contract.md` |
| A2 | Success 2: login/disconnect 事件 contract 冻结 | 检查 runtime/data glue | 会话相关事件口径稳定 | login/disconnect payload 已冻结 | 仍模糊 | `./evidence_20260402_marketdata_runtime_event_contract.md` |
| A3 | Success 3: bridge 语义可复用 | 检查 bridge/data contract | 后续 `LiveDataClient` 可复用 | `drain_marketdata_events()` 语义已明确 | 仍需重写 | `./evidence_20260402_marketdata_runtime_event_contract.md` |
| A4 | Failure 1: 不越界实现完整 LiveDataClient | 对照 scope | 范围保持在 contract | 未提前完成 Topic 3 `C2` | 范围失控 | `./evidence_20260402_marketdata_runtime_event_contract.md` |
| A5 | Failure 2: 不重造 Topic 1 baseline | 对照 baseline | 继承已有 MD baseline | 未新造 competing baseline | 新造 baseline | `./evidence_20260402_marketdata_runtime_event_contract.md` |
| A6 | Boundary 1: 可交接给 C2 | 对照 topic queue | C2 可直接接力 | topic queue 可切到 `C2` | topic queue 模糊 | `./evidence_20260402_marketdata_runtime_event_contract.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 当前 change 输出证据 | `./evidence_20260402_marketdata_runtime_event_contract.md` | event contract 与 bridge 语义 |
| 2 | 上游 MD baseline | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md` | 证明本 change 继承 Topic 1 真实行情基础 |

## 七、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：推进 `C2`，建立最小 LiveDataClient 主线
- **说明**：本 change 只冻结 event contract，不代表 Topic 3 已完成。
