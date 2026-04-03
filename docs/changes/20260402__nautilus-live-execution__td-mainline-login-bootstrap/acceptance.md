# TD Mainline Login Bootstrap 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：TD mainline login bootstrap
**change-id**：20260402__nautilus-live-execution__td-mainline-login-bootstrap
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-live-execution/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 12:15"
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

1. 证明 execution 侧已有正式 TD bootstrap 主线。
2. 证明 Topic 4 的后续 change 不需要再从 readiness smoke 里重找登录入口。

## 二、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: execution bootstrap 成立 | 检查 execution 主线 | 有正式 bootstrap 入口 | execution client 不再只是 smoke residue | 仍停留在诊断脚本 | 当前 change |
| A2 | Success 2: 输出模型冻结 | 检查 bootstrap output | 输出 shape 稳定 | C2/C3 可复用 | 输出仍漂移 | 当前 change |
| A3 | Success 3: 继承 guardrails | 对照 topic/mainline 规则 | 不绕过 guardrails | 统一边界仍生效 | execution bootstrap 绕开 guardrails | 当前 change |
| A4 | Failure 1: 不越界发单 | 对照 scope | 不接真实下单命令 | 范围收敛 | 越界到 order send | 当前 change |
| A5 | Failure 2: 不回退到托管主线 | 对照仓内口径 | 继续走 repo-owned c wrapper | 无 C# 主线依赖 | 回退到 managed host | 当前 change |
| A6 | Boundary 1: 可交接给 C2 | 对照 topic queue | C2 可直接接力 | next action 清楚 | topic queue 模糊 | 当前 change |

## 三、验收结论 / Conclusion

1. execution 侧已有正式 TD bootstrap 主线。
2. bootstrap 输出模型已经稳定，后续 C2/C3 不需要再从 readiness smoke 中重找入口。
3. 当前实现继续遵守 guardrails，并未越界接入真实发单。

## 四、验证命令 / Verification Commands

```powershell
python -m pytest
python -m pip install -e .
```

## 五、证据 / Evidence

1. [evidence_20260402_td_mainline_login_bootstrap.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-execution__td-mainline-login-bootstrap/evidence_20260402_td_mainline_login_bootstrap.md)
