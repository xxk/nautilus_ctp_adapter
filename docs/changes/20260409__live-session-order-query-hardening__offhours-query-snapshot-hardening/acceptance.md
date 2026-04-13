# Offhours Query Snapshot Hardening 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：🟨 已执行（in_progress / blocked）
**日期**：2026-04-09
**更新日期**：2026-04-11
**范围**：非交易时段 `instrument / query / reconciliation / truth-merge` 只读能力与失败语义加固
**change-id**：20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: blocked
allow_declare_pass: false
last_updated: "2026-04-10 00:00"
concluded_by: "GitHub Copilot"

exit_conditions:
  E1_success_scenarios: failed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: false, blocking: true }
  A2: { exec: true, result: false, blocking: true }
  A3: { exec: true, result: false, blocking: true }
  A4: { exec: true, result: true, blocking: true }
  A5: { exec: true, result: true, blocking: true }
  A6: { exec: false, result: null, blocking: true }
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
| E2 | 关键失败场景符合预期 | ✅ | A4/A5 阻塞失败场景全部 ✅ | 当前 change 证据文件 |
| E3 | 必跑验证命令已完成 | ✅ | 已执行 `python scripts/check_rust_gate.py`、`python scripts/check_topic_docs.py` 与 `python -m pytest -q` | 当前 change 证据文件 |
| E4 | 关键证据已留存 | ✅ | A1-A5 evidence 已回写，A6 已补 code-level contract evidence 与 blocked note | 当前 change 证据文件 |
| E5 | 正式验收不依赖 mock 或 test | ✅ | A1/A2/A3 使用真实本地 live config 与真实 CTP 登录路径 | 当前 change 证据文件 |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 已冻结，无需豁免 | 当前文档 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: query adapter 只读快照走通 | ✅ | ❌ | 是 | 真实执行拿到 `login_failed -> positions_query_failed`；后续 direct probe 证明更根原因是 `ctp_native.dll` scaffold-only；见 `./evidence_a1_query_adapter_snapshot.md`、`./evidence_20260410_td_mainline_scaffold_probe.md` |
| A2 | Success 2: reconciliation snapshot 走通 | ✅ | ❌ | 是 | 真实执行拿到 `login_failed -> account_id_missing`；后续 direct probe 证明更根原因是 `ctp_native.dll` scaffold-only；见 `./evidence_a2_reconciliation_snapshot.md`、`./evidence_20260410_td_mainline_scaffold_probe.md` |
| A3 | Success 3: merged reconciliation policy 给出结构化 disposition | ✅ | ❌ | 是 | 首次执行暴露本地 PyO3 TD callback bug，修复并重建后已进入真实路径；当前结果为 `manual_review_required + account_missing`，但 direct probe 证明主 blocker 仍是 scaffold-only `ctp_native.dll`；见 `./evidence_a3_merged_policy.md`、`./evidence_20260410_td_mainline_scaffold_probe.md` |
| A4 | Failure 1: query 路径异常时有清晰失败语义 | ✅ | ✅ | 是 | 使用本地未跟踪 broken-config 副本执行后，脚本返回结构化 JSON：`failure_reason=exception`、`error_type=ValueError`、`error_message=missing config fields: ['broker_id']`；见 `./evidence_a4_query_failure_semantics.md` |
| A5 | Failure 2: 只读路径不会接受交易语义或误导为 live-send | ✅ | ✅ | 是 | `ctp_query_adapter_smoke.py --live-send` 直接被 argparse 拒绝为 `unrecognized arguments: --live-send`；见 `./evidence_a5_readonly_rejects_trade_semantics.md` |
| A6 | Boundary 1: 空仓不等于查询失败 | ⬜ | ⬜ | 是 | 代码 contract 已补齐；真实 live evidence 仍受 scaffold-only `ctp_native.dll` 阻塞 |

## 一、验收目标 / Goals

