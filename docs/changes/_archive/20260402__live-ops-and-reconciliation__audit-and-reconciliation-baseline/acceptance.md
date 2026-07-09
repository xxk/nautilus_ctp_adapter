# Audit And Reconciliation Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：audit baseline、reconciliation baseline、证据链结构
**change-id**：20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-ops-and-reconciliation.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 19:12"
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

1. 冻结 Topic 5 的最小 audit / reconciliation baseline。
2. 明确自动证据链与人工复核边界。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: `C3` baseline 文档存在 | 读取 baseline 文档 | 五类证据链成文 | 文档存在且可读 | 缺 baseline | [evidence_20260402_audit_and_reconciliation_baseline.md](./evidence_20260402_audit_and_reconciliation_baseline.md) |
| A2 | Success 2: 自动证据链范围明确 | 检查 baseline 文档 | MD/order/trade 自动化边界明确 | 不再混淆自动与人工 | 范围模糊 | [evidence_20260402_audit_and_reconciliation_baseline.md](./evidence_20260402_audit_and_reconciliation_baseline.md) |
| A3 | Success 3: 持仓/资金被正确标为人工复核 | 检查 baseline 文档 | position/account 仅列能力预留 | 未误宣告完成 | 把 native export 写成已完成对账 | [evidence_20260402_audit_and_reconciliation_baseline.md](./evidence_20260402_audit_and_reconciliation_baseline.md) |
| A4 | Failure 1: topic 治理门禁失败 | `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | topic docs 漂移 | [evidence_20260402_audit_and_reconciliation_baseline.md](./evidence_20260402_audit_and_reconciliation_baseline.md) |
| A5 | Failure 2: 文档修改破坏回归 | `python -m pytest` | 测试继续通过 | 回归通过 | 文档改动破坏测试/入口 | [evidence_20260402_audit_and_reconciliation_baseline.md](./evidence_20260402_audit_and_reconciliation_baseline.md) |
| A6 | Boundary 1: 当前只宣告 baseline | 检查最终结论 | 仅通过 baseline，不宣告完整自动对账 | 结论克制 | 过度宣告 | [evidence_20260402_audit_and_reconciliation_baseline.md](./evidence_20260402_audit_and_reconciliation_baseline.md) |

## 十一、最终结论 / Final Verdict

- **结论**：✅ 已通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：Topic 5 的审计/对账口径已冻结为最小 baseline，并明确了自动证据与人工复核的边界。
