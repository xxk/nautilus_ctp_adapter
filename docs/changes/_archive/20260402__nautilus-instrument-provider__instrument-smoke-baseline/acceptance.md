# Instrument Smoke Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-02
**范围**：instrument smoke baseline
**change-id**：20260402__nautilus-instrument-provider__instrument-smoke-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-instrument-provider.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 11:18"
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

1. 证明 InstrumentProvider 方向已经有真实、可重复的 smoke baseline。
2. 证明 Topic 3 可以直接复用 Topic 2 的真实合约查询入口与证据口径。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 正式入口冻结 | 运行 `python scripts/ctp_instrument_query_smoke.py --config <path> --symbol rb2610` | 存在唯一正式入口 | 正式脚本稳定输出 JSON | 多条 competing 入口 | `./evidence_20260402_instrument_smoke_baseline.md` |
| A2 | Success 2: 真实 query 返回合约定义 | 使用本仓本地 `c wrapper` 执行真实 query | 至少返回 `rb2610.SHFE` | `instrument_count > 0` 且包含 `rb2610.SHFE` | 仅模拟链路 | `./evidence_20260402_instrument_smoke_baseline.md` |
| A3 | Success 3: provider 输出可复用 | 对照 smoke 输出 | Topic 3 可直接消费 | 返回 normalized instrument fields | 输出结构仍不稳 | `./evidence_20260402_instrument_smoke_baseline.md` |
| A4 | Failure 1: 不越界做 marketdata topic | 对照 scope | 只冻结 instrument smoke | 未提前实现 Topic 3 | 范围失控 | `./evidence_20260402_instrument_smoke_baseline.md` |
| A5 | Failure 2: 不绕过本仓 c wrapper | 对照实现路径 | 只走 repo-owned local c wrapper | 未回退到 C# 托管桥 | 再次引入 managed bridge | `./evidence_20260402_instrument_smoke_baseline.md` |
| A6 | Boundary 1: Topic 2 可完成 | 对照 topic queue | Topic 3 可激活 | Topic 2 出口条件已满足 | topic 仍缺正式 smoke | `./evidence_20260402_instrument_smoke_baseline.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 当前 change 输出证据 | `./evidence_20260402_instrument_smoke_baseline.md` | 正式入口、真实 query 结果、通过信号 |
| 2 | 上游 provider bootstrap | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-instrument-provider__instrument-provider-bootstrap/evidence_20260402_instrument_provider_bootstrap.md` | 证明 smoke baseline 建立在 C3 之上 |

## 七、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-04-02
- **执行人**：Codex
- **建议**：关闭 Topic 2，激活 Topic 3
- **说明**：当前通过的是 instrument smoke baseline，不代表 marketdata topic 已完成。
