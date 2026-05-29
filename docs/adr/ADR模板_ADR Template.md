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
- 覆盖摘要：decision 0/N, implementation 0/N, retirement 0/N 或 不适用；默认优先用 `0/N`，不要用百分比，除非分母在文中被明确冻结且不会引起歧义
- 适用范围：`D:\Nautilus\nautilus_ctp_adapter`
- 决策问题：一句话写清“要决定什么”。
- 当前倾向：一句话写当前推荐候选；若仍在评审中，可写“评审中”。
- 最终决策：仅在 Section 4 确认后填写；pre-decision 阶段写 `待决策`。

---

## 0. 使用说明

1. 该模板默认参考 [ADR-0028](../../../DSLresearch/docs/adr/0028-factor-board-read-model-without-acceptance-ledger-scan.md) 的论证骨架。
2. 标题、一级结论与关键 section 默认使用中英双语；正文说明以中文为主，关键术语保留英文。
3. `决策状态` 表达 ADR 是否已形成架构结论；`落地状态` 表达实现或退役是否完成；不得用一个“状态”同时表达两者。
4. 本模板采用“core + optional fragments”口径：默认先完成核心 section，再按风险补充 fragment；不要为了凑模板而重复写相同内容。
5. `Landing Map / 落地映射` 保留在 ADR 中，是为了表达 architecture rollout shape、proposal/change 承接关系与 legacy retirement 闭环；它不是 proposal `phase-plan.md` 的替代物，也不是实时执行状态源。
6. 若存在已批准的 proposal 或 child change，应在 `Landing Map / 落地映射` 中写明对应 proposal / change / evidence 落点；实时 phase 状态仍以 proposal `phase-plan.md` 与 child change 为准。
7. 未经用户明确确认，不得在 ADR 中默认引入 fallback / compat / retry / silent downgrade 方案作为推荐决策。
8. 若原有 ADR 的核心决策不变，只是在其上新增补充方案，默认不要重写原 ADR 主体；优先新增 proposal / change 承接补充执行，并在原 ADR 中回填承接关系。只有当该补充本身形成新的长期架构结论时，才新增一个 supplement ADR，并明确写清它与原 ADR 的补充关系，而不是标记 superseded。
9. **何时应改用 proposal 承接，而非在 ADR 中展开 / When to Hand Off to a Proposal**：以下任一条件成立时，相关内容必须移出 ADR、改由 proposal 或 child change 承接，不得在 ADR 中直接展开：
	1. 需要记录逐 phase 的执行状态（哪一步做完、哪一步还没开始）——这是 `phase-plan.md` 的职责。
	2. 需要记录可随实现迭代更新的 acceptance evidence（真实命令、artifact 路径、gate 结果、截图、run id）——这是 `acceptance.md` 的职责。
	3. 需要为 AI 执行写操作约束或禁止行为（`ai_constraints.md`），确保执行不偏离架构决策。
	4. 内容超过一个 child change 的范围，需要分 phase 落地且各 phase 有独立验收——整体由 proposal 统领，ADR 只保留架构锚点与 proposal 承接关系。
	5. 该内容在决策冻结后仍会频繁变更——ADR 只记录初始状态，后续更新应反映在 proposal acceptance 中，并在 ADR 的 `Landing Map` 里以 `completed via Pxxx Phase N` 收口。
	判断口诀：ADR 回答"架构上决定做什么、不做什么"；proposal/change 回答"现在做到哪一步、怎么证明做完"。两者分离，不互相替代。
10. **设计内核与实施计划分离 / Design Kernel vs Implementation Plan**：ADR 保留 design kernel，proposal `phase-plan.md` / `acceptance.md` 承载 implementation plan。ADR 中可以写稳定的组件职责、数据流、owner / truth-source / write-authority 边界、negative constraints 与 accepted 条件；不得在 ADR 中写入 future implementation acceptance，不得在 ADR 中写入逐 phase 的详细实施验收、测试命令、文件级改动计划或 closeout evidence。
11. **Closeout 沉淀不是 acceptance 复制 / ADR Closeout Distillation Is Not Acceptance Copy-Paste**：ADR closeout 时应把稳定结论抽回长期文档，把一次性证据留在 successor proposal / child change。不要把 `acceptance.md`、命令输出、artifact 路径或临时截图整段复制进 ADR；只沉淀稳定约束、导航入口与退役结果。

