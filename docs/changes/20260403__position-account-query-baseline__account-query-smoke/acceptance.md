# Account Query Smoke 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：真实 `025292` 资金查询 smoke 与 evidence
**change-id**：20260403__position-account-query-baseline__account-query-smoke
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/position-account-query-baseline/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 22:33"
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

1. 用真实账户 `025292` 建立正式 account query smoke。
2. 证明仓内本地 `c wrapper -> Python adapter -> runtime` 的 account query 主线有效。
3. 留下可供后续 reconciliation 复用的资金快照证据。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 真实 query 发起成功 | 运行 `ctp_account_query_smoke.py` | `query_code=0` | query 正常发出 | query code 非 0 | [evidence_20260402_account_query_smoke.md](./evidence_20260402_account_query_smoke.md) |
| A2 | Success 2: account snapshot 完整闭合 | 检查 smoke JSON | `completed=true` 且 `timed_out=false` | snapshot 完整闭合 | timeout 或未闭合 | [evidence_20260402_account_query_smoke.md](./evidence_20260402_account_query_smoke.md) |
| A3 | Success 3: account 数据有效 | 检查 `account` 字段 | `account_id=025292` 且 balance/available 可读 | 真实资金快照存在 | 仍无 account 数据 | [evidence_20260402_account_query_smoke.md](./evidence_20260402_account_query_smoke.md) |
| A4 | Failure 1: 治理状态未漂移 | 运行 `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | topic/active change 漂移 | [evidence_20260402_account_query_smoke.md](./evidence_20260402_account_query_smoke.md) |
| A5 | Failure 2: 回归未破坏 | 运行 `python -m pytest` | 回归通过 | `58 passed` | 新 query 主线破坏既有能力 | [evidence_20260402_account_query_smoke.md](./evidence_20260402_account_query_smoke.md) |
| A6 | Boundary 1: 不宣告交易动作 | 检查 change 结论 | 仅宣告只读 query | 没有新增真实交易动作 | 把只读 query 写成交易能力 | [evidence_20260402_account_query_smoke.md](./evidence_20260402_account_query_smoke.md) |

