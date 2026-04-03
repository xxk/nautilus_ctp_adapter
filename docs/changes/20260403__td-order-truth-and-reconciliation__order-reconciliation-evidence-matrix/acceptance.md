# Order Reconciliation Evidence Matrix 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：order reconciliation evidence matrix
**change-id**：20260403__td-order-truth-and-reconciliation__order-reconciliation-evidence-matrix
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/td-order-truth-and-reconciliation/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 16:08"
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

1. 收口 order truth/reconciliation 的正式 evidence matrix。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live order truth evidence smoke 成功 | 运行 `ctp_td_order_truth_evidence_matrix_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260402_td_order_truth_evidence_matrix.md](./evidence_20260402_td_order_truth_evidence_matrix.md) |
| A2 | Success 2: evidence version 稳定 | 检查 smoke JSON | `evidence_version=td-order-truth-evidence-v1` | evidence 结构固定 | 无 version 或结构漂移 | [evidence_20260402_td_order_truth_evidence_matrix.md](./evidence_20260402_td_order_truth_evidence_matrix.md) |
| A3 | Success 3: boundary 结果可直接消费 | 检查 smoke JSON | 输出 `historical/delayed/current_session` 计数 | evidence 可直接消费 | 只有原始日志没有结构化结果 | [evidence_20260402_td_order_truth_evidence_matrix.md](./evidence_20260402_td_order_truth_evidence_matrix.md) |
| A4 | Success 4: code bucket 稳定 | 检查 smoke JSON | 输出 `manual_review_codes/boundary_codes/evidence_only_codes` | evidence 有稳定 finding bucket | 无 code bucket | [evidence_20260402_td_order_truth_evidence_matrix.md](./evidence_20260402_td_order_truth_evidence_matrix.md) |
| A5 | Boundary 1: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260402_td_order_truth_evidence_matrix.md](./evidence_20260402_td_order_truth_evidence_matrix.md) |
| A6 | Boundary 2: 只读边界保持 | 检查脚本与结论 | 无真实交易动作 | 仅执行 TD callback observation | 出现真实交易动作 | [evidence_20260402_td_order_truth_evidence_matrix.md](./evidence_20260402_td_order_truth_evidence_matrix.md) |
