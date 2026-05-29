# ADR 索引 / ADR Index

> AI 先读本索引，再按需打开具体 ADR。

- 更新日期：2026-05-26
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
| 暂无 | 待补 | 新增 accepted ADR 后回填 | not_started |

---

## 2. 待决策 ADR / Under Decision

| ADR | 标题 | 核心问题 |
| --- | --- | --- |
| ADR001 | [高性能优先原生主线适配边界 / High-Performance Native-First Adapter Boundary](./ADR001%20%E9%AB%98%E6%80%A7%E8%83%BD%E4%BC%98%E5%85%88%E5%8E%9F%E7%94%9F%E4%B8%BB%E7%BA%BF%E9%80%82%E9%85%8D%E8%BE%B9%E7%95%8C_High-Performance%20Native-First%20Adapter%20Boundary.md) | 在继续支持 Nautilus provider / live client 的前提下，正式高性能主线是否采用 native-first runtime + thin Python glue，以及何时才允许 daemon 化 |

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