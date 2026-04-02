# Docs Index

This directory is the documentation and governance home for `nautilus_ctp_adapter`.

## Read Order

1. [Repository map](/D:/Nautilus/nautilus_ctp_adapter/AGENTS.md)
2. [Harness kit entry](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)
3. [Architecture index](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/README.md)
4. [Changes topic index](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/README.md)
5. [Changes index](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/README.md)
6. [Archive index](/D:/Nautilus/nautilus_ctp_adapter/docs/archive/README.md)

## Governance Layout

This repository now aligns to the `DSLReserach` split:

1. `docs/architecture/` for durable design conclusions
2. `docs/changes_topic/roadmap/` for long-running topic roadmaps
3. `docs/changes/` for executable child changes and evidence
4. `docs/topics/` as temporary compatibility pointers only

## Current Active Delivery

1. Master roadmap: [Nautilus CTP adapter mainline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md)
2. Current topic roadmap: [Nautilus instrument provider](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md)
3. Active change: [20260402__nautilus-instrument-provider__instrument-query-runtime-contract](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-instrument-provider__instrument-query-runtime-contract/plan.md)
4. Formal smoke baseline: [20260401__ctp-live-connectivity__nautilus-live-smoke-baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/acceptance.md)

## Official Validation Commands

```powershell
python -m pytest
python -m pip install -e .
# run after installing Rust toolchain
cargo check --manifest-path rust/Cargo.toml
```
