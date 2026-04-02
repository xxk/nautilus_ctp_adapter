# TD Truth Merge Snapshot 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：td truth merge snapshot
**change-id**：20260403__td-position-account-truth-merge__td-truth-merge-snapshot
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/td-position-account-truth-merge/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 16:23"
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

1. 收口 order/trade/position/account 的只读 truth merge snapshot。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: live truth merge snapshot smoke 成功 | 运行 `ctp_td_truth_merge_snapshot_smoke.py` | 返回 0 | smoke 正常退出 | 返回非 0 | [evidence_20260402_td_truth_merge_snapshot.md](./evidence_20260402_td_truth_merge_snapshot.md) |
| A2 | Success 2: baseline version 稳定 | 检查 smoke JSON | `baseline=td-truth-merge-snapshot-v1` | snapshot 结构固定 | 无 baseline 或结构漂移 | [evidence_20260402_td_truth_merge_snapshot.md](./evidence_20260402_td_truth_merge_snapshot.md) |
| A3 | Success 3: callback truth 与 query 可同时存在 | 检查 smoke JSON | 同时输出 `observed_callback_count`、`position_count`、`account_present` | merged truth 已成立 | 只能拿到单侧真相 | [evidence_20260402_td_truth_merge_snapshot.md](./evidence_20260402_td_truth_merge_snapshot.md) |
| A4 | Success 4: account identity 保持一致 | 检查 smoke JSON | `account_id=025292` 且 account snapshot 存在 | merged truth 可用于下一步 policy | 账户身份不一致或缺失 | [evidence_20260402_td_truth_merge_snapshot.md](./evidence_20260402_td_truth_merge_snapshot.md) |
| A5 | Boundary 1: real-only evidence | 检查 evidence 口径 | 不用 test/mock/fake 宣告通过 | evidence 只基于真实 live smoke | 用 test/mock/fake 冒充验收证据 | [evidence_20260402_td_truth_merge_snapshot.md](./evidence_20260402_td_truth_merge_snapshot.md) |
| A6 | Boundary 2: 只读边界保持 | 检查脚本与结论 | 无真实交易动作 | 仅执行 TD query/callback observation | 出现真实交易动作 | [evidence_20260402_td_truth_merge_snapshot.md](./evidence_20260402_td_truth_merge_snapshot.md) |
