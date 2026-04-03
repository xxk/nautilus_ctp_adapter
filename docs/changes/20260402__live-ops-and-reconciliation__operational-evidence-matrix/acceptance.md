# Operational Evidence Matrix 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：operational evidence matrix、Topic 5 收口、mainline 收口
**change-id**：20260402__live-ops-and-reconciliation__operational-evidence-matrix
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 19:20"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: pass
  E2_failure_scenarios: pass
  E3_verification_cmds: pass
  E4_evidence_collected: pass
  E5_real_acceptance_only: pass
  E6_minimum_scenarios: waived

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

1. 形成 Topic 5 的最终运维证据矩阵。
2. 支持 Topic 5 与 mainline 正式收口。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: matrix 文档存在 | 读取 matrix 文档 | 文档可读 | startup/recovery/audit/reconciliation 汇总完成 | 缺 matrix | [evidence_20260402_operational_evidence_matrix.md](./evidence_20260402_operational_evidence_matrix.md) |
| A2 | Success 2: Topic 5 已 completed | 读取 Topic 5 README | 状态为 `已完成` | child queue 全部完成 | 仍 in_progress | [evidence_20260402_operational_evidence_matrix.md](./evidence_20260402_operational_evidence_matrix.md) |
| A3 | Success 3: mainline 已 completed | 读取 mainline README | 状态为 `已完成` | 总 roadmap 收口 | 仍 in_progress | [evidence_20260402_operational_evidence_matrix.md](./evidence_20260402_operational_evidence_matrix.md) |
| A4 | Failure 1: docs gate 漂移 | `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | topic/docs 漂移 | [evidence_20260402_operational_evidence_matrix.md](./evidence_20260402_operational_evidence_matrix.md) |
| A5 | Failure 2: 文档收口破坏回归 | `python -m pytest` | 回归通过 | `53 passed` | 文档收口破坏测试 | [evidence_20260402_operational_evidence_matrix.md](./evidence_20260402_operational_evidence_matrix.md) |
| A6 | Boundary 1: 结论保持克制 | 检查 matrix 结论 | 只宣告初版运维矩阵完成 | 未过度宣告完整自动对账 | 结论过度 | [evidence_20260402_operational_evidence_matrix.md](./evidence_20260402_operational_evidence_matrix.md) |
