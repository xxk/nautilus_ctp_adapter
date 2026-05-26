# Proposal Index / 提案目录索引

- 创建日期：2026-05-26
- 最后更新：2026-05-26
- 状态：生效

---

## 一句话结论

`docs/proposals/` 用于承载很多步骤、需要多 phase 推进、且单个 child change 无法完整表达的正式提案容器。

它不替代 `docs/adr/`，也不替代 `docs/changes/`；它负责把待推进方案与稳定架构结论、单次执行切片分开。

---

## 与其他目录的边界

1. `docs/adr/`：回答“为什么做这个架构决策”。
2. `docs/proposals/`：回答“这条方案如何拆 phase、如何映射 change、当前收敛到哪一步”。
3. `docs/changes/`：回答“这次 child change 具体改什么、怎么验收”。
4. `docs/architecture/`：承载稳定长期设计结论，不承担 proposal 级执行状态。
5. `docs/topics/`：承载长期 topic queue 与 roadmap，不替代 proposal phase plan。

---

## 适用场景

1. 一项工作明显需要多个 phase 持续推进。
2. 一条方案需要多个 child change 分阶段落地。
3. 方案仍在评审、收敛、拆 phase，而不是稳定结论。
4. 需要把 proposal 主文档、phase 状态、change 映射与验收基线放在同一目录维护。

## 不适用场景

1. 已接受、当前生效且应长期稳定维护的架构结论。
2. 单个 child change 就能完整闭环的任务。
3. 只做历史回溯、不再推进的冷归档内容。

---

## 当前 Proposal

| Proposal | 目录 | 状态 | 说明 |
| --- | --- | --- | --- |
| 暂无 | 待创建 | draft | 使用下方模板入口创建 |

---

## 模板入口

优先使用本仓 proposal scaffold：

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --profile multi_phase
```

校验 proposal 文档闭环：

```bash
python scripts/check_proposal_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id <proposal-id>
```

模板结构位于 `docs/proposals/_template/`：

1. `base/`：每个 proposal 必需文件。
2. `fragments/`：可选附加片段。
3. `profiles/`：常见片段组合。
4. `meta/`：模板使用说明与 fragment registry。

---

## 规则

1. proposal 顶部 `**状态**` 只能投影自 `phase-plan.md` 里的 `AI-PHASE-STATUS.overall_status`。
2. 若 proposal 已产生稳定架构、owner 或 runtime 规则，必须回流到 `docs/adr/`、`docs/architecture/` 或等价长期文档。
3. proposal 验收必须落在 `acceptance.md`，不能只停留在聊天或 issue 备注。
4. proposal 允许承接多个 child change，但 proposal 完成不等于所有 topic closeout；正式执行仍以 proposal + change 为准。# Proposal Index

This directory carries formal proposals that need multiple phases or multiple child changes before they can graduate into stable architecture or ADRs.

## When To Use Proposals

1. The work is too large for a single child change.
2. The plan needs phase-level tracking before implementation is complete.
3. Review conclusions, child-change mapping, and acceptance evidence should stay together under one canonical path.

## Boundaries

1. [docs/architecture/README.md](../architecture/README.md) holds stable design conclusions.
2. [docs/adr/README.md](../adr/README.md) holds architecture decision records and their rationale.
3. [docs/changes/README.md](../changes/README.md) holds executable child changes.
4. Proposal status is tracked inside each proposal's [phase-plan.md](./_template/base/phase-plan.md) `AI-PHASE-STATUS` block; directory-level navigation here is human-readable only.

## Template Entry

1. Template root: [docs/proposals/_template](./_template)
2. Docs gate: `python scripts/check_proposal_docs.py --root .`
3. Scaffold command: `python scripts/new_proposal.py --root . --id <proposal-id> --profile multi_phase`

## Current Proposals

No active proposal bundles yet.