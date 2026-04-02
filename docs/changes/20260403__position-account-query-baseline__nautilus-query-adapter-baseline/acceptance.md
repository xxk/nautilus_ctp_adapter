# Nautilus Query Adapter Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：position/account query adapter baseline
**change-id**：20260403__position-account-query-baseline__nautilus-query-adapter-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/position-account-query-baseline/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 23:24"
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

1. 把真实 `position/account query` 收口成 Nautilus 可消费的最小 adapter baseline。
2. 证明 `query_adapter` 与现有 `execution_client/runtime_bridge` 共用同一条主线。
3. 通过统一 smoke 入口留下正式 evidence。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 统一 snapshot query 成功 | 运行 `ctp_query_adapter_smoke.py` | position/account 两段 query code 都为 `0` | query 正常发出并闭合 | 任一 query code 非 0 | [evidence_20260402_query_adapter_smoke.md](./evidence_20260402_query_adapter_smoke.md) |
| A2 | Success 2: position baseline 可消费 | 检查 smoke JSON | `positions.completed=true` 且 `position_count>0` | 真实 position snapshot 存在 | position baseline 仍为空或 timeout | [evidence_20260402_query_adapter_smoke.md](./evidence_20260402_query_adapter_smoke.md) |
| A3 | Success 3: account baseline 可消费 | 检查 smoke JSON | `account.completed=true` 且 `account_id=025292` | 真实 account snapshot 存在 | account baseline 仍为空或 timeout | [evidence_20260402_query_adapter_smoke.md](./evidence_20260402_query_adapter_smoke.md) |
| A4 | Failure 1: topic 治理未漂移 | 运行 `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | topic/active change 漂移 | [evidence_20260402_query_adapter_smoke.md](./evidence_20260402_query_adapter_smoke.md) |
| A5 | Failure 2: 回归未破坏 | 运行 `python -m pytest` | 回归通过 | `59 passed` | query adapter 破坏既有主线 | [evidence_20260402_query_adapter_smoke.md](./evidence_20260402_query_adapter_smoke.md) |
| A6 | Boundary 1: 不新增交易动作 | 检查 change 结论 | 仅宣告只读 query baseline | 没有新增真实交易动作 | 把 query baseline 写成交易能力 | [evidence_20260402_query_adapter_smoke.md](./evidence_20260402_query_adapter_smoke.md) |
