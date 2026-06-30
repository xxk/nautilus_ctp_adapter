# Platform-Neutral CTP Runtime Acceptance

**Status**: passed
**Date**: 2026-04-01
**Change ID**: 20260401__architecture__platform-neutral-ctp-runtime
**Related Plan**: ./plan.md
**Related AI Constraints**: ./ai_constraints.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-04-01 20:35"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
```
<!-- AI-STATUS-END -->

## Goal

Prove that the CTP core is no longer named or structured as Nautilus-only infrastructure.

## Scenarios

| # | Scenario | Execution | Expected | Evidence |
| --- | --- | --- | --- | --- |
| A1 | Rust core is platform-neutral in name and exports | Inspect `rust/Cargo.toml` and `rust/ctp_runtime_core/` | neutral runtime naming is present | `rust/Cargo.toml`, `rust/ctp_runtime_core/Cargo.toml` |
| A2 | Shared runtime commands and events exist | Inspect Rust and Python runtime models | runtime boundary is host-platform agnostic | `rust/ctp_runtime_core/src/commands.rs`, `rust/ctp_runtime_core/src/events.rs`, `src/nautilus_ctp_adapter/runtime/models.py` |
| A3 | Nautilus adapter is separated from shared runtime | Inspect `src/nautilus_ctp_adapter/` layout | runtime and adapter namespaces are distinct | `src/nautilus_ctp_adapter/runtime/__init__.py`, `src/nautilus_ctp_adapter/adapters/ctp/factory.py` |
| A4 | Docs explicitly describe Nautilus-now / SmartQuant-later split | Inspect topic and repo docs | future SmartQuant compatibility is reflected in docs | `README.md`, `docs/architecture/platform-neutral-ctp-runtime.md` |

## Exit Conditions

| # | Condition | Status | Evidence |
| --- | --- | :---: | --- |
| E1 | Blocking scenarios all pass | ☑ | A1-A4 passed |
| E2 | Failure interpretation is clear | ☑ | Runtime and adapter layers now have explicit boundaries |
| E3 | Required verification was executed | ☑ | `python -m pytest` passed |
| E4 | Evidence is recorded | ☑ | This file and referenced repository files |
