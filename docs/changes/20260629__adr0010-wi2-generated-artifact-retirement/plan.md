---
change-id: 20260629__adr0010-wi2-generated-artifact-retirement
status: completed
topic-id: adr0010-wi2
---

# ADR-0010 WI-2 Generated Artifact Retirement - nautilus_ctp_adapter

## Scope

- Retire tracked generated artifacts under `var/**`, `pytest_tmp/**`, and `output/debug/**` from source control.
- Add broad ignore rules so local runtime, pytest, and vendor-sync outputs cannot return to the index.
- Do not delete files from the working tree.
- Do not alter SendMode proposal files or runtime behavior in this change.

## Acceptance

See `acceptance.md`.

## Rollback Boundary

This change is limited to `.gitignore`, this change bundle, guards, and index retirement of generated runtime outputs.
It is independent from the WI-5 SendMode safety proposal.

## Completed Notes

- Tracked `var/**`, `pytest_tmp/**`, and residual `output/debug/**` generated artifacts are retired from the index and guarded by `tests/test_adr0010_wi2_generated_artifact_retirement.py`.
