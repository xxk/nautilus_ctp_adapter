# Proposal Template C+ Usage

`docs/proposals/_template/` uses the C+ pattern:

1. `base/` contains the required minimal files copied into every new proposal.
2. `fragments/` contains optional scenario or capability files.
3. `profiles/` contains common fragment combinations.
4. `meta/fragment_registry.yaml` is the machine-readable fragment list.
5. `docs/workflows/` owns reusable workflow/gate specs; proposal instances still own their own phase status and acceptance evidence.

Before selecting a profile, use `docs/workflows/work-item-type-system.md` to classify whether the work is `governance`, `delivery`, or `tracer`. Do not introduce `proposal_type`, `proposal_profile`, or `change_kind` as a second formal taxonomy.

Prefer profile creation:

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --profile parallel_tracer
```

For `p070+` tracer proposals, creation now includes a lightweight preflight gate. Freeze the tracer's own input binding at create time:

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --profile tracer \
	--tracer-input-case-dir input/<proposal-case-dir> \
	--tracer-case-id <case-id> \
	--tracer-case-ref <case-ref>
```

If you want to validate the binding first without writing anything, run the same command with `--check-only`:

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --profile tracer \
	--tracer-input-case-dir input/<proposal-case-dir> \
	--tracer-case-id <case-id> \
	--tracer-case-ref <case-ref> \
	--check-only
```

Use manual fragments only for uncommon combinations:

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --fragments parallel_execution,capability_contract
```

Rules:

1. Profile files only list fragment ids; they must not copy full template content.
2. Fragment files must be independently readable and must not require another fragment implicitly.
3. `fragment_registry.yaml` currently validates fragment existence and profile references only; dependency or conflict rules require a follow-up change.
4. `p070+` tracer proposal creation fails fast unless `--tracer-input-case-dir` / `--tracer-case-id` / `--tracer-case-ref` are provided together, the input path is under `input/` and starts with the proposal root, and the binding does not collide with an existing proposal's tracer binding.
5. When that tracer preflight passes, `new_proposal.py` writes the binding into the new proposal README, pins `source_input_templates` in `phase-plan.md`, and scaffolds `input/<proposal-case-dir>/study_request/request.json` with the same case identity plus `coverage_scope.case_ownership_contract=self_owned_case_local`.
6. `--check-only` runs the same creation preflight but does not create `docs/proposals/<proposal-id>/` or `input/<proposal-case-dir>/`; it only reports whether the create command would pass.
7. `new_proposal.py` now also self-checks the anti-drift skeleton after scaffold: README must still expose Goals and Non-Goals; phase-plan must still expose Artifact Trust Boundary, Execution Principles, at least one Fail-fast / Negative Cases section, and Closeout Checklist; acceptance must still expose Artifact Root Rule, Acceptance Evidence Boundary, and Scenario Matrix.
8. `new_proposal.py` writes hidden scaffold metadata into README: `<!-- PROPOSAL-SCAFFOLD: profile=...; fragments=... -->`. Proposal docs gate uses this metadata to decide whether `issue-list.md` is required, instead of relying only on whether the directory name contains `tracer`.
9. If a new proposal id contains `tracer`, creation fails fast unless the selected profile/fragments include `issue_list`.
10. Modern proposals reviewed on or after 2026-05-27 must keep the blocker handling gate text from the base template. `check_proposal_docs.py` verifies the phase-plan mentions `Blocker Handling Discipline`, `code/contract blocker`, `data blocker`, `governance blocker`, and `unknown blocker`; acceptance must mention repo-local repairable blockers plus external owner / real data / human approval typed waiting/blocked handling.

Phase-plan baseline:

1. `base/phase-plan.md` is intentionally stronger than the docs gate minimum: it includes artifact boundary, execution principles, AI tracking status, phase status board, deliverables, runtime/command freeze, fail-fast cases, verification commands, and closeout checklist.
2. Lightweight proposals may collapse unused sections to "not applicable", but should not delete artifact boundary, AI tracking status, phase status board, or fail-fast sections.
3. Tracer and parallel-tracer proposals should fill in exact case identity, artifact roots, runtime commands, worker/merge evidence, UI contract-lock tests, and cross-tracer gates before execution.
4. `AI-PHASE-STATUS.overall_status` is the canonical proposal-level status key. The top `**状态**` field in `phase-plan.md` and `README.md` must be treated as projections, not independent state sources.
5. There is no line-count limit for base templates; structure and evidence quality are the gate, not file length.
6. New proposals created from the current base template carry `<!-- PROPOSAL-ANTI-DRIFT-GATE:v1 -->` in README, and `check_proposal_docs.py` treats that marker as opt-in contract: for those proposals, removing the anti-drift skeleton is a docs-gate violation, not a style preference.
7. New proposals that carry scaffold metadata also let docs gate distinguish `issue_list` lanes from non-`issue_list` lanes without guessing from directory naming alone; old proposals still keep legacy fallback behavior.

