# Risk Preflight Expansion 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-06-08
**范围**：simulation risk preflight expansion
**change-id**：20260608__openctp-tts-simulation-provider__risk-preflight-expansion
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/openctp-tts-simulation-provider-completeness.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 23:40"
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

证明 simulation order native send 前的风险条件完整可判定。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Account/position facts loaded | readonly snapshot | risk facts available | redacted metrics | missing but pass | `evidence_risk_preflight_expansion_20260608.md` |
| A2 | Funds/margin guard | negative test | blocked | typed issue | native send | `blocked_missing_account_metrics.json` |
| A3 | Net position guard | negative test | blocked | typed issue | native send | `blocked_guardrails_combo.json` |
| A4 | Frequency cap guard | negative test | blocked | typed issue | native send | `blocked_guardrails_combo.json` |
| A5 | Kill switch guard | negative test | blocked | `paper-safety` | native send | `blocked_guardrails_combo.json` |
| A6 | Duplicate client order id guard | negative test | blocked/correlated | deterministic outcome | ambiguous lifecycle | `blocked_guardrails_combo.json` |
| A7 | Instrument allowlist guard | negative test | blocked | typed instrument_not_allowed | native send | `blocked_guardrails_combo.json` |
| A8 | Per-order max quantity guard | negative test | blocked | typed quantity issue | native send | `blocked_guardrails_combo.json` |
| A9 | Daily/session send budget guard | repeated command test | blocked after budget | rate/budget verdict recorded | uncontrolled repeated send | `blocked_guardrails_combo.json` |
| A10 | Risk preflight dry-run report | dry-run command | all guard inputs and verdict emitted | no native send; same contract as armed path | dry-run lacks risk facts | `risk_dry_run_c2609.json` |
| A11 | External account metric unavailable | readonly query unavailable | typed blocker or conservative block | no fake pass | missing metric treated as zero-risk | `blocked_missing_account_metrics.json` |
| A12 | Guardrail regression | focused tests | pass | no regression | P003 guard weakened | pytest |

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| risk dry-run report | `output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/risk_dry_run_c2609.json` | passed |
| guardrail combo block | `output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/blocked_guardrails_combo.json` | passed |
| missing account metrics block | `output/reports/p004-openctp-tts-simulation-provider-completeness/risk-preflight-expansion/blocked_missing_account_metrics.json` | passed |
| focused pytest | `python -m pytest tests/test_guarded_paper_order_loop.py -q --basetemp output/pytest-tmp -p no:cacheprovider` | `29 passed` |
