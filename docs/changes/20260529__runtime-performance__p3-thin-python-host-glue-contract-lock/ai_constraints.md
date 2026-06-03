# Thin Python Host Glue Contract AI Constraints

**change-id**：20260529__runtime-performance__p3-thin-python-host-glue-contract-lock
**关联 plan**：./plan.md
**关联 acceptance**：./acceptance.md

## 必读上下文

1. P001 proposal bundle.
2. ADR001.
3. Phase 2 owner inventory child change.
4. `docs/architecture/rust-python-adapter-split.md`.
5. `src/nautilus_ctp_adapter/adapters/ctp/`.

## 允许

1. Freeze host-glue allowlist / forbidden-list.
2. Bind focused guard commands.
3. Backfill P001 / ADR001 / architecture docs with stable contract rules.

## 禁止

1. Do not add new Python runtime truth.
2. Do not treat focused tests as live performance evidence.
3. Do not approve daemon or IPC path.
4. Do not change vendor/private runtime inputs.

## 验收纪律

1. Completed means contract lock exists and has guard path.
2. It does not mean all forbidden code has already been physically removed.
3. Runtime migration remains separate from host-glue contract freeze.
