---
change-id: "20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-execution__real-account-debug-guardrails"
      reason: "需要继承 c2609 / 1 手 / 5 手上限的实盘调试 guardrails"
      expected_status: completed
    - id: "20260403__position-account-query-baseline__nautilus-query-adapter-baseline"
      reason: "需要继承 position/account 正式 query 主线与只读 smoke 入口"
      expected_status: completed
  soft_dependency:
    - id: "20260403__td-order-truth-and-reconciliation__td-order-truth-baseline"
      reason: "需要复用 TD order truth 观察入口，作为交易时段 preflight 的正式证据来源"
      expected_status: completed
    - id: "20260403__live-ops-truth-snapshot__live-ops-policy-baseline"
      reason: "当前 active topic 已冻结 live ops truth 口径，本 change 不应重新发明运行真相"
      expected_status: in_progress
  blocked_by: []
---

# Session Window Guardrails 与真实场景验收驱动 Runbook 开发计划

**状态**：blocked
**进度**：80%
**进度说明**：runbook skeleton landed；offhours/trade-window/vendor-bridge routing frozen at document level；C3/U1 evidence 已接回当前 runbook，当前只剩 trade-window 场景等待 U1 ready 与真实交易窗口
**日期**：2026-04-09
**更新日期**：2026-04-11
**范围**：`docs/topics/live-session-order-query-hardening/`、`docs/changes/20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook/`、`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`
**topic-id**：live-session-order-query-hardening
**change-id**：20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把“交易时段可以直连 CTP”与“非交易时段只能做只读查询”的口径冻结成正式 child change，而不是继续留在聊天里。
2. 用真实场景验收驱动开发：先冻结实际会发生的交易/查询场景，再围绕这些场景补脚本入口、guardrails 和失败语义。
3. 交付一个 session-window runbook，让操作者能根据当前时段直接选择正确的正式入口。
4. 本 change 不追求一次完成全部功能，而是要把后续功能开发绑定到真实验收场景与真实证据路径上。
5. 当前执行优先级明确为：先完成非交易时段 A3/A6/A4，再在交易时段推进 A1/A2。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-session-window-runbook
- capability_name: 交易/非交易时段能力分流 / Session-window capability routing
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: 无
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_order_lifecycle_smoke.py ; /D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_query_adapter_smoke.py
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change 三件套、`docs/topics/live-session-order-query-hardening.md`、`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`。
2. 禁止修改：`vendor/`、外部宿主、仓外配置文件、任何绕过现有 guardrails 的临时自动发单流程。
3. 当前正式入口优先使用：`scripts/ctp_td_order_truth_smoke.py`、`scripts/ctp_order_lifecycle_smoke.py`、`scripts/ctp_account_query_smoke.py`、`scripts/ctp_position_query_smoke.py`、`scripts/ctp_query_adapter_smoke.py`。
4. AI 开始前必须阅读：当前 topic README、`nautilus-live-execution` topic README、`position-account-query-baseline` topic README、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、`src/nautilus_ctp_adapter/adapters/ctp/query_adapter.py`。
5. 改完后必须执行：`python scripts/check_topic_docs.py`；若触及 `scripts/`、`src/` 或 `tests/`，再执行 `python -m pytest`。

## 四、背景与约束

1. 当前仓内已有受管模板 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json)，但 `cfgs/local/` 仍保持忽略；正式验收必须从模板复制到本地未跟踪路径，例如 `cfgs/local/ctp.live.025292.local.json`，再填写真实敏感值。
2. 交易时段的真实开发只能围绕 `c2609`、单笔 `1` 手、净持仓上限 `5` 手展开。
3. 非交易时段不允许发送新的 live order；只允许做 `account / position / order / trade` 相关只读查询和证据收集。
4. 本 change 要优先回答的是“当前该跑哪个正式入口、以什么结果算通过/失败”，然后再决定是否需要补代码来支撑这些场景。

## 五、设计方案（可选）

### 方案核心：Acceptance-First / 验收先行

1. 先把交易时段与非交易时段的真实场景写进 `acceptance.md`，包括成功、失败和边界场景。
2. 再把每个场景绑定到当前仓内已有的正式脚本入口，而不是先发明新的脚本。
3. 若某个场景无法用现有入口清楚表达，再最小化修改 `scripts/` 或 `src/nautilus_ctp_adapter/adapters/ctp/`，让场景可执行、可判定、可留证。
4. 后续 `C2/C3/C4` 的功能开发都要以本 change 冻结的场景矩阵为准，不再另起一套验收口径。

## 六、阶段划分（可选）

