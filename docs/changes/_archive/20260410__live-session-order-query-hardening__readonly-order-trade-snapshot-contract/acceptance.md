# Readonly Order Trade Snapshot Contract 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ Repo-only 通过
**日期**：2026-04-10
**范围**：`ORDER / TRADE` 只读 snapshot contract
**change-id**：20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed_repo_only
allow_declare_pass: true
last_updated: "2026-06-08 16:58"
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

## 一、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: `ORDER` 只读快照成功 | focused pytest/source contract | 返回 orders snapshot | order snapshot taxonomy tests passed | 不可判定 | `./evidence_repo_only_order_trade_snapshot.md` |
| A2 | Success 2: `TRADE` 只读快照成功 | focused pytest/source contract | 返回 trades snapshot | trade snapshot taxonomy tests passed | 不可判定 | `./evidence_repo_only_order_trade_snapshot.md` |
| A3 | Success 3: 历史残留与当前 query 结果能分层 | focused pytest | callback truth 与 query snapshot 分层 | historical callback boundary tests passed | 混成单一结果 | `./evidence_repo_only_order_trade_snapshot.md` |
| A4 | Failure 1: query 失败语义清晰 | focused pytest | 明确 failure_reason | failure taxonomy tests passed | 静默失败 | `./evidence_repo_only_order_trade_snapshot.md` |
| A5 | Failure 2: account/session identity 缺失时拒绝冒充成功 | focused pytest | failure_reason 明确 | identity/boundary tests passed | 错误宣告成功 | `./evidence_repo_only_order_trade_snapshot.md` |
| A6 | Boundary 1: 无订单/无成交不等于失败 | focused pytest/README | boundary / evidence-only | `no_order_events / no_trade_events` semantics documented | 空结果被误判失败 | `./evidence_repo_only_order_trade_snapshot.md` |

## 二、最终结论 / Final Verdict

- **结论**：✅ Repo-only 通过
- **日期**：2026-06-08
- **执行人**：Codex
- **建议**：可宣告 read-only order/trade snapshot contract 通过；live evidence 仍需单独运行
- **说明**：正式聚合入口已暴露 `--include-order-trade-snapshot`，focused regression 通过。