Tracer naming baseline:

1. Proposal directory name carries the proposal-id and tracer identity; do not repeat `tracer` in every file name.
2. Common skeleton files keep their canonical names: `README.md`, `phase-plan.md`, `acceptance.md`.
3. Canonical tracer supporting files still prefer canonical file names over prefixed file names. Current example: `issue-list.md` remains the proposal-local tracer ledger because repo guard scripts already check that file name.
4. All second-layer canonical tracer supporting files should put `Tracer` in the H1 title even when the file name stays canonical, for example `P057 Tracer Issue Ledger` or `P057 Tracer Strict Acceptance Addendum`.
5. All third-layer optional add-on files are allowed to use a `tracer-<purpose>.md` name to improve scanability, but the purpose words must stay explicit.
6. Whether or not `tracer-` is used, avoid weak names like `notes.md`, `temp.md`, or `misc.md`; keep surface/purpose semantics such as `tracer-prework-review.md` or `tracer-case-assurance-blocker-cleanup.md`.
7. Existing files do not need to be renamed immediately; new tracer docs or touched add-on docs may adopt the `tracer-` prefix directly.
8. If a rename would change a script-guarded file name, update the owning script and CONTRACT-LOCK tests first; do not rename proposal docs in isolation.

ADR-carrier naming baseline:

1. If a proposal primarily carries implementation or rollout for an ADR, set `ADR carrier` to `yes` in the README top status block.
2. New ADR-carrier proposal ids must include the three-digit primary ADR slug directly after the proposal number, for example `p068-ADR056-<rollout-slug>`.
3. `Primary ADR` must use the canonical `ADR-00xx` spelling and must match the three-digit `ADRNNN` slug in the proposal id.
4. If the ADR-carrier proposal is also a tracer / carry-forward / reacceptance proposal with one direct predecessor, keep the predecessor as the first navigation token: `p068-p067-ADR056-<tracer-slug>`.
5. Existing proposal ids are not renamed for this rule; if a preexisting ADR carrier predates the rule, keep its directory name and add `Carrier naming note: preexisting proposal-id predates ADR-carrier naming rule`.
6. `python scripts/check_proposal_docs.py --root .` enforces the `ADR carrier`, `Primary ADR`, tracer predecessor, and preexisting naming note contract.

ADR-carrier landing gate:

1. New ADR-carrier proposals created from the current base template carry `<!-- PROPOSAL-ADR-CARRIER-GATE:v1 -->` in README.
2. A proposal with that marker and `ADR carrier=yes` must copy the Primary ADR's Decision Coverage IDs into `phase-plan.md` under `ADR Decision Coverage Mapping`.
3. The same proposal must map the ADR successor acceptance scenarios into `acceptance.md` under `ADR Carrier Acceptance Matrix`.
4. `phase-plan.md` owns `Covered decisions`; `acceptance.md` must cover every listed decision with a positive path, fail-fast path, authority boundary, and minimal evidence.
5. Generic A1/A2/A3 rows are still useful as proposal-level smoke scenarios, but they do not close an ADR-carrier obligation unless the ADR-carrier matrix maps the corresponding ADR decision item.

Two-layer tracer ledger baseline:

1. A tracer proposal's `issue-list.md` is the proposal-local tracer ledger. It owns current-tracer source issues, new findings, closeout status, acceptance mapping, and the next tracer carry-forward seed.
2. A stable chain master ledger may live at `docs/proposals/<anchor>-chain-master-ledger.md` when a continuous tracer chain needs a stable navigation surface. The current P055 chain uses `docs/proposals/p055-chain-master-ledger.md`.
3. The chain master ledger owns only high-level navigation: latest tracer proposal, latest proposal-local ledger path, current open issue summary, owner proposal map, proposal ledger index, and long-term anti-regression seed summary.
4. Do not copy the full proposal-local issue table, root cause narrative, acceptance matrix, or evidence ledger into the chain master ledger.
5. At tracer closeout, first normalize the current proposal-local `issue-list.md`, then promote only the high-level summary and latest pointer into the chain master ledger.
6. When starting the next tracer, read the chain master ledger first, then jump to the latest proposal-local tracer ledger and its README / acceptance.
