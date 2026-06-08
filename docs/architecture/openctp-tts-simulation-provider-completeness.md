# OpenCTP TTS Simulation Provider Completeness

**Status**: active
**Updated**: 2026-06-08
**Source proposal**: `docs/proposals/p004-openctp-tts-simulation-provider-completeness/`

## Scope

This document records the durable provider rules established by P004 for the OpenCTP TTS 7x24 simulation account profile.

P004 covers `openctp-tts-7x24-simulation` only. It does not restore `formal-trading` and does not claim broker production readiness.

## Stable Capability Boundary

The current simulation provider path has these completed capabilities:

1. Guarded simulation submit and cancel contracts with explicit arm, profile, allowlist, quantity, kill switch and redaction.
2. Close-position command construction for `CLOSE`, `CLOSETODAY`, and `CLOSEYESTERDAY`, including SHFE/INE today/yesterday split handling.
3. Post-order reconciliation against pre/post read-only account, position, order and trade snapshots.
4. Order type and price boundary checks for supported limit, FAK and FOK semantics, plus invalid quantity and off-tick price blocking.
5. Expanded risk preflight using redacted account/position facts, net position, frequency, session budget, duplicate client order id and missing metric blockers.
6. Nautilus-facing execution report projection through `CtpLiveExecutionClient`, including accepted, canceled, rejected, fill, account and position reports.
7. Callback idempotency for duplicate fill/order events in the Nautilus report path.
8. Controlled MD/TD reconnect evidence using a process-scoped localhost front proxy, including disconnect typing, resubscribe-once, TD readiness, query recovery and `paper_send_armed=false`.

## Controlled Reconnect Boundary

Real reconnect is verified by process-scoped controlled front proxy evidence. Public OpenCTP front control is not required; the proxy induces disconnect only for the local test process and preserves `paper_send_armed=false`.

The durable rule is:

1. The proxy must bind only to localhost.
2. Evidence must record MD and TD drop counts, reconnect disposition, resubscribe counts, query readiness and guardrail preservation.
3. Evidence must redact raw account secrets and raw external front details; front status should use fingerprints or typed channel names.
4. The proxy path does not authorize disruption of OpenCTP public simulation fronts or use of formal-trading accounts.

## Formal Trading Boundary

OpenCTP TTS 7x24 evidence can support 24-hour API debugging and simulation provider development. It must not be reused as final `formal-trading` or broker production readiness evidence.

Formal broker readiness needs a successor proposal or explicit future phase with its own account profile, config, safety review and evidence root.

## Canonical Entrypoints

1. Runtime and mapping: `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`
2. Nautilus execution projection: `src/nautilus_ctp_adapter/adapters/ctp/nautilus_execution.py`
3. Guarded order loop: `scripts/ctp_guarded_paper_order_loop.py`
4. Guarded cancel loop: `scripts/ctp_guarded_paper_cancel_loop.py`
5. Read-only truth snapshot: `scripts/ctp_paper_readonly_snapshot.py`
6. Reconnect/idempotency rehearsal: `scripts/ctp_paper_recovery_idempotency.py`
7. Controlled front proxy: `scripts/ctp_controlled_front_proxy.py`
8. Controlled reconnect harness: `scripts/ctp_controlled_reconnect_harness.py`
9. Nautilus engine harness: `scripts/ctp_nautilus_engine_harness.py`

## Verification

Current closeout verification:

```bash
python -m pytest tests/test_controlled_front_proxy.py tests/test_paper_recovery_idempotency.py tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py tests/test_nautilus_integration.py tests/test_guarded_paper_cancel_loop.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p004-openctp-tts-simulation-provider-completeness
python scripts/check_harness.py
python scripts/check_rust_gate.py
```
