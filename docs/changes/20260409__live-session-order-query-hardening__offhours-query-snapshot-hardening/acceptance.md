# Offhours Query Snapshot Hardening 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-09
**范围**：非交易时段 `query / reconciliation / truth-merge` 只读能力与失败语义加固
**change-id**：20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-session-order-query-hardening/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-04-09 00:00"
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

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ⬜ 待执行 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 否 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-04-09 00:00 | |
| AI 执行人 | — | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ⬜ | A1/A2/A3 阻塞成功场景全部 ✅ | 当前 change 证据文件 |
| E2 | 关键失败场景符合预期 | ⬜ | A4/A5 阻塞失败场景全部 ✅ | 当前 change 证据文件 |
| E3 | 必跑验证命令已完成 | ⬜ | 至少执行 `python scripts/check_topic_docs.py`；若触及代码再执行 `python -m pytest` | 当前 change 证据文件 |
| E4 | 关键证据已留存 | ⬜ | query / reconciliation / merged policy / failure / boundary 至少各有一份 evidence | 当前 change 证据文件 |
| E5 | 正式验收不依赖 mock 或 test | ⬜ | 正式场景必须使用真实 CTP、真实账户、真实本地配置路径 | 当前 change 证据文件 |
| E6 | 正式场景数不少于 6 个 | ⬜ | A1-A6 已冻结，无需豁免 | 当前文档 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: query adapter 只读快照走通 | ⬜ | ⬜ | 是 | `ctp_query_adapter_smoke.py` |
| A2 | Success 2: reconciliation snapshot 走通 | ⬜ | ⬜ | 是 | `ctp_reconciliation_snapshot_smoke.py` |
| A3 | Success 3: merged reconciliation policy 给出结构化 disposition | ⬜ | ⬜ | 是 | `ctp_td_merged_reconciliation_policy_smoke.py` |
| A4 | Failure 1: query 路径异常时有清晰失败语义 | ⬜ | ⬜ | 是 | broken-config real-path variant |
| A5 | Failure 2: 只读路径不会接受交易语义或误导为 live-send | ⬜ | ⬜ | 是 | argparse / runbook / clear rejection |
| A6 | Boundary 1: 空仓不等于查询失败 | ⬜ | ⬜ | 否 | `ctp_position_query_smoke.py` |

## 一、验收目标 / Goals

1. 在非交易时段优先跑通只读 query / snapshot / merged policy 主线。
2. 证明操作者不需要交易窗口，也能稳定推进账户、持仓、汇总快照相关开发。
3. 证明脚本输出能清楚区分成功、环境失败、边界状态和只读误用。
4. 为后续交易时段 `C2` 提供更可靠的 live state 背景。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `account / position` 只读查询。
2. `query snapshot`、`reconciliation snapshot`、`merged reconciliation policy`。
3. 非交易时段误用交易语义的阻断或明确拒绝。
4. 空仓、无新增回报、历史 callback residue 等只读边界。

### 不覆盖（Out of Scope）

1. 任何真实下单、撤单、改单。
2. 交易时段 `c2609` live-send 验收。
3. 敏感配置托管或仓外运维流程。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| 本地 real-account live config 已准备好 | 配置 | 是 | 是 | ⬜ | 从 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制到忽略目录 `cfgs/local/ctp.live.025292.local.json`，并填写真实 `Password/AuthCode/front/native path` |
| CTP 当前可直连 | 环境 | 是 | 是 | ⬜ | 非交易时段只读验收依赖真实连接 |
| 当前操作窗口属于非交易时段或明确只执行只读路径 | 流程 | 否 | 是 | ⬜ | 避免误把 C2 live-send 混入本 change |
| `python scripts/check_topic_docs.py` 可通过 | 治理 | 是 | 是 | ⬜ | 当前文档修改后的最低门禁 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 正式验收必须走真实 CTP、真实账户、本地真实配置路径。
2. `pytest` 只能锁定脚本/adapter 行为，不替代 A1-A6 的正式只读验收。
3. 当前 change 不得因为“只是查询”而静默容忍不完整或不可判定结果；必须给出清晰结构化语义。
4. 若需要构造失败场景，只允许使用本地未跟踪的 broken-config 副本，不得把假配置提交进仓库。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: query adapter 只读快照走通 | 在非交易时段使用从 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制出的本地 live config 运行 `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | position/account snapshot 都闭合 | `positions.query_code=0`、`positions.completed=true`、`account.query_code=0`、`account.completed=true`、`account.account_id` 存在 | 输出缺少结构化字段，或结果不可判定 | `./evidence_a1_query_adapter_snapshot.md` |
| A2 | Success 2: reconciliation snapshot 走通 | 在非交易时段使用同一本地 live config 运行 `python scripts/ctp_reconciliation_snapshot_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | 账户与持仓汇总可读 | `account_id` 存在、`position_line_count>=0`、`account_balance` 可读 | 汇总结果无法区分“空仓”与“失败” | `./evidence_a2_reconciliation_snapshot.md` |
| A3 | Success 3: merged reconciliation policy 给出结构化 disposition | 在非交易时段使用同一本地 live config 运行 `python scripts/ctp_td_merged_reconciliation_policy_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0 --observation-grace-seconds 1.5` | 只读 merged policy 能输出结构化 findings/disposition | 输出中 `account_id` 存在，且 `disposition` 属于 `clear/manual_review_required/boundary_required/evidence_only` 之一 | 只读汇总没有结论字段，或 findings 无法解释当前状态 | `./evidence_a3_merged_policy.md` |
| A4 | Failure 1: query 路径异常时有清晰失败语义 | 使用从模板复制出的本地未跟踪 broken-config 副本运行 `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.broken.json --timeout-seconds 20 --completion-grace-seconds 1.0` | 脚本必须非 0 退出或给出明确超时/缺失字段语义 | 输出能区分连接失败、查询超时、账户缺失等失败类型 | 把失败静默写成成功，或只给出模糊异常 | `./evidence_a4_query_failure_semantics.md` |
| A5 | Failure 2: 只读路径不会接受交易语义或误导为 live-send | 运行 `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --live-send` 或按 runbook 验证 offhours 入口不提供 live-send | read-only 入口明确拒绝交易语义 | `argparse` 或 runbook 给出清晰拒绝口径 | 只读脚本看起来可以接受交易语义，导致操作者误用 | `./evidence_a5_readonly_rejects_trade_semantics.md` |
| A6 | Boundary 1: 空仓不等于查询失败 | 在非交易时段使用同一本地 live config 运行 `python scripts/ctp_position_query_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | `no_positions=true` 时仍可视为成功完成的查询 | `query_code=0`、`completed=true`；若 `no_positions=true`，不被判成失败 | 空仓被误判为异常，导致 offhours 开发被卡住 | `./evidence_a6_empty_positions_boundary.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | query adapter snapshot | `./evidence_a1_query_adapter_snapshot.md` | A1 的 position/account 只读快照 |
| 2 | reconciliation snapshot | `./evidence_a2_reconciliation_snapshot.md` | A2 的汇总快照 |
| 3 | merged policy | `./evidence_a3_merged_policy.md` | A3 的 findings/disposition 证据 |
| 4 | query failure semantics | `./evidence_a4_query_failure_semantics.md` | A4 的异常/超时语义证据 |
| 5 | read-only reject trade semantics | `./evidence_a5_readonly_rejects_trade_semantics.md` | A5 的拒绝语义证据 |
| 6 | empty positions boundary | `./evidence_a6_empty_positions_boundary.md` | A6 的空仓边界证据 |

