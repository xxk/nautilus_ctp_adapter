# Query Flow Path And Session Labeling 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-10
**范围**：offhours flow/session/evidence 参数统一
**change-id**：20260410__live-session-order-query-hardening__query-flow-path-and-session-labeling
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 16:52"
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
| A1 | Success 1: shared flow 默认行为稳定 | focused pytest | 默认 shared flow 明确 | payload 说明 flow mode | 模式不明 | `./evidence_repo_only_flow_session_labeling.md` |
| A2 | Success 2: isolated flow 可显式指定 | focused pytest | isolated flow 被采用 | payload/evidence 含隔离路径 | 参数无效 | `./evidence_repo_only_flow_session_labeling.md` |
| A3 | Success 3: session label 进入 evidence 命名 | focused pytest | 文件名或内容含 session | 同日多次运行不覆盖 | evidence 被覆盖 | `./evidence_repo_only_flow_session_labeling.md` |
| A4 | Failure 1: 非法路径语义清晰 | focused pytest | 明确 failure_reason | 错误阶段可判定 | 静默失败 | `./evidence_repo_only_flow_session_labeling.md` |
| A5 | Failure 2: 冲突参数被明确拒绝 | focused pytest | CLI 或 payload 拒绝 | 参数冲突可读 | 模糊覆盖 | `./evidence_repo_only_flow_session_labeling.md` |
| A6 | Boundary 1: 未传 label 仍有稳定默认命名 | focused pytest | 默认 evidence 命名可预测 | 文件名可复现 | 随机命名 | `./evidence_repo_only_flow_session_labeling.md` |

## 二、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-06-08
- **执行人**：Codex
- **建议**：可宣告 repo-only flow/session/evidence naming contract 通过
- **说明**：successor implementation 已覆盖主要 evidence-bearing scripts，focused regression 通过。
