---
work_item_type: governance
work_item_layer: proposal
surface_mode: none
action_mode: execution_capable
---

# P005 / ADR-0010 SendMode Safety Hardening

**proposal-id**: `p005-adr0010-sendmode-safety-hardening`
**status**: implemented
**状态**：implemented
**governing ledger**: `global_docs/adr/0010-multirepo-arch-review-coordination-ledger.md`

## 评审结论 / Review Verdict

P005 is accepted as implemented for ADR-0010 WI-5. `SendMode` is the current source of truth for guarded paper order send semantics.

## 当前状态快照 / Reality Snapshot

| Item | Status |
| --- | --- |
| Source of truth | `src/nautilus_ctp_adapter/diagnostics/send_mode.py` |
| Runtime entry | `scripts/ctp_guarded_paper_order_loop.py` |
| Compatibility | `arm_paper_send` remains only as a wrapper into `resolve_send_mode` |
| Guard | `tests/test_send_mode_guard.py` |

## Graduation / Closeout Matrix

| Target | Status | Evidence |
| --- | --- | --- |
| Runtime behavior | graduated | explicit `SendMode` and illegal-combination rejection |
| Legacy bool path | deprecated compat | old bool path immediately resolves to `SendMode` |
| Anti-regression | active | SendMode guard test plus source scan |

## Goal

Replace the live-send 3-bool matrix with an explicit `SendMode` enum so illegal send-mode combinations are rejected at construction time.

## Scope

- In scope: WI-5 SendMode enum, illegal bool-combination rejection, old 3-bool entry retirement or wrapper-to-enum lock.
- Out of scope: broker connectivity, order-routing feature expansion, account profile changes.

## Acceptance

See `acceptance.md`.

## Historical Scheme & Bug Inventory

| Historical scheme / bug | Confusion risk | Retirement handling | Guard |
| --- | --- | --- | --- |
| `arm_paper_send` directly controlled `action_mode`, risk preflight, config validation and lifecycle dry-run behavior. | Future edits could reintroduce bool-derived send behavior without checking the full safety matrix. | supersede: `run_guarded_paper_order` now resolves `send_mode_resolution` once and uses it as the local authority. | test guard: `tests/test_send_mode_guard.py::test_guarded_order_entries_do_not_bypass_send_mode` |
| Lifecycle finalization accepted `arm_paper_send`, `dry_run`, and `live_send_armed` as separate truth sources. | Illegal combinations such as dry-run plus live-armed could be treated as a valid path by later AI edits. | rename/supersede: `finalize_order_lifecycle_payload` accepts `send_mode` and validates any legacy bools against it. | test guard: `test_finalize_order_lifecycle_payload_uses_send_mode_as_authority` |
| CLI exposed only `--arm-paper-send`, leaving dry-run vs armed-paper as an implicit boolean choice. | Users or generated prompts could describe send behavior with old wording and miss the safety enum. | deprecated compat: `--send-mode {dry_run,armed_paper}` is the preferred entry; `--arm-paper-send` remains a thin wrapper for existing scripts. | parser guard plus `resolve_send_mode` mismatch rejection |
| Historical fallback/default branch treated omitted values as safe without proving incompatible flags absent. | AI could add another flag and silently default to dry-run while still passing live intent elsewhere. | test guard: `resolve_send_mode` rejects inconsistent explicit bools at construction. | `test_send_mode_rejects_illegal_legacy_bool_combinations` |

## Compatibility Retained

- `--arm-paper-send` and `arm_paper_send=` remain accepted for existing dry-run / armed-paper callers, but they immediately convert through `resolve_send_mode`.
- `ARMED_LIVE` exists in the enum for explicit exhaustiveness, but the guarded paper order loop rejects it because this entry is scoped to OpenCTP paper simulation.

## Anti-Drift

- RC-1, RC-4, RC-6 apply.
- Old 3-bool API must not remain as a long-term path parallel to SendMode.
- Safety-critical behavior must not be closed with fallback/default branches.
- Source of truth: `src/nautilus_ctp_adapter/diagnostics/send_mode.py`.
