# OpenCTP TTS 7x24 Simulation Order Evidence: zn2610 BUY 2

**date**: 2026-06-08
**account_profile**: `openctp-tts-7x24-simulation`
**config**: `cfgs/local/ctp.openctp.tts.7x24.local.json`
**instrument**: `zn2610`
**side**: `BUY`
**quantity**: `2`
**limit_price**: `24985`
**scope**: simulated OpenCTP TTS 7x24 paper send; not formal-trading evidence

## Preconditions

1. User explicitly authorized simulated account order submission up to 3 lots.
2. Local ignored config was temporarily armed with:
   - `ExecutionGuardrails.AllowedInstruments=["zn2610"]`
   - `ExecutionGuardrails.MaxOrderQty=3`
   - `ExecutionGuardrails.AllowLiveOrderSmoke=true`
3. After the run, `AllowLiveOrderSmoke` was reset to `false`.

## Evidence

Instrument query:

```text
success=true
requested_symbol=zn2610
matched_symbols=["zn2610.SHFE"]
price_tick=5.0
volume_multiple=5
```

Marketdata smoke:

```text
success=true
first_tick_symbol=zn2610
first_tick_last=24980.0
first_tick_bid=24975.0
first_tick_ask=24985.0
```

Guarded order loop:

```text
success=true
action_mode=paper_send
paper_send_armed=true
instrument=zn2610
side=BUY
quantity=2
limit_price=24985.0
order_contract.accepted=true
order_lifecycle.bootstrap_ready=true
order_lifecycle.verdict.disposition=filled
order_lifecycle.verdict.fill_volume=2
order_lifecycle.verdict.leaves_qty=0
```

Raw machine-readable evidence is stored under ignored local output:

```text
output/debug/openctp-tts/zn2610-buy2/order_loop.json
output/debug/openctp-tts/zn2610-pre-snapshot/pre_snapshot.json
output/debug/openctp-tts/openctp-tts-724-md-zn2610/md_login_smoke.json
output/debug/openctp-tts/openctp-tts-724-instrument-zn2610/instrument_query.json
```

## Boundary

This evidence proves only OpenCTP TTS 7x24 simulation order submission behavior.
It must not be used as formal broker/trading readiness or real-account evidence.

