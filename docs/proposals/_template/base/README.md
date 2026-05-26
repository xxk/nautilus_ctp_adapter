# <proposal-title>

**proposal-id**：`<proposal-id>`
**状态**：draft
**范围**：<一句话说明 proposal 覆盖范围>

| 顶部状态块 / Top Status Block | 值 |
| --- | --- |
| ADR carrier | no |
| Primary ADR | not_applicable |
| Carrier naming note | not_applicable |

> proposal 用于“很多步骤、需要多 phase 推进”的正式任务容器；若单个 child change 就能完整闭环，不必建立 proposal。

---

## 一句话结论

<用 1-2 句写清 proposal 想解决什么问题、当前是否已经过评审。>

## 目标 / Goals

1. <目标 1>
2. <目标 2>
3. <目标 3>

## 非目标 / Non-Goals

1. <明确不做 1>
2. <明确不做 2>

## 评审结论 / Review Verdict

**当前结论**：draft

| 项 | 结论 |
| --- | --- |
| 是否进入正式 proposal | 待评审 |
| 是否需要 child change | 待评审 |
| 是否有 artifact trust boundary | 见 `phase-plan.md` |

## 当前状态快照 / Reality Snapshot

| 维度 | 当前事实 | 证据 |
| --- | --- | --- |
| 代码状态 | 待补 | <路径或命令> |
| 文档状态 | 待补 | <路径> |
| 验收状态 | 待补 | `acceptance.md` |

## Graduation / Closeout Matrix

若 proposal 产生稳定架构、owner、public entry、gate 或长期语义结论，必须用 `required` 行指向已回流的 ADR、architecture、runbook 或等价长期文档。

若本 proposal 只留下局部 evidence，不产生稳定规则毕业，必须保留明确声明：

No stable rule graduation: proposal-local evidence only.

| Graduation item | Policy | Target | Status |
| --- | --- | --- | --- |
| ADR backfill | required | docs/adr/<adr-file>.md | planned |
| Proposal-local evidence | archive_only | acceptance.md | planned |

## 文档地图 / Document Map

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | proposal 概览、评审结论、现实状态快照 | 必需 |
| `phase-plan.md` | phase 状态板与 artifact trust boundary | 必需 |
| `acceptance.md` | proposal 级验收基线 | 必需 |

## 稳定化规则 / Stabilization Rules

1. proposal 不等于 stable architecture。
2. proposal 中已经收敛为稳定结论的内容，应回写到 `docs/architecture/` 或 `docs/adr/`。
3. 本页顶部 `**状态**` 必须投影自 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status`。
4. proposal 的 AI 跟踪状态只回答收敛进度，不替代正式执行状态源。# <proposal-title>

**proposal-id**：`<proposal-id>`
**状态**：draft
**范围**：<一句话说明 proposal 覆盖范围>

| 顶部状态块 / Top Status Block | 值 |
| --- | --- |
| ADR carrier | no |
| Primary ADR | not_applicable |
| Carrier naming note | not_applicable |

---

## 一句话结论

<用 1-2 句写清 proposal 想解决什么问题、当前是否已经过评审。>

## 目标 / Goals

1. <目标 1>
2. <目标 2>
3. <目标 3>

## 非目标 / Non-Goals

1. <明确不做 1>
2. <明确不做 2>

## 评审结论 / Review Verdict

**当前结论**：draft

| 项 | 结论 |
| --- | --- |
| 是否进入正式 proposal | 待评审 |
| 是否需要 child change | 待评审 |
| 是否有 artifact trust boundary | 见 `phase-plan.md` |

## 当前状态快照 / Reality Snapshot

以下状态以本地代码、测试、已完成 changes 与相关文档为准，而不是只按 proposal 正文判断：

| 维度 | 当前事实 | 证据 |
| --- | --- | --- |
| 代码状态 | 待补 | <路径或命令> |
| 文档状态 | 待补 | <路径> |
| 验收状态 | 待补 | `acceptance.md` |

## Graduation / Closeout Matrix

若 proposal 产生稳定架构、owner、public entry、reader/writer、gate 或长期语义结论，必须用 `required` 行指向已经回流的 ADR、architecture、runbook 或等价长期文档。

若本 proposal 只留下局部 evidence，不产生稳定规则毕业，必须保留明确声明：

No stable rule graduation: proposal-local evidence only.

| Graduation item | Policy | Target | Status |
| --- | --- | --- | --- |
| ADR backfill | required | docs/adr/<adr-file>.md | planned |
| Architecture backfill | required | docs/architecture/<architecture-file>.md | planned |
| Proposal-local evidence | archive_only | acceptance.md | planned |

## 文档地图 / Document Map

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | proposal 概览、评审结论、现实状态快照 | 必需 |
| `phase-plan.md` | phase 状态板与 artifact trust boundary | 必需 |
| `acceptance.md` | proposal 级初步验收基线 | 必需 |

## 稳定化规则 / Stabilization Rules

1. 本目录承载的是 proposal，不等于 stable architecture。
2. proposal 中已经收敛为稳定结论的内容，应回写到 `docs/architecture/` 或 `docs/adr/`。
3. 本页顶部 `**状态**` 必须投影自 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status`，不得与 phase-plan 各自独立维护。
4. proposal 的 AI 追踪状态板只回答“这条 proposal 的收敛进度如何”，不替代 `proposal + change` 的正式执行状态源。