## 七、未通过处理 / On Failure

1. 回到 `plan.md` 只修当前阻塞场景，不同时扩大多条 read-only 路径。
2. 若失败来自真实环境或 broken-config 副本，不得修改文档掩盖环境问题。
3. 不得把任意只读脚本失败解释成“以后交易时段再说”的理由；本 change 就是为了先把 offhours 做稳。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | 文档已冻结，待执行 | 非交易时段实际跑通 query adapter snapshot | `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | positions/account 都闭合 | live config、CTP 连接 | `./evidence_a1_query_adapter_snapshot.md` |
| R2 | A2 | 文档已冻结，待执行 | 非交易时段实际跑通 reconciliation snapshot | `python scripts/ctp_reconciliation_snapshot_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | `account_id` 与 summary 指标可读 | live config、CTP 连接 | `./evidence_a2_reconciliation_snapshot.md` |
| R3 | A3 | 文档已冻结，待执行 | 非交易时段实际跑通 merged policy | `python scripts/ctp_td_merged_reconciliation_policy_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0 --observation-grace-seconds 1.5` | disposition/findings 结构化可读 | live config、CTP 连接 | `./evidence_a3_merged_policy.md` |
| R4 | A4 | 文档已冻结，待执行 | 用 broken-config 副本验证 query failure semantics | `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.broken.json --timeout-seconds 20 --completion-grace-seconds 1.0` | 非 0 退出或清晰超时/缺失语义 | broken-config 副本未准备 | `./evidence_a4_query_failure_semantics.md` |
| R5 | A5 | 文档已冻结，待执行 | 验证只读路径拒绝交易语义 | 见 A5 | 明确拒绝口径 | 脚本输出是否足够清楚待验证 | `./evidence_a5_readonly_rejects_trade_semantics.md` |
| R6 | A6 | 文档已冻结，待执行 | 验证空仓边界 | `python scripts/ctp_position_query_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | `no_positions` 非失败 | live config、CTP 连接 | `./evidence_a6_empty_positions_boundary.md` |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Governance 锁定 | `python scripts/check_topic_docs.py` | 锁定当前 topic queue 的 offhours-first 状态 |
| Function 锁定 | `python -m pytest` | 仅在实现阶段锁定脚本/adapter 行为，不替代真实只读验收 |

## 十一、当前自动推进结果 / Current Autopilot Result

1. 已完成本地 real-account config 准备：[cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 已复制为忽略文件 `cfgs/local/ctp.live.025292.local.json`，并填入真实连接参数。
2. 已完成代码层加固：只读 smoke 脚本现在会在失败时输出结构化 JSON，并显式给出 `success/failure_reason`。
3. 当前主阻塞不再是配置字段，而是运行时 bootstrap pack 缺失：仓内 `vendor/ctp/` 只有 README，没有 `vendor/ctp/bin/`；当前机器上也未找到 `ctp_native.dll`、`CTPProviderSwig.dll` 或 `CTPProviderSwig.Core.dll`，所以真实 CTP smoke 仍无法进入 TD/MD。
4. 已完成 contract/function 锁定：

```powershell
python scripts/check_topic_docs.py
.\.venv\Scripts\python.exe -m pytest tests/test_smoke_import.py -k "read_only_smokes_report_structured_config_load_failure or query_adapter_smoke_rejects_live_send_argument" -q
```

## 十二、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：2026-04-09
- **执行人**：—
- **建议**：暂不建议宣告通过
- **说明**：代码层只读语义已加固，本地 real-account config 已准备好；当前真实 offhours live acceptance 阻塞在 `vendor/ctp/bin` bootstrap DLL 缺失，而不是配置字段。