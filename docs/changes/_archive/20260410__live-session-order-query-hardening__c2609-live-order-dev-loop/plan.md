---
change-id: "20260410__live-session-order-query-hardening__c2609-live-order-dev-loop"
dependencies:
  hard_blocking:
    - id: "20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook"
      reason: "需要继承交易时段/非交易时段的正式入口、guardrails 与 evidence 口径"
      expected_status: draft
    - id: "20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff"
      reason: "需要先明确 vendor-bridge ready，才能进入真实 live-send 开发"
      expected_status: draft
    - id: "20260402__nautilus-live-execution__order-lifecycle-smoke-baseline"
      reason: "需要继承现有 submit/cancel/fill smoke baseline"
      expected_status: completed
  soft_dependency:
    - id: "20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening"
      reason: "需要继承 offhours query / truth 证据，作为 live-send 前的 background state"
      expected_status: in_progress
  blocked_by: []
---

# C2609 Live Order Dev Loop 开发计划

**状态**：blocked
**进度**：55%
**日期**：2026-04-10
**范围**：`scripts/ctp_order_lifecycle_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、`tests/`、当前 change 三件套、当前 topic README
**topic-id**：live-session-order-query-hardening
**change-id**：20260410__live-session-order-query-hardening__c2609-live-order-dev-loop
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 用 `c2609`、单笔 `1` 手、净持仓上限 `5` 手的 guardrails，推进真实 live order dev loop。
2. 把 trade-window preflight、submit/cancel/fill 与 guardrail 失败语义固定为正式 child change。
3. 本 change 只做最小交易开发闭环，不扩展到多合约、多手数或自动化策略。
4. 只有在 vendor-bridge ready 且交易窗口可用时才允许进入真实 live-send。

## 二、能力映射 / Capability Mapping

```text
- capability_id: c2609-live-order-dev-loop
- capability_name: C2609 live order dev loop
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: 无
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_order_lifecycle_smoke.py
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`scripts/ctp_order_lifecycle_smoke.py`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、`tests/`、当前 change 三件套、topic README。
2. 禁止修改：`vendor/`、仓外配置、任何放宽 `c2609 / 1 手 / 5 手上限` 的 guardrail。
3. 当前正式入口优先使用：`python scripts/ctp_td_order_truth_smoke.py --config <path>`、`python scripts/ctp_order_lifecycle_smoke.py ... --live-send`。
4. AI 开始前必须阅读：C1 `acceptance.md`、vendor-bridge handoff change、`nautilus-live-execution` 相关 change、`execution_client.py`。
5. 改完后必须执行：`python scripts/check_topic_docs.py`；若触及代码，再执行最小 targeted pytest。

## 四、背景与约束

1. 当前仓内已经有 order lifecycle baseline，但 topic 级 trade-window 开发还没有正式闭环。
2. 当前 change 不负责解决私有 SDK/live DLL 输入缺口；那是 sibling vendor-bridge change 的责任。
3. 任何真实 live-send 前都必须先有 preflight 通过证据。

## 五、阶段划分（可选）

1. P1：冻结 trade-window preflight 与 live-send 前置条件。
2. P2：补齐 submit/cancel/fill 的最小开发闭环与失败语义。
3. P3：回写 evidence 与 handoff 到 operator playbook。

## 六、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 trade-window preflight 入口与通过信号 | C1/A1 | 当前 change、`scripts/ctp_td_order_truth_smoke.py` | preflight checklist | help/source/focused pytest | topic README | live-send 前不再靠口头确认 | 已完成 |
| P2 | 推进 `c2609` 一手 submit/cancel/fill dev loop | A2/A5 | `scripts/ctp_order_lifecycle_smoke.py`、`execution_client.py`、`tests/` | 结构化 live-send 结果与 guardrail 失败语义 | focused pytest | 当前 change | `live_send_armed`、exec match、guardrail reject 可区分 | 部分完成 |
| P3 | 回写 trade-window evidence 与交接 | C4 handoff | 当前 change、topic README | evidence 路径、handoff note | `python scripts/check_topic_governance.py --root .` | topic README | C4 可直接消费当前 evidence | 阻塞 |

## 七、验证动作（可选）

```powershell
python scripts/check_topic_docs.py
python scripts/check_topic_governance.py --root .
python -m pytest
```

## 八、完成定义（可选）

### 开发完成

1. preflight / live-send / guardrail 三条路径口径清楚。
2. `ctp_order_lifecycle_smoke.py` 的输出足以支持真实开发闭环。
3. 当前 change 的证据路径与 operator playbook 已对接。

### 交付完成

1. `acceptance.md` 中阻塞场景通过。
2. 真实 trade-window evidence 已留存。
3. C4 可以不再重新定义交易路径。

## 九、长期规则增量摘要 / Long-Term Rule Delta Summary

本次无长期规则增量；本 change 只在既有 guardrails 下推进真实交易开发闭环。

## 十、回写与相关变更 / Write-back & Related Changes

1. 需要回写当前 topic README 的 queue 状态与 C2 交付结论。
2. 需要向 C4 交接 trade-window evidence 路径。

## 十一、阻塞项（可选）

1. formal-trading vendor-bridge/live front 未 ready 前，真实 `c2609` live-send 不应启动。
2. 交易窗口不可用或净持仓未知时，A2 无法执行。
3. OpenCTP paper baseline 已在 `20260607__openctp-tts__test-baseline` 完成；它只能解锁 paper simulation development，不能伪造 real-account `c2609` live-send pass。

## 十二、进度记录（可选）

1. 2026-04-10：创建 C2 正式 change bundle，作为 vendor-bridge ready 后的第一优先交易开发面。
2. 2026-06-08：repo-only contract 复核通过：`ctp_order_lifecycle_smoke.py` 暴露 `--live-send`；`ctp_td_order_truth_smoke.py` 暴露 `--flow-path`、`--session-label`、`--evidence-root`、`--output-json`；guardrail/live-send-arm focused tests 通过。
3. 2026-06-08：真实 A1/A2 live-send 验收阻塞于外部 live front/交易窗口/净持仓前置条件，不执行真实报单。
