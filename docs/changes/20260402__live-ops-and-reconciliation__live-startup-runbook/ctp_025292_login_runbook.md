# CTP 025292 Login And Account Query Runbook

**date**: 2026-06-16  
**scope**: formal broker account `025292`, TD login, settlement confirmation, read-only funds query  
**boundary**: no order, cancel, amend, or trade-send operation is allowed by this runbook

## 1. Inputs

Required local-only inputs:

1. `cfgs/local/ctp.live.025292.local.json`
2. Operator-trusted 025292 CTP 6.7.x runtime and SDK:

```text
output/vnpy_ctp_clone/vnpy_ctp/api
```

The config file owns secrets and account-specific values:

```text
BrokerID / UserID / Password / AppID / AuthCode / ProductInfo / Host / Pricer / Instruments
```

Do not paste these values into chat or tracked documentation.

## 2. Runtime Rule

Do not use OpenCTP TTS 6.6.9 runtime artifacts to judge formal broker account `025292`.

The ABI differs:

```text
6.6.9 TTS TD: CreateFtdcTraderApi(const char*)
6.7.x 025292 TD: CreateFtdcTraderApi(const char*, bool)
6.6.9 TTS MD: CreateFtdcMdApi(const char*, bool, bool)
6.7.x 025292 MD: CreateFtdcMdApi(const char*, bool, bool, bool)
```

If the bridge/runtime pair is mismatched, failures such as `WinError 127` or disconnect-only TD startup are not credential or front evidence.

## 3. Build The Matching Bridge

Create a temporary combined SDK directory outside tracked source if it does not already exist:

```powershell
New-Item -ItemType Directory -Force -Path output\debug\ctp-025292-rootcause\sdk-vnpy-combined | Out-Null
Copy-Item output\vnpy_ctp_clone\vnpy_ctp\api\include\ctp\ThostFtdc*.h output\debug\ctp-025292-rootcause\sdk-vnpy-combined\ -Force
Copy-Item output\vnpy_ctp_clone\vnpy_ctp\api\libs\thost*userapi_se.lib output\debug\ctp-025292-rootcause\sdk-vnpy-combined\ -Force
```

Build `ctp_native.dll` against the 6.7.x SDK:

```powershell
$env:CTP_VENDOR_SDK_ROOT = (Resolve-Path output\debug\ctp-025292-rootcause\sdk-vnpy-combined).Path
$env:PATH = (Resolve-Path output\vnpy_ctp_clone\vnpy_ctp\api).Path + ';' + $env:PATH
cargo build --manifest-path rust\Cargo.toml -p ctp_runtime_core
```

For isolated probing, copy the rebuilt bridge beside the 6.7.x runtime DLLs:

```powershell
New-Item -ItemType Directory -Force -Path output\debug\ctp-025292-rootcause\runtime-vnpy | Out-Null
Copy-Item rust\target\debug\ctp_native.dll output\debug\ctp-025292-rootcause\runtime-vnpy\ctp_native.dll -Force
Copy-Item output\vnpy_ctp_clone\vnpy_ctp\api\thosttraderapi_se.dll output\debug\ctp-025292-rootcause\runtime-vnpy\thosttraderapi_se.dll -Force
Copy-Item output\vnpy_ctp_clone\vnpy_ctp\api\thostmduserapi_se.dll output\debug\ctp-025292-rootcause\runtime-vnpy\thostmduserapi_se.dll -Force
```

After the formal-account probe, restore the default OpenCTP TTS build if the local development session needs paper/TTS defaults:

```powershell
$env:CTP_VENDOR_SDK_ROOT = (Resolve-Path output\openctp\tts-sdk\tts_6.6.9-win64-combined).Path
$env:PATH = (Resolve-Path vendor\ctp\bin).Path + ';' + $env:PATH
cargo build --manifest-path rust\Cargo.toml -p ctp_runtime_core
```

## 4. Login And Account Query

The successful 2026-06-16 probe used this sequence:

1. Load `output/debug/ctp-025292-rootcause/runtime-vnpy/ctp_native.dll`
2. Use `cfgs/local/ctp.live.025292.local.json`
3. `TdInit(Host)`
4. `TdAuthenticate(AppID, AuthCode, ProductInfo)`
5. `TdLogin(BrokerID, UserID, Password)`
6. `TdConfirmSettlement`
7. Wait about 1 second
8. `TdQryAccount`

Expected success signals:

```text
init_code=0
authenticate_code=0
login_code=0
login_success=true
settlement_code=0
query_code=0
account.account_id=025292
```

Write structured evidence under:

```text
output/debug/ctp-025292-account-query/<session-label>/account_query.json
```

The 2026-06-16 success evidence is:

```text
output/debug/ctp-025292-account-query/manual-runtime-vnpy-20260616/account_query.json
```

## 5. Failure Interpretation

Use these failure classes:

| Symptom | Interpretation | Next action |
| --- | --- | --- |
| `WinError 127` while loading `ctp_native.dll` with 6.7.x DLLs | Bridge was built against the wrong CTP SDK ABI | Rebuild bridge against 6.7.x SDK |
| repeated disconnect-only events with 6.6.9 runtime | Wrong runtime family for formal broker `025292` | Switch to 6.7.x runtime/SDK |
| `login_error_id=64` / client not authenticated | TD login was attempted without valid client auth | Check AppID/AuthCode presence in local config |
| `login_error_id=3` / illegal login | TD login rejected after auth | Check local Password/account trading-side state; do not reclassify as front discovery |
| MD login succeeds but TD login fails | Password may be valid for MD but TD still rejects trading login | Continue TD-specific diagnosis only |

## 6. Non-Goals

This runbook does not authorize:

1. live order send
2. cancel or amend
3. position-changing smoke
4. storing credentials in tracked files
5. using OpenCTP paper evidence as formal broker readiness
