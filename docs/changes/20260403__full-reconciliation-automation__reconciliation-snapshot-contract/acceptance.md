# Reconciliation Snapshot Contract 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：reconciliation snapshot contract
**change-id**：20260403__full-reconciliation-automation__reconciliation-snapshot-contract
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/full-reconciliation-automation/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 23:58"
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

1. 冻结 reconciliation snapshot / summary contract。
2. 证明它能基于真实 `025292` 的 query baseline 输出统一 summary。
3. 保持只读边界。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: contract 可被仓内 stack 消费 | 运行 `python -m pytest` | reconciliation tests 通过 | `60 passed` | 新 contract 破坏 stack 或聚合逻辑 | [evidence_20260402_reconciliation_snapshot_contract.md](./evidence_20260402_reconciliation_snapshot_contract.md) |
| A2 | Success 2: 真实 summary 可产出 | 运行 `ctp_reconciliation_snapshot_smoke.py` | 返回 0 | `account_id=025292` 且 summary 字段可读 | smoke 返回非 0 | [evidence_20260402_reconciliation_snapshot_contract.md](./evidence_20260402_reconciliation_snapshot_contract.md) |
| A3 | Success 3: 比率字段可计算 | 检查 smoke JSON | `available_ratio`、`margin_ratio` 非空 | summary 有稳定比率输出 | 比率仍为空 | [evidence_20260402_reconciliation_snapshot_contract.md](./evidence_20260402_reconciliation_snapshot_contract.md) |
| A4 | Failure 1: topic 治理未漂移 | 运行 `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | active topic/change 漂移 | [evidence_20260402_reconciliation_snapshot_contract.md](./evidence_20260402_reconciliation_snapshot_contract.md) |
| A5 | Failure 2: 不复写 query 主线 | 检查实现与 factory | 复用现有 `query_adapter` | 没有新造第二套 query runtime | reconciliation 自己偷偷造独立 query 主线 | [evidence_20260402_reconciliation_snapshot_contract.md](./evidence_20260402_reconciliation_snapshot_contract.md) |
| A6 | Boundary 1: 不新增交易动作 | 检查结论 | 仅宣告只读 reconciliation baseline | 没有新增真实交易动作 | 把对账 baseline 写成交易能力 | [evidence_20260402_reconciliation_snapshot_contract.md](./evidence_20260402_reconciliation_snapshot_contract.md) |
