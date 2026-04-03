---
change-id: "20260402__nautilus-instrument-provider__instrument-provider-bootstrap"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-instrument-provider__exchange-and-symbol-normalization"
      reason: "需要先继承已冻结的 normalization rule"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Instrument Provider Bootstrap 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`src/nautilus_ctp_adapter/runtime/`、当前 change 三件套
**topic-id**：nautilus-instrument-provider
**change-id**：20260402__nautilus-instrument-provider__instrument-provider-bootstrap
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 建立最小 `InstrumentProvider` 主线，使 query contract 与 normalization rule 真正合流。
2. 明确本 change 只做 bootstrap，不提前做完整 instrument smoke baseline。
3. 为 Topic 3 提供可被 `LiveDataClient` 复用的 instrument loading 入口。

## 二、能力映射 / Capability Mapping

```text
- capability_id: instrument-provider-bootstrap
- capability_name: InstrumentProvider 启动主线 / InstrumentProvider bootstrap
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md
- affects_long_term_rules: 是
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`instrument_provider.py`、相关 runtime/bootstrap glue、当前 change 三件套。
2. 禁止修改：Topic 1 baseline、完整 marketdata/execution 实现。
3. AI 开始前必须阅读：当前 topic README、`C1/C2` 的 evidence。
4. 改完后必须执行：`python -m pytest`。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立最小 provider load 主线 | topic C3 | provider/runtime files | 可调用的 provider bootstrap | `python -m pytest` | topic README | provider 不再只是占位 | 已完成 |
| P2 | 冻结 provider 输出中间模型 | acceptance | provider/docs/tests | 稳定 provider result shape | `python -m pytest` | architecture doc | Topic 3 可复用 | 已完成 |
| P3 | 回写 topic 队列与状态 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 2 可继续推 C4 | 已完成 |

## 八、执行结果

1. `InstrumentProvider` 已新增稳定的 load 结果模型
2. `load_all_instruments_mainline()` 已可返回 pending result shape
3. query 完成后可通过 `load_result_for_request(...)` 与 `latest_load_result` 读取稳定输出

## 九、验证记录

1. `python -m pytest`
2. `python -m pip install -e .`

## 十、证据

1. `./evidence_20260402_instrument_provider_bootstrap.md`