1. 在非交易时段优先跑通只读 query / snapshot / merged policy 主线。
2. 证明操作者不需要交易窗口，也能稳定推进账户、持仓、汇总快照相关开发。
3. 证明脚本输出能清楚区分成功、环境失败、边界状态和只读误用。
4. 为后续交易时段 `C2` 提供更可靠的 live state 背景。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `instrument / account / position` 只读查询。
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
| 本地 real-account live config 已准备好 | 配置 | 是 | 是 | ✅ | 从 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制到忽略目录 `cfgs/local/ctp.live.025292.local.json`，并填写真实 `Password/AuthCode/front/native path` |
| CTP 当前可直连 | 环境 | 是 | 是 | ❌ | 当前 direct probe 返回 `-9000 scaffold only`，说明 live vendor bridge 尚未接通 |
| 当前操作窗口属于非交易时段或明确只执行只读路径 | 流程 | 否 | 是 | ⬜ | 避免误把 C2 live-send 混入本 change |
| `python scripts/check_topic_docs.py` 可通过 | 治理 | 是 | 是 | ✅ | 当前文档修改后的最低门禁 |

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
| 7 | TD mainline scaffold probe | `./evidence_20260410_td_mainline_scaffold_probe.md` | 证明当前 mainline blocker 是 scaffold-only `ctp_native.dll`，不是单纯 config 问题 |
| 8 | Rust gate vendor bridge readiness | `./evidence_20260410_rust_gate_vendor_bridge_readiness.md` | 证明正式 Rust gate 已能前置报告 `ctp_vendor_bridge-scaffold-only` / `ctp_vendor_bridge-ready` |
| 9 | Query adapter aggregated reconciliation/export contract | `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md` | 证明统一 offhours 入口已支持 `reconciliation` 聚合与 JSON evidence 导出 |

## 七、未通过处理 / On Failure

1. 回到 `plan.md` 只修当前阻塞场景，不同时扩大多条 read-only 路径。
2. 若失败来自真实环境或 broken-config 副本，不得修改文档掩盖环境问题。
3. 不得把任意只读脚本失败解释成“以后交易时段再说”的理由；本 change 就是为了先把 offhours 做稳。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | 已执行，blocked | 在 live vendor bridge / SDK-backed build 条件补齐后重新验证 query adapter snapshot | `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | positions/account 都闭合 | 当前 gate 与 direct probe 都指向 scaffold-only `ctp_native.dll` | `./evidence_a1_query_adapter_snapshot.md` |
| R2 | A2 | 已执行，blocked | 在 live vendor bridge / SDK-backed build 条件补齐后重新验证 reconciliation snapshot | `python scripts/ctp_reconciliation_snapshot_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | `account_id` 与 summary 指标可读 | 当前 gate 与 direct probe 都指向 scaffold-only `ctp_native.dll` | `./evidence_a2_reconciliation_snapshot.md` |
| R3 | A3 | 已执行，blocked | 在 live vendor bridge / SDK-backed build 条件补齐后重新验证 merged policy | `python scripts/ctp_td_merged_reconciliation_policy_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0 --observation-grace-seconds 1.5` | disposition/findings 结构化可读 | 当前 gate 与 direct probe 都指向 scaffold-only `ctp_native.dll` | `./evidence_a3_merged_policy.md` |
| R4 | A4 | 已执行，passed | 无 | `python scripts/ctp_query_adapter_smoke.py --config <broken-config> --timeout-seconds 20 --completion-grace-seconds 1.0` | 结构化 `ValueError` + 缺字段信息 | 无 | `./evidence_a4_query_failure_semantics.md` |
| R5 | A5 | 已执行，passed | 无 | `python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --live-send` | argparse 明确拒绝非法交易语义 | 无 | `./evidence_a5_readonly_rejects_trade_semantics.md` |
| R6 | A6 | 文档已冻结，待执行 | 在 live vendor bridge ready 后验证空仓边界 | `python scripts/ctp_position_query_smoke.py --config cfgs/local/ctp.live.025292.local.json --timeout-seconds 20 --completion-grace-seconds 1.0` | `query_code=0`、`completed=true` 且 `no_positions=true` 不被判成失败 | 当前 gate 与 direct probe 都指向 scaffold-only `ctp_native.dll` | `./evidence_a6_empty_positions_boundary.md` |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Governance 锁定 | `python scripts/check_topic_docs.py` | 锁定当前 topic queue 的 offhours-first 状态 |
| Rust readiness 锁定 | `python scripts/check_rust_gate.py` | 在进入 A1/A2/A3 前先确认当前是 `ctp_vendor_bridge-ready` 还是 `scaffold-only` |
| Function 锁定 | `python -m pytest` | 仅在实现阶段锁定脚本/adapter 行为，不替代真实只读验收 |

## 十一、当前自动推进结果 / Current Autopilot Result

