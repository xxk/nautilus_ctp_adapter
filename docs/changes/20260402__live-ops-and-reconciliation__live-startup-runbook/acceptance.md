# Live Startup Runbook 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：live 启动 runbook、正式入口分层、最小运维启动口径
**change-id**：20260402__live-ops-and-reconciliation__live-startup-runbook
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-ops-and-reconciliation.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 18:42"
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

1. 让 Topic 5 有一个可执行的正式起点，而不是只停留在 roadmap 层。
2. 冻结正式 live 启动 runbook 的最小结构与入口。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. Topic 5 README 激活
2. `C1` child change bundle 存在且可读
3. 正式入口、诊断入口与人工步骤分层明确

### 不覆盖（Out of Scope）

1. reconnect/recovery 细节实现
2. audit/reconciliation 细节实现
3. 新的交易行为变更

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: Topic 5 已激活 | 读取 Topic 5 README | 状态为 `进行中` | active topic 已切换 | 仍为未开始 | |
| A2 | Success 2: `C1` bundle 已创建 | 检查当前 change 目录 | 三件套与 runbook 存在 | `plan/acceptance/ai_constraints` 和 `live_startup_runbook.md` 可读 | 缺少 bundle | [evidence_20260402_live_startup_runbook.md](./evidence_20260402_live_startup_runbook.md) |
| A3 | Success 3: mainline 已切到 Topic 5 | 读取 mainline README | 当前活动 topic 为 Topic 5 | mainline 口径同步 | 仍停在 Topic 4 | [evidence_20260402_live_startup_runbook.md](./evidence_20260402_live_startup_runbook.md) |
| A4 | Failure 1: AGENTS/docs 索引未切换 | 读取入口文档 | 入口都指向 Topic 5 | `AGENTS/docs/topics` 一致 | 入口漂移 | [evidence_20260402_live_startup_runbook.md](./evidence_20260402_live_startup_runbook.md) |
| A5 | Failure 2: topic 治理门禁失败 | `python scripts/check_topic_docs.py` | 返回 0 | `failures=0` | topic docs 漂移 | [evidence_20260402_live_startup_runbook.md](./evidence_20260402_live_startup_runbook.md) |
| A6 | Boundary 1: 测试入口未受影响 | `python -m pytest` | 通过 | 现有回归通过 | 文档切换破坏测试 | [evidence_20260402_live_startup_runbook.md](./evidence_20260402_live_startup_runbook.md) |

## 十一、最终结论 / Final Verdict

- **结论**：✅ 已通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：Topic 5 的首个 child change 已把正式 startup runbook、入口分层和最小验证顺序冻结完成。
