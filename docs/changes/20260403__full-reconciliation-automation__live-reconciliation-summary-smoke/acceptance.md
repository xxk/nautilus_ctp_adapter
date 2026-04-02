# Live Reconciliation Summary Smoke 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：live reconciliation summary smoke
**change-id**：20260403__full-reconciliation-automation__live-reconciliation-summary-smoke
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/full-reconciliation-automation/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-03 00:08"
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

1. 把 reconciliation summary smoke 升级成正式 live evidence 入口。
2. 明确 dominant exposure 与 top exposures 的输出口径。
3. 明确 test/mock/fake 不能作为验收证据。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live summary smoke 成功 | 运行 `ctp_reconciliation_snapshot_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260402_live_reconciliation_summary.md](./evidence_20260402_live_reconciliation_summary.md) |
| A2 | Success 2: 账户与总量字段有效 | 检查 smoke JSON | `account_id=025292`、`gross_position_qty>0` | 真实 summary 字段可读 | 账户或总量字段缺失 | [evidence_20260402_live_reconciliation_summary.md](./evidence_20260402_live_reconciliation_summary.md) |
| A3 | Success 3: dominant exposure 字段有效 | 检查 smoke JSON | `dominant_exposure_symbol` 非空，`dominant_exposure_abs_net_qty>0` | 主导敞口已输出 | dominant exposure 缺失 | [evidence_20260402_live_reconciliation_summary.md](./evidence_20260402_live_reconciliation_summary.md) |
| A4 | Success 4: top exposures 排序稳定 | 检查 `top_exposures` | 按 `abs_net_qty -> gross_qty -> position_cost` 排序 | 排序口径稳定 | 输出顺序不稳定 | [evidence_20260402_live_reconciliation_summary.md](./evidence_20260402_live_reconciliation_summary.md) |
| A5 | Boundary 1: 只读边界保持 | 检查结论和脚本 | 无真实交易动作 | 仅使用 query-based live summary | 出现发单/撤单行为 | [evidence_20260402_live_reconciliation_summary.md](./evidence_20260402_live_reconciliation_summary.md) |
| A6 | Boundary 2: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260402_live_reconciliation_summary.md](./evidence_20260402_live_reconciliation_summary.md) |
