# Python Mainline MD Subscribe Smoke Evidence

**Date**: 2026-04-02
**Change ID**: 20260401__ctp-live-connectivity__python-rust-md-login-path

## Success Command

```powershell
python scripts\ctp_md_login_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## Success Outcome

Observed on 2026-04-02:

```text
{"init_code": 0, "login_request_code": 0, "subscribe_code": 0, "login_success": true, "login_error_id": 0, "login_error_message": "", "first_tick_symbol": "rb2610", "first_tick_last": 3128.0, "first_tick_bid": 3127.0, "first_tick_ask": 3128.0, "first_tick_ts_epoch_us": 1775094714033056}
{"bridge_event_kinds": ["login_succeeded", "tick"], "bridge_tick_symbol": "rb2610"}
```

This proves:

1. Python mainline reaches the repository-owned `ctp_native.dll`
2. `MdCreate(flow_path)` / `MdInit` / `MdLogin` / `MdSubscribe(ptr, count)` are frozen enough for live MD use
3. `rb2610` tick can be received through the same Python mainline path
4. the tick reaches the runtime bridge boundary as a `tick` event

## Failure Scenario 1: Invalid MD Front

```powershell
python scripts\ctp_md_login_smoke.py --config C:\Users\kimi\AppData\Local\Temp\ctp.invalid-front.json --timeout-seconds 5
```

Observed:

```text
{"init_code": 0, "login_request_code": 0, "subscribe_code": -1, "login_success": false, "login_error_id": -1, "login_error_message": "", "first_tick_symbol": null, "first_tick_last": null, "first_tick_bid": null, "first_tick_ask": null, "first_tick_ts_epoch_us": null}
{"bridge_event_kinds": [], "bridge_tick_symbol": null}
```

Interpretation:

1. front misconfiguration fails cleanly without fake success
2. subscribe is not attempted before login is established

## Failure Scenario 2: Invalid Instrument

```powershell
python scripts\ctp_md_login_smoke.py --config C:\Users\kimi\AppData\Local\Temp\ctp.invalid-instrument.json --timeout-seconds 10
```

Observed:

```text
{"init_code": 0, "login_request_code": 0, "subscribe_code": 0, "login_success": true, "login_error_id": 0, "login_error_message": "", "first_tick_symbol": null, "first_tick_last": null, "first_tick_bid": null, "first_tick_ask": null, "first_tick_ts_epoch_us": null}
{"bridge_event_kinds": ["login_succeeded"], "bridge_tick_symbol": null}
```

Interpretation:

1. login and subscribe request can succeed while no matching tick ever arrives
2. the bridge output makes the failure boundary explicit: login happened, tick did not
