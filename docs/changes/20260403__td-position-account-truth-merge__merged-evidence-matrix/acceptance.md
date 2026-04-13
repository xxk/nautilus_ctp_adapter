# Merged Evidence Matrix 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：merged evidence matrix
**change-id**：20260403__td-position-account-truth-merge__merged-evidence-matrix
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/td-position-account-truth-merge.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 16:42"
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

1. 收口 merged truth 的正式 evidence matrix。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live merged evidence smoke 成功 | 运行 `ctp_td_merged_evidence_matrix_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260402_merged_evidence_matrix.md](./evidence_20260402_merged_evidence_matrix.md) |
| A2 | Success 2: evidence version 稳定 | 检查 smoke JSON | `evidence_version=td-merged-evidence-v1` | evidence 结构固定 | 无 version 或结构漂移 | [evidence_20260402_merged_evidence_matrix.md](./evidence_20260402_merged_evidence_matrix.md) |
| A3 | Success 3: code bucket 稳定 | 检查 smoke JSON | 输出 `manual_review_codes/boundary_codes/evidence_only_codes` | evidence 可直接消费 | 无 code bucket | [evidence_20260402_merged_evidence_matrix.md](./evidence_20260402_merged_evidence_matrix.md) |
| A4 | Success 4: merged truth 核心计数稳定 | 检查 smoke JSON | 输出 position/callback/account 核心字段 | evidence 能回指 merged truth | 只有单侧 evidence 没有 merged 全貌 | [evidence_20260402_merged_evidence_matrix.md](./evidence_20260402_merged_evidence_matrix.md) |
| A5 | Boundary 1: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260402_merged_evidence_matrix.md](./evidence_20260402_merged_evidence_matrix.md) |
| A6 | Boundary 2: 只读边界保持 | 检查脚本与结论 | 无真实交易动作 | 仅执行 TD callback observation 与 query | 出现真实交易动作 | [evidence_20260402_merged_evidence_matrix.md](./evidence_20260402_merged_evidence_matrix.md) |
