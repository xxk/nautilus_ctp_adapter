---
change-id: "20260402__nautilus-instrument-provider__exchange-and-symbol-normalization"
dependencies:
  hard_blocking:
    - id: "20260402__nautilus-instrument-provider__instrument-query-runtime-contract"
      reason: "需要先继承已冻结的 query contract"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Exchange And Symbol Normalization 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`src/nautilus_ctp_adapter/runtime/`、当前 change 三件套
**topic-id**：nautilus-instrument-provider
**change-id**：20260402__nautilus-instrument-provider__exchange-and-symbol-normalization
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 CTP `exchange/symbol/product kind` 到 Nautilus 侧中间模型的归一化规则。
2. 明确本 change 不做完整 `InstrumentProvider`，只做 normalization rule。
3. 为 Topic 2 的 `C3` 提供稳定的 symbol/exchange 输入输出。

## 二、能力映射 / Capability Mapping

```text
- capability_id: exchange-symbol-normalization
- capability_name: 交易所与符号归一化 / Exchange and symbol normalization
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：normalization helpers、runtime/query parsing、当前 change 三件套。
2. 禁止修改：完整 `InstrumentProvider`、Topic 3/4 代码、Topic 1 baseline。
3. AI 开始前必须阅读：当前 topic README、`C1` 的 `acceptance.md` 与 evidence。
4. 改完后必须执行：`python -m pytest`。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 exchange 映射规则 | topic C2 | adapter/runtime files | 稳定 exchange normalization | `python -m pytest` | topic README | 后续不再重定义交易所映射 | 已完成 |
| P2 | 冻结 symbol / product kind 归一化规则 | acceptance | adapter/runtime/docs | 稳定 symbol normalization | `python -m pytest` | architecture doc | 后续 C3 可直接消费 | 已完成 |
| P3 | 回写 topic 队列与长期规则 | governance | 当前 change 三件套 / topic README | 可交接结论 | 文档检查 | mainline roadmap | Topic 2 可继续推 C3 | 已完成 |

## 八、执行结果

1. 新增 normalization helper：`/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/normalization.py`
2. `InstrumentProvider` 已能返回 normalized instrument view
3. 交易所 alias、symbol case、product kind、contract month 提取规则已集中冻结

## 九、验证记录

1. `python -m pytest`
2. `python -m pip install -e .`

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

1. Topic 2 后续 change 必须复用统一 normalization helper
2. `SHFE/DCE/INE/GFEX -> lower-case symbol`
3. `CZCE/CFFEX -> upper-case symbol`
4. `CZCE 4位/3位月份转换` 暂不在本 change 处理

## 十一、证据

1. `./evidence_20260402_exchange_and_symbol_normalization.md`
