# Acceptance Plan

**Status**: passed
**Date**: 2026-04-01
**Change ID**: 20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610
**Related Plan**: ./plan.md
**Related AI Constraints**: ./ai_constraints.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 10:31"
concluded_by: "Codex"

exit_conditions:
  success_scenarios: pass
  failure_scenarios: pass
  verification_cmds: pass
  evidence_collected: pass
```
<!-- AI-STATUS-END -->

## Goal

Prove that `nautilus_ctp_adapter` can use locally sourced CTP dependencies and secure local config to log into account `025292` and receive market data for `rb2610` without storing live secrets in tracked files.

## Scenarios

| # | Scenario | Execution | Expected | Evidence |
| --- | --- | --- | --- | --- |
| A1 | Live config contract is complete | Inspect the tracked config schema and the local secret source selected for this change | All required live fields are accounted for, and secret values are loaded from untracked local material | [rb2610 quote evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md) |
| A2 | Native dependency pack is reproducible | Resolve the chosen sample dependency bundle and verify the loader targets `ctp_native.dll`, `thostmduserapi*.dll`, and `thosttraderapi*.dll` from one x64 source | The repository has one clear dependency source and matching loader expectations | [rb2610 quote evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260401_rb2610_quote.md) |
| A3 | Account `025292` can complete the login-ready path | Run the repo live smoke entrypoint added by this change with the local live config | The runtime reaches connected, authenticated, and logged-in ready state | Passed. `TD` readiness is now evidenced through the repository-owned local `c wrapper` path. See [TD readiness evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__td-auth-and-login-readiness/evidence_20260402_td_login_readiness.md) and [Nautilus live smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md). |
| A4 | `rb2610` subscription returns market data | Use the same live smoke path to request `rb2610` market data | At least one `rb2610` market-data event is observed by the runtime or adapter layer | Passed. See [Python MD subscribe evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__python-rust-md-login-path/evidence_20260402_python_md_subscribe_smoke.md) and [Nautilus live smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md). |
| A5 | Failure cases are diagnosable | Execute at least one negative-path check such as missing config or missing DLLs | Failure output clearly indicates which prerequisite is missing | Passed. Wrong `TdAuthenticate` argument order now cleanly reproduces `ErrorID=63`, and the resulting disconnect loop is documented in [TD readiness evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__td-auth-and-login-readiness/evidence_20260402_td_login_readiness.md). |

## Exit Conditions

| # | Condition | Status | Evidence |
| --- | --- | :---: | --- |
| E1 | Blocking scenarios A1-A4 all pass | ☑ | A1-A4 are now backed by live evidence across C1/C3/C4/C5 |
| E2 | Failure interpretation for missing config or missing DLLs is clear | ☑ | `ErrorID=63` is now explained by wrong `TdAuthenticate` argument order and captured in C4 evidence |
| E3 | Required verification commands were executed and recorded | ☑ | `python -m pytest`, `python -m pip install -e .`, `python scripts/ctp_nautilus_live_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --md-timeout-seconds 20 --td-timeout-seconds 20` |
| E4 | Evidence is stored in this change bundle | ☑ | [topic 1 closure evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/evidence_20260402_topic1_closure.md), plus linked C3/C4/C5 evidence |
