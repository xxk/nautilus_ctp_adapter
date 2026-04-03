---
change-id: "20260402__nautilus-live-marketdata__live-data-client-bootstrap"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-live-marketdata__marketdata-runtime-event-contract"
      reason: "需要先继承已冻结的 marketdata event contract"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Live Data Client Bootstrap 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、当前 change 三件套
**topic-id**：nautilus-live-marketdata
**change-id**：20260402__nautilus-live-marketdata__live-data-client-bootstrap
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 建立最小 `LiveDataClient` 主线。
2. 复用 Topic 1 的真实 MD 链路与 Topic 3 `C1` 的事件 contract。
3. 为后续订阅恢复和 marketdata smoke baseline 提供正式入口。

## 二、能力映射 / Capability Mapping

```text
- capability_id: live-data-client-bootstrap
- capability_name: LiveDataClient 启动主线 / LiveDataClient bootstrap
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md
- affects_long_term_rules: 是
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`data_client.py`、相关 bootstrap glue、当前 change 三件套。
2. 禁止修改：Topic 1 baseline、execution 代码。
3. AI 开始前必须阅读：Topic 3 README、`C1` evidence。
4. 改完后必须执行：`python -m pytest`。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立最小 LiveDataClient load 主线 | topic C2 | data client files | 可调用 bootstrap | `python -m pytest` | topic README | data client 不再只是 topic1 residue | 已完成 |
| P2 | 冻结 bootstrap 输出中间模型 | acceptance | data client/docs/tests | 稳定输出 shape | `python -m pytest` | architecture doc | C3/C4 可复用 | 已完成 |
| P3 | 回写 topic 队列与状态 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 3 可继续推 C3 | 已完成 |

## 八、完成结论

1. `CtpDataClient` 已具备正式 `LiveDataClient` bootstrap 主线，不再只是 Topic 1 的 residue。
2. `CtpLiveDataBootstrapResult` 已冻结成稳定输出模型。
3. live instrument query 返回 related instruments 时，当前主线会优先按 `config.instruments` 精确挑选订阅 symbol。
4. 当前 change 的真实证据见 `evidence_20260402_live_data_client_bootstrap.md`。
