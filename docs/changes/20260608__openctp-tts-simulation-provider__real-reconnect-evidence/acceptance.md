# Real Reconnect Evidence 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-06-08
**范围**：simulation real reconnect evidence
**change-id**：20260608__openctp-tts-simulation-provider__real-reconnect-evidence
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/openctp-tts-simulation-provider-completeness.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 23:59"
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
| 验收结论 | ✅ 通过 | controlled process-scoped front proxy evidence generated |
| AI 建议宣告通过 | 是 | MD/TD reconnect behavior is verified without public front disruption |

## 一、验收目标 / Goals

证明真实 simulation front reconnect 后 provider 状态、安全开关和 idempotency 仍正确。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | MD disconnect detected | controlled front proxy reconnect command | reason recorded | typed event | silent loss | `controlled_reconnect_pass.json` |
| A2 | MD resubscribe once | controlled front proxy reconnect command | symbols restored | count once | duplicate/missing | `controlled_reconnect_pass.json` |
| A3 | TD relogin ready | controlled front proxy reconnect command | readiness restored | session state typed | login ambiguity | `controlled_reconnect_pass.json` |
| A4 | Send remains disarmed | controlled front proxy reconnect command | `paper_send_armed=false` | guard preserved | armed true | `controlled_reconnect_pass.json` |
| A5 | Historical residue isolated | test/simulation | no current mutation | residue typed | current fill changed | `reconnect_rehearsal_pass.json` |
| A6 | In-flight order during reconnect | simulation or typed blocker | lifecycle preserved or conservative blocker | no duplicate fill/cancel | state lost | `controlled_reconnect_pass.json`; `inflight_order_conservative_blocker.json` |
| A7 | Query recovery after reconnect | account/position/order query after relogin | snapshot complete or typed blocker | query disposition recorded | query skipped | `controlled_reconnect_pass.json` |
| A8 | Multiple symbol resubscribe | reconnect command with 2+ symbols | each symbol restored once | per-symbol count recorded | duplicate/missing subscription | `reconnect_rehearsal_pass.json` |
| A9 | Reconnect attempt budget | forced retry path | retry count capped and typed | no infinite loop | unbounded retry | pytest |
| A10 | Evidence redaction and timeline | evidence review | timeline includes disconnect/reconnect/relogin/resubscribe; secrets absent | row can close | raw account/front leak | `evidence_real_reconnect_20260608.md` |
| A11 | Resource blocker typed | unavailable front path | typed blocker | next action present | fake pass | `forced_disconnect_resource_blocker.json` |
| A12 | Recovery/idempotency regression | focused tests | pass | no regression | baseline broken | pytest |

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| reconnect rehearsal help | `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/reconnect_rehearsal_help.txt` | command frozen |
| repo-only rehearsal | `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/reconnect_rehearsal_pass.json` | passed; not real disconnect |
| in-flight blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/inflight_order_conservative_blocker.json` | typed blocker |
| real disconnect blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/forced_disconnect_resource_blocker.json` | paper-resource blocker |
| controlled reconnect pass | `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/controlled_reconnect_pass.json` | passed; process-scoped MD/TD drop counts recorded |
| OpenCTP status page | `output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/openctp_simenv_status_20260608.json` | HTTP 200; `openctp-7x24` present |
| focused pytest | `python -m pytest tests/test_controlled_front_proxy.py tests/test_paper_recovery_idempotency.py -q --basetemp output/pytest-tmp -p no:cacheprovider` | `12 passed` |
