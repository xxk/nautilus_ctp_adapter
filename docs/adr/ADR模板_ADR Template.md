---
status: 待评审
owner: architecture
adr_id: "YYYY"
decision_status: proposed
landing_status: not_started
---

# ADR 模板 / ADR Template

- 日期：`YYYY-MM-DD`
- ADR 类型：lightweight / standard / governance
- 决策状态：draft / proposed / accepted / superseded / archived
- 落地状态：not_started / planned / active / completed / retired
- 落地摘要：not_started / planned via Pxxx / active via change YYYYMMDD__... / completed via Pxxx Phase N
- 覆盖摘要：decision 0/N, implementation 0/N, retirement 0/N 或 不适用
- 适用范围：`D:\Nautilus\nautilus_ctp_adapter`
- 决策问题：一句话写清“要决定什么”。
- 当前倾向：一句话写当前推荐候选；若仍在评审中，可写“评审中”。
- 最终决策：仅在 Section 4 确认后填写；pre-decision 阶段写 `待决策`。

---

## 0. 使用说明

1. ADR 只回答“架构上决定做什么、不做什么”；proposal/change 回答“现在做到哪一步、怎么证明做完”。
2. `决策状态` 与 `落地状态` 必须分离，不能把实现进度写成架构结论。
3. 若需要逐 phase 状态、验收证据、artifact boundary 或 AI 执行约束，必须转到 `docs/proposals/` 或 `docs/changes/`。
4. 未经用户明确确认，不得在 ADR 中默认引入 fallback / compat / retry / silent downgrade 方案作为推荐决策。
5. 若需要 ADR closeout 的作者清单，可参考跨仓手册 [ADR关闭后沉淀手册 / ADR Closeout Distillation Runbook](../../../DSLReserach/docs/runbooks/ADR关闭后沉淀手册_ADR%20Closeout%20Distillation%20Runbook.md)；该链接只用于帮助作者判断稳定结论应沉淀到哪里，不替代本仓 ADR 索引或本仓 proposal/change authority。

### ADR 类型分流 / ADR Type Routing

| 类型 | 适用场景 | 必填 section |
| --- | --- | --- |
| `lightweight` | 低风险命名、文档结构、小范围策略决策 | 核心 1、2、3、4 |
| `standard` | 影响 owner、public entry、schema、runtime 或正式入口 | 核心 1-7 |
| `governance` | 涉及 authority、truth source、owner 收口、跨 change 治理 | 核心 1-7，且 4.4 / 5.1 必填 |

---

## 1. Problem Frame / 问题框架

1. 当前现象与触发场景。
2. 已知根因或当前可验证假设。
3. 本次要达到的目标，以及不允许引入的退化行为。
4. 硬约束与 out-of-scope。
5. 当前仓库事实、已有实现与历史边界。

### 1.1 Hard Constraints / 硬约束

1. 约束 1。
2. 约束 2。
3. 约束 3。

### 1.2 Explicit Non-Goals / 明确不做

1. 不在本 ADR 中解决的事项 1。
2. 不在本 ADR 中解决的事项 2。

### 1.3 Owner / Canonical Entry Impact

1. 是否新增或修改 public entry / facade / loader / config。
2. 是否改变 canonical owner；若改变，写清旧 owner、新 owner 与退役口径。
3. 若不影响 owner / canonical entry，明确写 `无 owner / canonical entry 影响`。

---

## 2. 与既有 ADR / Architecture 的关系 / Relationship To Existing Decisions

1. 本 ADR 与哪些现有 ADR、architecture 文档、topic 或 change 有依赖关系。
2. 本 ADR 是补充、收紧、替代，还是局部具体化已有结论。
3. 若只是 rollout 或 phase 拆分，不要把执行面塞回 ADR，改由 proposal/change 承接。

---

## 3. 方案对比 / Options Comparison

| 方案 | 核心思路 | 适用场景 | 优点 | 风险 | 结论 | 采纳与落地 |
| --- | --- | --- | --- | --- | --- | --- |
| A. 方案名称 | 一句话说明 | 何时适用 | 优点 | 风险 | 推荐 / 评审中 / 拒绝 | accepted + planned |
| B. 方案名称 | 一句话说明 | 何时适用 | 优点 | 风险 | 过渡 / 拒绝 | future extension / rejected |

### 3.1 Landing Evidence / 落地证据

| 方案 | decision_state | landing_state | evidence_state | evidence_ref | residual_risk |
| --- | --- | --- | --- | --- | --- |
| A | accepted | not_implemented | docs_only | proposal / change | 待补 |

---

## 4. 决策 / Decision

### 4.1 决策结论 / Decision Summary

1. 明确采用哪个方案。
2. 明确拒绝哪些方案进入正式长期路径。
3. 明确哪些过渡技术只允许存在于 build-time / migration-time / debug-only 范围。

### 4.2 决策边界 / Decision Boundaries

1. 正式 truth source 是什么。
2. 哪些入口可以读写，哪些不允许跨层。
3. 哪些字段、命令或路径必须收口或删除。

### 4.3 Design Kernel / 设计内核

1. 稳定组件和职责边界。
2. 数据流方向和 truth source 边界。
3. owner / canonical entry / write authority 边界。
4. 不可违反的 negative constraints。

### 4.4 推荐产物 / Recommended Deliverables

1. 新 contract。
2. 新 projection / manifest / artifact。
3. 新测试锁。
4. 需要同步更新的文档。

### 4.5 决策覆盖与落地矩阵 / Decision Coverage And Landing Matrix

| 决策项 | 必须覆盖的落点 | 覆盖状态 | 承接 proposal / change | executable evidence | docs evidence | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
| D1. 决策项名称 | contract / owner / runtime / docs | planned | Pxxx / YYYYMMDD__... | 待补 | ADR / runbook / README | 待补 |

---

## 5. Landing Map / 落地映射

### 5.1 Successor Proposal / Change

1. 本 ADR 若仍需多 phase 推进，写清 successor proposal。
2. 本 ADR 若已有 child change 承接，写清 change id 与职责。
3. 若旧路径需要退役，写清退役闭环与 guard。

---

## 6. Acceptance And Evidence / 验收与证据

1. ADR 级验收只写 accepted 后必须满足的架构级条件。
2. 实际运行命令、artifact 证据、closeout 证据应写入 successor proposal 或 child change。

---

## 7. Related Documents / 关联文档

1. Proposal
2. Change
3. Runbook
4. README / owner page