# Startup Truth Evidence Matrix 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：startup truth evidence matrix
**change-id**：20260403__startup-truth-and-session-rebuild__startup-truth-evidence-matrix
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/startup-truth-and-session-rebuild/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 15:35"
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

1. 把 startup truth 与 session rebuild 结果收口成稳定 evidence matrix。
2. 保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live evidence matrix smoke 成功 | 运行 `ctp_startup_truth_evidence_matrix_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260402_startup_truth_evidence_matrix.md](./evidence_20260402_startup_truth_evidence_matrix.md) |
| A2 | Success 2: evidence version 稳定 | 检查 smoke JSON | `evidence_version=startup-truth-evidence-v1` | evidence 结构固定 | 无 version 或结构漂移 | [evidence_20260402_startup_truth_evidence_matrix.md](./evidence_20260402_startup_truth_evidence_matrix.md) |
| A3 | Success 3: rebuild codes 可直接消费 | 检查 smoke JSON | `rebuild_required_codes` 存在 | rebuild 口径可直接消费 | 无 code buckets | [evidence_20260402_startup_truth_evidence_matrix.md](./evidence_20260402_startup_truth_evidence_matrix.md) |
| A4 | Success 4: session truth 差异稳定输出 | 检查 smoke JSON | `session_rotated=true` 且输出 shared/isolated session 字段 | session rebuild 真相已结构化 | 无 session 差异输出 | [evidence_20260402_startup_truth_evidence_matrix.md](./evidence_20260402_startup_truth_evidence_matrix.md) |
| A5 | Boundary 1: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260402_startup_truth_evidence_matrix.md](./evidence_20260402_startup_truth_evidence_matrix.md) |
| A6 | Boundary 2: 只读边界保持 | 检查脚本与结论 | 无真实交易动作 | 仅执行 startup/rebuild 级只读 smoke | 出现发单/撤单行为 | [evidence_20260402_startup_truth_evidence_matrix.md](./evidence_20260402_startup_truth_evidence_matrix.md) |
