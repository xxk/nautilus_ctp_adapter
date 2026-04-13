# Session Window Guardrails 与真实场景验收驱动 Runbook 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：🟨 部分完成（blocked）
**日期**：2026-04-09
**更新日期**：2026-04-11
**范围**：交易时段 `c2609` 一手下单开发 + 非交易时段 `account / position / query snapshot` 只读开发的 session-window baseline
**change-id**：20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: blocked
allow_declare_pass: false
last_updated: "2026-04-11 00:45"
concluded_by: "GitHub Copilot"

exit_conditions:
  E1_success_scenarios: failed
  E2_failure_scenarios: pending
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: pending
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: false, result: null, blocking: true }
  A2: { exec: false, result: null, blocking: true }
  A3: { exec: true, result: true, blocking: true }
  A4: { exec: true, result: true, blocking: true }
  A5: { exec: false, result: null, blocking: true }
  A6: { exec: true, result: true, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | 🟨 blocked | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 否 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-04-10 00:00 | |
| AI 执行人 | GitHub Copilot | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ❌ | A1/A2/A3 阻塞成功场景全部 ✅ | 当前 change 证据文件 |
| E2 | 关键失败场景符合预期 | ⬜ | A4/A5 阻塞失败场景全部 ✅ | 当前 change 证据文件 |
| E3 | 必跑验证命令已完成 | ✅ | 已执行 `python scripts/check_topic_docs.py`；当前轮为文档/治理推进，无需代码级 pytest | 当前 change 证据文件 |
| E4 | 关键证据已留存 | ✅ | 已形成 runbook 与 U1/C2/C3 交接路径，offhours 路径已有 sibling change 证据 | 当前 change 证据文件 |
| E5 | 正式验收不依赖 mock 或 test | ⬜ | 交易时段成功场景仍需真实 CTP / 真实窗口 | 当前 change 证据文件 |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 已冻结，无需豁免 | 当前文档 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: 交易时段 TD preflight ready | ⬜ | ⬜ | 是 | `ctp_td_order_truth_smoke.py`；当前被 U1 vendor-bridge readiness 阻塞 |
| A2 | Success 2: `c2609` 一手 live order dev loop 走通 | ⬜ | ⬜ | 是 | `ctp_order_lifecycle_smoke.py --live-send`；当前被 U1 + 交易窗口阻塞 |
| A3 | Success 3: 非交易时段 query snapshot 走通 | ✅ | ✅ | 是 | C3 已冻结正式入口与结构化 failure semantics |
| A4 | Failure 1: 非交易时段误用 live-send 被明确阻断 | ✅ | ✅ | 是 | `ctp_query_adapter_smoke.py --live-send` 已被 argparse 明确拒绝；见 sibling C3 |
| A5 | Failure 2: guardrail 越界订单在触达 TD 前被拒绝 | ⬜ | ⬜ | 是 | 仍待 C2 形成 trade-window guardrail 失败证据 |
| A6 | Boundary 1: 空仓或无持仓不被误判成查询失败 | ✅ | ✅ | 否 | C3 已补 code-level contract 与 evidence 路径 |

## 一、验收目标 / Goals

1. 用真实交易时段与非交易时段场景，把后续功能开发锚定到固定的 live acceptance 矩阵。
2. 证明操作者可以根据当前时段选择正确的正式入口，而不是临时猜测。
3. 证明 `c2609` 一手 live-send 和 `account / position / query snapshot` 只读路径能被清楚区分。
4. 证明失败场景可判定：到底是时间窗口问题、guardrail 问题，还是 CTP/实现问题。

## 当前执行优先级 / Current Priority

1. 先执行 A3：验证非交易时段 query snapshot 主路径。
2. 再执行 A6：确认空仓边界不会误判失败。
3. 再执行 A4：确认 offhours 误用交易语义会被明确阻断。
4. 只有在非交易路径稳定后，再回到 A1/A2 的交易时段路径。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. 交易时段 TD readiness preflight。
2. 交易时段 `c2609` 单笔 `1` 手的 live order development loop。
3. 非交易时段 `account / position / query snapshot` 的只读路径。
4. guardrail 越界与误用时段的失败语义。

### 不覆盖（Out of Scope）

1. 多合约、多手数、自动化策略下单。
2. 超过 `5` 手净持仓上限的任何开发动作。
3. mock、fake、历史日志替代真实 live acceptance。
4. 仓外配置与敏感值托管方案。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| 本地 real-account live config 已准备好 | 配置 | 是 | 是 | ☑ | 本地忽略文件 `cfgs/local/ctp.live.025292.local.json` 已存在，并已用于 U1 formal live smoke |
| CTP 当前可直连 | 环境 | 是 | 是 | ⬜ | 交易时段和非交易时段都依赖真实连接 |
| `c2609` 处于可交易时段 | 市场窗口 | 否 | 是 | ⬜ | A1/A2 必需 |
| 当前净持仓未达到或超过 `5` 手 | 风控 | 否 | 是 | ⬜ | A2 live-send 前必须人工确认 |
| `python scripts/check_topic_docs.py` 可通过 | 治理 | 是 | 是 | ☑ | 2026-04-11 已复验通过 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 正式验收必须优先遵守 sibling `plan.md` 的修改边界与脚本入口口径。
2. `pytest` 只能锁定 contract/function，不得替代 A1-A6 的正式 live acceptance。
3. A2 只有在 A1 preflight 通过、且人工确认当前净持仓未突破上限后才允许执行。
4. A4 明确要求非交易时段不能把 `--live-send` 当成“顺手试一下”的可接受路径。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 交易时段 TD preflight ready | 在交易时段使用从 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制出的本地 live config 运行 `python scripts/ctp_td_order_truth_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20` | TD readiness、session identity 与 order truth 观察链路正常 | 输出中 `ready=true`、`login_success=true`，且无无法归因的断连风暴 | `ready=false`、`login_success=false`、或只能得到模糊失败 | `./evidence_a1_trade_window_preflight.md` |
| A2 | Success 2: `c2609` 一手 live order dev loop 走通 | 在 A1 通过后，使用同一本地 live config 运行 `python scripts/ctp_order_lifecycle_smoke.py --config cfgs/local/ctp.live.025292.local.json --instrument c2609 --quantity 1 --side <BUY|SELL> --limit-price <best-level-1-price> --client-order-id <session-window-order-id> --live-send --timeout-seconds 20` | live-send 仅在 guardrails 允许时被武装，且能拿到明确的 order/trade 回报 | 输出中 `bootstrap_ready=true`、`mapped_submit_error=null`、`live_send_armed=true`、`matched_exec_count>0` | 下单成功与失败无法区分，或 guardrail 未生效，或命令触达 TD 后仍无可解释结果 | `./evidence_a2_trade_window_live_order.md` |
| A3 | Success 3: 非交易时段 query snapshot 走通 | 在非交易时段使用从 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制出的本地 live config 运行 `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | position/account snapshot 都可读，且只读路径闭合 | 输出中 `positions.query_code=0`、`positions.completed=true`、`account.query_code=0`、`account.completed=true`、`account.account_id` 可读 | 只读场景仍要求 live-send，或 query 成功/失败没有明确结构化结果 | `./evidence_a3_offhours_query_snapshot.md` |
| A4 | Failure 1: 非交易时段误用 live-send 被明确阻断 | 在非交易时段按 runbook 校验交易入口；若需要脚本验证，则运行 `python scripts/ctp_order_lifecycle_smoke.py --config cfgs/local/ctp.live.025292.local.json --instrument c2609 --quantity 1 --side <BUY|SELL> --limit-price <best-level-1-price> --client-order-id <offhours-should-block> --live-send --timeout-seconds 20` | runbook 或脚本必须明确阻断“非交易时段 live-send” | 有清晰的“当前仅允许只读路径/当前不在交易窗口”口径，且不会把失败伪装成实现 bug | 仍只能靠操作者自己记忆时段边界，或脚本把误用写成模糊连接错误 | `./evidence_a4_offhours_live_send_block.md` |
| A5 | Failure 2: guardrail 越界订单在触达 TD 前被拒绝 | 使用同一本地 live config 运行一个明显越界的 dry-run，例如 `python scripts/ctp_order_lifecycle_smoke.py --config cfgs/local/ctp.live.025292.local.json --instrument rb2610 --quantity 2 --side BUY --limit-price <test-price> --client-order-id <guardrail-violation> --timeout-seconds 20` | precheck 在本地明确拒绝错误 symbol/qty/position/rate，不应靠 TD 错误码兜底 | 输出中的 `error` 或失败语义明确指出 guardrail violation | 越界订单仍可进入 TD，或失败原因只能归结为外部错误 | `./evidence_a5_guardrail_violation.md` |
| A6 | Boundary 1: 空仓或无持仓不被误判成查询失败 | 使用同一本地 live config 运行 `python scripts/ctp_position_query_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | 即使 `no_positions=true`，也应区分“空仓”与“查询失败” | 输出中 `query_code=0`、`completed=true`，且 `no_positions=true` 时不被判成失败 | 空仓被误判为系统故障，导致非交易时段调试无法继续 | `./evidence_a6_empty_position_boundary.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | session-window runbook | `./runbook.md` | 当前 change 的正式运行手册 |
| 2 | 交易时段 preflight | `./evidence_a1_trade_window_preflight.md` | A1 的 ready/login/order truth 证据 |
| 3 | 交易时段 live order loop | `./evidence_a2_trade_window_live_order.md` | A2 的 live-send 结构化结果 |
| 4 | 非交易时段 query snapshot | `../20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening/evidence_a1_query_adapter_snapshot.md` | A3 由 sibling C3 留证 |
| 5 | 非交易时段误用 live-send 阻断 | `../20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening/evidence_a5_readonly_rejects_trade_semantics.md` | A4 由 sibling C3 留证 |
| 6 | guardrail 失败语义 | `./evidence_a5_guardrail_violation.md` | A5 的 precheck 拒绝证据 |
| 7 | 空仓边界 | `../20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening/evidence_a6_empty_positions_boundary.md` | A6 由 sibling C3 留证 |

## 七、未通过处理 / On Failure

1. 回到 `plan.md` 只修当前最小阻塞场景，不得同时改写多个场景口径。
2. 若失败来自真实环境缺口，必须记录为环境阻塞，不能改文档把失败写没。
3. 不得覆盖已经收集到的历史 live evidence。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | 文档已冻结，待执行 | 交易时段实际跑通 TD preflight | `python scripts/ctp_td_order_truth_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20` | `ready=true` 且 `login_success=true` | 交易时段、live config、CTP 连接 | `./evidence_a1_trade_window_preflight.md` |
| R2 | A2 | 文档已冻结，待执行 | 交易时段实际跑通 `c2609` 一手 live-send | `python scripts/ctp_order_lifecycle_smoke.py --config cfgs/local/ctp.live.025292.local.json --instrument c2609 --quantity 1 --side <BUY|SELL> --limit-price <best-level-1-price> --client-order-id <session-window-order-id> --live-send --timeout-seconds 20` | `live_send_armed=true` 且 `matched_exec_count>0` | A1 未过、净持仓未知、市场不可交易 | `./evidence_a2_trade_window_live_order.md` |
| R3 | A3 | 文档已冻结，待执行 | 非交易时段实际跑通 query snapshot | `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | positions/account 都闭合 | live config、CTP 连接 | `./evidence_a3_offhours_query_snapshot.md` |
| R4 | A4 | 文档已冻结，待执行 | 验证 offhours 误用 live-send 会被明确阻断 | 见 A4 | 有清楚阻断语义 | 当前脚本可能尚无时段感知逻辑 | `./evidence_a4_offhours_live_send_block.md` |
| R5 | A5 | 文档已冻结，待执行 | 验证 guardrail violation 在本地被拒绝 | 见 A5 | 明确 violation 信息，且不触达 TD | 需确认现有 precheck 输出足够清楚 | `./evidence_a5_guardrail_violation.md` |
| R6 | A6 | 文档已冻结，待执行 | 验证空仓边界不会误判失败 | `python scripts/ctp_position_query_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | `query_code=0` 且 `no_positions` 可接受 | live config、CTP 连接 | `./evidence_a6_empty_position_boundary.md` |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Governance 锁定 | `python scripts/check_topic_docs.py` | 锁定 topic queue 与 current state 不漂移 |
| Function 锁定 | `python -m pytest` | 仅在实现阶段用于锁定 scripts/adapter 行为，不替代正式 live 验收 |

## 十一、当前自动推进结果 / Current Autopilot Result

1. 已正式落下 `runbook.md`，把当前 topic 的决策树固定成三条路径：`offhours read-only`、`vendor-bridge handoff`、`trade-window live order`。
2. 已明确：当前机器若继续出现 `WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`，当前 active lane 就是 U1 blocked handoff，不再回退到 C3，也不再继续围绕 auth/front/credential 调参。
3. 已明确：offhours 路径的正式入口和结构化失败语义由 sibling C3 负责，当前 C1 只做 session-window 路由与 handoff，不再重复扩脚本。
4. 当前剩余阻塞集中在交易时段 A1/A2/A5，需要 U1 ready 与真实交易窗口配合；因此当前 change 继续保持 `blocked/in_progress` 的 runbook 收口阶段。

## 十二、最终结论 / Final Verdict

- **结论**：🟨 blocked
- **日期**：2026-04-11
- **执行人**：GitHub Copilot
- **建议**：暂不建议宣告通过
- **说明**：session-window 决策树和 Autopilot handoff 已冻结；其中 vendor-bridge lane 已从“下一批切换目标”升级为“当前 U1 active lane”。交易时段成功场景仍受 U1 readiness 与真实窗口条件阻塞。