### ADR 类型分流 / ADR Type Routing

| 类型 | 适用场景 | 必填 section |
| --- | --- | --- |
| `lightweight` | 命名、文档结构、低风险策略或不改变正式 owner / runtime / schema 的小型决策 | 核心 1、2、3、4、7；5、6 与 optional fragments 可写不适用 |
| `standard` | 影响 owner、public entry、schema、runtime、UI projection、verifier 或正式入口的决策 | 核心 1-7；4.4 必填 |
| `governance` | 涉及 authority、truth source、owner 退役、cross-case evidence、AI 控制面语义或防分叉收口的决策 | 核心 1-7；4.4 与 5.1 必填；高风险时补 Red Lines fragment |

### 推荐填写顺序 / Recommended Fill Order

ADR 分两阶段填写，**决策前不得填写后决策内容**：

**阶段一：评审前（pre-decision）** — Section 1-3 可提前填写，Section 4 在评审收敛后填：

| Section | 内容 | 状态 |
| --- | --- | --- |
| 1. Problem Frame | 问题、目标、约束、非目标、owner 影响 | ✅ 可提前 |
| 2. 与既有 ADR 的关系 | 依赖、继承、替代关系 | ✅ 可提前 |
| 3. 方案对比 | 列出候选方案；结论列可写“评审中” | ✅ 可提前 |
| 4. 决策 | 选定方案、边界、推荐产物、coverage matrix | ⚠️ 评审收敛后填 |

**阶段二：决策后（post-decision）** — Section 5-7 与 optional fragments 须在 Section 4 确认后才填写：

| Section | 内容 |
| --- | --- |
| 5. Landing Map | rollout shape、proposal/change 承接关系、退役表 |
| 6. Acceptance And Evidence | architecture-level acceptance、handoff evidence |
| 7. Related Documents | change / runbook / proposal 链接 |
| Optional Fragments | Red Lines、单独列出的 Explicit Non-Goals |

---

## 1. Problem Frame / 问题框架

至少覆盖：

1. 当前现象与触发场景。
2. 已知根因或当前可验证假设。
3. 这次想达到的目标，以及不允许引入什么退化或混层行为。
4. 硬约束与 out of scope。
5. 当前仓库事实、已有实现、历史 change / ADR 的已知边界。
6. 候选概念、命名或术语与仓库现有 canonical vocabulary 的冲突风险。

### 1.1 Hard Constraints / 硬约束

1. 约束 1。
2. 约束 2。
3. 约束 3。

### 1.2 Explicit Non-Goals / 明确不做

1. 不在本 ADR 中解决的事项 1。
2. 不在本 ADR 中解决的事项 2。

### 1.3 Owner / Canonical Entry Impact

1. 是否新增或修改 public entry / facade / writer / reader / mapper / loader / config。
2. 是否改变 canonical owner；若改变，写清旧 owner、新 owner 与 caller/import guard。
3. 是否需要旧路径退役；若需要，必须在 Section 5.1 写入退役表。
4. 若本 ADR 不影响 owner / canonical entry，明确写 `无 owner / canonical entry 影响`。

### 1.4 概念判重 / Canonical Naming Check

本节是新 ADR 的命名防冲突闸口。若本 ADR 引入、重定义、细化或公开暴露任何 AI-facing 概念、状态、rule family、surface label、schema 字段、artifact 名称、CLI 术语或 proposal / change 命名，必须先在这里完成判重；不能等到 implementation 或 review 时再补。

至少覆盖：

1. 候选 canonical term 是什么；中文、英文、缩写是否一致。
2. 它属于哪一层：control loop、formal run、decision、lifecycle、projection、surface、rule family 或其他明确 owner 层。
3. 仓库内现有最接近的 canonical term、ADR、owner page、registry 或 schema 是什么。
4. 哪些旧词、近义词、裸词、历史别名或 UI label 容易混淆，必须显式禁止或降级为 legacy/reference-only。
5. 若名称仍沿用旧词，为什么不会形成第二语义、第二 owner 或跨层误读。
6. 需要补哪些机器约束：semantic vocabulary、CONTRACT-LOCK、docs gate 或 focused tests。

