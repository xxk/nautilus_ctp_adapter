# OpenCTP TTS 7x24 Simulation Order Evidence: c2609 SELL 3

**date**: 2026-06-08
**account_profile**: `openctp-tts-7x24-simulation`
**config**: `cfgs/local/ctp.openctp.tts.7x24.local.json`
**instrument**: `c2609`
**side**: `SELL`
**position_effect**: `OPEN`
**quantity**: `3`
**limit_price**: `2316`
**scope**: simulated OpenCTP TTS 7x24 paper send; not formal-trading evidence

## Preconditions

1. User explicitly authorized simulated account order submission up to 3 lots.
2. Local ignored config was temporarily armed with:
   - `ExecutionGuardrails.AllowedInstruments=["c2609"]`
   - `ExecutionGuardrails.MaxOrderQty=3`
   - `ExecutionGuardrails.AllowLiveOrderSmoke=true`
3. After the run, `AllowLiveOrderSmoke` was reset to `false`.

## Evidence

Instrument query:

```text
success=true
requested_symbol=c2609
matched_symbols=["c2609.DCE"]
price_tick=1.0
volume_multiple=10
```

Marketdata smoke:

```text
success=true
first_tick_symbol=c2609
first_tick_last=2317.0
first_tick_bid=2316.0
first_tick_ask=2317.0
```

Guarded order loop:

```text
success=true
action_mode=paper_send
paper_send_armed=true
instrument=c2609
side=SELL
position_effect=OPEN
quantity=3
limit_price=2316.0
order_contract.accepted=true
order_lifecycle.bootstrap_ready=true
order_lifecycle.verdict.disposition=rejected
order_lifecycle.verdict.fill_volume=0
order_lifecycle.verdict.leaves_qty=3
```

Raw machine-readable evidence is stored under ignored local output:

```text
output/debug/openctp-tts/c2609-sell3/order_loop.json
output/debug/openctp-tts/c2609-pre-snapshot/pre_snapshot.json
output/debug/openctp-tts/openctp-tts-724-md-c2609/md_login_smoke.json
output/debug/openctp-tts/openctp-tts-724-instrument-c2609/instrument_query.json
```

## Boundary

This evidence proves only OpenCTP TTS 7x24 simulation order submission and typed
rejection handling. It must not be used as formal broker/trading readiness or
real-account evidence.

