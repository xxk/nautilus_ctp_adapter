# Harness Minimal Adoption Plan

**Current Display Name**: Doc Harness Kit
**Status**: completed
**Progress**: 100%
**Date**: 2026-04-01
**Topic ID**: harness-adoption
**Change ID**: 20260401__harness-adoption__nautilus-ctp-adapter-minimal-adoption
**Related Acceptance**: ./acceptance.md

## Summary

Adopt the `Doc Harness Kit` into `nautilus_ctp_adapter` with a real repository entry map, local change templates, real validation commands, and a first completed trial change.

## Scope

In scope:

1. Copy `docs/doc_harness_kit/` into this repository
2. Add repository-local navigation and governance entry files
3. Add local `docs/changes/_template/` bundle templates
4. Replace validation commands with this repository's real commands
5. Use this change itself as the first real adoption trial

Out of scope:

1. Full guard script implementation
2. Remote deployment workflow
3. CTP business feature implementation

## Capability Mapping

```text
- capability_id: harness-minimal-adoption
- capability_name: minimal harness adoption for nautilus_ctp_adapter
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/跨项目最小接入5步法_Minimal 5-Step Adoption.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/AGENTS.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- affects_long_term_rules: yes
- change_type: governance bootstrap
```

## Tasks

| Step | Task | Files | Output | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| P1 | Copy upstream harness kit into local docs path | `docs/doc_harness_kit/` | Local harness source | Directory inspection | Completed |
| P2 | Add repository entry map and docs index | `AGENTS.md`, `docs/README.md` | Official navigation | Document inspection | Completed |
| P3 | Add local change templates and layering rules | `docs/changes/README.md`, `docs/changes/_template/*` | Local reusable bundle templates | Directory inspection | Completed |
| P4 | Replace with repository-real validation commands | `AGENTS.md`, `docs/README.md`, `acceptance.md` | Real commands for this repo | `python -m pytest`, `python -m pip install -e .` | Completed |
| P5 | Complete this change as the first real trial | current change bundle | Evidence and conclusion | Acceptance review | Completed |

## Done Definition

Development done:

1. The repository contains the harness kit, entry map, template bundle, and real validation commands.

Delivery done:

1. Acceptance A1-A5 pass and the current change stands as the first real trial change.

