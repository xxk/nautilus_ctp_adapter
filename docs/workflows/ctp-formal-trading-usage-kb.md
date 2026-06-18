# CTP Formal Trading Usage Knowledge Base

**Updated**: 2026-06-17  
**Status**: operator-knowledge-base  
**Scope**: CTP adapter usage for read-only checks, paper/simulation practice, and formal trading guardrails

## One-Line Verdict

The adapter has formal-account TD login, settlement confirmation, account query, order mapping, and guarded live-send code paths. It must still be operated in layers: read-only first, paper/simulation next, and formal live-send only after explicit guardrails and operator approval.

## Capability Layers

| Layer | Purpose | Current command family | Can change position |
| --- | --- | --- | --- |
| Read-only formal account | Login, settlement confirmation, funds, positions, order truth snapshots | `ctp_account_query_smoke.py`, `ctp_query_adapter_smoke.py`, `ctp_td_order_truth_smoke.py` | No |
| OpenCTP TTS simulation | 24h development, query, dry-run, guarded simulated sends | `cfgs/local/ctp.openctp.tts.7x24.local.json` plus smoke scripts | Yes, but simulation only |
| Formal broker live-send | Final broker-facing pre-go-live validation | `ctp_order_lifecycle_smoke.py --live-send` | Yes |

Do not use OpenCTP paper evidence as formal broker evidence.

## Current 025292 Fact Pattern

Formal broker account `025292` requires the matching 6.7.x CTP SDK/runtime pack under:

```text
output/vnpy_ctp_clone/vnpy_ctp/api
```

The default `vendor/ctp/bin` pack may point at OpenCTP TTS 6.6.9. That is not a valid runtime verdict for `025292`. If the bridge/runtime pair is mismatched, repeated disconnects or `WinError 127` are runtime/ABI evidence, not credential or front evidence.

Known current read-only evidence:

```text
output/debug/ctp-025292-account-query/manual-runtime-vnpy-20260617/account_query.json
```

That evidence shows TD init, auth, login, settlement confirmation, and `TdQryAccount` succeeded for `025292` with no disconnects. It does not authorize live order send.

## Safe Read-Only Usage

Use this path when the goal is to verify login or read funds/positions.

1. Confirm the local config exists:

```powershell
Test-Path cfgs/local/ctp.live.025292.local.json
```

2. For `025292`, confirm the 6.7.x runtime pack exists:

```powershell
Test-Path output/vnpy_ctp_clone/vnpy_ctp/api/thosttraderapi_se.dll
Test-Path output/debug/ctp-025292-rootcause/runtime-vnpy/ctp_native.dll
```

3. Prefer the `025292` runbook when using the formal account:

```text
docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/ctp_025292_login_runbook.md
```

4. If the default native search path has already been rebuilt for the matching 6.7.x runtime, the account query smoke shape is:

```powershell
python scripts/ctp_account_query_smoke.py `
  --config cfgs/local/ctp.live.025292.local.json `
  --timeout-seconds 30 `
  --session-label live-025292-account-query `
  --output-json output/debug/ctp-025292-account-query/account_query.json
```

On this machine, if that command returns disconnect-only events, switch to the `runtime-vnpy` runbook path instead of changing credentials or fronts.

## Paper/Simulation Practice

Use OpenCTP TTS for ordinary development and guarded order-lifecycle practice:

```powershell
python scripts/ctp_query_adapter_smoke.py `
  --config cfgs/local/ctp.openctp.tts.7x24.local.json `
  --include-reconciliation `
  --session-label openctp-query `
  --evidence-root output/debug/openctp-query
```

Dry-run order lifecycle first:

```powershell
python scripts/ctp_order_lifecycle_smoke.py `
  --config cfgs/local/ctp.openctp.tts.7x24.local.json `
  --instrument TEST `
  --quantity 1 `
  --limit-price 1 `
  --client-order-id openctp-dry-run-1
```

Only add `--live-send` for simulation after the local config deliberately sets `ExecutionGuardrails.AllowLiveOrderSmoke=true`, and reset it to `false` after the run.

## Formal Live-Send Checklist

Formal broker live-send is not the default path. Before any `--live-send` with a formal broker config, all of these must be true:

1. Matching broker SDK/runtime is active, not OpenCTP TTS 6.6.9.
2. TD login and settlement confirmation are green in current-session evidence.
3. A fresh read-only account/position snapshot exists.
4. TD order truth preflight has run and has no manual-review blocker.
5. Instrument, side, quantity, price, and client order id are explicit.
6. Guardrails are enabled with current values for allowed instruments, max order qty, max net position, submit frequency, and live-send arming.
7. The operator explicitly approves the live-send run.

Formal live-send command shape:

```powershell
python scripts/ctp_order_lifecycle_smoke.py `
  --config <approved-formal-config> `
  --instrument <approved-instrument> `
  --side <BUY-or-SELL> `
  --quantity <approved-qty> `
  --limit-price <approved-price> `
  --client-order-id <unique-id> `
  --timeout-seconds 30 `
  --live-send
```

Do not run that command from a generic development task or as a shortcut after a funds query.

## Failure Interpretation

| Symptom | Likely meaning | Action |
| --- | --- | --- |
| `WinError 127` loading `ctp_native.dll` | Bridge/runtime ABI mismatch | Rebuild or switch to matching SDK/runtime |
| Repeated disconnect-only TD events for `025292` | Often wrong runtime family | Use 6.7.x `runtime-vnpy` path |
| `login_error_id=64` | Client auth missing or invalid | Check local AppID/AuthCode presence |
| `login_error_id=3` | TD login rejected | Check password/account trading-side state |
| Query success but no live-send approval | Normal guarded state | Keep read-only; do not escalate automatically |

## Source Pointers

| Topic | Path |
| --- | --- |
| 025292 login/account query runbook | `docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/ctp_025292_login_runbook.md` |
| 6.7 runtime evidence | `docs/changes/20260403__position-account-query-baseline__account-query-smoke/evidence_20260616_account_query_6_7_runtime.md` |
| Script operator notes | `scripts/README.md` |
| Top-level operator matrix | `docs/README.md` |
| Guardrail config model | `src/nautilus_ctp_adapter/adapters/ctp/config.py` |

## Non-Goals

This knowledge base does not authorize:

1. Storing account secrets in tracked files.
2. Treating a funds query as live-trading acceptance.
3. Treating OpenCTP simulation as formal broker readiness.
4. Running `--live-send` without explicit guardrail review and operator approval.
