# RB2610 Quote Evidence

**Date**: 2026-04-01  
**Change ID**: 20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610

## Command

```powershell
python scripts\sync_ctp_native.py
dotnet run --project scripts\ctp_live_smoke_host\CtpLiveSmokeHost.csproj -- --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 30
```

## Interpretation Rule

The `CtpLiveSmokeHost` command above is temporary verification tooling only.

It is used to prove:

1. The repository-maintained `ctpnative` bootstrap pack can run
2. The selected live config can receive `rb2610` market data

It is not the target adapter implementation path. The formal delivery target remains the Nautilus Python/Rust adapter stack in this repository.

## Local Config Source

1. Secret-bearing source used to seed the local ignored config:
   `D:\3.9.3_Spec-Kit\bin\Debug\net9.0\appsettings.Live.json`
2. Repo-local ignored runtime config used for the smoke:
   `D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json`

## Config Comparison Finding On 2026-04-01

The local source comparison narrowed one likely TD readiness issue:

1. `Spec-Kit` live config uses:
   `ProductInfo=iQuant`, `AppID=client_iq_3.6.2`, `AuthCode=RFLEXUGHCKIKWGPC`
2. `myvnpy` live gateway config uses:
   `产品名称=client_iq_3.6.2`, `授权编码=RFLEXUGHCKIKWGPC`, with no separate `AppID`
3. Therefore the Chinese-key gateway config shape should treat `产品名称=client_iq_3.6.2` as an `AppID` compatibility source first, not as sufficient evidence of `ProductInfo`
4. This finding improves VnPy-style config compatibility, but it does not by itself close the current `TD Authenticate Failed: ErrorID=63` gap, because the `Spec-Kit` smoke config already includes an explicit `AppID`

## Repo-Owned Native Pack

The repository-local bootstrap pack was synced into:

1. `D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\CTPProviderSwig.dll`
2. `D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\CTPProviderSwig.Core.dll`
3. `D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\iTrading.Core.dll`
4. `D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\iTradingQuant.dll`
5. `D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\ctp_native.dll`
6. `D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\thostmduserapi_se.dll`
7. `D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\thosttraderapi_se.dll`

## Outcome

Observed successful `MD` login and `rb2610` market data on 2026-04-01:

```text
MD login callback: success=True error=0 message=
MD subscribe => 0 [rb2610]
TICK rb2610 last=3137 bid=3136 ask=3137 ts=1775052501781380
SUCCESS first matching tick => rb2610 last=3137 bid=3136 ask=3137 ts=1775052501781380
```

Full output is stored at:

1. [rb2610_md_smoke_20260401.log](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/rb2610_md_smoke_20260401.log)

## Open Issue

The same smoke still shows `TD` authentication instability on the selected front:

```text
TD Authenticate Failed: ErrorID=63
```

So the current state is:

1. `rb2610` quote receipt is proven
2. Repo-owned `ctpnative` bootstrap pack is proven
3. Full `TD` account-ready acceptance remains open
4. VnPy-style Chinese-key configs now have a clearer compatibility rule for `AppID`
5. The current `TD Authenticate Failed: ErrorID=63` root cause remains partially open
