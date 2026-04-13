---
change-id: "20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening"
dependencies:
  hard_blocking:
    - id: "20260403__position-account-query-baseline__nautilus-query-adapter-baseline"
      reason: "需要继承 position/account query 主线与正式脚本入口"
      expected_status: completed
    - id: "20260403__full-reconciliation-automation__reconciliation-snapshot-contract"
      reason: "需要继承 reconciliation summary 的正式 contract"
      expected_status: completed
    - id: "20260403__td-position-account-truth-merge__td-truth-merge-snapshot"
      reason: "需要继承 order truth + query baseline 的 merged read-only snapshot"
      expected_status: completed
  soft_dependency:
    - id: "20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook"
      reason: "C1 负责冻结 session-window 验收矩阵，本 change 负责优先推进其中的 offhours 路径"
      expected_status: in_progress
    - id: "20260403__live-ops-truth-snapshot__live-ops-policy-baseline"
      reason: "当前 active topic 已冻结 live ops truth 口径，本 change 不应重新定义 snapshot/disposition"
      expected_status: in_progress
  blocked_by: []
---

# Offhours Query Snapshot Hardening 开发计划

**状态**：blocked
**进度**：local live config prepared；runtime/compat pack synced into vendor/ctp/bin；A1/A2/A3/A4/A5 executed；`check_rust_gate.py` now surfaces vendor-bridge readiness；`ctp_query_adapter_smoke.py` 现支持在同一次 offhours 查询里可选聚合 `order_truth / reconciliation` 并导出 JSON evidence；同一套 `session-label / evidence-root / output-json` contract 已继续扩到相邻 snapshot/live-ops 入口，并已补齐到 `td_login`/MD leaf；当前剩余 blocker 已正式切入 U1 handoff
**日期**：2026-04-09
**更新日期**：2026-04-11
**范围**：`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`、当前 change 三件套、`docs/topics/live-session-order-query-hardening.md`
**topic-id**：live-session-order-query-hardening
**change-id**：20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把当前 topic 的开发优先级明确切到非交易功能，先推进 offhours 只读 query/snapshot/disposition 能力。
2. 用真实非交易场景验收驱动开发，而不是先补抽象接口。
3. 让操作者在非交易时段可以稳定执行 `instrument / account / position / reconciliation / truth-merge` 等只读路径，并拿到清晰的成功/失败语义。
4. 本 change 不做真实下单、撤单、改单，只服务于非交易时段的开发与验收。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-offhours-query-hardening
- capability_name: 非交易时段只读查询加固 / Offhours query snapshot hardening
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: 无
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_query_adapter_smoke.py ; /D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_reconciliation_snapshot_smoke.py ; /D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_td_merged_reconciliation_policy_smoke.py
- affects_long_term_rules: 是
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`、当前 change 三件套、当前 topic README。
2. 禁止修改：任何会触发真实交易副作用的 live-send 入口、仓外 live config、`vendor/`。
3. 当前正式入口优先使用：`scripts/ctp_query_adapter_smoke.py`、`scripts/ctp_position_query_smoke.py`、`scripts/ctp_account_query_smoke.py`、`scripts/ctp_reconciliation_snapshot_smoke.py`、`scripts/ctp_td_truth_merge_snapshot_smoke.py`、`scripts/ctp_td_merged_reconciliation_policy_smoke.py`。
4. AI 开始前必须阅读：C1 的 `acceptance.md` 与 `plan.md`、`src/nautilus_ctp_adapter/adapters/ctp/query_adapter.py`、`reconciliation.py`、`truth_merge.py`。
5. 改完后必须执行：`python scripts/check_rust_gate.py`、`python scripts/check_topic_docs.py`；若触及 `scripts/`、`src/` 或 `tests/`，再执行 `python -m pytest`。

## 四、背景与约束

1. 用户已明确要求“优先开发非交易功能”，因此本 change 的优先级高于 `C2 c2609 live order dev loop`。
2. 当前仓内已经有 `instrument / position / account` 等只读 query 与 reconciliation / truth merge baseline，但还缺少统一的 offhours-first runbook 与失败语义加固。
3. 本 change 必须继续使用真实 CTP 和真实账户配置路径，但不能把敏感配置写入仓库；本地配置应以 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 为模板，复制到忽略目录 `cfgs/local/ctp.live.025292.local.json` 后再填写真实值。
4. 空仓、无新增回报、历史 callback residue 都是正常会出现的真实边界，不应被粗暴判成脚本失败。

## 五、设计方案（可选）

1. 先沿用现有正式脚本入口，不引入新的 read-only CLI，除非现有入口无法判定成功/失败。
2. 先加固 `query -> reconciliation -> merged policy` 三层只读路径，再考虑是否需要把 `live_ops_snapshot` 纳入本 change。
3. 若当前失败语义不够清楚，优先补充结构化输出与明确 disposition，而不是增加更多脚本。

## 六、阶段划分（可选）

1. P1：冻结 offhours 场景矩阵与 evidence 路径。
2. P2：加固 `query adapter` 与 `position/account` 成功/边界语义。
3. P3：加固 `reconciliation snapshot` 与 `merged policy` 的 disposition 语义。
4. P4：回写 topic queue，确认 `C2` 延后、`C3` 优先。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结非交易时段真实验收场景 | 用户优先级 + topic C3 | 当前 change 三件套 | A1-A6 场景、命令、证据路径 | `python scripts/check_topic_docs.py` | topic README | 之后的 offhours 改动不再改口验收矩阵 | 已完成 |
| P2 | 加固 instrument/account/position/query snapshot 语义 | A1/A5/A6 | `scripts/ctp_instrument_query_smoke.py`、`scripts/ctp_query_adapter_smoke.py`、`scripts/ctp_position_query_smoke.py`、`scripts/ctp_account_query_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/query_adapter.py`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、`rust/ctp_py/`、`rust/ctp_runtime_core/`、`tests/` | 只读 query 成功/失败/空仓边界更清晰 | `python scripts/check_topic_docs.py`；必要时 `python -m pytest` | 当前 change | query 成功、空仓、断连三类状态可区分 | 进行中 |
| P3 | 加固 reconciliation / truth-merge / merged policy 语义 | A2/A3/A4 | `scripts/ctp_reconciliation_snapshot_smoke.py`、`scripts/ctp_td_truth_merge_snapshot_smoke.py`、`scripts/ctp_td_merged_reconciliation_policy_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py`、`src/nautilus_ctp_adapter/adapters/ctp/truth_merge.py`、`tests/` | 只读汇总快照与 disposition 输出更清晰 | `python scripts/check_topic_docs.py`；必要时 `python -m pytest` | 当前 change | 可以区分 clear / manual_review_required / boundary_required / evidence_only | 已完成（证据已冻结，真实 blocker 交接 U1） |
| P4 | 回写 topic queue 与 offhours-first 顺序 | 用户优先级 | 当前 topic README、当前 change | 优先级同步 | `python scripts/check_topic_docs.py` | topic README | topic 队列清楚声明 `C3` 先于 `C2` | 已完成 |

## 八、验证动作（可选）

```powershell
python scripts/check_rust_gate.py
python scripts/check_topic_docs.py
python -m pytest
```

正式 live 验收命令以 `acceptance.md` 为准，测试不替代真实只读验收。

## 九、完成定义（可选）

### 开发完成

1. offhours-first 场景矩阵已冻结。
2. 只读 query、reconciliation、merged policy 的成功/失败/边界口径已清楚。
3. 当前 topic 已显式把 `C3` 提升为下一优先级。

### 交付完成

1. `acceptance.md` 中阻塞场景通过。
2. 真实非交易时段 evidence 已写入当前 change bundle。
3. `C2` 交易时段功能开发可以基于更稳定的只读 snapshot/disposition 背景继续推进。

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

本次无长期规则增量；本 change 主要是按既有长期规则优先推进 offhours read-only 能力。

## 十一、回写与相关变更 / Write-back & Related Changes

1. 需要回写当前 topic README 的 child change 优先顺序与 first action。
2. 若执行中发现 `live_ops_snapshot` 也必须纳入 offhours-first 主线，再补 topic README，不在本 plan 预设扩大范围。

## 十二、阻塞项（可选）

1. `vendor/ctp/bin/` 已完成本地同步，不再是当前主阻塞。
2. 当前 A1/A2/A3 的 `login_failed` 输出已被进一步定位：直接探针 `run_live_td_readiness_smoke` 返回 `init/authenticate/login = -9000`，说明 formal pack 中的 `ctp_native.dll` 仍是 scaffold-only。
3. 当前机器未找到仓外 live `ctp_native.dll`，本地 `vnpy_ctp` 也只提供 `thost*api*_se.dll`，不提供 build.rs 需要的 CTP SDK 头文件与 `thost*_se.lib`；因此现在缺的是 live vendor bridge 来源，而不是 config 字段。
4. 当前已把该 blocker 正式前置到 `python scripts/check_rust_gate.py`：若 gate 输出 `WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`，则不应继续把后续 smoke 症状解释成 auth/front/credential 调参问题。

## 十三、进度记录（可选）

1. 2026-04-09：因用户明确要求“优先开发非交易功能”，创建 `C3` change bundle，作为当前 topic 的下一优先级执行单元。
2. 2026-04-09：已为 `ctp_query_adapter_smoke.py`、`ctp_position_query_smoke.py`、`ctp_account_query_smoke.py`、`ctp_reconciliation_snapshot_smoke.py`、`ctp_td_truth_merge_snapshot_smoke.py`、`ctp_td_merged_reconciliation_policy_smoke.py` 补齐结构化失败输出与 `success/failure_reason` 语义，并用 targeted pytest 锁定缺失配置与只读拒绝交易语义的行为。
3. 2026-04-09：已准备好本地 `cfgs/local/ctp.live.025292.local.json`，并确认当前真实阻塞转向本地 runtime pack 缺失；当时 `scripts/sync_ctp_native.py` 仍只支持硬编码 sample-project root，不能直接适配本机现状。
4. 2026-04-10：已确认当前 offhours 正式入口走的是 PyO3 `CtpTdLiveSession` 主线，而不是 managed `CTPProviderSwig.dll` 主线；`src/ctp_runtime/__init__.py` 只需要 `vendor/ctp/bin` 提供 `thost*api*_se.dll` 供 `_ctp_runtime` 解析 vendor 依赖。
5. 2026-04-10：已把 `scripts/sync_ctp_native.py` 改成支持 `runtime/compat/full` 三种 pack、`--repo-native-source` / `--ctp-api-source` / `--managed-source` split-source 输入，以及 `--scan-root` 自动发现；并在本机确认可用源至少包括仓内 `rust/target/*/ctp_native.dll` 与 `D:\wt\main\.venv\Lib\site-packages\vnpy_ctp\api\thost*api*_se.dll`。
6. 2026-04-10：已把 compat pack 正式同步到 `vendor/ctp/bin/`，来源为仓内 `rust/target/debug/ctp_native.dll` 与 `D:\wt\main\.venv\Lib\site-packages\vnpy_ctp\api\thost*api*_se.dll`。
7. 2026-04-10：已执行 A1/A2，输出表面上都收敛到 `login_failed`。
8. 2026-04-10：首次执行 A3 暴露 PyO3 `CtpTdLiveSession` 缺少 `set_exec_callback` 的本地桥接 bug；已修复 `rust/ctp_py/src/lib.rs` 中 TD callback 方法误挂到 `CtpMdLiveSession` 的问题，重建 editable install 后重新执行 A3，输出同样表现为 `account_missing/manual_review_required`。
9. 2026-04-10：进一步对 mainline `run_live_td_readiness_smoke` 做直接探针，确认当前真实根因是 `ctp_native.dll` 仍返回 `-9000 scaffold only; live vendor bridge not implemented`，见 `./evidence_20260410_td_mainline_scaffold_probe.md`。
10. 2026-04-10：已扩展 `python scripts/check_rust_gate.py`，使其在 cargo/build 通过之外，额外显式报告 `ctp_vendor_bridge-ready` 或 `ctp_vendor_bridge-scaffold-only sdk-not-found`；当前机器实测输出为 scaffold-only，见 `./evidence_20260410_rust_gate_vendor_bridge_readiness.md`。
11. 2026-04-10：已执行 A4/A5 的真实脚本级失败语义验收；A4 对缺失 `broker_id` 的 broken-config 副本返回结构化 `ValueError`，A5 对 `--live-send` 非法参数返回 argparse 拒绝，见 `./evidence_a4_query_failure_semantics.md` 与 `./evidence_a5_readonly_rejects_trade_semantics.md`。
12. 2026-04-10：已再次执行 `C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py tests/test_sync_ctp_native.py -q`、`C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe scripts/check_topic_docs.py` 与增强后的 `scripts/check_rust_gate.py`；结果分别为 `99 passed`、`SUMMARY topics=16 failures=0` 与 `WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`，说明代码回归已收敛，当前剩余阻塞仍是外部 live vendor bridge 条件。
13. 2026-04-10：按“非交易时间优先开发合约查询、持仓查询”的当前需求，已把 `scripts/ctp_instrument_query_smoke.py` 升级为与 position/account 同级的结构化只读入口：现在会输出 `baseline/success/failure_reason/requested_symbol/matched_symbols/exact_symbol_found`，并补齐 config-load 失败语义与 `instrument_missing` 回归测试。
14. 2026-04-10：已补 A6 根因修复而不是仅补文档：TD position callback 现在透传 `request_id/is_last`，vendor bridge 的空快照完成信号可以进入 Python 主线；`run_live_position_query_smoke()` 不再把“空仓 + is_last=true”误判成 timeout，并已补 execution-client 与 CLI 两层回归测试。
15. 2026-04-10：已把 `ctp_query_adapter_smoke.py` 扩成统一的 offhours 只读聚合入口：新增可选 `--instrument-symbol`，让一次运行即可同时返回 `instrument / position / account` 三类结构化结果，并用 targeted pytest 锁定成功与 `instrument_missing` 失败语义。
16. 2026-04-10：已把 `ctp_reconciliation_snapshot_smoke.py` 从“纯 summary 数字输出”升级成“query status + reconciliation disposition/findings”入口；现在非交易时段执行一次即可同时看到 `positions/account` 完整度、汇总指标，以及 `manual_review_required / evidence_only / clear` 等判断结果，并已用 targeted pytest 锁定成功与 `positions_incomplete` 失败语义。
17. 2026-04-10：已把 `ctp_td_truth_merge_snapshot_smoke.py` 从精简计数输出升级成完整 snapshot 入口：新增 `order_truth` codes/disposition、`positions` query 状态与 `account` query 状态，让 offhours 可直接判断是 callback residue、positions incomplete 还是 account 缺失，并已用 targeted pytest 锁定成功与 `positions_incomplete` 失败语义。
18. 2026-04-10：已把 `ctp_td_merged_reconciliation_policy_smoke.py` 升级成与前两条入口一致的 operator 级结构化输出：新增 `order_truth`/`positions`/`account` 三层上下文，以及 `manual_review_codes / boundary_codes / evidence_only_codes`，并已用 targeted pytest 锁定成功与 `positions_incomplete` 失败语义。
19. 2026-04-10：已把 `ctp_live_ops_snapshot_smoke.py` 从旧式摘要输出升级为结构化 operator 入口：现在会同时输出 `startup / md / td / reconciliation` 四层上下文、聚合 `disposition`、`findings` 以及 `success / failure_reason` 语义，并已用 targeted pytest 锁定成功与 `account_id_missing` 失败路径。
20. 2026-04-10：已把 `ctp_live_ops_policy_smoke.py` 与 `ctp_live_ops_evidence_matrix_smoke.py` 一并补齐为结构化 operator 入口：两者现在都统一输出 `baseline / success / failure_reason`，并对 `account_id_missing / symbol_missing / unexpected_disposition` 给出明确失败语义；对应 regression 已补入 `tests/test_smoke_import.py` 并通过 targeted pytest。
21. 2026-04-10：已继续把剩余 reconciliation / TD order truth 只读脚本补齐为统一 contract：`ctp_reconciliation_policy_smoke.py`、`ctp_reconciliation_evidence_smoke.py`、`ctp_td_order_truth_smoke.py`、`ctp_td_order_truth_evidence_matrix_smoke.py`、`ctp_td_merged_evidence_matrix_smoke.py` 现在都统一输出 `baseline / success / failure_reason`，并对 `findings_missing / finding_count_missing / bootstrap_not_ready / login_failed / settlement_not_confirmed / account_id_missing / unexpected_disposition` 等失败语义给出结构化结果；对应 11 条 targeted regression 已补入 `tests/test_smoke_import.py`，并通过 `11 passed, 114 deselected` 与 `python scripts/check_topic_docs.py` 的二次验证。
22. 2026-04-10：已把 startup/session/login/boundary 这一组 TD 只读脚本也收口到同一 contract：`ctp_startup_truth_smoke.py`、`ctp_startup_truth_evidence_matrix_smoke.py`、`ctp_session_rebuild_policy_smoke.py`、`ctp_td_historical_callback_boundary_smoke.py`、`ctp_td_login_smoke.py` 现在统一输出 `baseline / success / failure_reason`，并显式区分 `bootstrap_not_ready / login_failed / settlement_not_confirmed / account_id_missing / findings_missing / shared_bootstrap_not_ready / isolated_bootstrap_not_ready / login_response_missing / unexpected_disposition` 等失败语义；对应 targeted pytest 已新增 10 条回归并通过 `10 passed, 125 deselected`，topic docs 复验仍为 `SUMMARY topics=16 failures=0`。
23. 2026-04-10：已把 formal baseline 与 repo-only debug baseline 也补齐为结构化 operator contract：`ctp_nautilus_live_smoke.py` 现在统一输出 `baseline / success / failure_reason`，并显式区分 `md_bootstrap_not_started / md_login_failed / md_first_tick_missing / td_login_failed / td_settlement_not_confirmed`；`ctp_repo_debug_smoke.py` 现在也统一输出 `baseline / success / failure_reason`，并把 public scaffold 路径的 contract mismatch 与 internal symbol 缺失分开报告。对应 targeted pytest 已新增 4 条回归并通过 `6 passed, 133 deselected`（含现有 contract-lock），`python scripts/check_topic_docs.py` 复验仍为 `SUMMARY topics=16 failures=0`。
24. 2026-04-10：`check_rust_gate.py` 已补齐 runtime pack、SDK probe roots、repo-only probe 与 formal-live verdict 四类 operator 输出，后续进入 U1 handoff 时不再需要重复解释路径。
25. 2026-04-10：已把 `ctp_query_adapter_smoke.py` 扩成更强的 offhours 聚合入口：新增 `--include-order-truth` 与 `--observation-grace-seconds`，允许在一次非交易时段查询中同时拿到 `position / account / order_truth` 三层结构化结果，并对 `order_truth_manual_review_required` 给出明确失败语义；对应 targeted pytest 已新增 2 条回归并通过。
26. 2026-04-10：已继续把 `ctp_query_adapter_smoke.py` 扩成更完整的统一入口：新增 `--include-reconciliation` 与 `--output-json`，允许在同一次 offhours 查询中继续聚合 `reconciliation` 摘要/disposition/findings，并把整份 payload 稳定导出到 JSON evidence；对应 targeted pytest 已新增 3 条回归并通过，证据见 `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md`。
27. 2026-04-10：已继续把 `ctp_query_adapter_smoke.py` 扩成更接近 operator 单入口的聚合面：新增 `--include-merged-policy`，允许在同一次 offhours 查询中继续聚合 `truth_merge_adapter` 的 merged truth/reconciliation disposition，并对 `merged_policy_manual_review_required` 给出明确失败语义；对应 targeted pytest 已新增 2 条回归并通过，证据仍回写到 `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md`。
28. 2026-04-10：已把 `ctp_query_adapter_smoke.py` 的共享会话路径也贯通到统一入口：新增 `--flow-path`，并把 query / instrument / order-truth / merged-policy 四条 lane 固定到同一个 TD flow path；对应 targeted pytest 已新增 1 条回归并通过，证据仍回写到 `./evidence_20260410_query_adapter_aggregated_reconciliation_export_contract.md`。
29. 2026-04-10：已继续把 `ORDER / TRADE` 从 callback truth 里拆出一层独立只读摘要，并先接到 `ctp_query_adapter_smoke.py`：新增 `--include-order-trade-snapshot`，统一入口现在可以额外输出 `no_order_events / no_trade_events / historical_residue_* / current_session_*` 等语义，并对 `order_trade_snapshot_manual_review_required` 给出明确失败口径；对应 targeted pytest 已新增 2 条回归，并把共享 `--flow-path` 覆盖扩到该 lane。
30. 2026-04-10：已继续把统一入口的 session/evidence 命名也前置到 active C3：`ctp_query_adapter_smoke.py` 新增 `--session-label` 与 `--evidence-root`，现在可把 evidence 自动写到 `<evidence-root>/<session-label>/aggregated_query.json`，并冻结 `shared-flow / isolated-flow` 默认命名与 `output_json conflicts with evidence_root` 冲突语义；对应 targeted pytest 已新增 3 条回归并通过。
31. 2026-04-10：已把同一套 `session-label / evidence-root / output-json` contract 继续扩到 `ctp_reconciliation_snapshot_smoke.py` 与 `ctp_td_truth_merge_snapshot_smoke.py`，不再让 query 聚合入口独占这套命名规则；其中 truth-merge snapshot 还把该 contract 与现有 `--flow-path` 一起收口，保证 isolated TD flow 也能稳定落到 `<evidence-root>/<session-label>/...`。对应 targeted pytest 已新增 3 条回归并通过。
32. 2026-04-10：已把同一套 `session-label / evidence-root / output-json` contract 继续扩到 `ctp_live_ops_snapshot_smoke.py`，并让其按 `td_isolated / md / td / query / td_shared` 的 effective flow path 推导 `flow_mode` 与默认 session 命名；对应 targeted pytest 已新增 success/conflict 回归并通过，说明更上层 live ops snapshot 也已纳入统一 evidence namespace。
33. 2026-04-10：已把同一套 `session-label / evidence-root / output-json` contract 继续扩到 `ctp_live_ops_policy_smoke.py` 与 `ctp_live_ops_evidence_matrix_smoke.py`；两者现在也会输出 `flow_mode / session_label / export` 元数据并把 evidence 稳定落到 `<evidence-root>/<session-label>/...`，说明 live-ops 这一整组入口已基本对齐同一 evidence namespace。对应 targeted pytest 已新增 4 条 export/conflict 回归并通过。
34. 2026-04-10：已把同一套 `session-label / evidence-root / output-json` contract 继续扩到 `ctp_reconciliation_policy_smoke.py`、`ctp_reconciliation_evidence_smoke.py`、`ctp_td_merged_reconciliation_policy_smoke.py` 与 `ctp_td_merged_evidence_matrix_smoke.py`；其中 merged policy/evidence 两条脚本还把该 contract 与 `--flow-path` 一起收口，因此 reconciliation-only、merged truth/reconciliation 和 live-ops 三个支线现在都能稳定落到同一 session namespace。对应 targeted pytest 已新增 8 条 export/conflict 回归并通过。
35. 2026-04-10：已把同一套 `session-label / evidence-root / output-json` contract 继续扩到 `ctp_startup_truth_smoke.py`、`ctp_startup_truth_evidence_matrix_smoke.py`、`ctp_session_rebuild_policy_smoke.py`、`ctp_td_order_truth_smoke.py`、`ctp_td_order_truth_evidence_matrix_smoke.py` 与 `ctp_td_historical_callback_boundary_smoke.py`；其中 startup/session 比较脚本会基于 effective shared/isolated flow override 推导默认 session 命名，TD order/boundary 三条脚本则把该 contract 与 `--flow-path` 一起收口，因此 startup truth、session rebuild、TD order truth 与 historical callback boundary 现在都已纳入统一 evidence namespace。对应 targeted pytest 已新增 12 条 export/conflict 回归，并与原有 structured/failure 用例一起通过 `24 passed, 159 deselected`。
36. 2026-04-10：已把同一套 `session-label / evidence-root / output-json` contract 继续扩到 `ctp_md_startup_truth_smoke.py`、`ctp_md_restore_policy_smoke.py` 与 `ctp_md_truth_evidence_matrix_smoke.py`，并顺手把这三条旧式脚本补齐到统一 `baseline / success / failure_reason` operator contract；三者现在都会输出 `flow_mode / session_label / export` 元数据，并对 `bootstrap_not_ready / login_failed / subscribe_failed / first_tick_missing / restore_not_triggered / restore_not_succeeded / account_id_missing / symbol_missing / unexpected_disposition` 等失败语义给出结构化结果。对应 targeted pytest 已新增 success/failure/export/conflict 回归，并连同共享 config-load gate 一起通过 `13 passed, 182 deselected`。
37. 2026-04-10：已把同一套 `flow-path / session-label / evidence-root / output-json` contract 继续扩到 `ctp_instrument_query_smoke.py`、`ctp_position_query_smoke.py` 与 `ctp_account_query_smoke.py` 这三条核心只读 leaf 入口；它们现在也会输出 `flow_mode / session_label / export` 元数据，并允许把单脚本 evidence 稳定落到 `instrument_query.json / position_query.json / account_query.json`。对应 targeted pytest 已新增 6 条 export/conflict 回归并通过。
38. 2026-04-10：已把剩余三条旧式 MD 诊断入口 `ctp_md_login_smoke.py`、`ctp_live_data_client_bootstrap_smoke.py` 与 `ctp_marketdata_smoke.py` 也收口到同一套 `flow-path / session-label / evidence-root / output-json` contract，并统一输出 `baseline / success / failure_reason`、`flow_mode / session_label / export` 元数据；其中 `ctp_marketdata_smoke.py` 还冻结了 `instrument_not_loaded / symbol_not_selected / bootstrap_not_started / login_failed / subscribe_failed / first_tick_missing / unexpected_tick_symbol` 这些 operator 失败语义。对应 targeted pytest 已新增 6 条 export/conflict 回归，并把三条脚本纳入共享 config-load gate。
39. 2026-04-11：已把 `ctp_td_login_smoke.py` 也补齐到同一套 `flow-path / session-label / evidence-root / output-json` contract；它现在会稳定输出 `flow_path / flow_mode / session_label / export` 元数据，并允许把 TD login-only 诊断结果导出到 `td_login_smoke.json`，从而补齐 TD leaf 入口里最后一个未纳入统一 evidence namespace 的脚本。对应 targeted pytest 已新增 2 条 export/conflict 回归。