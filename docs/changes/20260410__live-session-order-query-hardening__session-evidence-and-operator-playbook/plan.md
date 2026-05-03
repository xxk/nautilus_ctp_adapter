---
change-id: "20260410__live-session-order-query-hardening__session-evidence-and-operator-playbook"
dependencies:
  hard_blocking:
    - id: "20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook"
      reason: "需要继承 session-window 路由规则与场景矩阵"
      expected_status: draft
    - id: "20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening"
      reason: "需要继承 offhours query / snapshot / disposition 证据"
      expected_status: in_progress
    - id: "20260410__live-session-order-query-hardening__c2609-live-order-dev-loop"
      reason: "需要继承 trade-window 开发证据与失败语义"
      expected_status: draft
  soft_dependency:
    - id: "20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff"
      reason: "需要把 vendor-bridge readiness 纳入 operator 决策树"
      expected_status: draft
  blocked_by: []
---

# Session Evidence 与 Operator Playbook 开发计划

**状态**：draft
**进度**：0%
**日期**：2026-04-10
**范围**：当前 change 三件套、当前 topic README、`docs/README.md`、`scripts/README.md`、必要的 `docs/architecture/` 回写
**topic-id**：live-session-order-query-hardening
**change-id**：20260410__live-session-order-query-hardening__session-evidence-and-operator-playbook
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把 trade-window 与 offhours 两条能力面收成 operator 可直接执行的 playbook。
2. 把 gate、入口、成功信号、failure reason、evidence 路径收成单一决策树。
3. 让后续操作者不再依赖临时聊天判断“现在该跑哪个入口”。
4. 本 change 只做 playbook 与 evidence matrix 收口，不新增业务能力。

## 二、能力映射 / Capability Mapping

```text
- capability_id: session-evidence-playbook
- capability_name: Session evidence and operator playbook
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md ; /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change 三件套、topic README、`docs/README.md`、`scripts/README.md`、必要的 architecture 文档。
2. 禁止修改：`vendor/`、仓外配置、真实交易代码路径。
3. 当前正式入口优先使用：`check_rust_gate.py`、`ctp_nautilus_live_smoke.py`、`ctp_query_adapter_smoke.py`、`ctp_order_lifecycle_smoke.py`。
4. AI 开始前必须阅读：C1/C2/C3 与 vendor-bridge handoff 四个 sibling change 的 `acceptance.md/plan.md`。
5. 改完后必须执行：`python scripts/check_topic_docs.py`、`python scripts/check_topic_governance.py --root .`。

## 四、背景与约束

1. 当前 topic 已积累大量 evidence，但还分散在多个 child change 中。
2. 若没有 playbook，后续操作者仍需要重新问“该跑哪个入口”。
3. 本 change 的目标是把 evidence 与入口组合成行动决策，而不是再扩脚本功能。

## 五、阶段划分（可选）

1. P1：冻结 session-window 决策树。
2. P2：收口 evidence matrix 与路径索引。
3. P3：回写 topic/docs/scripts 三层导航。

## 六、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 operator 决策树 | C1/C2/C3/U1 | 当前 change、topic README | trade-window vs offhours 决策树 | `python scripts/check_topic_docs.py` | topic README | operator 不再需要临时判断入口 | 未开始 |
| P2 | 收口 evidence matrix 与入口索引 | sibling change evidence | 当前 change、`docs/README.md`、`scripts/README.md` | 统一证据索引 | `python scripts/check_topic_governance.py --root .` | docs/README | evidence 可按 change/session 查找 | 未开始 |
| P3 | 回写长期导航与 closeout 说明 | topic closeout | 当前 change、必要的 architecture 文档 | playbook closeout | `python scripts/check_topic_docs.py` | 长期文档 | topic 可以从“推进中”切向稳定操作面 | 未开始 |

## 七、验证动作（可选）

```powershell
python scripts/check_topic_docs.py
python scripts/check_topic_governance.py --root .
```

## 八、完成定义（可选）

### 开发完成

1. topic 级 operator 决策树已写清楚。
2. 关键入口、success signal、failure reason 与 evidence path 已集中化。
3. docs/scripts 两层导航已对齐。

### 交付完成

1. `acceptance.md` 中阻塞场景通过。
2. operator 可在不依赖聊天的前提下执行同一路径。
3. 当前 topic 具备 closeout 或长期冻结条件。

## 九、长期规则增量摘要 / Long-Term Rule Delta Summary

本次新增长期规则：session-window topic 的 operator 决策必须基于统一的 gate + entrypoint + evidence matrix，而不是临时聊天指令。

## 十、回写与相关变更 / Write-back & Related Changes

1. 需要回写 topic README、`docs/README.md` 与 `scripts/README.md`。
2. 若形成稳定长期口径，应回写 architecture 文档。

## 十一、阻塞项（可选）

1. 若 sibling changes 没有形成足够 evidence，本 change 只能先冻结框架，不能宣告完成。

## 十二、进度记录（可选）

1. 2026-04-10：创建 C4 正式 change bundle，作为 session-window topic 的 operator playbook 收口面。