---
change-id: "20260403__position-account-query-baseline__runtime-query-contract"
dependencies:
  hard_blocking: []
  soft_dependency:
    - "20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline"
  blocked_by: []
---

# Runtime Query Contract 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`docs/`
**topic-id**：position-account-query-baseline
**change-id**：20260403__position-account-query-baseline__runtime-query-contract
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 `QUERY_POSITIONS / QUERY_ACCOUNT` 与 `POSITION / ACCOUNT` 的正式 runtime contract。
2. 明确 position/account 查询请求、事件和结果模型。
3. 给后续真实 `025292` position/account smoke 提供稳定边界。
4. 不在本 change 里直接宣告 position/account 实盘查询完成。

## 二、能力映射 / Capability Mapping

```text
- capability_id: query.position_account_runtime_contract
- capability_name: Position And Account Runtime Query Contract
- long_term_target: D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/position-account-query-baseline/README.md
- secondary_targets: D:/Nautilus/nautilus_ctp_adapter/docs/README.md; D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/README.md
- decision_target: D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/position-account-query-baseline/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改 `src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`、`docs/`。
2. 不扩展新的真实交易动作。
3. 本 change 只冻结查询 contract，不把 manifest export 直接写成“实盘查询已通过”。
4. 改完后至少执行 `python scripts/check_topic_docs.py` 与 `python -m pytest`。

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 position/account query 请求模型 | capability:query.position_account_runtime_contract | `runtime/` `docs/` | command contract | `python -m pytest` | topic README | `QUERY_POSITIONS / QUERY_ACCOUNT` 稳定成文 | 已完成 |
| P2 | 冻结 position/account query 事件模型 | capability:query.position_account_runtime_contract | `runtime/` `docs/` | event/result contract | `python -m pytest` | topic README | `POSITION / ACCOUNT` 稳定成文 | 已完成 |
| P3 | 留证并准备 C2/C3 | capability:query.position_account_runtime_contract | 当前 change bundle | evidence | `python scripts/check_topic_docs.py` | 当前 change bundle | 后续 smoke 可直接继承 contract | 已完成 |