1. 已完成本地 real-account config 准备：[cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 已复制为忽略文件 `cfgs/local/ctp.live.025292.local.json`，并填入真实连接参数。
2. 已完成代码层加固：`instrument / position / account / reconciliation / merged-policy / live-ops-snapshot / live-ops-policy / live-ops-evidence-matrix` 只读 smoke 脚本现在会在失败时输出结构化 JSON，并显式给出 `success/failure_reason`。
3. 已把 `ctp_instrument_query_smoke.py` 对齐到与 position/account 同级的只读 contract：新增 `baseline`、`requested_symbol`、`matched_symbols`、`exact_symbol_found` 与 `instrument_missing / instrument_symbol_mismatch / instrument_query_incomplete` 语义。
4. 当前主阻塞不再是配置字段，也不再是 `vendor/ctp/bin` 缺少基础 DLL：compat pack 已正式同步到 `vendor/ctp/bin`，但 current `ctp_native.dll` 仍是 scaffold-only。
5. 已完成 contract/function 锁定：

```powershell
python scripts/check_topic_docs.py
.\.venv\Scripts\python.exe -m pytest tests/test_smoke_import.py -k "read_only_smokes_report_structured_config_load_failure or query_adapter_smoke_rejects_live_send_argument" -q
```

6. 已完成 runtime pack tooling 侧验证：`scripts/sync_ctp_native.py` 现已支持 `runtime/compat/full` pack 与 split-source/scan-root 发现，且 compat pack 已正式同步到 `vendor/ctp/bin`。
7. 已完成 A1/A2/A3 真实执行：三条路径都不再卡在基础 DLL 缺失；A3 的 PyO3 TD callback 暴露错误也已修复。
8. 已完成 direct TD mainline probe：当前 `run_live_td_readiness_smoke` 直接返回 `init/authenticate/login = -9000`、`login_error_message = repo-owned ctp_native scaffold only; live vendor bridge not implemented`，说明当前 formal blocker 是缺 live vendor bridge，而不是单纯 config 调参。
9. 已完成 `python scripts/check_rust_gate.py` 增强：正式 gate 现在会显式输出 `ctp_vendor_bridge-ready` 或 `WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`；当前机器实测为 scaffold-only，可在进入 A1/A2/A3 前直接挡住错误方向的排查。
10. 已完成 A4/A5 真实脚本级失败语义验收：A4 的 broken-config 副本返回结构化 `ValueError`，A5 的 `--live-send` 参数被 argparse 直接拒绝。
11. 已补 A6 的代码级 contract 锁定：TD position callback 现在透传 `request_id/is_last`，空仓完成不会再因为缺少 position payload 被误判成 timeout；同时新增了 execution-client 与 CLI 两层回归测试。
12. A6 的正式 live evidence 仍未执行，因为当前 `check_rust_gate.py` 与 direct TD probe 都表明本机仍处于 scaffold-only `ctp_native.dll`，无法把真实非交易时段空仓结果与桥接缺失区分开。
13. 已把 `ctp_query_adapter_smoke.py` 扩成统一的 offhours 只读入口：在原有 `position/account` snapshot 基线之外，现支持可选 `--instrument-symbol`，可以在一次运行里同时拿到 `instrument / position / account` 结构化结果，并对 `instrument_missing / instrument_symbol_mismatch / instrument_query_incomplete` 给出明确失败语义。
14. 已把 `ctp_reconciliation_snapshot_smoke.py` 升级为更接近 operator 视角的只读摘要入口：除了 summary 指标外，现在还会输出 `positions/account` query 状态、`disposition`、`requires_manual_review`、`manual_review_codes` 与 `findings`，从而把“summary 可读”和“是否需要人工复核”区分开。
15. 已把 `ctp_td_truth_merge_snapshot_smoke.py` 补成更完整的 snapshot 入口：现在会同时输出 `order_truth` codes/disposition、`positions` query 状态、`account` query 状态，能直接区分 callback residue、query 不完整与 account 缺失等 offhours 只读边界。
16. 已把 `ctp_td_merged_reconciliation_policy_smoke.py` 也补齐为 operator 级结构化入口：现在会同时输出 `order_truth`、`positions`、`account` 三层上下文，以及 `manual_review_codes / boundary_codes / evidence_only_codes / findings`，从而把最终 disposition 与其来源边界一起暴露出来。
17. 已把 `ctp_live_ops_snapshot_smoke.py` 也补齐为结构化只读入口：现在会同时输出 `startup / md / td / reconciliation` 四层上下文、聚合后的 `disposition / findings`，以及 `account_id_missing / symbol_missing / unexpected_disposition` 等失败语义；对应 regression 已纳入 `tests/test_smoke_import.py`。
18. 已把 `ctp_live_ops_policy_smoke.py` 与 `ctp_live_ops_evidence_matrix_smoke.py` 也补齐为结构化 operator 入口：两者现在都统一输出 `baseline / success / failure_reason`，并把 `account_id_missing / symbol_missing / unexpected_disposition` 这类失败语义显式暴露给 operator；对应 regression 已纳入 `tests/test_smoke_import.py`。
19. 已把剩余 reconciliation / TD order truth 只读脚本全部对齐到同一 operator contract：`ctp_reconciliation_policy_smoke.py`、`ctp_reconciliation_evidence_smoke.py`、`ctp_td_order_truth_smoke.py`、`ctp_td_order_truth_evidence_matrix_smoke.py`、`ctp_td_merged_evidence_matrix_smoke.py` 现在也统一输出 `baseline / success / failure_reason`，并显式区分 `findings_missing / finding_count_missing / bootstrap_not_ready / login_failed / settlement_not_confirmed / account_id_missing / unexpected_disposition` 等失败语义；对应 targeted pytest 已新增 11 条回归并实测通过，`python scripts/check_topic_docs.py` 复验仍为 `SUMMARY topics=16 failures=0`。
20. 已把 startup/session/login/boundary 这一组 TD 只读入口也补齐为统一 operator contract：`ctp_startup_truth_smoke.py`、`ctp_startup_truth_evidence_matrix_smoke.py`、`ctp_session_rebuild_policy_smoke.py`、`ctp_td_historical_callback_boundary_smoke.py`、`ctp_td_login_smoke.py` 现在也统一输出 `baseline / success / failure_reason`，并显式区分 `bootstrap_not_ready / login_failed / settlement_not_confirmed / account_id_missing / findings_missing / shared_bootstrap_not_ready / isolated_bootstrap_not_ready / login_response_missing / unexpected_disposition` 等失败语义；对应 targeted pytest 已新增 10 条回归并实测通过，`python scripts/check_topic_docs.py` 复验仍为 `SUMMARY topics=16 failures=0`。
21. 已把 formal live baseline 与 repo-only debug baseline 也对齐到同一 operator contract：`ctp_nautilus_live_smoke.py` 现在统一输出 `baseline / success / failure_reason`，并显式区分 `md_bootstrap_not_started / md_login_failed / md_first_tick_missing / td_login_failed / td_settlement_not_confirmed`；`ctp_repo_debug_smoke.py` 现在也统一输出 `baseline / success / failure_reason`，并把 public scaffold 路径的 `scaffold_contract_mismatch` 与 `internal_md_live_session_missing` 分开报告。对应 targeted pytest 已新增 4 条回归并实测通过，同时保留现有 `repo_only_debug_smoke_contract_is_stable` 的 CONTRACT-LOCK 验证；`python scripts/check_topic_docs.py` 复验仍为 `SUMMARY topics=16 failures=0`。
22. `check_rust_gate.py` 已补齐 runtime pack、SDK probe roots、repo-only probe 与 formal-live verdict 四类 operator 输出，后续进入 U1 handoff 时不再需要重复解释路径。
23. `ctp_query_adapter_smoke.py` 现在支持 `--include-order-truth`，可以在同一次 offhours run 中聚合 `position / account / order_truth`；当额外的 order-truth lane 只达到 `manual_review_required` 时，会返回明确失败语义 `order_truth_manual_review_required`。
24. `ctp_query_adapter_smoke.py` 现在也支持 `--include-reconciliation` 与 `--output-json`，可以在同一次 offhours run 中继续聚合 `reconciliation` 摘要/disposition/findings，并把整份 payload 作为 UTF-8 JSON evidence 落到 `output/debug/...`；当 reconciliation lane 达到 `manual_review_required` 时，会返回明确失败语义 `reconciliation_manual_review_required`，对应 contract evidence 见 `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md`。
25. `ctp_query_adapter_smoke.py` 现在还支持 `--include-merged-policy`，可以在同一次 offhours run 中继续聚合 `truth_merge_adapter` 的 merged truth/reconciliation disposition、order-truth context 与 positions/account query 状态；当 merged lane 达到 `manual_review_required` 时，会返回明确失败语义 `merged_policy_manual_review_required`，对应 contract evidence 仍见 `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md`。
26. `ctp_query_adapter_smoke.py` 现在还支持 `--flow-path`，可以把 query / instrument / order-truth / merged-policy lane 绑定到同一个共享 TD flow path，从而避免同一次 offhours 聚合运行落到不同 session 上下文；对应 contract evidence 仍见 `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md`。
27. `ctp_query_adapter_smoke.py` 现在还支持 `--include-order-trade-snapshot`，可以在同一次 offhours run 中把 `ORDER / TRADE` 的只读摘要从 callback truth 里独立抽出来，额外输出 `no_order_events / no_trade_events / historical_residue_* / current_session_*` 等 operator 语义；当该 lane 连只读摘要都无法可信分类时，会返回明确失败语义 `order_trade_snapshot_manual_review_required`，对应 contract evidence 仍见 `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md`。
28. `ctp_query_adapter_smoke.py` 现在还支持 `--session-label` 与 `--evidence-root`，可以把同一次 offhours run 的 evidence 自动写到 `<evidence-root>/<session-label>/aggregated_query.json`，并在 payload 中显式输出 `session_label / flow_mode / export` 元数据；若误同时传入 `--output-json` 与 `--evidence-root`，会返回明确的 `argument_validation` 冲突语义，避免 evidence 命名被静默覆盖。
29. `ctp_reconciliation_snapshot_smoke.py` 与 `ctp_td_truth_merge_snapshot_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract；其中 truth-merge snapshot 还会把 `flow_path / flow_mode / session_label / export` 一起暴露给 operator，从而避免 isolated flow 运行的 evidence 覆盖到 shared-flow 结果。
30. `ctp_live_ops_snapshot_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract；它会从 `td_isolated / md / td / query / td_shared` 的 effective flow path 推导 `flow_mode` 与默认 session 命名，并把 live ops 聚合 evidence 稳定落到 `<evidence-root>/<session-label>/live_ops_snapshot.json`。
31. `ctp_live_ops_policy_smoke.py` 与 `ctp_live_ops_evidence_matrix_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract；因此 live-ops 的 snapshot / policy / evidence 三层入口现在都能在同一个 session namespace 下稳定导出证据，而不再只靠终端输出拼接结果。
32. `ctp_reconciliation_policy_smoke.py` 与 `ctp_reconciliation_evidence_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract；因此 reconciliation-only 的 disposition/evidence 两条入口也能稳定落到 `<evidence-root>/<session-label>/...`，不再只由 snapshot 聚合入口承载命名规则。
33. `ctp_td_merged_reconciliation_policy_smoke.py` 与 `ctp_td_merged_evidence_matrix_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract，并继续保留 `--flow-path` 对 isolated-flow 的显式表达；因此 merged truth/reconciliation 这一支线也已纳入统一 evidence namespace。
34. `ctp_startup_truth_smoke.py`、`ctp_startup_truth_evidence_matrix_smoke.py` 与 `ctp_session_rebuild_policy_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract；其中 startup/session 比较类脚本会按 effective shared/isolated flow override 推导默认 session 命名，因此 startup truth 与 session rebuild 这一支线也能稳定落到同一个 session namespace。
35. `ctp_td_order_truth_smoke.py`、`ctp_td_order_truth_evidence_matrix_smoke.py` 与 `ctp_td_historical_callback_boundary_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract，并继续保留 `--flow-path` 对 isolated-flow 的显式表达；因此 TD order truth / callback boundary 这一支线也已纳入统一 evidence namespace。对应 targeted pytest 已把这 6 条脚本的原有 structured/failure 回归与新增 export/conflict 回归一起跑通，结果为 `24 passed, 159 deselected`。
36. `ctp_md_startup_truth_smoke.py`、`ctp_md_restore_policy_smoke.py` 与 `ctp_md_truth_evidence_matrix_smoke.py` 现在也已对齐同一套 `--session-label / --evidence-root / --output-json` contract，并补齐到统一 `baseline / success / failure_reason` operator contract；因此 MD startup / restore / evidence 这一支线也已纳入统一 evidence namespace。对应 targeted pytest 已把 success/failure/export/conflict 回归与共享 config-load gate 一起跑通，结果为 `13 passed, 182 deselected`。
37. `ctp_instrument_query_smoke.py`、`ctp_position_query_smoke.py` 与 `ctp_account_query_smoke.py` 现在也已对齐同一套 `--flow-path / --session-label / --evidence-root / --output-json` contract；因此除了聚合入口和 evidence-bearing snapshot/policy/evidence 脚本之外，三条最常用的只读 leaf 入口也都能稳定落到统一 session namespace，并把 `instrument_query.json / position_query.json / account_query.json` 写成单脚本证据。
38. 截至当前回合，统一 `session-label / evidence-root / output-json` evidence contract 已覆盖 query、instrument、position、account、reconciliation、truth-merge、live-ops、startup/session、TD order/boundary、MD startup/restore/evidence 这些主要 offhours 入口；C3 在脚本参数面上的剩余工作已经进一步收敛，后续更适合把精力转向 runbook/topic rule 收口与少量非 evidence 产物入口的选择性清理。
39. `ctp_md_login_smoke.py`、`ctp_live_data_client_bootstrap_smoke.py` 与 `ctp_marketdata_smoke.py` 现在也已对齐同一套 `--flow-path / --session-label / --evidence-root / --output-json` contract，并统一输出 `baseline / success / failure_reason`；因此当前仓内剩余的 MD diagnostics-only leaf 入口也都已纳入同一个 offhours evidence namespace，而不再保留多行 print 或一脚本一口径的旧式输出。

## 十二、最终结论 / Final Verdict

- **结论**：🟨 blocked
- **日期**：2026-04-09
- **执行人**：GitHub Copilot
- **建议**：暂不建议宣告通过
- **说明**：代码层只读语义已继续加固，统一 `ctp_query_adapter_smoke.py` 入口现在已可聚合 `instrument / position / account / order_truth / order_trade_snapshot / reconciliation / merged policy`，并支持共享 `flow_path` 与 JSON evidence 导出；相邻的 `instrument / position / account` leaf 入口，以及 `reconciliation snapshot / policy / evidence`、`truth-merge snapshot / merged policy / merged evidence`、`live-ops snapshot / policy / evidence`、`startup truth / startup evidence / session rebuild policy`、`TD order truth / TD order evidence / historical callback boundary`、`MD startup truth / MD restore policy / MD truth evidence matrix` 这些支线入口也已对齐到同一套 `session-label / evidence-root / output-json` evidence contract。compat pack 已正式同步到 `vendor/ctp/bin`，A3 的本地桥接接口错误也已修复。direct TD mainline probe 与增强后的 `check_rust_gate.py` 现在都已明确证明当前 `ctp_native.dll` 仍是 scaffold-only。没有 live vendor bridge，就不能把当前 blocker 继续解释成 auth/front/credential 问题；当前 active C3 在主要 offhours 入口上的 contract 收口已基本完成，后续更适合把增量收敛到 runbook/topic rule 与少量剩余入口整理，再切入 U1 handoff。
- **说明**：代码层只读语义已继续加固，统一 `ctp_query_adapter_smoke.py` 入口现在已可聚合 `instrument / position / account / order_truth / order_trade_snapshot / reconciliation / merged policy`，并支持共享 `flow_path` 与 JSON evidence 导出；相邻的 `instrument / position / account` leaf 入口，以及 `reconciliation snapshot / policy / evidence`、`truth-merge snapshot / merged policy / merged evidence`、`live-ops snapshot / policy / evidence`、`startup truth / startup evidence / session rebuild policy`、`TD login-only leaf`、`TD order truth / TD order evidence / historical callback boundary`、`MD login / live data bootstrap / marketdata baseline`、`MD startup truth / MD restore policy / MD truth evidence matrix` 这些支线入口也已对齐到同一套 `session-label / evidence-root / output-json` evidence contract。compat pack 已正式同步到 `vendor/ctp/bin`，A3 的本地桥接接口错误也已修复。direct TD mainline probe 与增强后的 `check_rust_gate.py` 现在都已明确证明当前 `ctp_native.dll` 仍是 scaffold-only。没有 live vendor bridge，就不能把当前 blocker 继续解释成 auth/front/credential 问题；当前 active C3 在主要 offhours 入口上的 contract 收口已基本完成，后续更适合把增量收敛到 runbook/topic rule 与少量剩余入口整理，再切入 U1 handoff。