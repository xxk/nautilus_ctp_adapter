---
change-id: "20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract"
dependencies:
  hard_blocking:
    - id: "20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening"
      reason: "需要继承当前 offhours query 与 order-truth contract"
      expected_status: in_progress
    - id: "20260403__td-order-truth-and-reconciliation__td-order-truth-baseline"
      reason: "需要继承 TD order truth 基线与当前 callback 口径"
      expected_status: completed
  soft_dependency:
    - id: "20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff"
      reason: "若正式 TD query 仍依赖 live vendor bridge，应复用同一 blocker 术语"
      expected_status: draft
  blocked_by: []
---

# Readonly Order Trade Snapshot Contract 开发计划

**状态**：draft
**进度**：0%
**日期**：2026-04-10
**范围**：新的 `ORDER / TRADE` 只读 snapshot 入口、必要的 adapter contract、`tests/`、当前 change 三件套
**topic-id**：live-session-order-query-hardening
**change-id**：20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把 `ORDER / TRADE` 只读快照从当前 callback truth 语义中拆成独立 contract。
2. 明确 `无订单 / 无成交 / 历史残留 / query 失败` 四类结果的正式区分。
3. 本 change 只做 read-only snapshot，不扩展为下单或撤单验证。
4. 为 topic 目标中的 `order / trade snapshot` 留出正式宿主，不让它长期混在 callback truth 里。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-readonly-order-trade-snapshot
- capability_name: Read-only Order/Trade Snapshot Contract
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: <新建或扩展的正式 read-only order/trade entrypoint>
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：新的 read-only entrypoint、必要 adapter、`tests/`、当前 change 三件套。
2. 禁止修改：任何 live-send 入口、submit/cancel mapping、仓外 live config。
3. 当前正式入口优先使用：现有 TD truth / merged policy / query scripts 作为参考，不直接改成交易入口。
4. AI 开始前必须阅读：`execution_client.py` 中 order truth baseline、`ctp_td_order_truth_smoke.py`、C3 `acceptance.md`。
5. 改完后必须执行：`python scripts/check_topic_docs.py --root .` 与 targeted pytest。

## 四、阶段划分（可选）

1. P1：冻结 read-only order/trade snapshot 的 payload 与 failure taxonomy。
2. P2：实现最小入口与 adapter 映射。
3. P3：补回归与 README / topic 回写。

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 `ORDER / TRADE` 只读结果 taxonomy | topic 目标 | 当前 change、必要入口 | success/failure/boundary taxonomy | 文档自检 | topic README | `无订单/无成交/历史残留/query失败` 可区分 | 未开始 |
| P2 | 实现 read-only snapshot 入口 | 持续开发 backlog | 脚本、adapter、`tests/` | 正式 read-only snapshot | targeted pytest | `scripts/README.md` | 新入口不依赖交易动作 | 未开始 |
| P3 | 回写长期导航 | operator 可发现性 | 当前 change、`scripts/README.md`、topic README | 使用说明与 evidence path | `python scripts/check_topic_docs.py --root .` | topic README | 后续 operator 能直接找到入口 | 未开始 |

## 六、长期规则增量摘要 / Long-Term Rule Delta Summary

本次预期新增长期规则：`ORDER / TRADE` 的 read-only snapshot 必须与 callback truth / live-send 分层，不能只靠历史 callback 语义替代。

## 七、进度记录（可选）

1. 2026-04-10：创建 C6 change bundle，作为 offhours `ORDER / TRADE` 只读 contract 的正式宿主。