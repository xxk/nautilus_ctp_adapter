---
change-id: "20260402__live-ops-and-reconciliation__operational-evidence-matrix"
dependencies:
  hard_blocking:
    - id: "20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline"
      reason: "需要先继承 Topic 5 已冻结的证据链分层与人工复核边界"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Operational Evidence Matrix 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`docs/`
**topic-id**：live-ops-and-reconciliation
**change-id**：20260402__live-ops-and-reconciliation__operational-evidence-matrix
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 收口 Topic 5 的长期运维验收矩阵。
2. 把 startup、recovery、audit、reconciliation 的证据入口汇总成单页。
3. 明确每类证据的自动入口、人工复核项和通过信号。
4. 让 mainline 可以被标记为初版 completed。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ops.operational_evidence_matrix
- capability_name: Operational Evidence Matrix
- long_term_target: D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md
- secondary_targets: D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md; D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- decision_target: D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 仅修改 `docs/` 与当前 change bundle。
2. 不扩展新的 live 行为或新的交易权限。
3. 改完后至少执行 `python scripts/check_topic_docs.py` 与 `python -m pytest`。

## 四、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 汇总 Topic 5 运维证据矩阵 | capability:ops.operational_evidence_matrix | `docs/` | matrix 文档 | `python scripts/check_topic_docs.py` | Topic 5 README | startup/recovery/audit/reconciliation 证据入口汇总完成 | 已完成 |
| P2 | 回写 Topic 5 与 mainline 完成状态 | capability:ops.operational_evidence_matrix | `docs/` | README 状态收口 | `python -m pytest` | mainline README | Topic 5 与 mainline 标记 completed | 已完成 |
| P3 | 留证并关账 | capability:ops.operational_evidence_matrix | 当前 change bundle | evidence + acceptance | `python -m pytest` | 当前 change bundle | 可宣告 Topic 5 完成 | 已完成 |
