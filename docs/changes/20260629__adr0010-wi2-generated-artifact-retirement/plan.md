---
change-id: 20260629__adr0010-wi2-generated-artifact-retirement
status: in_progress
topic-id: adr0010-wi2
---

# ADR-0010 WI-2 Generated Artifact Retirement - nautilus_ctp_adapter

## Scope

- Retire tracked generated artifacts under `var/**` and `pytest_tmp/**` from source control.
- Add broad ignore rules so local runtime, pytest, and vendor-sync outputs cannot return to the index.
- Do not delete files from the working tree.
- Do not alter SendMode proposal files or runtime behavior in this change.

## Acceptance

See `acceptance.md`.

## Rollback Boundary

This change is limited to `.gitignore`, this change bundle, and index retirement of `var/**` and `pytest_tmp/**`.
It is independent from the WI-5 SendMode safety proposal.
