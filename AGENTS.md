# AGENTS.md

**Updated**: 2026-04-01  
**Status**: Active

## Read First

Read these in order:

1. [README.md](/D:/Nautilus/nautilus_ctp_adapter/README.md)
2. [docs/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/README.md)
3. [docs/doc_harness_kit/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)
4. [docs/architecture/runtime-performance-guidelines.md](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md)
5. [docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md)
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
| `docs/changes_topic/` | Long-running topic roadmap governance |
| `docs/changes/` | Executable child changes, acceptance, and evidence |
| `docs/topics/` | Legacy compatibility pointers only |

## Change Governance

This repository adopts the `Doc Harness Kit` at:

1. [docs/doc_harness_kit/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)

Governance layout is aligned toward `DSLReserach`:

1. Long-running topic roadmaps live under `docs/changes_topic/roadmap/`
2. Stable architecture docs live under `docs/architecture/`
3. Executable child changes live under `docs/changes/<change-id>/`
4. New child changes should start from the local `_template` bundle, including `design.md` when needed

## Official Entry Points

1. Package metadata: [pyproject.toml](/D:/Nautilus/nautilus_ctp_adapter/pyproject.toml)
2. Rust workspace: [rust/Cargo.toml](/D:/Nautilus/nautilus_ctp_adapter/rust/Cargo.toml)
3. Runtime namespace: [src/nautilus_ctp_adapter/runtime/__init__.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/__init__.py)
4. CTP adapter namespace: [src/nautilus_ctp_adapter/adapters/ctp/__init__.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/__init__.py)
5. Test entry: `python -m pytest`

## Verification

Current real verification commands:

1. `python -m pytest`
2. `python -m pip install -e .`
3. `cargo check --manifest-path rust/Cargo.toml` after Rust toolchain installation

Temporary outputs should stay out of the repository root.
