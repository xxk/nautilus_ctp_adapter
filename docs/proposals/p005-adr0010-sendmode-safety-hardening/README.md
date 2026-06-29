---
work_item_type: governance
work_item_layer: proposal
surface_mode: none
action_mode: execution_capable
---

# P005 / ADR-0010 SendMode Safety Hardening

**proposal-id**: `p005-adr0010-sendmode-safety-hardening`
**status**: draft
**governing ledger**: `global_docs/adr/0010-multirepo-arch-review-coordination-ledger.md`

## Goal

Replace the live-send 3-bool matrix with an explicit `SendMode` enum so illegal send-mode combinations are rejected at construction time.

## Scope

- In scope: WI-5 SendMode enum, illegal bool-combination rejection, old 3-bool entry retirement or wrapper-to-enum lock.
- Out of scope: broker connectivity, order-routing feature expansion, account profile changes.

## Acceptance

See `acceptance.md`.

## Anti-Drift

- RC-1, RC-4, RC-6 apply.
- Old 3-bool API must not remain as a long-term path parallel to SendMode.
- Safety-critical behavior must not be closed with fallback/default branches.
