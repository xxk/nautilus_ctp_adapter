# A2 Evidence: OpenCTP Live Smoke

**change-id**: `20260607__openctp-tts__test-baseline`
**captured-at**: 2026-06-08 Asia/Shanghai
**scenario**: A2 OpenCTP MD/TD live smoke
**verdict**: passed

## Official Inputs Checked

1. Current monitor page: `http://www.openctp.cn/simenv.html`
2. TTS SDK/runbook page: `http://www.openctp.cn/TTS-CTPAPI.html`
3. Selected front values:
   - TD: `tcp://trading.openctp.cn:30001`
   - MD: `tcp://trading.openctp.cn:30011`
   - BrokerID: `9999`
   - AppID/AuthCode: empty

No password or secret value is recorded in this evidence file.

## Local Runtime

The repository bridge was built against the official TTS CTPAPI 6.6.9 Windows
SDK downloaded from:

```text
http://www.openctp.cn/download/CTPAPI/TTS/tts_6.6.9.zip
```

Local ignored SDK/runtime path:

```text
output/openctp/tts-sdk/tts_6.6.9-win64-combined
```

Build gate:

```powershell
$env:CTP_VENDOR_SDK_ROOT=(Resolve-Path output/openctp/tts-sdk/tts_6.6.9-win64-combined).Path
python scripts/check_rust_gate.py
```

Result:

```text
PASS rust-gate: ctp_vendor_bridge-ready sdk_dir=...\output\openctp\tts-sdk\tts_6.6.9-win64-combined
PASS rust-gate: ctp_py-build extension=...\rust\target\debug\_ctp_runtime.dll
PASS rust-gate: cargo-test
```

## Smoke Commands

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:PATH=(Resolve-Path rust/target/debug).Path + ';' + $env:PATH

python scripts/ctp_md_login_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --timeout-seconds 30 --flow-path output/debug/openctp-tts/md-flow-tts669-9999 --session-label openctp-tts-724-md-tts669-9999 --evidence-root output/debug/openctp-tts

python scripts/ctp_td_login_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --timeout-seconds 30 --flow-path output/debug/openctp-tts/td-flow-tts669-9999 --session-label openctp-tts-724-td-tts669-9999 --evidence-root output/debug/openctp-tts

python scripts/ctp_instrument_query_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --symbol TEST --timeout-seconds 30 --flow-path output/debug/openctp-tts/instrument-flow-tts669-test --session-label openctp-tts-724-instrument-tts669-test --evidence-root output/debug/openctp-tts

python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --md-timeout-seconds 30 --td-timeout-seconds 30
```

## Results

| Smoke | Result | Key signals | Evidence |
| --- | --- | --- | --- |
| MD login/subscription | passed | `success=true`, `login_success=true`, `subscribe_code=0`, `first_tick_symbol=TEST` | `output/debug/openctp-tts/openctp-tts-724-md-tts669-9999/md_login_smoke.json` |
| TD login/settlement | passed | `success=true`, `login_success=true`, `settlement_code=0`, no disconnects | `output/debug/openctp-tts/openctp-tts-724-td-tts669-9999/td_login_smoke.json` |
| Instrument query | passed | `instrument_count=1`, `symbols=["TEST.TEST"]`, `exact_symbol_found=true` | `output/debug/openctp-tts/openctp-tts-724-instrument-tts669-test/instrument_query.json` |
| Nautilus aggregate live smoke | passed | `success=true`, MD tick observed, TD settlement observed | console JSON |

## Conclusion

A2 passed with the OpenCTP paper account and official TTS 6.6.9 SDK/runtime.
The previous `20002/20004` TCP blocker is obsolete for current OpenCTP docs;
current evidence uses `trading.openctp.cn:30001/30011`.