推荐最小表：

| Candidate term | Layer / Owner | Existing nearby term | Collision risk | Decision | Guard / Evidence |
| --- | --- | --- | --- | --- | --- |
| `example_term` | `runtime` / owner page or ADR | `runtime_event_batch` | AI may treat it as per-event callback path | rename / reuse / reject / legacy-only | contract-lock / ADR / focused test |

---

## 2. 与既有 ADR / Architecture 的关系 / Relationship To Existing Decisions

1. 本 ADR 与哪些现有 ADR、architecture 文档、topic 或 change 有依赖关系。
2. 本 ADR 是补充、收紧、替代，还是局部具体化已有结论。
3. 若存在上位长期方向，说明本 ADR 如何把它收敛成可实施约束。
4. 若只是 rollout 或 phase 拆分，不要把执行面塞回 ADR，改由 proposal/change 承接。

---

## 3. 方案对比 / Options Comparison

先写一段总说明，解释本次对比不只比较“能不能做”，还比较性能、truth-source 分层、长期扩展性、治理成本与退役成本。

| 方案 | 核心思路 | 适用场景 | 优点 | 缺点 / 风险 | 架构一致性 | 实施成本 | 结论 | 采纳与落地 / Decision + Landing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. 方案名称 | 一句话说明 | 何时适用 | 优点 | 缺点 | 高 / 中 / 低 | 高 / 中 / 低 | 推荐 / 过渡 / 拒绝 / 评审中 | accepted + implemented / accepted + planned / future extension / rejected / superseded |
| B. 方案名称 | 一句话说明 | 何时适用 | 优点 | 缺点 | 高 / 中 / 低 | 高 / 中 / 低 | 推荐 / 过渡 / 拒绝 / 评审中 | future extension |
| C. 方案名称 | 一句话说明 | 何时适用 | 优点 | 缺点 | 高 / 中 / 低 | 高 / 中 / 低 | 推荐 / 过渡 / 拒绝 / 评审中 | rejected |

### 3.1 Landing Evidence / 落地证据

| 方案 | decision_state | landing_state | evidence_state | evidence_ref | residual_risk |
| --- | --- | --- | --- | --- | --- |
| A | accepted / included / future / rejected / superseded | implemented / partially_implemented / not_implemented / rejected_not_applicable | contract_locked / docs_only / missing_evidence / not_applicable | test path / gate command / proposal / change | remaining risk or `无` |

推荐枚举 / Recommended Enum Values:

1. `decision_state`: `accepted` / `included` / `future` / `rejected` / `superseded`。
2. `landing_state`: `implemented` / `partially_implemented` / `not_implemented` / `rejected_not_applicable`。
3. `evidence_state`: `contract_locked` / `docs_only` / `missing_evidence` / `not_applicable`。
4. 不使用 `80%`、`基本完成`、`差不多完成` 这类主观完成度表达。

### 3.2 架构一致性分析 / Architecture Consistency Analysis

本节用于显式回答候选方案与仓库既有 architecture、owner、truth source、正式入口和退役约束是否一致；不能只把“一致性”藏在方案表的单个单元格里。

至少覆盖：

1. 哪个方案与当前 binding architecture 最一致，为什么。
2. 哪个方案会导致第二 owner、第二 truth source、第二 mainline 或 host/runtime 混层。
3. 哪个方案只可作为 future extension，进入正式主线前还缺什么量测或治理前提。

### 3.3 取舍说明 / Trade-Off Notes

对每个被拒绝或仅保留为过渡的方案，明确写出：

1. 为什么它不能作为长期正式方案。
2. 若允许短期存在，它只能存在于哪个 phase、哪个边界内。
3. 何时必须退出正式路径。

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

至少覆盖：

1. 稳定组件和职责边界。
2. 数据流方向和 truth source 边界。
3. owner / canonical entry / write authority 边界。
4. 不可违反的 negative constraints。
5. 与 successor proposal 的接口或 handoff 粒度。

