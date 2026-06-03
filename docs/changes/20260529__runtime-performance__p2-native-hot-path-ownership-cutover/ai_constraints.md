# Hot-Path Owner Inventory AI Constraints

**change-id**：20260529__runtime-performance__p2-native-hot-path-ownership-cutover
**关联 plan**：./plan.md
**关联 acceptance**：./acceptance.md

## 必读上下文

1. P001 proposal bundle.
2. ADR001.
3. `docs/architecture/runtime-performance-guidelines.md`.
4. `docs/architecture/rust-python-adapter-split.md`.
5. `src/nautilus_ctp_adapter/runtime/`.
6. `src/nautilus_ctp_adapter/adapters/ctp/`.

## 允许

1. Update owner inventory and migration boundary docs.
2. Reference source evidence for current owner classification.
3. Backfill P001 / ADR001 / architecture docs with stable owner rules.

## 禁止

1. Do not claim full native cutover.
2. Do not add runtime state ownership to Python adapter.
3. Do not merge Phase 3 thin-shell lock or Phase 4 benchmark gate into this phase.
4. Do not modify live trading config, vendor SDK, or active vendor-bridge change scope.

## 验收纪律

1. A completed Phase 2 means the owner inventory is frozen, not that code migration is finished.
2. Evidence must cite source files, docs gates, or focused tests.
3. Missing future implementation is not a blocker for this boundary-freeze change.
