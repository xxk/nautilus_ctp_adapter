# TD 鉴权与登录就绪 验收方案

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-01
**范围**：TD auth/login readiness
**change-id**：20260401__ctp-live-connectivity__td-auth-and-login-readiness
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 10:18"
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

1. 证明 TD readiness 的缺口已经被收敛成明确输入或明确失败原因
2. 证明后续 Topic 4 可以在已知条件上推进，而不是继续盲试

## 二、启动前提 / Entry Preconditions

1. `20260401__ctp-live-connectivity__python-rust-md-login-path` 必须先完成，至少要让 MD 主线路径和主线证据站稳。
2. `20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610` 中的 `ErrorID=63` 留证是本 change 的输入，不是最终结论。
3. 本 change 的目标是把“还差什么”收敛清楚，而不是把 TD execution 直接做完。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: ErrorID=63 被明确解释 | 对照证据与配置模型 | 失败原因被收敛 | 已证明错误顺序调用可复现 `ErrorID=63` | 仍是模糊失败 | `./evidence_20260402_td_login_readiness.md` |
| A2 | Success 2: TD 输入模型冻结 | 检查 config/runtime | 字段模型一致 | 已冻结 `app_id -> auth_code -> product_info` | 字段口径还在漂移 | `./evidence_20260402_td_login_readiness.md` |
| A3 | Success 3: readiness 结论可交接 Topic 4 | 检查 roadmap 回写 | Topic 4 可直接接力 | Topic 1 可继续推进 `C5`，后续 execution 不必重摸 TD 参数 | 仍需重新摸索 | `./evidence_20260402_td_login_readiness.md` |
| A4 | Failure 1: 无效参数时可诊断 | 失败路径验证 | 错误可解释 | 错误顺序下出现 `ErrorID=63` 与 `4097` 断开信号 | 错误静默 | `./evidence_20260402_td_login_readiness.md` |
| A5 | Failure 2: 不把“未 ready”误写成“可交易” | 对照 verdict | 结论保守准确 | 文档明确只接受 readiness，不宣称 execution ready | 结论越界 | 当前 change |
| A6 | Boundary 1: 不提前实现完整 execution client | 对照 scope | 本 change 不越界 | 只新增 TD smoke 与边界冻结 | 范围失控 | 当前 change |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 继承的 TD 失败证据 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md` | 当前已知 `ErrorID=63` 来源 |
| 2 | 上游主线 MD 前置 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__python-rust-md-login-path/acceptance.md` | 证明 TD readiness 不再和 MD 主线问题混在一起 |
| 3 | 当前 change 输出证据 | `./evidence_20260402_td_login_readiness.md` | 用于冻结缺项清单、输入模型和 readiness verdict |

## 七、最终结论 / Final Verdict

- **结论**：✅ 通过
- **建议**：推进 `C5`，把现有 MD/TD readiness 收口成 Nautilus 向的 live smoke baseline
- **说明**：当前 verdict 只代表 C4 bundle 状态，不代表 execution 已 ready。
