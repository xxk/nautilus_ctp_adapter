---
change-id: "20260402__nautilus-live-marketdata__marketdata-runtime-event-contract"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-instrument-provider__instrument-smoke-baseline"
      reason: "需要先继承 Topic 2 已冻结的 instrument baseline"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Marketdata Runtime Event Contract 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/`、当前 change 三件套
**topic-id**：nautilus-live-marketdata
**change-id**：20260402__nautilus-live-marketdata__marketdata-runtime-event-contract
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 runtime 到 adapter 的市场数据事件 contract。
2. 明确本 change 不做完整 `LiveDataClient` bootstrap，只做事件 contract。
3. 为 Topic 3 的 `C2/C3/C4` 提供稳定的 marketdata 输入输出语义。

## 二、能力映射 / Capability Mapping

```text
- capability_id: marketdata-runtime-event-contract
- capability_name: 市场数据事件契约 / Marketdata runtime event contract
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：marketdata event models、data client bridge glue、当前 change 三件套。
2. 禁止修改：Topic 1/2 baseline、完整 execution 实现。
3. AI 开始前必须阅读：Topic 3 README、Topic 1 live smoke evidence、Topic 2 instrument baseline evidence。
4. 改完后必须执行：`python -m pytest`。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 marketdata event 字段口径 | topic C1 | runtime/data files | 稳定事件 contract | `python -m pytest` | topic README | 后续不再重定义 tick payload | 已完成 |
| P2 | 冻结 runtime -> adapter bridge 语义 | acceptance | data/bridge/docs | 稳定出桥语义 | `python -m pytest` | architecture doc | C2/C3 可直接复用 | 已完成 |
| P3 | 回写 topic 队列与状态 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 3 可继续推 C2 | 已完成 |

## 八、执行结果

1. `CtpDataClient` 已拥有专属 marketdata event deque
2. login / tick / disconnect payload 已冻结成明确 dataclass
3. 后续 `LiveDataClient` 可消费 `drain_marketdata_events()`，不必直接依赖全局 bridge 混合队列

## 九、验证记录

1. `python -m pytest`
2. `python -m pip install -e .`

## 十、证据

1. `./evidence_20260402_marketdata_runtime_event_contract.md`
