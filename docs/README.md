# Docs Index

This directory is the documentation and governance home for `nautilus_ctp_adapter`.

## Read Order

1. [Repository map](/D:/Nautilus/nautilus_ctp_adapter/AGENTS.md)
2. [Harness kit entry](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)
3. [ADR index](/D:/Nautilus/nautilus_ctp_adapter/docs/adr/README.md)
4. [Proposal index](/D:/Nautilus/nautilus_ctp_adapter/docs/proposals/README.md)
5. [Workflow specs](/D:/Nautilus/nautilus_ctp_adapter/docs/workflows/README.md)
6. [Architecture index](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/README.md)
7. [Changes index](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/README.md)
8. [Topic index](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/README.md)（legacy grouping projection only）
9. [Archive index](/D:/Nautilus/nautilus_ctp_adapter/docs/archive/README.md)

## Governance Layout

This repository uses Route B governance:

1. `docs/architecture/` for durable design conclusions
2. `docs/adr/` for architecture decision records and decision rationale
3. `docs/proposals/` for multi-phase proposal containers and proposal-local acceptance
4. `docs/workflows/` for reusable template fragments and gate specs; it is not an execution state source
5. `docs/changes/` for executable child changes and evidence; `docs/changes/*/plan.md` is the default executable frontier source
6. `topic-id` in change `plan.md` frontmatter is a grouping label, not a proposal or execution container
7. `docs/topics/` and the legacy topic registry are grouped roadmap projections only
8. `docs/archive/` for archived docs and historical snapshots

topic 不作为 proposal 推进容器。Proposal 状态由 `docs/proposals/<proposal-id>/phase-plan.md` 的 `AI-PHASE-STATUS` 承载；执行状态由 child change `plan.md` 承载。

## Current Frontier

1. Frontier source: `docs/changes/*/plan.md`
2. Current active change: `none`
3. Grouped topic projection: [/D:/Nautilus/nautilus_ctp_adapter/docs/topics/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/README.md)
4. Legacy parked topic labels: [Live session order query hardening](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md)（`blocked`，等待私有 SDK/live DLL 输入）；[Live ops truth snapshot](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-ops-truth-snapshot.md)（`blocked`，当前因 disconnect storm 挂起）

## Operator Entry Matrix

1. Repo-only/offhours evidence export: `python scripts/ctp_query_adapter_smoke.py --config <local-config> --include-reconciliation --include-order-truth --include-order-trade-snapshot --session-label <label> --evidence-root output/debug/<topic>`.
2. OpenCTP paper evidence: use `cfgs/local/ctp.openctp.tts.7x24.local.json` generated from `.env`; current official 7x24 TTS fronts are TD `tcp://trading.openctp.cn:30001` and MD `tcp://trading.openctp.cn:30011`, with BrokerID `9999` and local TTS runtime/SDK readiness required.
3. Formal-trading evidence: use ignored formal local config only for final/pre-go-live checks; never use it to close ordinary paper-development rows.
4. Real `c2609` live-send: run TD order truth preflight first; only add `ctp_order_lifecycle_smoke.py ... --live-send` when vendor/runtime, trade window, and net-position guardrails are explicit.

## Change / Proposal Workflow Commands

```powershell
python scripts/show_current_frontier.py --root .
python scripts/show_current_frontier.py --by-topic  # grouping projection only
python scripts/check_harness.py
python scripts/check_adr_docs.py --root .
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root .
python scripts/new_proposal.py --root . --id <proposal-id> --profile multi_phase --check-only
```

## Official Bootstrap And Validation Commands

```powershell
python -m pip install -e ".[dev]"
python scripts/check_rust_gate.py
python scripts/ctp_repo_debug_smoke.py
python -m pytest
```

## Cross-Machine Live-Ready Note

1. The repo-only debug path above proves the repository can build its own scaffold/runtime artifacts on a fresh clone.
2. A second machine still needs a local `vendor/ctp/bin/` runtime pack plus a full CTP SDK under `vendor/ctp/sdk/` or `CTP_VENDOR_SDK_ROOT` / `CTP_SDK_ROOT` before it can build the live-ready vendor bridge.
3. The durable runbook for that layout lives in [/D:/Nautilus/nautilus_ctp_adapter/vendor/ctp/README.md](/D:/Nautilus/nautilus_ctp_adapter/vendor/ctp/README.md) and the top-level repository guide in [/D:/Nautilus/nautilus_ctp_adapter/README.md](/D:/Nautilus/nautilus_ctp_adapter/README.md).
4. `python scripts/ctp_repo_debug_smoke.py` intentionally checks the public PyO3 scaffold contract; TD `-9000` there is expected before C3 and does not by itself prove the formal TD ctypes/live path is scaffold-only.
5. The formal TD readiness verdict remains `python scripts/ctp_nautilus_live_smoke.py --config <path>`.
