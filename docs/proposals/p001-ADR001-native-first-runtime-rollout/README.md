# P001 ADR001 Native-First Runtime Rollout / ADR001 原生优先运行时落地提案

**proposal-id**：`p001-ADR001-native-first-runtime-rollout`
**状态**：completed
**范围**：承接 ADR001，把 `native-first runtime + thin Python host glue` 拆成多 phase proposal 与后续 child change，不扩张当前 vendor-bridge active change 的职责。

| 顶部状态块 / Top Status Block | 值 |
| --- | --- |
| ADR carrier | yes |
| Primary ADR | ADR001 |
| Carrier naming note | This proposal carries rollout only; ADR001 remains the long-term decision authority. |

> proposal 用于“很多步骤、需要多 phase 推进”的正式任务容器；若单个 child change 就能完整闭环，不必建立 proposal。

---

## 一句话结论

本 proposal 是 ADR001 的正式落地容器，已把性能路线从“讨论结论”收敛成 `proposal + change` 的执行面，并完成 Phase 1-4 边界冻结。真实 runtime 迁移与 daemon 实现仍需按后续 changes / proposal 承接，不能反向扩张当前 vendor-bridge readiness change。

## 目标 / Goals

1. 冻结 ADR001 的 phase 拆分、child change 映射和 acceptance boundary。
2. 明确 batch boundary、hot-path owner inventory / migration boundary、thin Python shell 与 daemon gate 的落地顺序。
3. 保持当前 active change 只处理 vendor bridge / SDK handoff，不混入性能 rollout 主线。

## 非目标 / Non-Goals

1. 本 proposal 当前不直接实现 external daemon，也不把 pure native plugin / host fork 带入正式执行面。
2. 本 proposal 当前不承诺“性能已达最终上限”；它只负责建立后续自动化推进所需的正式 carrier。
3. 本 proposal 当前不改写 `20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff` 的 scope。

## 评审结论 / Review Verdict

**当前结论**：accepted_for_planning

| 项 | 结论 |
| --- | --- |
| 是否进入正式 proposal | 是；作为 ADR001 的 canonical rollout carrier |
| 是否需要 child change | 是；Phase 1-4 已分别由 `20260529__runtime-performance__p1`、`20260529__runtime-performance__p2-native-hot-path-ownership-cutover`、`20260529__runtime-performance__p3-thin-python-host-glue-contract-lock`、`20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision` 完成 |
| 是否有 artifact trust boundary | 有；见 `phase-plan.md` |

## 当前状态快照 / Reality Snapshot

以下状态以本地代码、已完成 changes 与相关文档为准，而不是只按 proposal 正文判断：

| 维度 | 当前事实 | 证据 |
| --- | --- | --- |
| 代码状态 | Rust runtime / Python adapter split 已存在；P001 已冻结 batch boundary、hot path owner inventory、thin-shell contract 与 benchmark/daemon gate，真实迁移继续由后续 implementation changes 承接 | `docs/architecture/platform-neutral-ctp-runtime.md`；`docs/architecture/rust-python-adapter-split.md`；`docs/changes/20260529__runtime-performance__p2-native-hot-path-ownership-cutover/design.md` |
| 文档状态 | ADR001 已定义正式性能主线；本 proposal 现为其 canonical rollout path | `docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md`；当前 proposal 目录 |
| 验收状态 | proposal 收敛层与 Phase 1-4 child changes 均已完成；P001 closeout 不等于 live performance 或 daemon implementation 已完成 | `acceptance.md`；`docs/changes/20260529__runtime-performance__p1/`；`docs/changes/20260529__runtime-performance__p2-native-hot-path-ownership-cutover/`；`docs/changes/20260529__runtime-performance__p3-thin-python-host-glue-contract-lock/`；`docs/changes/20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision/` |

## Graduation / Closeout Matrix

若 proposal 产生稳定架构、owner、public entry、reader/writer、gate 或长期语义结论，必须用 `required` 行指向已经回流的 ADR、architecture、runbook 或等价长期文档。

No stable rule graduation: proposal-local evidence only.

| Graduation item | Policy | Target | Status |
| --- | --- | --- | --- |
| ADR backfill | required | `docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md` | completed |
| Architecture backfill | required | `docs/architecture/runtime-performance-guidelines.md` and related runtime docs | completed |
| Operator/runbook backfill | required | `scripts/README.md` | completed |
| Proposal-local evidence | archive_only | `acceptance.md` | completed |

## 文档地图 / Document Map

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | proposal 概览、评审结论、现实状态快照 | 必需 |
| `phase-plan.md` | phase 状态板、artifact trust boundary、child change 入口 | 必需 |
| `acceptance.md` | proposal 级验收基线 | 必需 |
| `design.md` | 设计冻结：runtime / adapter / benchmark gate 边界 | 已启用 |
| `change-map.md` | proposal phase 到 child change 的映射 | 已启用 |
| `decision-log.md` | proposal 评审判断和 scope freeze 记录 | 已启用 |

## 稳定化规则 / Stabilization Rules

1. 本目录承载的是 proposal，不等于 stable architecture。
2. proposal 中已经收敛为稳定结论的内容，应回写到 `docs/architecture/` 或 `docs/adr/`。
3. 本页顶部 `**状态**` 必须投影自 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status`，不得与 phase-plan 各自独立维护。
4. proposal 的 AI 追踪状态板只回答“这条 proposal 的收敛进度如何”，不替代 `proposal + change` 的正式执行状态源。
