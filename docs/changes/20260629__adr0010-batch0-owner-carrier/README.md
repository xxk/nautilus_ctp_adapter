---
change-id: 20260629__adr0010-batch0-owner-carrier
status: draft
work_item_layer: change_stub
---

# ADR-0010 Batch 0 Owner Carrier - nautilus_ctp_adapter

## Owner / Scope

- Owner repo: `nautilus_ctp_adapter`
- Governing ledger: `global_docs/adr/0010-multirepo-arch-review-coordination-ledger.md`
- Scope in this repo:
  - WI-2: retire tracked generated artifacts under `var/**` and `pytest_tmp/**`
  - WI-5: formal SendMode safety proposal; see `docs/proposals/p005-adr0010-sendmode-safety-hardening/`

## WI-2 Tracked Artifact Inventory

Classification snapshot, generated before any `git rm --cached`:

| Class | Pattern | Count | Initial disposition |
| --- | --- | ---: | --- |
| runtime generated artifact | `var/**` | 751 | retire from source after fixture/evidence review |
| runtime generated artifact | `pytest_tmp/**` | 742 | retire from source after fixture/evidence review |
| binary/generated vendor artifact | `var/**`, `pytest_tmp/**` binary-like suffixes | 675 | retire or explicitly vendor under owner-approved path |
| required fixture | none classified yet | 0 | must be explicitly moved to `tests/fixtures/` before retirement |
| evidence artifact | none classified yet | 0 | must move to explicit evidence root or external storage before retirement |

Sample paths:

- `pytest_tmp/ctp025292_account_console_runtime_lineage/test_account_source_artifact_d0/acceptance.json`
- `pytest_tmp/ctp025292_account_console_runtime_lineage_gate/test_cli_writes_blocker_json_a1/cfgs/local/ctp.live.025292.local.json`
- `pytest_tmp/ctp025292_account_console_runtime_lineage_gate/test_cli_writes_blocker_json_a1/vendor/ctp/bin/_synced_from.txt`

## Acceptance Evidence Slots

| Scenario | red command | green command | fresh-clone command | Status |
| --- | --- | --- | --- | --- |
| RC-1 Batch entry gate | pending | pending | pending | slot-created |
| RC-2 WI-2 inventory classification | inventory above | pending | pending | slot-created |
| RC-3 WI-2 post-retirement guard | pending | pending | pending | slot-created |
| RC-4 WI-5 safety matrix | see proposal stub | see proposal stub | see proposal stub | delegated |
| RC-6 Evidence replay | pending | pending | pending | slot-created |

## Rollback Boundary

WI-2 generated-artifact retirement and WI-5 SendMode implementation must be separate changes.

## Anti-Drift

- Do not untrack `pytest_tmp/**` or `var/**` until required fixtures/evidence are explicitly classified.
- Do not keep legacy 3-bool live-send paths as a long-term peer to SendMode.
