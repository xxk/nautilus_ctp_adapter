# TD Session Truth Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-03
**范围**：td startup truth baseline
**change-id**：20260403__startup-truth-and-session-rebuild__td-session-truth-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/startup-truth-and-session-rebuild.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-03 00:48"
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

1. 冻结 TD startup truth 的正式 live baseline。
2. 让 flow path、session identity、disconnect 证据可结构化输出。
3. 明确 test/mock/fake 不能作为验收证据。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live startup truth smoke 成功 | 运行 `ctp_startup_truth_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260403_td_startup_truth.md](./evidence_20260403_td_startup_truth.md) |
| A2 | Success 2: session truth 字段可读 | 检查 smoke JSON | `front_id/session_id/max_order_ref` 可读 | session truth 已结构化 | 核心 session 字段缺失 | [evidence_20260403_td_startup_truth.md](./evidence_20260403_td_startup_truth.md) |
| A3 | Success 3: flow path 口径冻结 | 检查 smoke JSON | `flow_path/flow_mode` 可读 | flow truth 已结构化 | flow 归属仍只停留在隐含约定 | [evidence_20260403_td_startup_truth.md](./evidence_20260403_td_startup_truth.md) |
| A4 | Success 4: startup event truth 存在 | 检查 smoke JSON | `bridge_event_kinds` 含 `login_succeeded` 和 `settlement_confirmed` | startup truth 有事件支撑 | 只有 readiness 布尔值，无事件证据 | [evidence_20260403_td_startup_truth.md](./evidence_20260403_td_startup_truth.md) |
| A5 | Boundary 1: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260403_td_startup_truth.md](./evidence_20260403_td_startup_truth.md) |
| A6 | Boundary 2: 只读边界保持 | 检查脚本与结论 | 无真实交易动作 | 仅执行 TD bootstrap 级只读 smoke | 出现发单/撤单行为 | [evidence_20260403_td_startup_truth.md](./evidence_20260403_td_startup_truth.md) |
