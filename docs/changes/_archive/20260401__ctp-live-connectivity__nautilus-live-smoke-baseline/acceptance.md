# Nautilus 实盘 Smoke 基线 验收方案

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-01
**范围**：Nautilus live smoke baseline
**change-id**：20260401__ctp-live-connectivity__nautilus-live-smoke-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/ctp-live-connectivity.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 10:24"
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

1. 证明 Nautilus 方向已经有统一的实盘 smoke 基线
2. 证明 Topic 2/3/4 后续会复用同一套入口与证据口径

## 二、启动前提 / Entry Preconditions

1. `20260401__ctp-live-connectivity__td-auth-and-login-readiness` 必须先完成。
2. 当前 change 只负责冻结正式 smoke baseline，不负责替代 Topic 2-4 的实现。
3. 若仍需临时诊断脚本协助，也必须把它明确标记为 diagnostics，而不是正式 baseline。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: smoke 最小入口冻结 | 检查 scripts/README/plan | 有唯一 smoke 入口 | 已冻结 `python scripts\ctp_nautilus_live_smoke.py --config <path>` | 存在多个 competing 入口 | `./evidence_20260402_nautilus_live_smoke_baseline.md` |
| A2 | Success 2: 最小成功信号冻结 | 检查 acceptance | “何为通过”被明确写清 | `MD tick + TD readiness + bridge events` 三类信号已冻结 | 成功口径模糊 | `./evidence_20260402_nautilus_live_smoke_baseline.md` |
| A3 | Success 3: 证据包格式冻结 | 检查 evidence 要求 | 后续 smoke 证据可复用 | 单个 JSON 结果与 evidence 结构已明确 | 证据结构不统一 | `./evidence_20260402_nautilus_live_smoke_baseline.md` |
| A4 | Failure 1: 不把临时脚本冒充正式 smoke | 对照 scope | 临时诊断与正式 smoke 分离 | `ctp_md_login_smoke.py` 与 `ctp_td_login_smoke.py` 仅保留 diagnostics 角色 | 临时脚本继续混用 | 当前 change |
| A5 | Failure 2: 不越界做完整 adapter | 对照 scope | 只冻结 baseline | 未宣称 Topic 2-4 已完成 | 任务范围失控 | 当前 change |
| A6 | Boundary 1: Topic 1 收尾但不替代 Topic 2-4 | 对照 roadmap | 交接边界清楚 | Topic 1 只交付 baseline，后续 topic 继续正式实现 | Topic 分层混乱 | 当前 change |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | Topic 1 上游结论 | `/D:/Nautilus/nautilus_ctp_adapter/docs/topics/ctp-live-connectivity.md` | baseline 必须建立在 Topic 1 已冻结结论上 |
| 2 | 当前 change 输出证据 | `./evidence_20260402_nautilus_live_smoke_baseline.md` | 正式 smoke 入口、成功信号、证据格式 |
| 3 | docs index 回写 | `/D:/Nautilus/nautilus_ctp_adapter/docs/README.md` | 用于声明后续 topic 的统一 smoke 入口 |

## 七、最终结论 / Final Verdict

- **结论**：✅ 通过
- **建议**：返回 `C1` 收口 Topic 1 总验收，然后再进入 Topic 2
- **说明**：当前 verdict 只代表 C5 bundle 状态，不代表 Topic 2-4 已完成。
