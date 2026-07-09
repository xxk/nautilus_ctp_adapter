# Nautilus Engine Harness 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-06-08
**范围**：simulation Nautilus engine harness
**change-id**：20260608__openctp-tts-simulation-provider__nautilus-engine-harness
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/openctp-tts-simulation-provider-completeness.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 23:58"
concluded_by: "Codex"
exit_conditions: { E1_success_scenarios: passed, E2_failure_scenarios: passed, E3_verification_cmds: passed, E4_evidence_collected: passed, E5_real_acceptance_only: passed, E6_minimum_scenarios: passed }
scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: true }
  A7: { exec: true, result: passed, blocking: true }
  A8: { exec: true, result: passed, blocking: true }
  A9: { exec: true, result: passed, blocking: true }
  A10: { exec: true, result: passed, blocking: true }
  A11: { exec: true, result: passed, blocking: false }
  A12: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | passed |
| AI 建议宣告通过 | 是 | |

## 一、验收目标 / Goals

证明 provider completeness 不是 script-only smoke，而是 Nautilus-facing command/report path 可用。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Engine harness imports provider | command/test | provider stack built | no script shortcut only | import failure | `engine_harness_provider_reports.json` |
| A2 | Engine submit command | simulation command | order report emitted | Nautilus-facing report | direct native-only smoke | `engine_harness_provider_reports.json` |
| A3 | Engine cancel command | simulation command | cancel report or typed reject | report emitted | direct script-only | `engine_harness_provider_reports.json` |
| A4 | Account report projection | command/test | account state emitted | redacted account | missing report | `engine_harness_provider_reports.json` |
| A5 | Position report projection | command/test | position report emitted | side/qty typed | missing report | `engine_harness_provider_reports.json` |
| A6 | Engine rejects formal-trading profile in P004 scope | negative test/config check | startup fails fast | simulation-only boundary enforced | formal profile accepted | canonical P004 profile in evidence |
| A7 | Engine dry-run path emits same provider contract | harness dry-run | command/report contract emitted without native send | same ids and guard verdict | dry-run bypasses provider | `paper_send_armed=false` |
| A8 | Engine handles rejected order report | simulation rejected order | typed reject report emitted | reason/status mapped | rejected order lost | `REJECTED` report |
| A9 | Engine handles fill report idempotently | filled order or callback test | one fill report emitted | duplicate fill ignored/typed | duplicate fill report | `duplicate_fill_ignored=true` |
| A10 | Engine evidence schema and redaction | evidence review | proposal/change/scenario/run/profile present; secrets absent | evidence can close | evidence leak/missing id | `evidence_nautilus_engine_harness_20260608.md` |
| A11 | P002 regression | `pytest tests/test_nautilus_integration.py -q` | pass | no provider regression | regression | pytest |
| A12 | P004 closeout projection | proposal docs gate | P004 acceptance rows updated | engine harness rows closed or typed blocked | stale proposal state | proposal docs gate |

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| engine harness evidence | `output/reports/p004-openctp-tts-simulation-provider-completeness/nautilus-engine-harness/engine_harness_provider_reports.json` | passed |
| focused pytest | `python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider` | passed |
| proposal docs gate | `python scripts/check_proposal_docs.py --root . --proposal-id p004-openctp-tts-simulation-provider-completeness` | passed in final verification |
