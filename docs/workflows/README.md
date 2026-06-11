# Workflows / 工作流规范

**创建日期**：2026-06-07
**状态**：binding-specification
**Authority boundary**：本目录定义“工作如何被规划、拆分、约束、验收、gate”。它不是新的执行状态源。

---

## One-Line Boundary / 一句话边界

```text
docs/workflows/ defines reusable template and gate shapes.
docs/proposals/<proposal-id>/ owns proposal phases and roll-up acceptance.
docs/changes/<change-id>/ owns executable plan, tests and acceptance evidence.
```

## Purpose / 目的

本目录是 ADR003 的首批 workflow 对齐落点。它从 `D:\Nautilus\nautilus_strategies\docs\workflows\` 裁剪治理能力，但保留本仓 Route B authority：

1. `docs/workflows/` 只定义 reusable work item metadata、fragments 与 gate shape。
2. proposal 实例仍落在 `docs/proposals/<proposal-id>/`。
3. 可执行状态仍落在 `docs/changes/<change-id>/plan.md`。
4. 真实证据仍落在 child change `acceptance.md` 或明确声明的 artifact root。

ADR003 closeout status:

1. 本目录已经成为本仓 binding workflow specification。
2. 后续若继续补 profile-aware validation，应在本仓 change 中推进，而不是把外部仓目录直接当作运行时依赖。

## Non-Goals / 非目标

1. 不在本目录存放 active proposal phase status。
2. 不在本目录存放 concrete `tracer-manifest.md` 实例。
3. 不在本目录存放 acceptance evidence、run id、artifact evidence 或 current queue marker。
4. 不复制 `nautilus_strategies` 的 portfolio、PM UI、strategy owner 或 GitHub issue lane 语义。

## Directory Map / 目录地图

| Path | Role |
| --- | --- |
| [work-item-type-system.md](work-item-type-system.md) | Canonical type/layer/mode schema |
| [fragments/](fragments/) | Reusable template fragments |
| [gates/](gates/) | Gate designs that scripts may enforce |

Governance fragments and gates:

| Item | Role |
| --- | --- |
| [adr-template-contract.md](fragments/adr-template-contract.md) | ADR creation/edit template contract |
| [adr-template-contract-gate.md](gates/adr-template-contract-gate.md) | Machine-checkable ADR contract gate |

## Start Here / 从这里开始

1. Read [work-item-type-system.md](work-item-type-system.md).
2. Decide whether the work is a Proposal or a Change.
3. For new ADR work, apply [adr-template-contract.md](fragments/adr-template-contract.md).
4. Run `python scripts/check_adr_docs.py --root .` and the aggregate `python scripts/check_harness.py`.

## Executable Gate Boundary / 可执行 Gate 边界

`scripts/check_adr_docs.py` owns the current executable ADR gate.
`scripts/check_proposal_docs.py` owns the current executable proposal template gate.
`scripts/check_harness.py` remains the aggregate docs gate.
