---
change-id: "20260402__nautilus-instrument-provider__instrument-smoke-baseline"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-instrument-provider__instrument-provider-bootstrap"
      reason: "需要先继承已冻结的 provider bootstrap 和输出模型"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Instrument Smoke Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、当前 change 三件套
**topic-id**：nautilus-instrument-provider
**change-id**：20260402__nautilus-instrument-provider__instrument-smoke-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 InstrumentProvider 方向的正式 smoke 入口与证据格式。
2. 使用本仓本地 `c wrapper` 路径留证真实 instrument query，而不是停留在模拟 callback。
3. 为 Topic 3 提供可复用的 instrument smoke 入口。

## 二、能力映射 / Capability Mapping

```text
- capability_id: instrument-smoke-baseline
- capability_name: 合约查询 smoke 基线 / Instrument smoke baseline
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：instrument smoke 入口、provider live query glue、当前 change 三件套。
2. 禁止修改：Topic 1 baseline、完整 marketdata/execution 实现。
3. 改完后必须执行：`python scripts/ctp_instrument_query_smoke.py --config <path> --symbol rb2610` 与 `python -m pytest`。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 instrument smoke 正式入口 | topic C4 | scripts/provider files | 正式 smoke 入口 | real smoke + `python -m pytest` | topic README | 后续 topic 不再自定义 instrument smoke 口径 | 已完成 |
| P2 | 留证真实 instrument query 结果 | acceptance | 当前 change 三件套 | 真实 evidence bundle | real smoke | docs index | `rb2610` 实盘合约查询可复现 | 已完成 |
| P3 | 回写 Topic 2 完成状态 | governance | topic README / mainline roadmap | Topic 3 可激活 | 文档检查 | mainline roadmap | Topic 2 达到出口条件 | 已完成 |

## 八、验证记录

1. `python scripts\ctp_instrument_query_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --symbol rb2610 --timeout-seconds 20`
2. `python -m pytest`

## 九、证据

1. `./evidence_20260402_instrument_smoke_baseline.md`
