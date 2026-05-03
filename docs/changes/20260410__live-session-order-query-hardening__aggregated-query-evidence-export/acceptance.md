# Aggregated Query Evidence Export 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-10
**范围**：offhours 聚合查询入口与 evidence export
**change-id**：20260410__live-session-order-query-hardening__aggregated-query-evidence-export
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-04-10 00:00"
concluded_by: ""

exit_conditions:
  E1_success_scenarios: pending
  E2_failure_scenarios: pending
  E3_verification_cmds: pending
  E4_evidence_collected: pending
  E5_real_acceptance_only: pending
  E6_minimum_scenarios: pending

scenarios:
  A1: { exec: false, result: null, blocking: true }
  A2: { exec: false, result: null, blocking: true }
  A3: { exec: false, result: null, blocking: true }
  A4: { exec: false, result: null, blocking: true }
  A5: { exec: false, result: null, blocking: true }
  A6: { exec: false, result: null, blocking: false }
```
<!-- AI-STATUS-END -->

## 一、验收目标 / Goals

1. 验证单次 offhours 入口可以覆盖聚合查询结果。
2. 验证 evidence export 路径与文件内容稳定。
3. 验证失败语义不会被聚合入口吞掉。

## 二、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 聚合返回 `position/account/reconciliation` | 运行聚合入口 | 三层结果同次返回 | payload 含 reconciliation | 缺字段或不可判定 | `./evidence_a1_aggregated_query.md` |
| A2 | Success 2: 聚合返回 `instrument/order_truth` | 运行带可选参数的聚合入口 | instrument 与 order_truth 被并入 | payload 含两个可选块 | 可选块缺失 | `./evidence_a2_optional_blocks.md` |
| A3 | Success 3: evidence export 成功落盘 | 运行带 export 参数的聚合入口 | evidence 写入目标目录 | 文件存在且 JSON 可读 | 落盘失败或编码异常 | `./evidence_a3_export_path.md` |
| A4 | Failure 1: export 路径异常时语义清晰 | 构造无效导出路径 | 输出明确 exception/failure reason | 错误阶段可判定 | 静默失败 | `./evidence_a4_export_failure.md` |
| A5 | Failure 2: 聚合中某一子块 manual review 时整体失败语义明确 | 构造 order_truth/reconciliation failure | failure_reason 明确 | 子块 codes 仍保留 | 模糊失败 | `./evidence_a5_subblock_failure.md` |
| A6 | Boundary 1: 空仓/无 callback 仍可作为成功 evidence-only 结果 | 边界场景运行 | success 或 evidence-only 可区分 | boundary 不被误判 | 边界被视为异常 | `./evidence_a6_boundary.md` |

## 三、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：2026-04-10
- **执行人**：—
- **建议**：暂不建议宣告通过
- **说明**：当前仅完成规划，待实现与真实 evidence。