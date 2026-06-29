# Reconnect And Recovery Policy 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：reconnect/recovery 规则、恢复边界、人工介入升级口径
**change-id**：20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-ops-and-reconciliation.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 18:58"
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

1. 给 Topic 5 冻结可执行的 reconnect/recovery 策略起点。
2. 明确自动恢复、重试、失败升级和人工介入边界。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: `C2` bundle 已创建 | 检查当前 change 目录 | 三件套与 policy 文档存在 | `plan/acceptance/ai_constraints/reconnect_recovery_policy.md` 可读 | 缺少 bundle | [evidence_20260402_reconnect_and_recovery_policy.md](./evidence_20260402_reconnect_and_recovery_policy.md) |
| A2 | Success 2: Topic 5 active change 已切到 `C2` | 读取 docs 入口 | active change 正确 | `docs/README` 与 `docs/topics/README` 一致 | 仍停在 `C1` | [evidence_20260402_reconnect_and_recovery_policy.md](./evidence_20260402_reconnect_and_recovery_policy.md) |
| A3 | Success 3: 恢复边界已冻结 | 读取 policy 文档 | 自动恢复 / 人工介入边界明确 | MD/TD/runtime/flow 四层规则成文 | 仍是零散结论 | [evidence_20260402_reconnect_and_recovery_policy.md](./evidence_20260402_reconnect_and_recovery_policy.md) |
| A4 | Failure 1: topic 治理门禁失败 | `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | topic docs 漂移 | [evidence_20260402_reconnect_and_recovery_policy.md](./evidence_20260402_reconnect_and_recovery_policy.md) |
| A5 | Failure 2: 文档切换破坏回归 | `python -m pytest` | 测试继续通过 | 回归通过 | 索引切换破坏测试 | [evidence_20260402_reconnect_and_recovery_policy.md](./evidence_20260402_reconnect_and_recovery_policy.md) |
| A6 | Boundary 1: 不扩展真实交易权限 | 检查本 change 修改范围 | 仅冻结规则与证据 | 未引入新的 live send 行为 | 借恢复策略扩张交易行为 | [evidence_20260402_reconnect_and_recovery_policy.md](./evidence_20260402_reconnect_and_recovery_policy.md) |

## 十一、最终结论 / Final Verdict

- **结论**：✅ 已通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：Topic 5 的 reconnect/recovery 规则已形成正式成文口径，可继续推进审计与对账基线。
