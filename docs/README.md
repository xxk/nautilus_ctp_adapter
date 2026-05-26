# Docs Index

This directory is the documentation and governance home for `nautilus_ctp_adapter`.

## Read Order

1. [Repository map](/D:/Nautilus/nautilus_ctp_adapter/AGENTS.md)
2. [Harness kit entry](/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md)
3. [ADR index](/D:/Nautilus/nautilus_ctp_adapter/docs/adr/README.md)
4. [Proposal index](/D:/Nautilus/nautilus_ctp_adapter/docs/proposals/README.md)
5. [Architecture index](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/README.md)
6. [Topic state registry](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/主题状态注册表_Topic%20State%20Registry.yaml)
7. [Topic index](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/README.md)
8. [Changes index](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/README.md)
9. [Archive index](/D:/Nautilus/nautilus_ctp_adapter/docs/archive/README.md)

## Governance Layout

This repository aligns to the `DSLReserach` topic/change split:

1. `docs/architecture/` for durable design conclusions
2. `docs/adr/` for architecture decision records and decision rationale
3. `docs/proposals/` for multi-phase proposal containers and proposal-local acceptance
4. `docs/topics/<topic-id>.md` for long-running topic roadmaps
5. `docs/topics/主题状态注册表_Topic State Registry.yaml` for machine-readable topic state and execution order
6. `docs/changes/` for executable child changes and evidence
7. `docs/archive/` for archived docs and historical snapshots

## Current Active Delivery

1. Master roadmap: [Nautilus CTP adapter mainline](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-ctp-adapter-mainline.md)
2. Topic state registry: [/D:/Nautilus/nautilus_ctp_adapter/docs/topics/主题状态注册表_Topic State Registry.yaml](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/主题状态注册表_Topic%20State%20Registry.yaml)
3. Topic index: [/D:/Nautilus/nautilus_ctp_adapter/docs/topics/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/README.md)
4. Current topic roadmap: [Live session order query hardening](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md)（`in_progress` / `execution_order=1`，C3 脚本面已 blocked-closeout，当前聚焦 U1 vendor-bridge handoff）
5. Active change: [20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff/plan.md)（执行中，当前正式冻结 `sdk-not-found / scaffold-only` blocker 与 SDK/live DLL handoff 路径）
6. Parked topic: [Live ops truth snapshot](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-ops-truth-snapshot.md)（`blocked`，当前因 disconnect storm 挂起）
7. Recent completed topic: [Rust-owned CTP runtime cutover](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/rust-ctp-runtime-cutover.md)

## Topic / Change Workflow Commands

```powershell
python scripts/show_current_frontier.py --root .
python scripts/show_current_frontier.py --by-topic
python scripts/check_harness.py
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
