# Runtime Query Contract 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：position/account runtime query contract
**change-id**：20260403__position-account-query-baseline__runtime-query-contract
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/position-account-query-baseline/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 19:39"
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

1. 冻结 position/account 的 runtime query contract。
2. 给后续 `025292` 真查询 smoke 提供稳定边界。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: query model 已扩展 | 读取 runtime query 代码 | 存在 position/account 模型 | record 与计数接口存在 | 仍只有 instrument | [evidence_20260402_runtime_query_contract.md](./evidence_20260402_runtime_query_contract.md) |
| A2 | Success 2: position contract 已锁定 | 运行 pytest | position lifecycle 测试通过 | `QUERY_POSITIONS -> POSITION` 成立 | 无 position contract | [evidence_20260402_runtime_query_contract.md](./evidence_20260402_runtime_query_contract.md) |
| A3 | Success 3: account contract 已锁定 | 运行 pytest | account lifecycle 测试通过 | `QUERY_ACCOUNT -> ACCOUNT` 成立 | 无 account contract | [evidence_20260402_runtime_query_contract.md](./evidence_20260402_runtime_query_contract.md) |
| A4 | Failure 1: topic 治理漂移 | `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | 激活新 topic 后入口漂移 | [evidence_20260402_runtime_query_contract.md](./evidence_20260402_runtime_query_contract.md) |
| A5 | Failure 2: 修改破坏回归 | `python -m pytest` | 回归通过 | 测试通过 | query contract 改动破坏既有行为 | [evidence_20260402_runtime_query_contract.md](./evidence_20260402_runtime_query_contract.md) |
| A6 | Boundary 1: 不过度宣告 | 检查最终结论 | 仅宣告 contract 通过 | 未宣告真查询已完成 | 过度宣告 | [evidence_20260402_runtime_query_contract.md](./evidence_20260402_runtime_query_contract.md) |
