# AGENTS.md

**Updated**: 2026-04-10
**Status**: Active

## Read First

Read these in order:

1. [README.md](/D:/Nautilus/nautilus_ctp_adapter/README.md)
2. [docs/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/README.md)
3. [docs/doc_harness_kit/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)
4. [docs/architecture/runtime-performance-guidelines.md](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md)
5. [docs/topics/roadmap/rust_ctp/rust-ctp-runtime-cutover/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/rust_ctp/rust-ctp-runtime-cutover/README.md)
6. The current change bundle under `docs/changes/<change-id>/`

## Repository Role

This repository is the standalone CTP adapter workspace for Nautilus projects.

Primary responsibilities:

1. Build and maintain the platform-neutral CTP runtime under `rust/` and `src/nautilus_ctp_adapter/runtime/`
2. Build and maintain the Nautilus integration layer under `src/nautilus_ctp_adapter/adapters/ctp/`
3. Keep repository-maintained `ctpnative` bootstrap ownership under local native/vendor tooling
4. Treat any C# smoke host as temporary verification tooling, not as the formal implementation path
5. Keep tests under `tests/` and local runnable diagnostics under `scripts/`
6. Keep architecture, topic roadmap, child change, and evidence governance under `docs/`

## Directory Map

| Directory | Responsibility |
| --- | --- |
| `rust/` | Platform-neutral Rust runtime crates |
| `src/nautilus_ctp_adapter/runtime/` | Platform-neutral Python-side runtime boundary |
| `src/nautilus_ctp_adapter/adapters/ctp/` | Python Nautilus glue layer |
| `src/nautilus_ctp_adapter/adapters/smartquant/` | Future SmartQuant glue layer |
| `src/nautilus_ctp_adapter/native/` | Native loading and FFI-facing helpers |
| `tests/` | Package tests and smoke validation |
| `scripts/` | Local diagnostics and runnable helpers |
| `docs/architecture/` | Stable design and architecture conclusions |
| `docs/topics/` | Long-running topic roadmap governance |
| `docs/changes/` | Executable child changes, acceptance, and evidence |
| `docs/archive/` | Archived docs and historical evidence |

## Change Governance

This repository adopts the `Doc Harness Kit` at:

1. [docs/doc_harness_kit/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)

Governance layout is aligned toward `DSLReserach`:

1. Long-running topic roadmaps live under `docs/topics/roadmap/`
2. Stable architecture docs live under `docs/architecture/`
3. Executable child changes live under `docs/changes/<change-id>/`
4. New child changes should start from the local `_template` bundle, including `design.md` when needed

## Topic Transition Rule

When a topic README `**状态**` changes from `进行中` to `已完成` and the next topic enters `in_progress`, the following updates are **mandatory** and must be done in the same commit:

1. Update **this file** (`AGENTS.md`) read order step 5 to point to the new active topic README.
2. Update `docs/topics/README.md` Current State section to reflect the new active topic and active change.
3. Update `docs/README.md` Current Active Delivery section to reflect the new active topic and active change.

Verification: `python scripts/check_topic_docs.py`

## Official Entry Points

1. Package metadata: [pyproject.toml](/D:/Nautilus/nautilus_ctp_adapter/pyproject.toml)
2. Rust workspace: [rust/Cargo.toml](/D:/Nautilus/nautilus_ctp_adapter/rust/Cargo.toml)
3. Runtime namespace: [src/nautilus_ctp_adapter/runtime/__init__.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/__init__.py)
4. CTP adapter namespace: [src/nautilus_ctp_adapter/adapters/ctp/__init__.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/__init__.py)
5. Test entry: `python -m pytest`

## Verification

Current real verification commands:

1. `python -m pip install -e ".[dev]"`
2. `python scripts/check_rust_gate.py`
3. `python scripts/ctp_repo_debug_smoke.py`
4. `python -m pytest`

Temporary outputs should stay out of the repository root.
