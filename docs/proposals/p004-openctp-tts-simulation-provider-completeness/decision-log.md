# P004 Decision Log

**fragment-id**：`decision_log`
**proposal-id**：`p004-openctp-tts-simulation-provider-completeness`
**状态**：completed

---

## Decision Log

| 日期 | 决策 | 原因 | 回写动作 | 明确不做 |
| --- | --- | --- | --- | --- |
| 2026-06-08 | 新开 P004 successor proposal，不重开 P003 | P003 已 completed；继续修改 P003 会污染完成态 | 在 P004 README、phase-plan、acceptance 中声明 P003 为 baseline/reference | 不把 P003 pass 当作 P004 pass |
| 2026-06-08 | Canonical account profile 使用 `openctp-tts-7x24-simulation` | 用户需要 24 小时调试 API；该 profile 已配置并完成模拟下单 evidence | 修正 P003 closeout runbook 旧 alias 投影，并在 P004 artifact boundary 固化 | 不使用 `formal-trading` |
| 2026-06-08 | 下单类 P004 验收必须有 simulation evidence 或 typed blocker | 撤单、平仓、重连、engine harness 不能只靠 mock/test 关闭 | 在 acceptance evidence boundary 中写明 test-only 限制 | 不用 mock 伪造外部 front 行为 |
| 2026-06-08 | Nautilus engine harness 作为最终 provider evidence | scripts 可以证明 API 调试闭环，但 provider completeness 需要 Nautilus-facing command/report path | Phase 7 单独承接 engine harness | 不让 script-only smoke 代替 provider evidence |
| 2026-06-08 | Phase 6 reconnect 采用 process-scoped controlled front proxy | 公共 OpenCTP 7x24 front 不应被干扰；本地 proxy 可只影响测试进程并产生可复核断连证据 | 回写 architecture、Phase 6 acceptance 和 `controlled_reconnect_pass.json` evidence | 不控制或干扰公共 simulation front |

## 记录规则

1. 只记录会影响后续执行边界的稳定判断。
2. 已升格为长期规则的内容应回写到 `docs/architecture/`、`docs/adr/` 或 runbook。
