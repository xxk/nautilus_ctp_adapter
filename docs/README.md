# Docs Index

This directory is the documentation and governance home for `nautilus_ctp_adapter`.

## Read Order

1. [Repository map](/D:/Nautilus/nautilus_ctp_adapter/AGENTS.md)
2. [Harness kit entry](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)
3. [Architecture index](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/README.md)
4. [Topic index](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/README.md)
5. [Changes index](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/README.md)
6. [Archive index](/D:/Nautilus/nautilus_ctp_adapter/docs/archive/README.md)

## Governance Layout

This repository now aligns to the `DSLReserach` split:

1. `docs/architecture/` for durable design conclusions
2. `docs/topics/roadmap/` for long-running topic roadmaps
3. `docs/changes/` for executable child changes and evidence
4. `docs/archive/` for archived docs and historical snapshots

## Current Delivery

1. Master roadmap: [Nautilus CTP adapter mainline](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md)
2. Current topic roadmap: [Rust-owned CTP runtime cutover](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/rust_ctp/rust-ctp-runtime-cutover/README.md)
3. Active change: [20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime/plan.md)
4. Parallel blocked topic: [Live ops truth snapshot](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-truth-snapshot/README.md)

## Official Bootstrap And Validation Commands

```powershell
python -m pip install -e ".[dev]"
python scripts/check_rust_gate.py
python scripts/ctp_repo_debug_smoke.py
python -m pytest
```
