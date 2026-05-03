# Query Adapter 聚合 Reconciliation / Merged Policy 与导出 Contract 证据 / Contract Evidence

**日期**：2026-04-10
**更新日期**：2026-04-11
**change-id**：20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening

## 目的

1. 为 C3 active change 补充 `ctp_query_adapter_smoke.py` 在仓内可验证的聚合 contract 证据。
2. 证明统一 offhours 入口现在不仅能聚合 `position / account / instrument / order_truth`，还可以可选聚合 `reconciliation / merged policy`，并把这些 lane 固定到同一个 `flow_path` 下后稳定导出到 JSON 文件。
3. 证明统一 offhours 入口现在也能把 `ORDER / TRADE` 只读摘要从 callback truth 里单独抽成一层 operator payload，并冻结 `no_order_events / no_trade_events / historical_residue_*` 语义。
4. 证明统一 offhours 入口现在也能用 `session-label / evidence-root` 把 evidence 命名收进稳定命名空间，而不是只支持裸 `output-json`。
5. 证明相邻的 offhours snapshot / policy / evidence / live-ops 入口也已开始复用同一套命名/export contract，而不是只在 query 聚合入口生效。
6. 明确这份证据是 code-level acceptance support，不替代真实 live vendor bridge ready 之后的 A1/A2/A3 正式验收。

## 执行命令

```powershell
C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "test_query_adapter_smoke_rejects_live_send_argument or test_query_adapter_smoke_reports_optional_instrument_snapshot_as_structured_json or test_query_adapter_smoke_reports_instrument_missing_when_requested or test_query_adapter_smoke_reports_optional_order_truth_snapshot_as_structured_json or test_query_adapter_smoke_reports_optional_order_trade_snapshot_as_structured_json or test_query_adapter_smoke_reports_order_truth_manual_review_failure or test_query_adapter_smoke_reports_order_trade_snapshot_manual_review_failure or test_query_adapter_smoke_reports_optional_reconciliation_snapshot_and_exports_json or test_query_adapter_smoke_reports_reconciliation_manual_review_failure or test_query_adapter_smoke_reports_export_path_failure_semantics or test_query_adapter_smoke_writes_session_labeled_export_under_evidence_root or test_query_adapter_smoke_uses_stable_default_label_for_evidence_root or test_query_adapter_smoke_rejects_conflicting_output_json_and_evidence_root or test_query_adapter_smoke_reports_optional_merged_policy_snapshot_as_structured_json or test_query_adapter_smoke_reports_merged_policy_manual_review_failure or test_query_adapter_smoke_propagates_shared_flow_path_to_optional_lanes" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "test_reconciliation_snapshot_smoke_reports_disposition_and_findings or test_reconciliation_snapshot_smoke_reports_positions_incomplete_failure or test_reconciliation_snapshot_smoke_writes_session_labeled_export or test_reconciliation_snapshot_smoke_rejects_conflicting_export_targets or test_td_truth_merge_snapshot_smoke_reports_structured_snapshot or test_td_truth_merge_snapshot_smoke_reports_positions_incomplete_failure or test_td_truth_merge_snapshot_smoke_writes_isolated_flow_export" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "test_live_ops_snapshot_smoke_writes_session_labeled_export or test_live_ops_snapshot_smoke_rejects_conflicting_export_targets or test_live_ops_snapshot_smoke_reports_account_id_missing_failure" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "test_live_ops_policy_smoke_reports_structured_result or test_live_ops_policy_smoke_reports_account_id_missing_failure or test_live_ops_policy_smoke_writes_session_labeled_export or test_live_ops_policy_smoke_rejects_conflicting_export_targets or test_live_ops_evidence_matrix_smoke_reports_structured_result or test_live_ops_evidence_matrix_smoke_reports_account_id_missing_failure or test_live_ops_evidence_matrix_smoke_writes_session_labeled_export or test_live_ops_evidence_matrix_smoke_rejects_conflicting_export_targets" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "test_reconciliation_policy_smoke_writes_session_labeled_export or test_reconciliation_policy_smoke_rejects_conflicting_export_targets or test_reconciliation_evidence_smoke_writes_session_labeled_export or test_reconciliation_evidence_smoke_rejects_conflicting_export_targets or test_td_merged_reconciliation_policy_smoke_writes_isolated_flow_export or test_td_merged_reconciliation_policy_smoke_rejects_conflicting_export_targets or test_td_merged_evidence_matrix_smoke_writes_isolated_flow_export or test_td_merged_evidence_matrix_smoke_rejects_conflicting_export_targets" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "td_order_truth_smoke or td_order_truth_evidence_matrix_smoke or startup_truth_smoke or startup_truth_evidence_matrix_smoke or session_rebuild_policy_smoke or td_historical_callback_boundary_smoke" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "read_only_smokes_report_structured_config_load_failure or md_startup_truth_smoke or md_restore_policy_smoke or md_truth_evidence_matrix_smoke" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "instrument_query_smoke_writes_isolated_flow_export or instrument_query_smoke_rejects_conflicting_export_targets or position_query_smoke_writes_session_labeled_export or position_query_smoke_rejects_conflicting_export_targets or account_query_smoke_writes_isolated_flow_export or account_query_smoke_rejects_conflicting_export_targets" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe scripts/check_topic_docs.py --root .

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "test_read_only_smokes_report_structured_config_load_failure or test_md_login_smoke_writes_isolated_flow_export or test_md_login_smoke_rejects_conflicting_export_targets or test_live_data_client_bootstrap_smoke_writes_session_labeled_export or test_live_data_client_bootstrap_smoke_rejects_conflicting_export_targets or test_marketdata_smoke_writes_session_labeled_export or test_marketdata_smoke_rejects_conflicting_export_targets" -q

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe scripts/check_topic_governance.py --root .

$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe scripts/check_rust_gate.py

C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe -m pytest tests/test_smoke_import.py -k "test_td_login_smoke_writes_isolated_flow_export or test_td_login_smoke_rejects_conflicting_export_targets" -q
```