1. P1：冻结真实场景矩阵与前置条件。
2. P3：先冻结非交易时段入口、成功信号和失败语义。
3. P2：再冻结交易时段入口、成功信号和失败语义。
4. P4：收口 runbook 与 evidence 路径，给后续 `C2/C3` 做明确交接。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结交易时段/非交易时段的真实验收场景矩阵 | 用户约束 + topic C1 | 当前 change 三件套 | A1-A6 场景、前置条件、证据路径 | `python scripts/check_topic_docs.py` | topic README | 后续功能开发必须围绕同一组真实场景推进 | 已完成 |
| P3 | 把非交易时段路径绑定到 account/position/query snapshot 正式入口 | A3/A4/A6 | `scripts/ctp_account_query_smoke.py`、`scripts/ctp_position_query_smoke.py`、`scripts/ctp_query_adapter_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/query_adapter.py`、当前 change | offhours runbook、只读查询成功/失败语义 | `python scripts/check_topic_docs.py`；必要时 `python -m pytest` | topic README | 能明确区分“只读可用/连接失败/空仓非失败/误用 live-send” | 已完成（通过 C3 冻结） |
| P2 | 把交易时段路径绑定到现有 order truth 与 order lifecycle 正式入口 | A1/A2/A5 | `scripts/ctp_td_order_truth_smoke.py`、`scripts/ctp_order_lifecycle_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、当前 change | trading-window runbook、成功/失败语义 | `python scripts/check_topic_docs.py`；必要时 `python -m pytest` | topic README | 能明确区分“可交易/不可交易/guardrail 拒绝/连接失败” | 阻塞（等待 U1 / vendor bridge ready） |
| P4 | 收口 evidence 路径与后续 child change 交接 | topic C1 -> C2/C3 | 当前 change、`docs/topics/live-session-order-query-hardening.md`、`./runbook.md` | session-window playbook 与 handoff 说明 | `python scripts/check_topic_docs.py` | topic README | `C2/C3` 可直接复用当前 change 的场景矩阵和命令口径 | 进行中 |

## 八、任务说明（可选）

1. `C1` 的核心不是“再做一个大而全的新脚本”，而是用现有正式入口建立一个可执行的 session-window 路由层。
2. 如果场景 A4/A5 暴露出当前脚本缺少“明确拒绝错误用法”的行为，本 change 允许做最小代码补强。
3. 真实交易时段的 live-send 验收必须先有 A1 preflight 通过，不能跳过。

## 九、验证动作（可选）

```powershell
python scripts/check_topic_docs.py
python -m pytest
```

说明：只有在实际执行 A1-A6 场景时，才追加对应的 live smoke 命令；它们写在 `acceptance.md` 中，不用测试替代。

## 十、完成定义（可选）

### 开发完成

1. `acceptance.md` 已冻结实际交易时段与非交易时段场景。
2. 每个场景都绑定了正式入口、通过信号、失败口径与证据路径。
3. topic queue 已明确 `C1` 的角色是后续功能开发的验收基线。

### 交付完成

1. `acceptance.md` 中阻塞场景通过。
2. 真实验收证据已留存在当前 change bundle。
3. `C2/C3/C4` 后续功能开发不再需要重新定义场景矩阵。

## 十一、长期规则增量摘要 / Long-Term Rule Delta Summary

本次新增长期规则：`live-session-order-query-hardening` topic 的功能推进必须先按 session-window 划分真实场景，再围绕这些场景实现或补强正式入口。

## 十二、回写与相关变更 / Write-back & Related Changes

1. 本 change 需要回写当前 topic README 的 queue 状态与当前 first action。
2. 暂不要求回写其他长期文档，除非执行中发现正式入口判断仍有长期歧义。

## 十三、阻塞项（可选）

1. 是否已从 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制出本地未跟踪的 `cfgs/local/ctp.live.025292.local.json` 并填好真实值。
2. 交易时段窗口是否可用，以及是否有人能在 live-send 前确认当前净持仓未突破 `5` 手上限。

## 十四、进度记录（可选）

1. 2026-04-09：创建 `C1` change bundle，冻结以真实场景验收驱动后续开发的执行框架。
2. 2026-04-10：已基于当前 topic 与 C3/U1/C2 队列落下 `runbook.md`，把 session-window 路由明确拆成三条正式路径：`offhours read-only`、`vendor-bridge handoff`、`trade-window live order`；后续 Autopilot 不再依赖聊天决定“该跑哪个入口”。
3. 2026-04-11：已把 U1 的真实 blocker/handoff evidence 接回当前 runbook；当前 active lane 改为 U1，`sdk-not-found / scaffold-only` 不再表示“下一批才切 U1”，而是当前就停留在 U1 blocked handoff，直到私有 SDK/live DLL 输入补齐。
