---
change-id: "20260410__live-session-order-query-hardening__aggregated-query-evidence-export"
dependencies:
  hard_blocking:
    - id: "20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening"
      reason: "需要继承当前 offhours query / order-truth / reconciliation 的基础 contract"
      expected_status: in_progress
  soft_dependency:
    - id: "20260410__live-session-order-query-hardening__session-evidence-and-operator-playbook"
      reason: "后续 evidence export 路径应与 operator playbook 保持一致"
      expected_status: draft
  blocked_by: []
---

# Aggregated Query Evidence Export 开发计划

**状态**：draft
**进度**：0%
**日期**：2026-04-10
**范围**：`scripts/ctp_query_adapter_smoke.py`、必要的 `src/nautilus_ctp_adapter/adapters/ctp/` 聚合辅助、`tests/`、当前 change 三件套
**topic-id**：live-session-order-query-hardening
**change-id**：20260410__live-session-order-query-hardening__aggregated-query-evidence-export
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把当前分散的 `instrument / position / account / order-truth / reconciliation` 只读结果收成同一个 offhours 聚合入口。
2. 支持把同次查询结果落到明确的 evidence 路径，而不是只停留在终端输出。
3. 不新增真实交易副作用，不扩展为 trade-window live-send 入口。
4. 让后续 operator 或 AI 在非交易时间一次运行就拿到完整诊断面。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-aggregated-query-export
- capability_name: Offhours 聚合查询与证据导出 / Aggregated Query And Evidence Export
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_query_adapter_smoke.py
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`scripts/ctp_query_adapter_smoke.py`、必要的 adapter 聚合辅助、`tests/test_smoke_import.py`、当前 change 三件套。
2. 禁止修改：任何 live-send 入口、仓外 live config、`vendor/`。
3. 当前正式入口优先使用：`python scripts/ctp_query_adapter_smoke.py --config <path>`。
4. AI 开始前必须阅读：C3 `plan.md/acceptance.md`、`scripts/ctp_query_adapter_smoke.py`、`scripts/ctp_reconciliation_snapshot_smoke.py`。
5. 改完后必须执行：`python scripts/check_topic_docs.py --root .`；若触及脚本或测试，再执行 targeted pytest。

## 四、背景与约束

1. 当前仓内已有多条只读入口，但 operator 仍需要多次运行才能拼出完整状态。
2. 当前聚合入口已支持 `instrument` 与 `order_truth`，但还缺 reconciliation 摘要与 evidence export。
3. 本 change 不把 operator playbook 一次性收口到 docs；那是 C4 的职责。

## 五、阶段划分（可选）

1. P1：冻结聚合 payload 与 evidence export 最小 contract。
2. P2：补 `reconciliation disposition/findings` 聚合与可选 evidence 输出。
3. P3：补 regression 与 README 回写。

## 六、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结聚合 payload 范围 | C3 当前入口 | `scripts/ctp_query_adapter_smoke.py`、当前 change | 聚合字段与导出路径 contract | targeted pytest | 当前 change | operator 一次运行可覆盖五类只读结果 | 未开始 |
| P2 | 补 reconciliation 聚合与 evidence export | offhours 持续开发 | `scripts/ctp_query_adapter_smoke.py`、必要 adapter、`tests/` | 聚合输出 + evidence file | targeted pytest | `scripts/README.md` | reconciliation 可直接并入单次聚合运行 | 未开始 |
| P3 | 回写 README 与 evidence 示例 | operator 可用性 | 当前 change、`scripts/README.md` | 入口说明与示例路径 | `python scripts/check_topic_docs.py --root .` | topic README | 使用方式不再依赖聊天说明 | 未开始 |

## 七、验证动作（可选）

```powershell
python scripts/check_topic_docs.py --root .
python -m pytest tests/test_smoke_import.py -k aggregated_query
```

## 八、完成定义（可选）

### 开发完成

1. 单次 offhours 聚合入口可选返回五类只读结果。
2. evidence export 的路径与文件命名口径已冻结。
3. targeted regression 已补齐。

### 交付完成

1. `acceptance.md` 中关键场景通过。
2. 当前 change bundle 中存在最小 evidence 示例。
3. `scripts/README.md` 已补入口说明。

## 九、长期规则增量摘要 / Long-Term Rule Delta Summary

本次无长期规则增量；本 change 只是在 C3 基础上继续推进 offhours 聚合入口。

## 十、回写与相关变更 / Write-back & Related Changes

1. 需要回写 `scripts/README.md` 的使用说明。
2. topic README 仅在入口职责发生变化时回写。

## 十一、阻塞项（可选）

1. 若 formal live TD 路径仍是 scaffold-only，真实验收证据仍会被 U1 blocker 限制。

## 十二、进度记录（可选）

1. 2026-04-10：创建 C5 change bundle，作为 C3 后续的持续 offhours 聚合开发面。