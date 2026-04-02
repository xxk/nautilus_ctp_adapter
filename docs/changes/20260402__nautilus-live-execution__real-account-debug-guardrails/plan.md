---
change-id: "20260402__nautilus-live-execution__real-account-debug-guardrails"
dependencies:
  hard_blocking: []
  soft_dependency:
    - id: "20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610"
      reason: "需要继承已确认的真实账户、前置地址与 live smoke 背景"
      expected_status: in_progress
  blocked_by: []
---

# 实盘账户调试 Guardrails 冻结 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-execution/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`cfgs/`、`tests/`
**topic-id**：nautilus-live-execution
**change-id**：20260402__nautilus-live-execution__real-account-debug-guardrails
**关联 acceptance**：./acceptance.md

## 一、需求简述

本 change 要先于正式 execution 实现，冻结 `025292` 实盘账户的调试下单边界，并把这些边界落成仓内可执行 guardrails。当前不做真实发单，不做 TD 主线实现，也不做完整 `LiveExecutionClient`。做完后应能明确回答：后续任何 execution change 在什么边界内才允许继续推进，以及这些边界已经落在什么配置和代码入口上。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-real-account-debug-guardrails
- capability_name: 实盘账户调试 Guardrails / Real-account debug guardrails
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-execution/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/execution_client.py
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：`docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-execution/`、`docs/changes_topic/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`cfgs/`、`tests/`、当前 change 三件套。
2. 禁止修改：任何会触发真实 TD 发单的脚本、外部宿主、临时 smoke host。
3. 本 change 的正式落点是“guardrails 规则 + 配置表达 + 执行预检入口”，不是完整 execution 实现。
4. AI 开始前必须阅读：`nautilus-live-execution` topic README、mainline roadmap、`src/nautilus_ctp_adapter/adapters/ctp/config.py`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`。
5. 改完后至少执行：`python -m pytest`。

## 四、背景与约束

1. `025292` 是实盘账户，任何调试行为都必须按保守边界冻结。
2. 用户给出的约束是：仅允许 `c2609`、每次最多 `1` 手、净持仓最大 `5` 手、每分钟不超过 `10` 次报单、挂一档价格下单。
3. 用户原话中出现“5 收”，当前按“`5` 手”处理；若后续被更正，必须先更新本 change 和 topic README。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 topic 与 mainline 的实盘 guardrails 规则 | 用户约束 | `docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-execution/README.md`、`docs/changes_topic/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md`、当前 change 三件套 | 长期规则清单 | 文档检查 | topic/mainline README | 后续 execution change 无法绕过 guardrails | 已完成 |
| P2 | 扩展配置模型表达 execution guardrails | capability | `src/nautilus_ctp_adapter/adapters/ctp/config.py`、`cfgs/ctp.live.example.json` | 可装载的 guardrails config | `python -m pytest` | topic README | 真实账户配置可以显式携带 guardrails | 已完成 |
| P3 | 在执行侧增加预检入口 | implementation | `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、`src/nautilus_ctp_adapter/adapters/ctp/factory.py` | 不触达 TD 的 order precheck | `python -m pytest` | decision target | 执行链路正式接线前已有可复用 guardrails 入口 | 已完成 |
| P4 | 用测试锁定 guardrails 行为 | contract | `tests/test_smoke_import.py` | guardrails contract 证据 | `python -m pytest` | 当前 change | 关键限制被测试覆盖 | 已完成 |

## 十、完成定义（可选）

### 开发完成

1. `025292` 的调试边界已在 topic/mainline README 中冻结。
2. 配置模型可显式表达 execution guardrails。
3. 执行侧存在不会触发真实下单的 precheck 入口。
4. 最小测试已锁定关键 guardrails。

### 交付完成

1. `acceptance.md` 中的阻塞场景通过。
2. 当前 change 目录已可作为 Topic 4 的 guardrails 依据。
3. 后续 `C1` 及之后的 execution change 已能直接复用 guardrails 结论。

## 十一、长期规则增量摘要 / Long-Term Rule Delta Summary

本次新增长期规则：`025292` 实盘账户的调试 execution 路径必须先满足 `c2609 only / qty<=1 / abs(net_position)<=5 / <=10 submits per minute / best_level_1 price`。

## 十二、回写与相关变更 / Write-back & Related Changes

1. 本 change 需要回写 `nautilus-live-execution` topic README。
2. 本 change 需要同步回写 mainline roadmap 的统一安全边界。
