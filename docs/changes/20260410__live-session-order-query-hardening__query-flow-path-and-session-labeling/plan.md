---
change-id: "20260410__live-session-order-query-hardening__query-flow-path-and-session-labeling"
dependencies:
  hard_blocking:
    - id: "20260410__live-session-order-query-hardening__aggregated-query-evidence-export"
      reason: "需要继承聚合入口与 evidence export 的正式参数面"
      expected_status: draft
  soft_dependency:
    - id: "20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract"
      reason: "若新增 order/trade 入口，应一起统一 session labeling 口径"
      expected_status: draft
  blocked_by: []
---

# Query Flow Path And Session Labeling 开发计划

**状态**：draft
**进度**：0%
**日期**：2026-04-10
**范围**：offhours 相关 `scripts/`、必要的 evidence 命名辅助、`tests/`、当前 change 三件套
**topic-id**：live-session-order-query-hardening
**change-id**：20260410__live-session-order-query-hardening__query-flow-path-and-session-labeling
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 统一 offhours 入口的 `flow-path`、`session-label`、`evidence-root` 参数与命名口径。
2. 让 operator 可以显式区分 shared flow、isolated flow 与同日多次 query session。
3. 让 evidence 文件名能反映 session，而不是互相覆盖。
4. 本 change 不新增新的业务查询能力，只做 flow/session 归属治理。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-query-flow-session-labeling
- capability_name: Query Flow Path And Session Labeling
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: offhours 脚本参数口径
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：相关 offhours 脚本参数、必要的 helper、`tests/`、当前 change 三件套。
2. 禁止修改：live-send 入口、真实交易逻辑、仓外 flow 文件。
3. 当前正式入口优先使用：`ctp_query_adapter_smoke.py`、`ctp_reconciliation_snapshot_smoke.py`、`ctp_td_truth_merge_snapshot_smoke.py`。
4. AI 开始前必须阅读：C5 `plan.md`、当前 topic runbook、现有 flow-path 参数脚本。
5. 改完后必须执行：`python scripts/check_topic_docs.py --root .` 与 targeted pytest。

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结参数命名与默认行为 | operator 使用痛点 | 当前 change、脚本 | `flow-path/session-label/evidence-root` contract | 文档自检 | `scripts/README.md` | 多入口参数语义一致 | 未开始 |
| P2 | 实现参数下沉与 evidence 命名 | 持续开发 backlog | 脚本、helper、`tests/` | 一致的 flow/session 命名 | targeted pytest | topic README | evidence 不再互相覆盖 | 未开始 |
| P3 | 回写导航与示例 | operator discoverability | 当前 change、`scripts/README.md` | 参数示例 | `python scripts/check_topic_docs.py --root .` | scripts/README | 使用方式清楚 | 未开始 |

## 五、长期规则增量摘要 / Long-Term Rule Delta Summary

本次预期新增长期规则：offhours 入口若涉及 flow/session/evidence 归属，必须采用统一的参数名与命名规则。

## 六、进度记录（可选）

1. 2026-04-10：创建 C7 change bundle，作为 offhours flow/session/evidence 命名统一的正式宿主。
2. 2026-04-10：active C3 已先在 `ctp_query_adapter_smoke.py` 落下第一批可复用 contract：新增 `--session-label`、`--evidence-root`、稳定默认命名 `shared-flow / isolated-flow`，以及 `output_json conflicts with evidence_root` 冲突语义；后续若切到 C7，应优先复用这套参数与命名规则扩到其他 offhours 入口，而不是重新发明口径。
3. 2026-04-10：同一套 contract 已继续扩到 `ctp_reconciliation_snapshot_smoke.py` 与 `ctp_td_truth_merge_snapshot_smoke.py`，并由 targeted pytest 锁定；后续若切到 C7，优先剩余目标应转向更多 snapshot/policy/evidence 脚本与 runbook，而不是重复定义参数名。
4. 2026-04-10：同一套 contract 已继续扩到 `ctp_live_ops_snapshot_smoke.py`；它会基于 effective flow path 推导 `flow_mode` 与默认 session 命名，说明 C7 后续更适合继续统一剩余 policy/evidence 入口与 runbook，而不是重新设计 snapshot 类脚本的 evidence namespace。
5. 2026-04-10：同一套 contract 已继续扩到 `ctp_live_ops_policy_smoke.py` 与 `ctp_live_ops_evidence_matrix_smoke.py`；这说明 C7 在 live-ops 这一支线上的主要重复工作已经被 active C3 提前吸收，后续更适合收口 runbook、topic 规则和剩余零散入口。
6. 2026-04-10：同一套 contract 已继续扩到 `ctp_reconciliation_policy_smoke.py`、`ctp_reconciliation_evidence_smoke.py`、`ctp_td_merged_reconciliation_policy_smoke.py` 与 `ctp_td_merged_evidence_matrix_smoke.py`；这说明 C7 在 reconciliation / merged truth 这两条支线上的主要脚本命名工作也已被 active C3 提前吸收，后续更适合把剩余工作集中在 runbook、topic 规则和少量漏网入口上。
7. 2026-04-10：同一套 contract 已继续扩到 `ctp_startup_truth_smoke.py`、`ctp_startup_truth_evidence_matrix_smoke.py`、`ctp_session_rebuild_policy_smoke.py`、`ctp_td_order_truth_smoke.py`、`ctp_td_order_truth_evidence_matrix_smoke.py` 与 `ctp_td_historical_callback_boundary_smoke.py`；这说明 C7 在 startup/session rebuild 与 TD order/boundary 这两条支线上的主要脚本命名工作也已被 active C3 提前吸收，后续更适合把剩余工作收敛到 MD 三条脚本、runbook 与 topic 规则，而不是重复改 TD/offhours 主线入口。
8. 2026-04-10：同一套 contract 已继续扩到 `ctp_md_startup_truth_smoke.py`、`ctp_md_restore_policy_smoke.py` 与 `ctp_md_truth_evidence_matrix_smoke.py`，并补齐为统一 `baseline / success / failure_reason` operator contract；这说明 C7 在主要 offhours evidence-bearing 脚本面上的参数/命名重复工作已经基本被 active C3 吸收，后续更适合把剩余工作收敛到 runbook、topic 规则、少量非 evidence 入口与是否保留独立 C7 的治理判断。
9. 2026-04-10：同一套 contract 已继续扩到 `ctp_instrument_query_smoke.py`、`ctp_position_query_smoke.py` 与 `ctp_account_query_smoke.py` 这三条核心只读 leaf 入口，连单脚本 query evidence 也能稳定落到统一 session namespace；这说明 C7 在 offhours 查询主线上的参数/命名重复工作已进一步被 active C3 吸收，后续更适合把剩余工作聚焦到 runbook、topic 规则与是否保留独立 change 的治理判断。
10. 2026-04-10：同一套 contract 已继续扩到 `ctp_md_login_smoke.py`、`ctp_live_data_client_bootstrap_smoke.py` 与 `ctp_marketdata_smoke.py` 这三条剩余 MD diagnostics-only leaf 入口；这说明 C7 在脚本参数/命名层面的重复工作几乎已被 active C3 吸收，后续若仍保留独立 C7，更适合只承接 runbook、topic rule 与 change 治理收口。