### 4.4 推荐产物 / Recommended Deliverables

1. 新 contract。
2. 新 projection / manifest / artifact。
3. 新测试锁。
4. 需要同步更新的文档。

### 4.5 决策覆盖与落地矩阵 / Decision Coverage And Landing Matrix

`standard` / `governance` ADR 必填；`lightweight` ADR 可写 `不适用`。本矩阵用于回答“方案是否已被 proposal/change 承接、是否已实现、是否有 executable evidence、旧路径是否已退役”。

若需要人读层面的落地进度，优先把它投影成 `decision 0/N, implementation 0/N, retirement 0/N` 这类覆盖摘要；不要把 `verified/implemented/retired` 强行折算成百分比，除非分母、统计口径和排除项都已冻结。

| 决策项 | 必须覆盖的落点 | 覆盖状态 | 承接 proposal / change | executable evidence | docs evidence | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
| D1. 决策项名称 | contract / owner / runtime / docs | planned | Pxxx / YYYYMMDD__... | 待补 | ADR / runbook / README | 待补 |

覆盖状态语义 / Coverage Status:

1. `not_covered`：ADR 已写，但没有 proposal / change / test / docs 承接。
2. `planned`：已有 proposal 或 phase 计划，但没有 active child change。
3. `active`：已有 active child change 正在落地。
4. `implemented`：代码或文档已改，但尚未有完整 executable evidence。
5. `verified`：已有测试、gate 或 artifact evidence 证明覆盖。
6. `retired`：旧路径已退役，且有防回退证据。
7. `superseded`：该决策项被后续 ADR 或 architecture 文档替代。

---

> ⚠️ **决策门 / Decision Gate**：以下 Section 5-7 与 optional fragments 须在 Section 4 决策确认后才填写。若决策尚未收敛，请在各 section 标注 `（待决策后填写）`，不要提前写入具体 rollout 或红线。

---

## 5. Landing Map / 落地映射

若本 ADR 仍处于 pre-decision，或 ADR 类型为 `lightweight` 且不需要落地映射，本 section 写 `（待决策后填写 / 不适用）`，不得提前写入具体 phase。

### 5.0 Accepted Decision Boundary / 已接受决策边界

仅在 ADR 已经 accepted 时填写；pre-decision 阶段写 `（待决策后填写）`。

### 5.0.1 Not Accepted By This ADR / 本 ADR 不接受

1. 不接受在本 ADR 中决定的事项。
2. 不接受一次性实施的范围。
3. 不接受会导致 owner 分叉、truth source 分叉或语义污染的路径。

### 5.0.2 Successor Proposal Boundary / 后续 Proposal 边界

若后续需要落地实现，必须由 proposal / child change 承接，并在 proposal `phase-plan.md` / `acceptance.md` 中写清实施步骤、验收矩阵、测试命令、artifact evidence 与 closeout evidence。

ADR 不得替代 successor proposal 的执行台账。

| Phase | 目标 | 承接 proposal / change | 退出条件 | retirement 影响 | 承接状态 / Landing Status |
| --- | --- | --- | --- | --- | --- |
| Phase 0 | ADR 冻结或前置准备 | proposal Pxxx / docs-only | 为什么还不算长期完成 | 是否涉及旧路径 inventory | ADR-only completed / planned via proposal Pxxx |
| Phase 1 | 第一层正式收口 | proposal Pxxx / change YYYYMMDD__... | 进入下一层的前提 | 是否新增 retirement 义务 | planned via proposal Pxxx / active via change YYYYMMDD__... |
| Final | 旧代码退役与文档收口 | proposal Pxxx / change YYYYMMDD__... | 旧路径已退役或明确写清残留边界与最终移除条件 | retired / residual boundary | completed via Pxxx Phase N / retired |

推荐状态值 / Recommended Status Values:

1. `ADR-only completed`：本 phase 只完成架构定性或文档冻结，尚未进入 proposal 执行。
2. `planned via proposal Pxxx`：已明确由某个 proposal 承接，但 proposal / change 尚未实际开工。
3. `active via change YYYYMMDD__...`：对应 child change 已经进入 active execution。
4. `completed via Pxxx Phase N`：该层已经由 proposal 的某个 phase 完成落地。
5. `retired`：仅用于最终退役层，表示旧路径已正式退出。

