# A3 Evidence: OpenCTP Query And Order Dry-Run

**change-id**: `20260607__openctp-tts__test-baseline`
**captured-at**: 2026-06-08 Asia/Shanghai
**scenario**: A3 OpenCTP query/order dry-run path
**verdict**: passed

No password or secret value is recorded in this evidence file.

## Environment

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:PATH=(Resolve-Path rust/target/debug).Path + ';' + $env:PATH
```

Runtime was built and run with the official TTS 6.6.9 SDK/runtime under:

```text
output/openctp/tts-sdk/tts_6.6.9-win64-combined
```

## Commands And Results

| Smoke | Command summary | Result | Evidence |
| --- | --- | --- | --- |
| Account query | `python scripts/ctp_account_query_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json ...` | `success=true`, `completed=true`, balance/available returned | `output/debug/openctp-tts/openctp-tts-724-account-tts669/account_query.json` |
| Position query | `python scripts/ctp_position_query_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json ...` | `success=true`, `completed=true`, `no_positions=true` | `output/debug/openctp-tts/openctp-tts-724-position-tts669/position_query.json` |
| Query adapter aggregate | `python scripts/ctp_query_adapter_smoke.py --instrument-symbol TEST --include-reconciliation --include-order-truth --include-order-trade-snapshot ...` | `success=true`; account, position, instrument, reconciliation, order-truth snapshots emitted | `output/debug/openctp-tts/openctp-tts-724-query-tts669/aggregated_query.json` |
| Order lifecycle dry-run | `python scripts/ctp_order_lifecycle_smoke.py --instrument TEST --quantity 1 --limit-price 1` | `dry_run=true`, `live_send_requested=false`, `live_send_armed=false`, submit command mapped without live send | console JSON |

## Guardrail Check

The order lifecycle smoke was intentionally run without `--live-send`.
The result confirmed:

```text
dry_run=true
live_send_requested=false
live_send_armed=false
command_kinds=["connect", "submit_order"]
event_kinds=["login_succeeded", "settlement_confirmed"]
```

## Conclusion

A3 passed for OpenCTP paper account query and dry-run order lifecycle evidence.
This evidence is valid for paper simulation/development only and must not be used
as formal broker/trading final readiness.
