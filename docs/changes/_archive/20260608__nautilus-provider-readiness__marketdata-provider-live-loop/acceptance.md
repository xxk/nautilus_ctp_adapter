# Nautilus Provider Readiness Phase 2 Marketdata Provider Live Loop 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ Repo-only 通过；L5 移交 Phase 5
**日期**：2026-06-08
**范围**：P002 Phase 2 marketdata provider/tick path
**change-id**：20260608__nautilus-provider-readiness__marketdata-provider-live-loop
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/proposals/p002-nautilus-provider-production-readiness/

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed_repo_only_l5_deferred
allow_declare_pass: true
last_updated: "2026-06-08 16:10"
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
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: deferred_to_phase_5, blocking: false }
```
<!-- AI-STATUS-END -->

## 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success: known CTP tick resolves via provider metadata | ✅ | ✅ | 是 | `evidence_tick_provider_resolution.md` |
| A2 | Success: hydrated provider instrument is reused for QuoteTick construction | ✅ | ✅ | 是 | `evidence_tick_provider_resolution.md` |
| A3 | Success: restore/resubscribe keeps provider-backed symbol set | ✅ | ✅ | 是 | provider-backed subscription symbol helper test |
| A4 | Failure: unknown tick has explicit diagnostic | ✅ | ✅ | 是 | `ctp_metadata_missing` diagnostic |
| A5 | Failure: provider metadata missing does not fabricate `.CTP` instrument | ✅ | ✅ | 是 | no-fabrication negative test |
| A6 | Boundary: OpenCTP paper L5 evidence does not block repo-only work | ✅ | ✅ | 否 | C8 OpenCTP paper baseline is available; provider-specific L5 evidence is deferred to P002 Phase 5 |

## 验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | known CTP tick resolves via provider metadata | focused pytest | `rb2610` resolves to `rb2610.SHFE` | test passed | hardcoded `.CTP` remains | `./evidence_tick_provider_resolution.md` |
| A2 | hydrated provider instrument reused | focused pytest | QuoteTick uses hydrated instrument price factory | test passed | cache/provider bypassed | `./evidence_tick_provider_resolution.md` |
| A3 | restore/resubscribe provider symbols | focused pytest | active symbols come from provider/subscriptions | test passed | restore loses symbol set | `./evidence_tick_provider_resolution.md` |
| A4 | unknown tick diagnostic | focused pytest | explicit unknown instrument evidence | test passed | silent drop only | `./evidence_tick_provider_resolution.md` |
| A5 | missing metadata no fabrication | focused pytest | no partial `.CTP` instrument | test passed | fabricated instrument | `./evidence_tick_provider_resolution.md` |
| A6 | OpenCTP baseline separated | docs/evidence | L5 provider evidence deferred unless explicitly in Phase 5 scope | typed blocker/pass | fake pass | `../20260607__openctp-tts__test-baseline/` |