### 5.1 旧代码退役与文档收口 / Legacy Retirement And Documentation Closure

| 旧项 / 路径 | 当前职责 | 新归宿 / 替代物 | 处理动作 | 暂留边界 | 最终移除条件 | 文档同步项 | 承接状态 / Landing Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `old/path.py` | 旧职责 | `new/path.py` 或新 contract | 删除 / 降级为 debug-only / 重写 | 为什么暂时保留 | 何时必须删除 | ADR / change / runbook / README | planned via proposal Pxxx / active via change YYYYMMDD__... / retired |

---

## 6. Acceptance And Evidence / 验收与证据

若本 ADR 仍处于 pre-decision，或 ADR 类型为 `lightweight` 且没有 implementation child change，本 section 写 `（待决策后填写 / 不适用）`。

### 6.0 ADR-Level Acceptance Only / 仅限 ADR 级验收

本 section 只回答“本 ADR accepted 需要什么”。若需要证明某个实现 phase 已完成，应写入 successor proposal `acceptance.md`，而不是写入本 ADR。

不得在 ADR 中写入 future implementation acceptance；不得在 ADR 中写入逐 phase 的详细实施验收。

### 6.1 通用规则 / General Rules

1. 每个 child change 在回填 `acceptance.md` 前，先补对应 `[CONTRACT-LOCK]` 测试。
2. 正式验收只认结构化证据：contract tests、定向行为测试、性能结果、文档回填与 evidence path。
3. 不得以人工点页面、口头结论或临时截图替代正式验收。

### 6.2 Architecture-Level Acceptance

1. 哪些决策项必须进入 `verified` 或 `retired` 才算 ADR 真正落地。
2. proposal / change 至少要提供哪些 executable evidence，ADR 才能从 `planned/active` 升到 `implemented/verified`。
3. 哪些 docs evidence 必须同步回填，才能视为落地闭环。
4. 若存在 retirement，写明旧代码退役、旧文档收口与最终残留说明。

### 6.3 ADR Closeout Distillation / ADR closeout 沉淀

本节在 ADR 对应的 proposal / child change closeout 后填写；若当前 ADR 仍在 `planned` / `active`，写 `（closeout 后回填）`。

本节只负责把**稳定结论**沉淀回长期文档，不复制一次性 evidence。

| Distillation target | Stable conclusion distilled from this ADR | Source proposal / change / evidence | Do not copy forward | Closeout action |
| --- | --- | --- | --- | --- |
| `docs/architecture/...` | 长期边界、owner、truth source 或 negative constraint | Pxxx / change / test / gate | 命令输出、artifact 细节、截图 | update canonical doc / not_needed |
| `docs/adr/README.md` | binding / legacy / superseded 状态与一句话约束 | ADR + closeout evidence | phase 进度、临时计划 | update index / not_needed |
| `docs/runbooks/...` | canonical entry、操作口径、退役说明 | change / runtime evidence | acceptance 明细 | update runbook / not_needed |

Closeout checklist / 推荐检查项:

1. 本 ADR 的稳定结论是否已经被某个 canonical 文档吸收，而不只停留在 ADR 本文。
2. `docs/adr/README.md` 与 `docs/architecture/README.md` 是否已反映当前 authority。
3. 若影响 owner / canonical entry / runbook，相关长期入口是否已经同步。
4. 若有旧文档、旧术语、旧路径退役，是否已在 `Landing Map` 或退役文档中收口。

---

## 7. Related Documents / 关联文档

1. 相关 ADR。
2. 对应 architecture 文档。
3. 对应 proposal。
4. 当前 child change bundle。
5. 相关 runbook / ownership。

---

## Optional Fragments / 可选片段

### A. Red Lines

1. 红线 1。
2. 红线 2。
3. 红线 3。

### B. Expanded Explicit Non-Goals

1. 不在本 ADR 中决定的事项 1。
2. 不在本 ADR 中决定的事项 2。
3. 不在本 ADR 中决定的事项 3。