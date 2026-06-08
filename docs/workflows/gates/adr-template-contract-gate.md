# ADR Template Contract Gate / ADR 模板契约 Gate

This gate makes ADR template usage machine-checkable. It is intentionally a contract gate, not a byte-for-byte template copier.

## Applies When / 适用时机

1. A new ADR is created.
2. An existing ADR changes H1, decision summary, owner/canonical entry, design kernel, landing map, or successor proposal boundary.
3. A governance proposal/change says it creates or updates an ADR.

## Must Pass / 必须通过

1. Required frontmatter keys exist and are non-empty.
2. Required opening metadata labels exist.
3. Required core sections exist.
4. Standard/governance ADRs keep the stronger template fragments: owner/canonical-entry impact, canonical naming check, design kernel, decision coverage and landing matrix, successor proposal boundary, ADR-level acceptance only, and ADR closeout distillation.
5. `decision_status`, `landing_status`, opening metadata, and final decision wording are consistent.
6. ADR evidence is architecture-level only.
7. Every checked-in ADR is discoverable from `docs/adr/README.md`.

## Must Fail / 必须失败

1. ADR text omits the template contract and only contains a free-form rationale.
2. A proposed ADR claims a final accepted decision.
3. A standard/governance ADR omits successor proposal boundary or ADR-level acceptance.
4. ADR uses CLI output, test output, UI text, report text, latest/debug paths, screenshots, stdout, or chat as decision or landing truth.
5. A new ADR file exists but the ADR index does not reference it.

## Executable Owner / 可执行 owner

`scripts/check_adr_docs.py --root . --adr-id ADR003` is the repository entry.
`scripts/check_harness.py --root .` remains the aggregate docs gate.

