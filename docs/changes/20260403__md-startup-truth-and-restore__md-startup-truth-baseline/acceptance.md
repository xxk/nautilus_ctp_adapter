# MD Startup Truth Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：md startup truth baseline
**change-id**：20260403__md-startup-truth-and-restore__md-startup-truth-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/md-startup-truth-and-restore/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 15:52"
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

1. 收口 MD login、subscribe、first tick 的正式 startup truth baseline。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live MD startup truth smoke 成功 | 运行 `ctp_md_startup_truth_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260402_md_startup_truth.md](./evidence_20260402_md_startup_truth.md) |
| A2 | Success 2: baseline version 稳定 | 检查 smoke JSON | `baseline=md-startup-truth-v1` | baseline 结构固定 | 无 baseline 或结构漂移 | [evidence_20260402_md_startup_truth.md](./evidence_20260402_md_startup_truth.md) |
| A3 | Success 3: subscribe 与 first tick 成功 | 检查 smoke JSON | `subscribe_code=0` 且 `first_tick_symbol=rb2610` | MD startup truth 已成立 | 无首个 tick 或订阅失败 | [evidence_20260402_md_startup_truth.md](./evidence_20260402_md_startup_truth.md) |
| A4 | Success 4: command/event bridge 可留证 | 检查 smoke JSON | 同时输出 `bridge_command_kinds` 与 `bridge_event_kinds` | startup truth 有完整上下文 | 只有结果没有链路上下文 | [evidence_20260402_md_startup_truth.md](./evidence_20260402_md_startup_truth.md) |
| A5 | Boundary 1: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260402_md_startup_truth.md](./evidence_20260402_md_startup_truth.md) |
| A6 | Boundary 2: 只读边界保持 | 检查脚本与结论 | 无真实交易动作 | 仅执行 MD login/subscribe/tick 级 smoke | 出现真实交易动作 | [evidence_20260402_md_startup_truth.md](./evidence_20260402_md_startup_truth.md) |
