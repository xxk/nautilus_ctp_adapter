# Order Lifecycle Smoke Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：order lifecycle smoke baseline
**change-id**：20260402__nautilus-live-execution__order-lifecycle-smoke-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-live-execution.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 17:06"
concluded_by: "GitHub Copilot"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: false }
  A6: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 验收结论

1. `dry-run` 与正式 `--live-send` 脚本入口都已通过，`connect` 与 `submit_order` 命令映射正常。
2. 仓内已新增 `matched_execs / exec_events` 结构化证据输出，并冻结了“native id 漂移时仍可回绑到 Python smoke `client_order_id`”以及“真实 smoke 默认使用唯一 flow 目录”的 contract-lock 测试。
3. 当前正式 live smoke 已稳定产出 `c2609` 的发送后新增回报，`matched_exec_count = 2`，并且两条匹配回报都已回绑到本次 Python smoke `client_order_id`。
4. 当前 `c2609` 未出现 `TRADE` 回报，`trade_volume = 0`，本次验证停留在“单已发出且未成交”的低风险 smoke 口径。

## 本次证据

1. dry-run 输出：`command_kinds = ["connect", "submit_order"]`
2. 实时一档探针：`c2609 last=2378.0 bid=2377.0 ask=2378.0`
3. live-send 通过留证：正式脚本输出 `matched_exec_count = 2`，`match_reason = post_send_symbol_qty / native_alias`
4. 修复点：真实 smoke 默认改为唯一 TD flow 目录，避免复用旧 session artifact 干扰当前回报判定
