# Account Query 6.7 Runtime Evidence

**change-id**: `20260403__position-account-query-baseline__account-query-smoke`  
**date**: 2026-06-16  
**scope**: real account `025292` read-only account query

## Command Shape

The run used the repository-owned `ctp_native.dll` rebuilt against the operator-trusted 025292 CTP 6.7.x SDK/runtime pack, then executed a TD login and `TdQryAccount` only.

No order, cancel, or trade-send API was called.

Evidence payload:

```text
output/debug/ctp-025292-account-query/manual-runtime-vnpy-20260616/account_query.json
```

## Result

```text
init_code=0
authenticate_code=0
login_code=0
settlement_code=0
query_code=0
login_success=true
login_error_id=0
account_id=025292
currency_id=CNY
```

Account snapshot:

```text
balance=1626519.79
available=398087.68000000087
withdraw_quota=278661.37
curr_margin=1228432.1099999992
frozen_margin=0.0
commission=0.0
position_profit=0.0
close_profit=0.0
```

## Root-Cause Note

The default `vendor/ctp/bin` runtime pack on this machine currently points at the OpenCTP TTS 6.6.9 SDK/runtime. That pack is suitable for OpenCTP TTS paper flows, but it is not the correct runtime family for the formal broker account `025292`.

For 025292, the compatible runtime is the operator-trusted 6.7.x pack under:

```text
output/vnpy_ctp_clone/vnpy_ctp/api
```

The binary ABI difference is observable in the CTP factory exports:

```text
6.6.9 TTS TD: CreateFtdcTraderApi(const char*)
6.7.x 025292 TD: CreateFtdcTraderApi(const char*, bool)
6.6.9 TTS MD: CreateFtdcMdApi(const char*, bool, bool)
6.7.x 025292 MD: CreateFtdcMdApi(const char*, bool, bool, bool)
```

Using a bridge built against 6.6.9 with the 025292 runtime failed at DLL load with `WinError 127`. Using the 6.6.9 runtime against the 025292 front produced misleading disconnect-only symptoms. Rebuilding the bridge against the 6.7.x SDK exposed the real TD state and, after the local credential update, completed TD login and account query.

## Operator Rule

When querying formal broker account `025292`, use a bridge built against the matching 6.7.x SDK/runtime pack. Do not use OpenCTP TTS 6.6.9 runtime artifacts to judge formal broker TD readiness.