## 结果摘要

1. 定向 pytest 结果：`16 passed, 138 deselected in 0.54s`。
2. 相邻 snapshot 脚本命名/export 回归结果：`10 passed, 147 deselected in 0.43s`。
3. live ops snapshot 命名/export 回归结果：`3 passed, 156 deselected in 0.42s`。
4. live ops policy/evidence 命名/export 回归结果：`8 passed, 155 deselected in 0.44s`。
5. reconciliation / merged policy / merged evidence 命名/export 回归结果：`8 passed, 163 deselected in 0.50s`。
6. startup/session/order-truth/boundary 命名/export 与原有 structured/failure 回归结果：`24 passed, 159 deselected in 0.53s`。
7. MD startup/restore/evidence 命名/export 与 operator contract 回归结果：`13 passed, 182 deselected in 2.83s`。
8. instrument/position/account leaf 入口命名/export 回归结果：`6 passed, 195 deselected in 0.53s`。
9. 剩余 MD diagnostics-only leaf 入口命名/export 回归结果：`7 passed, 200 deselected in 2.62s`。
10. `td_login_smoke` 命名/export 回归结果：`2 passed, 207 deselected in 0.54s`。
11. `check_topic_docs.py` 结果：`SUMMARY topics=16 failures=0`。
12. `check_topic_governance.py` 结果：`TOPIC_GOVERNANCE_CHECK_OK: index=docs/topics/README.md topics=16 active_topic=live-session-order-query-hardening active_change=20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening`。
13. `check_rust_gate.py` 在补齐 `C:\Users\Administrator\.cargo\bin` 到 PATH 后通过；当前正式口径仍是 `WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`，说明本轮改动没有改变 live vendor bridge blocker，只验证了 repo-level gate 仍稳定。
14. 本轮新增 contract 锁定了十一类新增语义：
   - `--include-reconciliation` 会把 `reconciliation` 摘要、disposition、findings 与 evidence 字段并入同一次 offhours payload。
   - `--include-order-trade-snapshot` 会把 `ORDER / TRADE` 的只读摘要独立并入同一次 offhours payload，并显式输出 `no_order_events / no_trade_events / historical_residue_* / current_session_*`。
   - `--include-merged-policy` 会把 merged truth/reconciliation disposition、order-truth context、positions/account query 状态与 findings 并入同一次 offhours payload。
   - `--flow-path <dir>` 会把 query / instrument / order-truth / order-trade-snapshot / merged-policy lane 固定到同一个共享 TD flow path。
   - `--session-label <label>` 与 `--evidence-root <dir>` 会把 evidence 自动写到 `<evidence-root>/<session-label>/aggregated_query.json`，并把 `session_label / flow_mode / export` 元数据并入 payload。
   - 未传 `--session-label` 时，默认命名稳定为 `shared-flow` 或 `isolated-flow`；误同时传 `--output-json` 与 `--evidence-root` 时，会返回 `argument_validation` 冲突语义。
   - `ctp_instrument_query_smoke.py`、`ctp_position_query_smoke.py`、`ctp_account_query_smoke.py`、`ctp_reconciliation_snapshot_smoke.py`、`ctp_reconciliation_policy_smoke.py`、`ctp_reconciliation_evidence_smoke.py`、`ctp_td_login_smoke.py`、`ctp_td_truth_merge_snapshot_smoke.py`、`ctp_td_merged_reconciliation_policy_smoke.py`、`ctp_td_merged_evidence_matrix_smoke.py`、`ctp_live_ops_snapshot_smoke.py`、`ctp_live_ops_policy_smoke.py`、`ctp_live_ops_evidence_matrix_smoke.py`、`ctp_startup_truth_smoke.py`、`ctp_startup_truth_evidence_matrix_smoke.py`、`ctp_session_rebuild_policy_smoke.py`、`ctp_td_order_truth_smoke.py`、`ctp_td_order_truth_evidence_matrix_smoke.py`、`ctp_td_historical_callback_boundary_smoke.py`、`ctp_md_startup_truth_smoke.py`、`ctp_md_restore_policy_smoke.py` 与 `ctp_md_truth_evidence_matrix_smoke.py` 现在也复用了同一套命名/export 规则，不再产生脚本间割裂的 evidence 命名口径。
   - `--output-json <path>` 会把聚合 payload 以 UTF-8 JSON 稳定落盘。
   - 当 reconciliation lane 达到 `manual_review_required` 时，统一入口会返回明确失败语义 `reconciliation_manual_review_required`。
   - 当 order/trade snapshot lane 达到 `manual_review_required` 时，统一入口会返回明确失败语义 `order_trade_snapshot_manual_review_required`。
   - 当 merged policy lane 达到 `manual_review_required` 时，统一入口会返回明确失败语义 `merged_policy_manual_review_required`。
   - `ctp_md_startup_truth_smoke.py`、`ctp_md_restore_policy_smoke.py` 与 `ctp_md_truth_evidence_matrix_smoke.py` 现在也统一输出 `baseline / success / failure_reason`，并把 `bootstrap_not_ready / login_failed / subscribe_failed / first_tick_missing / restore_not_triggered / restore_not_succeeded / account_id_missing / symbol_missing / unexpected_disposition` 这类 MD 失败语义冻结成结构化 contract，而不再只靠 exit code 判断。
   - `ctp_md_login_smoke.py`、`ctp_live_data_client_bootstrap_smoke.py` 与 `ctp_marketdata_smoke.py` 这三条剩余 MD diagnostics-only leaf 入口现在也统一支持 `--flow-path / --session-label / --evidence-root / --output-json`，并冻结 `md-login-smoke-v1`、`live-data-client-bootstrap-smoke-v1` 与 `marketdata-smoke-v1` baseline，以及对应 `login_failed / subscribe_failed / first_tick_missing / instrument_missing / bootstrap_not_started / connect_request_missing / subscribe_requests_missing / unexpected_tick_symbol` 失败语义。
   - `ctp_td_login_smoke.py` 现在也统一支持 `--flow-path / --session-label / --evidence-root / --output-json`，并把 TD login-only 诊断结果稳定落到 `td_login_smoke.json`；对应 `shared-flow / isolated-flow` 默认命名与 `output_json conflicts with evidence_root` 冲突语义也已用脚本级回归冻结。

## 结论

1. C3 的统一 offhours 查询入口已进一步接近 operator 级验收入口。
2. 当前剩余 blocker 仍是正式 live vendor bridge 未 ready；这份证据不宣告 A1/A2/A3 通过，只证明脚本 contract 与导出语义已冻结。