# <proposal-title>

<!-- PROPOSAL-ANTI-DRIFT-GATE:v1 -->
<!-- PROPOSAL-ADR-CARRIER-GATE:v1 -->

**proposal-id**：`<proposal-id>`
**状态**：draft
**范围**：<一句话说明 proposal 覆盖范围>

| 顶部状态块 / Top Status Block | 值 |
| --- | --- |
| ADR carrier | no |
| Primary ADR | not_applicable |
| Carrier naming note | not_applicable |
| Tracer input case dir | not_applicable |
| Tracer case id | not_applicable |
| Tracer case ref | not_applicable |
| Work item type | governance / delivery / tracer |
| Work item layer | proposal |
| Surface mode | none / ui / report / board / console |
| Action mode | read_only / request_only / execution_capable |
| CTP account profile | repo-only / openctp-paper / formal-trading / not_applicable |
| CTP config path | not_applicable |
| CTP evidence class | repo-only / paper-simulation / formal-broker / not_applicable |

> 适用前提：proposal 用于“很多步骤、需要多 phase 推进”的正式任务容器；若单个 child change 就能完整闭环，不必建立 proposal。
>
> 状态口径：本页顶部 `**状态**` 只是 human-readable projection；proposal 级唯一 machine-readable 主状态源是 `phase-plan.md` 中 `AI-PHASE-STATUS` 区块的 `overall_status`。
>
> Topic 边界：topic 不作为 proposal 推进容器；`topic-id` 只允许作为 child change `plan.md` frontmatter 标签和 `--by-topic` 分组维度。
>
> Workflow 边界：`docs/workflows/` 只定义 reusable fragments / gate specs；本 proposal 的 phase、queue、acceptance 和 evidence 仍由本目录与 child changes 承载。

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

> 当 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status` 进入 `completed`，且 `reviewed_at >= 2026-05-22` 时，本节由 `python scripts/check_proposal_docs.py --root .` 检查。

若 proposal 产生稳定架构、owner、public entry、reader/writer、gate 或长期语义结论，必须用 `required` 行指向已经回流的 ADR、architecture、ownership、runbook 或等价长期文档。

ADR carrier proposal 还必须在 `phase-plan.md` 和 `acceptance.md` 中完成 Primary ADR 的 Decision Coverage IDs 与后续验收场景映射；ADR carrier acceptance rows are incomplete until mapped.

若本 proposal 只留下局部 evidence，不产生稳定规则毕业，必须保留明确声明：

No stable rule graduation: proposal-local evidence only.

| Graduation item | Policy | Target | Status |
| --- | --- | --- | --- |
| ADR backfill | required | docs/adr/<adr-file>.md | not_started / not_applicable / verified after closeout |
| Architecture / ownership backfill | required | docs/architecture/<architecture-file>.md | not_started / not_applicable / verified after closeout |
| Proposal-local evidence | archive_only | acceptance.md | not_started / verified after closeout |

## 文档地图 / Document Map

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | proposal 概览、评审结论、现实状态快照 | 必需 |
| `phase-plan.md` | phase 状态板与 artifact trust boundary | 必需 |
| `acceptance.md` | proposal 级初步验收基线 | 必需 |
| `docs/workflows/` | 可复用 workflow/gate 规范来源；不是本 proposal 状态源 | reference-only |
| `issue-list.md` | 持续曳光弹 / tracer proposal 的问题账本；把当前遗留问题映射到本 proposal 验收，并为下一枚 tracer 留 carry-forward 输入 | tracer/cross-tracer proposal 必需 |

## 稳定化规则 / Stabilization Rules

1. 本目录承载的是 proposal，不等于 stable architecture。
2. proposal 中已经收敛为稳定结论的内容，应回写到 `docs/architecture/` 或 `docs/adr/`。
3. 本页顶部 `**状态**` 必须投影自 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status`，不得与 phase-plan 各自独立维护。
4. proposal 的 AI 追踪状态板只回答“这条 proposal 的收敛进度如何”，不替代 `proposal + change` 的正式执行状态源。
5. 若 proposal 属于持续曳光弹 / tracer / cross-tracer 研发，必须维护 `issue-list.md`：把当前发现的问题、根因、当前验收落点、是否 carry-forward 到下一枚 tracer 写成可复用账本，不能只散落在 acceptance 或聊天记录里。
6. 若使用 Work Item Contract metadata，必须对齐 `docs/workflows/work-item-type-system.md`，不得新增 `proposal_type`、`proposal_profile` 或 `change_kind` 作为第二分类体系。
7. P070 及之后的新 tracer proposal 必须把顶部状态块中的 `Tracer input case dir`、`Tracer case id`、`Tracer case ref` 填成真实独立 input 绑定；不得复用上游 tracer 的 input 目录。
8. 若本 proposal 需要 CTP live front 或账号证据，顶部状态块必须填写 `CTP account profile`、`CTP config path` 和 `CTP evidence class`；profile 规则以 `docs/changes/20260607__openctp-tts__test-baseline/runbook.md` 为准。
