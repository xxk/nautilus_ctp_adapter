# Design Fragment

**fragment-id**：`design`
**适用场景**：架构设计较复杂，需要独立设计文档。

---

## Design Scope

本 design 冻结 proposal 级设计边界，而不是具体实现细节。它回答三件事：后续 child change 应按什么顺序推进，runtime / adapter / benchmark gate 各自归谁拥有，以及哪些路径明确不允许作为默认性能主线。

## Interfaces

| 接口 / 文件 | Owner | 约束 |
| --- | --- | --- |
| `docs/adr/ADR001 ...` | ADR / architecture | 冻结长期架构结论，不承担 phase 状态 |
| `docs/proposals/p001-ADR001-native-first-runtime-rollout/phase-plan.md` | proposal | proposal 级唯一 machine-readable 状态源 |
| `rust/` + repository-owned native boundary | runtime | 拥有 hot path、queue、normalize、state machine、batch boundary |
| `src/nautilus_ctp_adapter/adapters/ctp/` | host adapter | 只保留 Nautilus host integration，不再扩张 runtime ownership |
| future benchmark gate | proposal phase / child change | benchmark 命令、阈值、formal artifact boundary 与 daemon trigger policy 必须在 child change 中冻结；只有 benchmark 越线时，才允许 daemon proposal 进入评审 |

## Data Flow

1. ADR001 冻结长期主线：`native-first runtime + thin Python host glue`。
2. P001 把 ADR001 拆成 Phase 0-4，并映射到后续 child change。
3. Phase 1 先冻结 adapter-facing batch boundary，避免实现继续在 callback 风格上漂移；它不承担 hot-path owner inventory。
4. Phase 2 再冻结 query / market / trading hot path 的 owner inventory 与 migration boundary；实际代码迁移属于后续 child change 执行。
5. Phase 3 用 contract lock 把 Python adapter 固定为 host shell，并显式阻止 runtime logic 回流。
6. Phase 4 只在已有 batch/in-process 主线之后，冻结 benchmark gate 的命令、阈值、artifact boundary 与 daemon trigger policy；external daemon 仍需后续独立 proposal。

## Phase Responsibility Boundaries

1. Phase 1 只冻结 adapter-facing batch contract；不得把 hot-path owner inventory、thin-shell contract 或 daemon policy 混入完成定义。
2. Phase 2 只冻结 hot-path owner inventory 与 migration boundary；不得把 thin-shell contract 或 benchmark gate 误写成 Phase 2 closeout。
3. Phase 3 只冻结 thin Python host glue contract 与 anti-regression guard 入口；不得把新的 runtime logic 合法化为 Python adapter 常驻职责。
4. Phase 4 只冻结 benchmark gate child change 的判定口径；没有 benchmark 越线证据时，external daemon 不能升级为默认主线。

## Error Handling

1. 若任何 phase 试图把当前 active vendor-bridge readiness change 改写成性能 rollout mainline，立即 fail-fast 并回写 proposal/change docs。
2. 若任何 child change 在没有 benchmark 证据时直接把 daemon 升为默认方向，立即视为 proposal 边界违规。
3. 若任何实现把新的 callback parsing、state machine、query lifecycle ownership 写回 Python adapter，立即视为违反 ADR001 和本 proposal 的 thin-shell design。
4. 若任何文档把 proposal-level `allowed_evidence_roots` 误写成 Phase 4 formal benchmark pass artifact root，立即视为 artifact boundary 违规。