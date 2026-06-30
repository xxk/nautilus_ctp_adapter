# Benchmark Gate And Daemon Trigger Policy 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-05-29
**范围**：P001 Phase 4、runtime performance gate、daemon trigger policy
**change-id**：20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-05-29 00:00"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: pass, blocking: true }
  A2: { exec: true, result: pass, blocking: true }
  A3: { exec: true, result: pass, blocking: true }
  A4: { exec: true, result: pass, blocking: true }
  A5: { exec: true, result: pass, blocking: true }
  A6: { exec: true, result: pass, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | Benchmark gate / daemon trigger policy 已收口 |
| AI 建议宣告通过 | 是 | A1-A6 已全部执行 |
| 最后更新 | 2026-05-29 00:00 | |
| AI 执行人 | Codex | |

## 一、验收目标 / Goals

1. 冻结 benchmark gate command。
2. 冻结 threshold 和 artifact boundary。
3. 冻结 daemon trigger policy，防止 daemon 默认化。

## 二、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: Phase 4 child change bundle 存在 | 审阅当前 bundle | 四件套存在 | scope 只覆盖 benchmark / daemon policy | bundle 缺文件 | 当前 bundle |
| A2 | Success 2: benchmark command 可复跑 | `python scripts/check_runtime_performance_gate.py --events 5000 --limit 1000 --min-events-per-sec 1000` | gate exits 0 | `RUNTIME_PERFORMANCE_GATE_OK` | command 缺失或失败 | script output / JSON report |
| A3 | Success 3: threshold and artifact boundary 冻结 | 审阅 `design.md` | threshold/path 清楚 | `events_per_sec >= 1000` and JSON path fixed | 只有“以后 benchmark”口号 | `design.md` |
| A4 | Failure 1: daemon 不得默认化 | 审阅 `design.md` / ADR001 | daemon remains future proposal | trigger policy requires formal benchmark | P001 直接批准 daemon | `design.md` |
| A5 | Failure 2: synthetic gate 不得冒充 live benchmark | 审阅 acceptance/design | gate 被标为 lower-bound regression gate | live benchmark out of scope | synthetic output 被写成 live pass | `design.md` |
| A6 | Boundary 1: generated JSON 不成为 ADR authority | 文档审阅 | ADR 只保留 pointer/rule | evidence 留在 acceptance/report | ADR 复制 benchmark 输出 | ADR001 / current acceptance |

## 三、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | Change bundle | `docs/changes/20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision/` | Phase 4 child change |
| 2 | Benchmark gate script | `scripts/check_runtime_performance_gate.py` | repo-local gate |
| 3 | Benchmark artifact boundary | `output/reports/p001-ADR001-native-first-runtime-rollout/runtime_performance_gate.json` | generated JSON report |
| 4 | Verification | `check_runtime_performance_gate`; proposal docs gate; change docs gate; harness gate | 必跑 gate |

## 四、最终结论 / Final Verdict

- **结论**：✅ passed
- **日期**：2026-05-29
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：A1-A6 已用 executable gate + docs evidence 收口；daemon remains future proposal only。
