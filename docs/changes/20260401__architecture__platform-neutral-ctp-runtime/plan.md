# Platform-Neutral CTP Runtime Plan

**Status**: completed
**Progress**: 100%
**Date**: 2026-04-01
**Topic ID**: ctp-runtime-architecture
**Change ID**: 20260401__architecture__platform-neutral-ctp-runtime
**Related Acceptance**: ./acceptance.md

## Summary

Refactor the repository architecture so the CTP core is platform-neutral and can later support both Nautilus and SmartQuant adapters.

## Scope

In scope:

1. Rename the Rust core to a neutral runtime name
2. Add platform-neutral runtime commands and events
3. Add a Python runtime namespace distinct from adapter namespaces
4. Mark Nautilus and SmartQuant as separate adapter layers in the repository layout
5. Update repository docs to reflect the new layering

Out of scope:

1. Real PyO3 bindings
2. Real SmartQuant provider implementation
3. Real CTP DLL execution logic

## Capability Mapping

```text
- capability_id: ctp-runtime-platform-neutrality
- capability_name: platform-neutral ctp runtime
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/README.md
- affects_long_term_rules: yes
- change_type: architecture refactor
```

## Tasks

| Step | Task | Files | Output | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| P1 | Rename host-specific Rust core to neutral runtime name | `rust/` | `ctp_runtime_core` workspace member | file inspection | Completed |
| P2 | Add neutral commands and event model | `rust/ctp_runtime_core/src/*`, `src/nautilus_ctp_adapter/runtime/*` | shared runtime API placeholders | `python -m pytest` | Completed |
| P3 | Separate runtime and adapter namespaces | `src/nautilus_ctp_adapter/*` | runtime vs adapter split | file inspection | Completed |
| P4 | Document Nautilus-now / SmartQuant-later architecture | `README.md`, `AGENTS.md`, `docs/*` | stable architecture docs | document inspection | Completed |

## Done Definition

Development done:

1. The repository exposes a platform-neutral runtime boundary and separate adapter namespaces.

Delivery done:

1. Acceptance blocking scenarios pass and the architecture is documented in-repo.
