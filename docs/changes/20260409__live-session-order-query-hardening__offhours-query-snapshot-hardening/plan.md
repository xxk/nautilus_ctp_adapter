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

**状态**：in_progress
**进度**：local live config prepared；blocked by missing vendor/ctp/bin bootstrap pack
**日期**：2026-04-09
**范围**：`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`、当前 change 三件套、`docs/topics/roadmap/nautilus_adapter/live-session-order-query-hardening/README.md`
**topic-id**：live-session-order-query-hardening
**change-id**：20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把当前 topic 的开发优先级明确切到非交易功能，先推进 offhours 只读 query/snapshot/disposition 能力。
2. 用真实非交易场景验收驱动开发，而不是先补抽象接口。
3. 让操作者在非交易时段可以稳定执行 `account / position / reconciliation / truth-merge` 等只读路径，并拿到清晰的成功/失败语义。
4. 本 change 不做真实下单、撤单、改单，只服务于非交易时段的开发与验收。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-offhours-query-hardening
- capability_name: 非交易时段只读查询加固 / Offhours query snapshot hardening
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-session-order-query-hardening/README.md
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
5. 改完后必须执行：`python scripts/check_topic_docs.py`；若触及 `scripts/`、`src/` 或 `tests/`，再执行 `python -m pytest`。

## 四、背景与约束

1. 用户已明确要求“优先开发非交易功能”，因此本 change 的优先级高于 `C2 c2609 live order dev loop`。
2. 当前仓内已经有只读 query、reconciliation、truth merge 的 baseline，但还缺少统一的 offhours-first runbook 与失败语义加固。
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
| P1 | 冻结非交易时段真实验收场景 | 用户优先级 + topic C3 | 当前 change 三件套 | A1-A6 场景、命令、证据路径 | `python scripts/check_topic_docs.py` | topic README | 之后的 offhours 改动不再改口验收矩阵 | 未开始 |
| P2 | 加固 account/position/query snapshot 语义 | A1/A5/A6 | `scripts/ctp_query_adapter_smoke.py`、`scripts/ctp_position_query_smoke.py`、`scripts/ctp_account_query_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/query_adapter.py`、`tests/` | 只读 query 成功/失败/空仓边界更清晰 | `python scripts/check_topic_docs.py`；必要时 `python -m pytest` | 当前 change | query 成功、空仓、断连三类状态可区分 | 进行中 |
| P3 | 加固 reconciliation / truth-merge / merged policy 语义 | A2/A3/A4 | `scripts/ctp_reconciliation_snapshot_smoke.py`、`scripts/ctp_td_truth_merge_snapshot_smoke.py`、`scripts/ctp_td_merged_reconciliation_policy_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/reconciliation.py`、`src/nautilus_ctp_adapter/adapters/ctp/truth_merge.py`、`tests/` | 只读汇总快照与 disposition 输出更清晰 | `python scripts/check_topic_docs.py`；必要时 `python -m pytest` | 当前 change | 可以区分 clear / manual_review_required / boundary_required / evidence_only | 进行中 |
| P4 | 回写 topic queue 与 offhours-first 顺序 | 用户优先级 | 当前 topic README、当前 change | 优先级同步 | `python scripts/check_topic_docs.py` | topic README | topic 队列清楚声明 `C3` 先于 `C2` | 未开始 |

## 八、验证动作（可选）

```powershell
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

1. `vendor/ctp/bin/` 当前缺少 bootstrap DLL；至少缺 `ctp_native.dll`、`CTPProviderSwig.dll`、`CTPProviderSwig.Core.dll`、`iTrading.Core.dll`，因此真实只读 smoke 还不能真正进入 TD/MD。
2. 当前机器上 `scripts/sync_ctp_native.py` 默认引用的 `D:\3.9.3_Spec-Kit\...` 源路径不存在，不能直接用默认 profile 同步 bootstrap pack。
3. 本地未跟踪的 real-account live config 已从 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制到 `cfgs/local/ctp.live.025292.local.json`，并已填入真实连接参数；当前不再是主阻塞。

## 十三、进度记录（可选）

1. 2026-04-09：因用户明确要求“优先开发非交易功能”，创建 `C3` change bundle，作为当前 topic 的下一优先级执行单元。
2. 2026-04-09：已为 `ctp_query_adapter_smoke.py`、`ctp_position_query_smoke.py`、`ctp_account_query_smoke.py`、`ctp_reconciliation_snapshot_smoke.py`、`ctp_td_truth_merge_snapshot_smoke.py`、`ctp_td_merged_reconciliation_policy_smoke.py` 补齐结构化失败输出与 `success/failure_reason` 语义，并用 targeted pytest 锁定缺失配置与只读拒绝交易语义的行为。
3. 2026-04-09：已准备好本地 `cfgs/local/ctp.live.025292.local.json`，并确认当前真实阻塞变为缺少 `vendor/ctp/bin/` bootstrap pack；本机上未找到 `ctp_native.dll`、`CTPProviderSwig.dll` 或 `CTPProviderSwig.Core.dll`，`scripts/sync_ctp_native.py` 默认源路径 `D:\3.9.3_Spec-Kit\...` 也不存在。