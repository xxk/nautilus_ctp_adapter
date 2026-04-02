# Change Plan

**Status**: completed
**Progress**: 100%
**Date**: 2026-04-01
**Topic ID**: ctp-live-connectivity
**Change ID**: 20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610
**Related Acceptance**: ./acceptance.md

## Summary

Implement the first Nautilus-targeted live CTP bootstrap in `nautilus_ctp_adapter` so the repository can log into futures account `025292` and subscribe market data for `rb2610`, while sourcing dependencies and secrets from local sample projects instead of committing them here.

## Scope

In scope:

1. Define the live config contract needed for account `025292`
2. Map the reusable dependency and DLL sample sources from local CTP projects into a repository-maintained `ctpnative` pack
3. Add the minimum runtime path for login, post-login readiness, and `rb2610` subscription
4. Add a repeatable smoke verification path and store evidence in this change bundle
5. Keep temporary C# tooling explicitly outside the long-term adapter path

Out of scope:

1. Full order-entry support
2. Position, account, and reconciliation completeness
3. SmartQuant adapter implementation
4. Multi-account configuration management
5. Long-term ownership of a C# host implementation

## Capability Mapping

```text
- capability_id: ctp-live-connectivity
- capability_name: Minimal live login and single-instrument market data bootstrap
- long_term_target: Nautilus adapter implementation backed by a repository-maintained ctpnative and shared runtime
- secondary_targets: secure config loading, dependency packaging, live diagnostics
- decision_target: prove the current runtime boundary can support real login and single-instrument market data without Nautilus core changes
- affects_long_term_rules: yes
- change_type: delivery
```

## Known Inputs And Missing Information

### Known local sample sources

1. Live-account sample config source: `D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig.Tests\bin\Debug\net9.0\appsettings.Live.json`
2. Generic CTP settings source: `D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig.Tests\bin\Debug\net9.0\CtpSettings.json`
3. Native dependency source: `D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig\native\bin`
4. Alternate packaged dependency source: `D:\3.9.3_Spec-Kit\QuantConnect\LeanWorkspaceRoll\bin\Plugins\Debug\net9.0`
5. External live gateway source: `D:\wt\myvnpy-main\.vntrader\connect_ctp.json`

### Required config fields

1. `user_id`: target is `025292`
2. `broker_id`
3. `password`
4. `auth_code`
5. `app_id`
6. `product_info`
7. `md_front`
8. `td_front`
9. `instruments`: must include `rb2610`
10. Optional runtime timing fields such as post-login delay and flow-file directory
11. Compatibility with Chinese-key live configs such as `用户名` / `密码` / `经纪商代码` / `交易服务器` / `行情服务器`

### Missing or must-confirm items before declaring success

1. Confirm the live sample credentials are still valid and should be injected from an untracked local file or environment variables
2. Confirm the chosen MD/TD fronts are reachable from the current machine
3. Confirm the `rb2610` contract is active and subscribable on the selected front
4. Confirm which x64 dependency bundle will be treated as the project-default sample pack
5. Confirm whether `AppID` is mandatory for the selected TD path, because the VnPy live config contains `产品名称` and `授权编码` but not an explicit `AppID`

### New confirmed finding on 2026-04-01

1. `D:\3.9.3_Spec-Kit\bin\Debug\net9.0\appsettings.Live.json` explicitly sets:
   `ProductInfo=iQuant`, `AppID=client_iq_3.6.2`, `AuthCode=RFLEXUGHCKIKWGPC`
2. `D:\wt\myvnpy-main\.vntrader\connect_ctp.json` contains:
   `产品名称=client_iq_3.6.2`, `授权编码=RFLEXUGHCKIKWGPC`, but no separate `AppID`
3. This means the Chinese-key VnPy config shape is not sufficient to infer `ProductInfo=iQuant` on its own, and `产品名称=client_iq_3.6.2` should be treated as an `AppID` compatibility source first

## Tasks

| Step | Task | Files | Output | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| P1 | Freeze the live-config contract and secret-loading rule for account `025292` | `docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md`, `docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/*`, `src/nautilus_ctp_adapter/adapters/ctp/config.py`, `cfgs/ctp.live.example.json` | Tracked config schema plus documented untracked secret source | `python -m pytest` | Completed |
| P2 | Select and document the dependency bundle for `ctp_native.dll` and the CTP API DLLs | `docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/*`, `src/nautilus_ctp_adapter/native/loader.py`, `vendor/ctp/README.md`, `scripts/sync_ctp_native.py` | One documented sample dependency pack and loader expectations | `python -m pytest`, `python scripts/sync_ctp_native.py` | Completed |
| P3 | Implement the minimum runtime login path up to post-login ready state | `rust/ctp_runtime_core/src/session.rs`, `rust/ctp_runtime_core/src/native.rs`, `src/nautilus_ctp_adapter/runtime/session.py`, `src/nautilus_ctp_adapter/runtime/bridge.py` | Runtime can reach connected, authenticated, and logged-in state through the Nautilus-targeted path | Runtime tests plus repo smoke evidence | Completed |
| P4 | Implement single-instrument market data subscription for `rb2610` | `rust/ctp_runtime_core/src/market.rs`, `src/nautilus_ctp_adapter/runtime/market.py`, `src/nautilus_ctp_adapter/adapters/ctp/data_client.py`, `cfgs/local/ctp.live.025292.rb2610.10675.json` | Runtime emits market-data events for `rb2610` and provides evidence for Nautilus wiring | Repo smoke evidence plus adapter integration follow-up | Completed |
| P5 | Capture smoke evidence and close acceptance gaps | `docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/*` | Evidence bundle with pass/fail interpretation | `python -m pytest`, `python -m pip install -e .` | Completed |

## Done Definition

Development done:

1. The repository has a documented and implemented live bootstrap path for account `025292`
2. Secrets remain outside tracked files
3. A single dependency-pack path is documented and supported by loader expectations
4. Temporary verification tooling is clearly marked as non-target architecture

Delivery done:

1. Acceptance scenarios for login and `rb2610` subscription pass
2. Evidence is stored in this change bundle

## Closure Notes

1. `rb2610` live tick is now evidenced through the Python mainline and the formal Nautilus-facing baseline.
2. `TD` readiness no longer blocks this anchor change; it is covered by `C4` and linked evidence.
3. Temporary C# host evidence remains historical only and is no longer part of the formal pass path.
