# Readonly Order Trade Snapshot Contract 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-10
**范围**：`ORDER / TRADE` 只读 snapshot contract
**change-id**：20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract
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

## 一、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: `ORDER` 只读快照成功 | 运行正式入口 | 返回 orders snapshot | order_count / completion 可读 | 不可判定 | `./evidence_a1_order_snapshot.md` |
| A2 | Success 2: `TRADE` 只读快照成功 | 运行正式入口 | 返回 trades snapshot | trade_count / completion 可读 | 不可判定 | `./evidence_a2_trade_snapshot.md` |
| A3 | Success 3: 历史残留与当前 query 结果能分层 | 带残留场景运行 | callback truth 与 query snapshot 分层 | 两类语义同时保留 | 混成单一结果 | `./evidence_a3_residue_split.md` |
| A4 | Failure 1: query 失败语义清晰 | 构造 query 失败 | 明确 failure_reason | query_code / stage 可读 | 静默失败 | `./evidence_a4_query_failure.md` |
| A5 | Failure 2: account/session identity 缺失时拒绝冒充成功 | 缺身份场景运行 | failure_reason 明确 | identity 缺失可见 | 错误宣告成功 | `./evidence_a5_identity_failure.md` |
| A6 | Boundary 1: 无订单/无成交不等于失败 | 空结果场景运行 | boundary / evidence-only | 空结果与失败分离 | 空结果被误判失败 | `./evidence_a6_empty_snapshot.md` |

## 二、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：2026-04-10
- **执行人**：—
- **建议**：暂不建议宣告通过
- **说明**：当前仅完成规划，待正式实现。