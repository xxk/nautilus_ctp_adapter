# TD 鉴权与登录就绪 验收方案

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-01
**范围**：TD auth/login readiness
**change-id**：20260401__ctp-live-connectivity__td-auth-and-login-readiness
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-04-01 00:00"
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
| A1 | Success 1: ErrorID=63 被明确解释 | 对照证据与配置模型 | 失败原因被收敛 | 有明确缺项或组合要求 | 仍是模糊失败 | 当前 change |
| A2 | Success 2: TD 输入模型冻结 | 检查 config/runtime | 字段模型一致 | `AuthCode/AppID/...` 口径稳定 | 字段口径还在漂移 | 当前 change |
| A3 | Success 3: readiness 结论可交接 Topic 4 | 检查 roadmap 回写 | Topic 4 可直接接力 | 有清楚交接结论 | 仍需重新摸索 | 当前 change |
| A4 | Failure 1: 无效参数时可诊断 | 失败路径验证 | 错误可解释 | 失败留证清楚 | 错误静默 | 当前 change |
| A5 | Failure 2: 不把“未 ready”误写成“可交易” | 对照 verdict | 结论保守准确 | readiness 与 execution 区分清楚 | 结论越界 | 当前 change |
| A6 | Boundary 1: 不提前实现完整 execution client | 对照 scope | 本 change 不越界 | 只解决 readiness | 范围失控 | 当前 change |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 继承的 TD 失败证据 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md` | 当前已知 `ErrorID=63` 来源 |
| 2 | 上游主线 MD 前置 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__python-rust-md-login-path/acceptance.md` | 证明 TD readiness 不再和 MD 主线问题混在一起 |
| 3 | 当前 change 输出证据 | 当前 change bundle 内新增 | 用于冻结缺项清单、输入模型和 readiness verdict |

## 七、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **建议**：等待 C3 站稳后再启动，并把 readiness 结论收敛为可交接 verdict
- **说明**：当前 verdict 只代表 C4 bundle 状态，不代表 execution 已 ready。
