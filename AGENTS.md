# AGENTS.md

**Updated**: 2026-05-30
**Status**: Active

## Read First

Read these in order:

1. [README.md](/D:/Nautilus/nautilus_ctp_adapter/README.md)
2. [docs/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/README.md)
3. [docs/doc_harness_kit/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)
4. [docs/adr/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/adr/README.md)
5. [docs/proposals/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/proposals/README.md)
6. [docs/workflows/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/workflows/README.md)
7. [../docs/harness/任务分层与命名统一口径_Cross-Repo Work Item Layering And Naming.md](/D:/Nautilus/docs/harness/%E4%BB%BB%E5%8A%A1%E5%88%86%E5%B1%82%E4%B8%8E%E5%91%BD%E5%90%8D%E7%BB%9F%E4%B8%80%E5%8F%A3%E5%BE%84_Cross-Repo%20Work%20Item%20Layering%20And%20Naming.md)
8. [docs/architecture/runtime-performance-guidelines.md](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md)
9. The current change bundle under `docs/changes/<change-id>/` when the frontier reports one

## Autonomous Execution Policy

Default objective: keep advancing the current formal change frontier until the queue is empty or a real blocker is hit.

Execution rules:

1. Run `python scripts/autopilot.py --root .` to get current frontier at TASK-LIST granularity.
2. Run `python scripts/show_current_frontier.py --root .` to see active/completed child changes from `docs/changes/*/plan.md`.
3. If an active change exists, continue it; if none, pick the first `not_started` change.
4. After completing a change, mark plan.md status as completed and backfill acceptance.md.
5. Do not stop unless a real blocker is hit.

### Real Blockers

Only these count as true blockers:

1. Missing permissions or missing environment capability for the formal entry point.
2. Missing external dependency or live resource with no local fallback verification path.
3. A conflict between roadmap state, change docs, and registry that cannot be resolved from repository facts.
4. Acceptance criteria that cannot be judged as pass/fail.

## Current Frontier Shortcut

When the goal is to enter the formal frontier quickly, use this order:

1. `python scripts/autopilot.py --root .`
2. `python scripts/show_current_frontier.py --root .`
3. `python scripts/show_current_frontier.py --by-topic` only when a grouped topic projection is useful
4. `python scripts/check_harness.py`
5. `python scripts/check_change_docs.py --root .`
6. Open only the active change bundle.

## Repository Role

This repository is the standalone CTP adapter workspace for Nautilus projects.

Primary responsibilities:

1. Build and maintain the platform-neutral CTP runtime under `rust/` and `src/nautilus_ctp_adapter/runtime/`
2. Build and maintain the Nautilus integration layer under `src/nautilus_ctp_adapter/adapters/ctp/`
3. Keep repository-maintained `ctpnative` bootstrap ownership under local native/vendor tooling
4. Treat any C# smoke host as temporary verification tooling, not as the formal implementation path
5. Keep tests under `tests/` and local runnable diagnostics under `scripts/`
6. Keep architecture, proposal, child change, and evidence governance under `docs/`

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
| `docs/adr/` | ADR index and architecture decision records |
| `docs/workflows/` | Reusable workflow fragments and gate specs; not an execution state source |
| `docs/proposals/` | Multi-phase proposal containers and proposal-local acceptance |
| `docs/architecture/` | Stable design and architecture conclusions |
| `docs/topics/` | Legacy roadmap and `--by-topic` grouping projection only |
| `docs/changes/` | Executable child changes, acceptance, and evidence |
| `docs/archive/` | Archived docs and historical evidence |

## Change Governance

This repository adopts the `Doc Harness Kit` at:

1. [docs/doc_harness_kit/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)

Governance layout is aligned toward `DSLReserach`:

1. ADR records live under `docs/adr/`
2. Proposal containers live under `docs/proposals/<proposal-id>/`
3. Reusable workflow fragments and gate specs live under `docs/workflows/`; concrete status and evidence must not live there
4. Topic labels may appear as `topic-id` in child change `plan.md` frontmatter for grouping only
5. Stable architecture docs live under `docs/architecture/`
6. Executable child changes live under `docs/changes/<change-id>/`
7. New child changes should start from the local `_template` bundle, including `design.md` when needed

## Topic Transition Rule

> **DEPRECATED**: Topic registry and sync_topic_index are replaced by Route B.
> topic-id is now a label in plan.md frontmatter. No independent registry required.
> Use `python scripts/show_current_frontier.py --by-topic` for topic grouping.

Default executable frontier: `docs/changes/*/plan.md`
Legacy topic state registry: `docs/topics/主题状态注册表_Topic State Registry.yaml`

Topic 不作为 proposal 推进容器。Proposal 的推进状态只能来自 `docs/proposals/<proposal-id>/phase-plan.md`，实际执行切片只能来自 `docs/changes/<change-id>/plan.md`。

Current active topic: `none`
Parked topics: `live-session-order-query-hardening`, `live-ops-truth-snapshot`
Recent completed topic: `autopilot-session-management`

When the current frontier changes, update the child change `plan.md` status and run `python scripts/autopilot.py --root . --backfill`.

## Official Entry Points

1. Package metadata: [pyproject.toml](/D:/Nautilus/nautilus_ctp_adapter/pyproject.toml)
2. Rust workspace: [rust/Cargo.toml](/D:/Nautilus/nautilus_ctp_adapter/rust/Cargo.toml)
3. Runtime namespace: [src/nautilus_ctp_adapter/runtime/__init__.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/__init__.py)
4. CTP adapter namespace: [src/nautilus_ctp_adapter/adapters/ctp/__init__.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/__init__.py)
5. Test entry: `python -m pytest`

## Verification

Current real verification commands:

```bash
# Harness structure check
python scripts/check_harness.py

# ADR docs completeness
python scripts/check_adr_docs.py --root .

# Change docs completeness
python scripts/check_change_docs.py --root .

# Proposal docs completeness
python scripts/check_proposal_docs.py --root .

# Frontier status
python scripts/show_current_frontier.py --root .
python scripts/show_current_frontier.py --by-topic

# Autopilot with TASK-LIST granularity
python scripts/autopilot.py --root .
python scripts/autopilot.py --root . --update-checkpoint "T1 done: description"
python scripts/autopilot.py --root . --log-action "edit" --log-target "path" --log-detail "what changed"
python scripts/autopilot.py --root . --show-trajectory 5
python scripts/autopilot.py --root . --detect-drift
python scripts/autopilot.py --root . --report-blocker "dependency_missing: description"
python scripts/autopilot.py --root . --backfill

# Build and test
python scripts/check_rust_gate.py
python scripts/ctp_repo_debug_smoke.py
python -m pytest
```

Temporary outputs should stay out of the repository root.
