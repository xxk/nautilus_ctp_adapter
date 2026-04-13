# Session Rebuild Policy 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-03
**范围**：session rebuild policy
**change-id**：20260403__startup-truth-and-session-rebuild__session-rebuild-policy
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/startup-truth-and-session-rebuild.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-03 00:57"
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

1. 冻结 session rebuild policy baseline。
2. 明确共享 flow 不可直接复用为 rebuild-safe truth。
3. 明确 test/mock/fake 不能作为验收证据。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live rebuild policy smoke 成功 | 运行 `ctp_session_rebuild_policy_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260403_session_rebuild_policy.md](./evidence_20260403_session_rebuild_policy.md) |
| A2 | Success 2: shared flow 不可复用 | 检查 smoke JSON | `shared_flow_reuse_allowed=false` | 共享 flow 边界已冻结 | 共享 flow 仍被允许盲复用 | [evidence_20260403_session_rebuild_policy.md](./evidence_20260403_session_rebuild_policy.md) |
| A3 | Success 3: rebuild 判定可输出 | 检查 smoke JSON | `disposition=rebuild_required` | rebuild 口径已结构化 | 无总判定字段 | [evidence_20260403_session_rebuild_policy.md](./evidence_20260403_session_rebuild_policy.md) |
| A4 | Success 4: 隔离 flow 真相可输出 | 检查 smoke JSON | `isolated_truth.flow_mode=explicit_override` | 隔离 flow 真相已结构化 | 无 isolated truth | [evidence_20260403_session_rebuild_policy.md](./evidence_20260403_session_rebuild_policy.md) |
| A5 | Boundary 1: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260403_session_rebuild_policy.md](./evidence_20260403_session_rebuild_policy.md) |
| A6 | Boundary 2: 只读边界保持 | 检查脚本与结论 | 无真实交易动作 | 仅执行 startup/rebuild 级只读 smoke | 出现发单/撤单行为 | [evidence_20260403_session_rebuild_policy.md](./evidence_20260403_session_rebuild_policy.md) |
