# Nautilus Provider Readiness Phase 4 Query Report Generation 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ Repo-only 通过
**日期**：2026-06-08
**范围**：P002 Phase 4 query report generation
**change-id**：20260608__nautilus-provider-readiness__query-report-generation
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/proposals/p002-nautilus-provider-production-readiness/

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 17:30"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: false }
  A6: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success: position row maps to `PositionStatusReport` | ✅ | ✅ | 是 | focused pytest |
| A2 | Success: account row maps to `AccountState` | ✅ | ✅ | 是 | focused pytest |
| A3 | Failure: provider metadata missing avoids false instrument report | ✅ | ✅ | 是 | helper returns `None` |
| A4 | Regression: query truth remains runtime/query owned | ✅ | ✅ | 是 | wrapper translates normalized rows only |
| A5 | Boundary: OpenCTP paper query evidence remains paper simulation | ✅ | ✅ | 否 | C8 baseline |
| A6 | Boundary: formal-trading evidence remains final-only | ✅ | ✅ | 否 | P002 account profile |

## 最终结论 / Final Verdict

- **结论**：✅ Repo-only 通过
- **说明**：本 change 关闭 P002 Phase 4 repo-only query report/state generation。
