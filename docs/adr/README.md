# ADR 索引 / ADR Index

> AI 先读本索引，再按需打开具体 ADR。

- 更新日期：2026-06-10
- 模板入口：[ADR模板 / ADR Template](./ADR模板_ADR%20Template.md)

---

## 0. 使用规则 / Usage Rules

1. 先看本索引确认哪些 ADR 已经形成约束，避免把草稿当成正式口径。
2. `accepted` ADR 才是当前 binding constraint；`proposed` 只代表待评审方向。
3. 若某条结论仍在多 phase 推进，正式执行面应下沉到 proposal + change，而不是把执行状态写进 ADR。
4. 旧 ADR 若只剩历史背景，应移到 Legacy 区，不再充当当前 authority。

---

## 1. 当前约束 ADR / Currently Binding ADRs

| ADR | 标题 | 约束范围 | Landing |
| --- | --- | --- | --- |
| ADR001 | [高性能优先原生主线适配边界 / High-Performance Native-First Adapter Boundary](./ADR001%20%E9%AB%98%E6%80%A7%E8%83%BD%E4%BC%98%E5%85%88%E5%8E%9F%E7%94%9F%E4%B8%BB%E7%BA%BF%E9%80%82%E9%85%8D%E8%BE%B9%E7%95%8C_High-Performance%20Native-First%20Adapter%20Boundary.md) | native-first runtime + thin Python host glue | completed via p001 |
| ADR002 | [OpenCTP TTS / Paper Simulation Test Environment](./ADR002%20OpenCTP%20TTS%20Paper%20Simulation%20Test%20Environment.md) | 默认 paper simulation / development test environment 采用 OpenCTP TTS 7x24；real-account CTP 保留为最终证据路径 | completed via `20260607__openctp-tts__test-baseline` |
| ADR003 | [Doc Harness Capability Replication And Strategies Alignment](./ADR003%20Doc%20Harness%20Capability%20Replication%20And%20Strategies%20Alignment.md) | 本仓 doc / harness 能力缺失时，默认向 `D:\Nautilus\nautilus_strategies` 的治理能力对齐，但保持本仓 local frontier authority | completed via `20260610__governance__adr003-landing-closeout` |
| ADR004 | [Adapter Governance Owner Truth Retirement Boundary](./ADR004%20Adapter%20Governance%20Owner%20Truth%20Retirement%20Boundary.md) | CTP adapter owner registry、truth-source matrix、防 fork 规则与旧代码安全退役边界 | active via architecture governance gate |

---

## 2. 待决策 ADR / Under Decision

| ADR | 标题 | 核心问题 |
| --- | --- | --- |
| 暂无 | 待补 | 当前无 proposed ADR |

---

## 3. Legacy / Reference-Only ADRs

| ADR | 标题 | 说明 |
| --- | --- | --- |
| 暂无 | 待补 | 只作参考，不作为当前约束 |

---

## 4. 新 ADR 创建规范 / New ADR Contract

1. 新 ADR 先从 [ADR模板 / ADR Template](./ADR模板_ADR%20Template.md) 创建。
2. `decision_status` 表示决策是否收敛；`landing_status` 表示实现或退役是否完成；两者不得混写成一个状态。
3. 需要多 phase 推进、多个 child change 映射或 proposal-local 验收时，应把执行面下沉到 `docs/proposals/`。
4. 需要 owner / public entry / runtime / truth source 调整时，必须在 ADR 中写清边界与不允许引入的退化路径。
