# Aggregated Query Evidence Export 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ Repo-only 通过；OpenCTP paper baseline 可复用
**日期**：2026-04-10
**范围**：offhours 聚合查询入口与 evidence export
**change-id**：20260410__live-session-order-query-hardening__aggregated-query-evidence-export
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed_repo_only
allow_declare_pass: true
last_updated: "2026-06-08 16:35"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 一、验收目标 / Goals

1. 验证单次 offhours 入口可以覆盖聚合查询结果。
2. 验证 evidence export 路径与文件内容稳定。
3. 验证失败语义不会被聚合入口吞掉。

## 二、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 聚合返回 `position/account/reconciliation` | `--help`/source contract + focused pytest | 三层结果同次返回 | `--include-reconciliation` 与 payload path 存在 | 缺字段或不可判定 | `./evidence_repo_only_aggregated_query_export.md` |
| A2 | Success 2: 聚合返回 `instrument/order_truth` | `--help`/source contract + focused pytest | instrument 与 order_truth 被并入 | `--instrument-symbol`、`--include-order-truth`、`--include-order-trade-snapshot`、`--include-merged-policy` 存在 | 可选块缺失 | `./evidence_repo_only_aggregated_query_export.md` |
| A3 | Success 3: evidence export 成功落盘 | focused pytest | evidence 写入目标目录 | session-labeled export tests passed | 落盘失败或编码异常 | `./evidence_repo_only_aggregated_query_export.md` |
| A4 | Failure 1: export 路径异常时语义清晰 | focused pytest | 输出明确 exception/failure reason | conflict/invalid export tests passed | 静默失败 | `./evidence_repo_only_aggregated_query_export.md` |
| A5 | Failure 2: 聚合中某一子块 manual review 时整体失败语义明确 | source contract | failure_reason 明确 | `*_manual_review_required` failure reasons retained | 模糊失败 | `./evidence_repo_only_aggregated_query_export.md` |
| A6 | Boundary 1: 空仓/无 callback 仍可作为成功 evidence-only 结果 | source contract + README | success 或 evidence-only 可区分 | `evidence_only` / boundary codes retained, no live-send semantics | 边界被视为异常 | `./evidence_repo_only_aggregated_query_export.md` |

## 三、最终结论 / Final Verdict

- **结论**：✅ Repo-only 通过
- **日期**：2026-06-08
- **执行人**：Codex
- **建议**：可以宣告 C5 repo-only contract 通过；OpenCTP paper evidence 已由 C8 baseline 复用，formal-trading live evidence 仍按 real-account change 处理
- **说明**：聚合入口与 evidence export 参数面已由 successor implementation 落地，且 focused regression 通过。
