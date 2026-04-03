---
change-id: "20260402__nautilus-instrument-provider__instrument-query-runtime-contract"
dependencies:
  hard_blocking:
    - id: "20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610"
      reason: "需要先继承 Topic 1 已冻结的 live/bootstrap 口径"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Instrument Query Runtime Contract 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`rust/ctp_runtime_core/`、`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/`、当前 change 三件套
**topic-id**：nautilus-instrument-provider
**change-id**：20260402__nautilus-instrument-provider__instrument-query-runtime-contract
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 CTP 合约查询在 runtime 与 adapter 之间的 command/event contract。
2. 明确本 change 只解决 query contract，不提前实现完整 `InstrumentProvider`。
3. 为后续 symbol normalization 和 provider bootstrap 提供稳定输入面。
4. 用真实 query 方向的 smoke 或最小 contract 证据判断“边界已经站稳”。

## 二、能力映射 / Capability Mapping

```text
- capability_id: instrument-query-runtime-contract
- capability_name: 合约查询运行时契约 / Instrument query runtime contract
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：runtime query contract、adapter query bootstrap、当前 change 三件套。
2. 禁止修改：完整 `InstrumentProvider`、symbol normalization、Topic 3/4 代码。
3. 当前正式入口必须继承 Topic 1 冻结的 `ctp_nautilus_live_smoke.py` 口径，不得新造 live baseline。
4. AI 开始前必须阅读：Topic 1 roadmap、当前 topic README、sibling `acceptance.md`。
5. 改完后必须执行：`python -m pytest`。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 instrument query command/event 边界 | topic C1 | runtime / adapter files | 稳定 query contract | `python -m pytest` | topic README | 后续 change 不再重定义 query interface | 已完成 |
| P2 | 定义最小 query bootstrap 入口 | acceptance | adapter / scripts / docs | 最小 query 验证入口 | `python -m pytest` | architecture doc | 后续 C2/C3 可直接复用 | 已完成 |
| P3 | 回写 topic 队列与长期规则 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 2 可继续推 C2 | 已完成 |

## 八、执行结果

1. 新增 Python query runtime：`/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/query.py`
2. 共享 `runtime_bridge` 已接入 query state
3. `CtpInstrumentProvider` 已具备最小 query bootstrap 与 callback 语义
4. Rust placeholder 已对齐 `QUERY_INSTRUMENTS -> INSTRUMENT -> INSTRUMENT_END`

## 九、验证记录

1. `python -m pytest`
2. `python -m pip install -e .`

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

1. Topic 2 后续 change 必须继承 `QUERY_INSTRUMENTS -> INSTRUMENT* -> INSTRUMENT_END` 这条 contract
2. `INSTRUMENT_END` 是正式结束语义，后续不得退回隐式结束
3. Query bootstrap 必须复用共享 `runtime_bridge`

## 十一、证据

1. `./evidence_20260402_instrument_query_runtime_contract.md`
