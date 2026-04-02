# Acceptance Plan

**Status**: pending
**Date**: 2026-04-01
**Change ID**: 20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610
**Related Plan**: ./plan.md
**Related AI Constraints**: ./ai_constraints.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-04-01 22:31"
concluded_by: ""

exit_conditions:
  success_scenarios: partial
  failure_scenarios: partial
  verification_cmds: partial
  evidence_collected: partial
```
<!-- AI-STATUS-END -->

## Goal

Prove that `nautilus_ctp_adapter` can use locally sourced CTP dependencies and secure local config to log into account `025292` and receive market data for `rb2610` without storing live secrets in tracked files.

## Scenarios

| # | Scenario | Execution | Expected | Evidence |
| --- | --- | --- | --- | --- |
| A1 | Live config contract is complete | Inspect the tracked config schema and the local secret source selected for this change | All required live fields are accounted for, and secret values are loaded from untracked local material | [rb2610 quote evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md) |
| A2 | Native dependency pack is reproducible | Resolve the chosen sample dependency bundle and verify the loader targets `ctp_native.dll`, `thostmduserapi*.dll`, and `thosttraderapi*.dll` from one x64 source | The repository has one clear dependency source and matching loader expectations | [rb2610 quote evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md) |
| A3 | Account `025292` can complete the login-ready path | Run the repo live smoke entrypoint added by this change with the local live config | The runtime reaches connected, authenticated, and logged-in ready state | Pending. Current evidence shows `MD` login success but `TD Authenticate Failed: ErrorID=63`. New config analysis on 2026-04-01 clarified how VnPy-style Chinese-key configs should map `AppID` and `ProductInfo`, but it does not yet fully explain the current TD failure because the existing `Spec-Kit` smoke config already contains an explicit `AppID`. See [rb2610 quote evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md) |
| A4 | `rb2610` subscription returns market data | Use the same live smoke path to request `rb2610` market data | At least one `rb2610` market-data event is observed by the runtime or adapter layer | Passed on 2026-04-01. See [rb2610 smoke log](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/rb2610_md_smoke_20260401.log) |
| A5 | Failure cases are diagnosable | Execute at least one negative-path check such as missing config or missing DLLs | Failure output clearly indicates which prerequisite is missing | Partial. The live smoke clearly surfaces `TD Authenticate Failed: ErrorID=63`, but missing-config and missing-DLL negative paths are still open. |

## Exit Conditions

| # | Condition | Status | Evidence |
| --- | --- | :---: | --- |
| E1 | Blocking scenarios A1-A4 all pass | ⬜ | A4 passed, A3 still open because `TD` auth failed with error 63 |
| E2 | Failure interpretation for missing config or missing DLLs is clear | ☑ | `TD Authenticate Failed: ErrorID=63` is reproducible and captured; 2026-04-01 config comparison clarified the VnPy-style config compatibility rule, though the current TD root cause remains partially open |
| E3 | Required verification commands were executed and recorded | ☑ | `python -m pytest`, `python scripts/sync_ctp_native.py`, `dotnet run --project scripts/ctp_live_smoke_host/CtpLiveSmokeHost.csproj -- --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 30` |
| E4 | Evidence is stored in this change bundle | ☑ | [rb2610 quote evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md), [rb2610 smoke log](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/rb2610_md_smoke_20260401.log) |
