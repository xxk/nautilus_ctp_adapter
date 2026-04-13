# 实盘账户调试 Guardrails 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已完成
**日期**：2026-04-02
**范围**：`docs/topics/nautilus-live-execution/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`cfgs/`、`tests/`
**change-id**：20260402__nautilus-live-execution__real-account-debug-guardrails
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-live-execution.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-04-02 18:20"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

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

1. 证明 `025292` 的 execution 调试边界已经从聊天约束收敛成仓内长期规则。
2. 证明配置与执行预检都能表达并执行这些 guardrails。
3. 证明当前 change 不会因为“加 guardrails”而偷偷引入真实发单逻辑。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: mainline 与 topic README 都冻结 guardrails | 检查 roadmap 文档 | 两层文档规则一致 | `025292/c2609/1手/5手/10次/一档价` 全部出现且无冲突 | 规则仍散落在聊天或只写一层 | 当前 change + roadmap |
| A2 | Success 2: 配置模型可表达 execution guardrails | 运行 `python -m pytest` | config 可装载并验证 guardrails | 测试通过且示例配置包含 guardrails | config 不可装载或未验证 | 当前 change + `tests/` |
| A3 | Success 3: execution precheck 可阻止越界订单 | 运行 `python -m pytest` | 预检能拒绝不允许的 symbol/qty/position/rate | 测试通过且 precheck 不触达 TD | 仍需靠人工记忆限制 | 当前 change + `tests/` |
| A4 | Failure 1: 非 `c2609` 调试单被拒绝 | 运行 `python -m pytest` | `rb2610` 等 symbol 不能通过 guardrails | 测试中出现明确 violation | 非授权 symbol 仍可通过 | 当前 change + `tests/` |
| A5 | Failure 2: 超量、超持仓、超频被拒绝 | 运行 `python -m pytest` | qty>1、净持仓>5、分钟报单>=10 不能通过 | 测试中出现明确 violation | 限制未生效 | 当前 change + `tests/` |
| A6 | Boundary 1: 一档价选择可复用 | 运行 `python -m pytest` | `BUY -> ask1`，`SELL -> bid1` | 测试中价格选择符合规则 | 仍允许随意价格模式 | 当前 change + `tests/` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | roadmap 规则 | `/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-live-execution.md` | Topic 级 guardrails |
| 2 | mainline 规则 | `/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-ctp-adapter-mainline.md` | 仓级 guardrails |
| 3 | contract 锁定 | `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py` | config + precheck 测试 |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Contract 锁定 | `python -m pytest` | 锁定 config 与 execution precheck 行为 |

## 十一、最终结论 / Final Verdict

- **结论**：✅ 已完成
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：本 change 已冻结 guardrails、配置表达与 precheck contract；execution 主线仍未 ready。
