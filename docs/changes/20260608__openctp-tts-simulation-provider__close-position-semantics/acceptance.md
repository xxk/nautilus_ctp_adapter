# Close Position Semantics 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-06-08
**范围**：simulation close position semantics
**change-id**：20260608__openctp-tts-simulation-provider__close-position-semantics
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/openctp-tts-simulation-provider-completeness.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 21:20"
concluded_by: "codex"
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
  A10: { exec: true, result: passed_with_caveat, blocking: true }
  A11: { exec: true, result: passed, blocking: false }
  A12: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | close semantics contract + TTS 7x24 evidence passed |
| AI 建议宣告通过 | 是 | armed close stdout caveat recorded |

## 一、验收目标 / Goals

证明 close position command 不会错误处理今昨仓和可平数量。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Select close candidate | read-only snapshot | position candidate redacted | td/yd split present | account leak | 本 change evidence |
| A2 | CLOSE mapping | dry-run/simulation command | CTP position effect deterministic | native payload typed | generic silent fallback | 本 change evidence |
| A3 | CLOSE TODAY/YESTERDAY mapping | focused tests | exchange-specific mapping | SHFE/INE explicit | split collapsed | test output |
| A4 | No position blocks send | negative test | no native order | typed blocker | native send occurs | test output |
| A5 | Insufficient position blocks send | negative test | no native order | typed blocker | over-close allowed | test output |
| A6 | Opposite-side close direction | dry-run command from position snapshot | close side is opposite of held position | long position maps to SELL close; short maps to BUY close | same-side close opens more exposure | test/evidence |
| A7 | SHFE/INE close today priority | focused test with td/yd split | explicit close today/yesterday selected | no generic `CLOSE` where split required | today/yesterday ambiguity | test output |
| A8 | Non-SHFE generic close behavior | focused test with DCE/CZCE style position | exchange-appropriate close effect selected | generic close allowed only where valid | over-specific close rejected by front | test/evidence |
| A9 | Close preflight uses current snapshot | stale snapshot negative test | blocked before native send | run id/fingerprint freshness checked | stale position used | test output |
| A10 | Post-close reconciliation | simulation close or typed blocker | pre/post position delta explained | closed qty matches reported trade or blocker typed | unexplained position delta | 本 change evidence |
| A11 | Residual position carry-forward | no closable position or contract unavailable | typed carry-forward with next action | no fake pass | scenario silently skipped | 本 change evidence |
| A12 | P004 docs update | docs gate | acceptance row updated | gate pass | stale state | command output |

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| Server status preflight | `http://www.openctp.cn/simenv.html` | `openctp-7x24` TD/MD running; generated at `2026-06-08 21:02:00` |
| Close semantics evidence | `docs/changes/20260608__openctp-tts-simulation-provider__close-position-semantics/evidence_close_position_semantics_20260608.md` | A1-A11 evidence recorded |
| c2609 pre snapshot | `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_c2609.json` | c2609 LONG/SHORT candidates selected without account leak |
| zn2610 pre snapshot | `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_zn2610.json` | SHFE exchange recovered from instrument record |
| c2609 close dry-run | `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_dry_run_c2609_short1_after_fix.json` | SHORT maps to `BUY CLOSE`, DCE generic close allowed |
| zn2610 close dry-run | `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_dry_run_zn2610_long1.json` | LONG maps to `SELL CLOSEYESTERDAY`, no SHFE generic close fallback |
| insufficient close blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_over_blocked_c2609_short3.json` | `insufficient_closable_position`, no native send |
| stale snapshot blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_stale_snapshot_blocked_c2609.json` | `pre_snapshot_run_id_mismatch`, no native send |
| armed close post snapshot | `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_c2609_after_stdout_fix.json` | c2609 SHORT reduced from 3 to 2; stdout exporter caveat fixed |
| focused tests | `python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider -k "ClosePositionSemantics"` | `7 passed, 70 deselected` |
| order loop tests | `python -m pytest tests/test_guarded_paper_order_loop.py -q --basetemp output/pytest-tmp -p no:cacheprovider` | `15 passed` |

## Verdict

Passed. Provider close semantics are now explicit for `CLOSE`, `CLOSETODAY`, and `CLOSEYESTERDAY`; SHFE/INE split handling is not silently collapsed to generic close; stale/no/insufficient position cases block before native send.

Caveat: the armed c2609 close command hit a Windows stdout `UnicodeEncodeError` after execution and before JSON export. The post snapshot confirms c2609 SHORT reduced from `3` to `2`; the exporter bug is fixed and covered by tests. A second armed close was intentionally not sent to avoid duplicate position changes.
