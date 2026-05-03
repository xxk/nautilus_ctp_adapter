# Query Flow Path And Session Labeling 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-10
**范围**：offhours flow/session/evidence 参数统一
**change-id**：20260410__live-session-order-query-hardening__query-flow-path-and-session-labeling
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
| A1 | Success 1: shared flow 默认行为稳定 | 不传 `flow-path` 运行 | 默认 shared flow 明确 | payload 说明 flow mode | 模式不明 | `./evidence_a1_shared_flow.md` |
| A2 | Success 2: isolated flow 可显式指定 | 传 `flow-path` 运行 | isolated flow 被采用 | payload/evidence 含隔离路径 | 参数无效 | `./evidence_a2_isolated_flow.md` |
| A3 | Success 3: session label 进入 evidence 命名 | 传 `session-label` / `evidence-root` | 文件名或内容含 session | 同日多次运行不覆盖 | evidence 被覆盖 | `./evidence_a3_session_label.md` |
| A4 | Failure 1: 非法路径语义清晰 | 构造无效路径 | 明确 failure_reason | 错误阶段可判定 | 静默失败 | `./evidence_a4_invalid_path.md` |
| A5 | Failure 2: 冲突参数被明确拒绝 | 构造冲突参数 | CLI 或 payload 拒绝 | 参数冲突可读 | 模糊覆盖 | `./evidence_a5_conflict.md` |
| A6 | Boundary 1: 未传 label 仍有稳定默认命名 | 默认运行 | 默认 evidence 命名可预测 | 文件名可复现 | 随机命名 | `./evidence_a6_default_naming.md` |

## 二、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：2026-04-10
- **执行人**：—
- **建议**：暂不建议宣告通过
- **说明**：当前仅完成规划，待实现与验证。