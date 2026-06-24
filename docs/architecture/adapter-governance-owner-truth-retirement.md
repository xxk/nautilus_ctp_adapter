# Adapter Governance Owner Truth Retirement Boundary

**Status**: Active  
**Owner**: architecture  
**Authority ADR**: [ADR004](../adr/ADR004%20Adapter%20Governance%20Owner%20Truth%20Retirement%20Boundary.md)

This document is the stable owner, truth-source, fork-prevention and retirement boundary for `nautilus_ctp_adapter`. It is governance-first and now also records the staged code-retirement state: migrated surfaces remain compatibility entrypoints only when executable gates prove delegation to their successor owners.

## Owner Registry

<!-- ARCH-GOV:OWNER-REGISTRY:v1 -->

| owner_id | canonical owner | allowed responsibility | forbidden responsibility | public entry |
| --- | --- | --- | --- | --- |
| `runtime_core` | `rust/ctp_runtime_core/`, `src/nautilus_ctp_adapter/runtime/` | platform-neutral commands, events, session state, runtime bridge contracts | Nautilus host policy, smoke evidence policy, script-only verdicts | `nautilus_ctp_adapter.runtime` |
| `native_loader` | `src/nautilus_ctp_adapter/native/` | native DLL discovery, runtime pack resolution, FFI-facing helpers | broker credentials, live readiness verdicts, adapter policy | `nautilus_ctp_adapter.native` |
| `nautilus_adapter_glue` | `src/nautilus_ctp_adapter/adapters/ctp/` | Nautilus-facing config, data, execution, instrument and factory glue | long-lived diagnostics policy, evidence ledgers, runtime pack lineage authority | `nautilus_ctp_adapter.adapters.ctp` |
| `diagnostics` | `src/nautilus_ctp_adapter/diagnostics/` or package-owned diagnostics modules | reusable smoke orchestration, evidence shaping, redacted diagnostics | becoming adapter runtime truth or live trading authority | package functions called by scripts |
| `cli_wrappers` | `scripts/` | local runnable entrypoints and thin wrappers | owning reusable business logic or canonical truth | `python scripts/<entry>.py` |
| `governance` | `docs/adr/`, `docs/architecture/`, `scripts/check_*` | owner/truth rules, validators, retirement gates | live runtime pass/fail truth, raw secrets, broker authority | `python scripts/check_architecture_governance.py` |

## Truth-Source Matrix

<!-- ARCH-GOV:TRUTH-SOURCE-MATRIX:v1 -->

| truth_id | canonical source | writers | readers | forbidden second truth |
| --- | --- | --- | --- | --- |
| `runtime_behavior_truth` | `rust/ctp_runtime_core/` + runtime tests | runtime owner changes | adapter, diagnostics, scripts | duplicate Python runtime core |
| `native_loading_truth` | `src/nautilus_ctp_adapter/native/` + runtime pack refs | native owner changes | runtime, scripts, diagnostics | ad hoc DLL search in scripts or adapter methods |
| `adapter_stack_truth` | `src/nautilus_ctp_adapter/adapters/ctp/factory.py` and typed stack owner | adapter owner changes | scripts, downstream hosts | alternate stack builders with different semantics |
| `formal_live_verdict_truth` | `python scripts/ctp_nautilus_live_smoke.py --config <path>` until successor ADR/change | formal smoke owner | docs, operators, downstream repos | new live-ready script claiming pass without retirement |
| `governance_truth` | ADR + architecture docs + executable gates | architecture/governance owner | all contributors | chat-only architecture decisions |
| `evidence_artifact_truth` | redacted owner artifacts and typed blockers under documented evidence paths | owner-specific evidence writers | governance and diagnostics readers | `output/debug`, root `.con`, stdout-only claims |

## Fork-Prevention Rules

<!-- ARCH-GOV:FORK-PREVENTION:v1 -->

1. New code must not introduce a second runtime core, second native loader, second adapter stack builder, second live-ready verdict, second artifact root, or second governance validator outside this registry.
2. Diagnostics may read runtime and adapter truth but must not become runtime or adapter truth.
3. Scripts may remain public entrypoints, but reusable logic belongs in package-owned modules.
4. A compatibility wrapper must delegate to a canonical owner or fail loudly with a successor owner message.
5. Any new owner category requires ADR or architecture update plus `check_architecture_governance.py` coverage.
6. Any new formal live verdict entrypoint must retire or explicitly supersede the previous one in the retirement ledger.

## Legacy Retirement Ledger

<!-- ARCH-GOV:RETIREMENT-LEDGER:v1 -->

| legacy_path | current role | successor_owner | retirement_action | compatibility_boundary | retirement_gate | status |
| --- | --- | --- | --- | --- | --- | --- |
| `src/nautilus_ctp_adapter/adapters/ctp/data_client.py` | MD adapter glue with delegated diagnostics models/policy | `diagnostics` + `nautilus_adapter_glue` | keep adapter-facing facade; diagnostics dataclasses/policy live under `diagnostics` | legacy imports delegate to diagnostics owner | focused pytest proving same result shape and no second truth | `guarded_transitional` |
| `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py` | TD adapter glue, order mapping and guardrails with delegated diagnostics policy | `diagnostics` + `nautilus_adapter_glue` | keep order mapping/guardrails; delegate reusable diagnostics/policy and dry-run evidence shaping | guardrails remain adapter-owned until a successor ADR extracts them | focused pytest for mapping, guardrails, dry-run native isolation and diagnostics delegation | `guarded_transitional` |
| `scripts/ctp_*.py` | CLI entrypoints and compatibility wrappers | `cli_wrappers` + `diagnostics` | move reusable payload/verdict logic into package modules; leave scripts runnable | scripts may own CLI args, IO, and explicit safety arm parameters only | script owner delegation tests plus architecture governance gate | `guarded_transitional` |
| `src/ctp_runtime/__init__.py` | compatibility import shim for native runtime | `native_loader` | delegate native runtime bootstrap to `nautilus_ctp_adapter.native.pyo3_runtime` | import shim remains compatibility surface only | runtime loader isolation tests and architecture governance gate | `guarded_transitional` |

## Safe Retirement Protocol

1. Name the legacy path and successor owner before editing code.
2. Add or update focused tests that prove behavior is delegated, preserved, or intentionally blocked.
3. Keep secrets local to owner runtime paths; record only refs, redacted checksums, typed blockers and negative assertions.
4. Update this ledger only when a successor change provides executable evidence.
5. Do not remove an entry merely because the code was moved; remove or mark retired only when the old path is guarded against re becoming canonical.

## Gate

Run:

```powershell
python scripts/check_architecture_governance.py --root .
python scripts/check_harness.py
```

The first gate validates this document and ADR004. The second gate proves the architecture governance gate is part of the aggregate harness.
