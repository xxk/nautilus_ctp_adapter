# Python Mainline MD Login Smoke Evidence

**Date**: 2026-04-02
**Change ID**: 20260401__ctp-live-connectivity__python-rust-md-login-path

## Command

```powershell
python scripts\ctp_md_login_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## Goal

This smoke proves the repository-owned Python mainline can reach `ctp_native.dll` directly enough to:

1. locate the repository-managed native pack
2. initialize the MD front
3. complete MD login for live account `025292`

It does **not** yet prove `rb2610` subscription or tick receipt through the same Python mainline path.

## Outcome

Observed on 2026-04-02:

```text
MdInit => 0
MdLogin => 0
{"success": true, "error_id": 0, "error_message": "", "front_id": 0, "session_id": 0, "max_order_ref": 0}
MD Front Connected
MD Auto-login: 0155/025292
MD OnRspUserLogin called: pRspInfo=...
  ErrorID=0, ErrorMsg=CTP:No Error
MD Login Success: FrontID=0, SessionID=0
```

## Current Blocker

`MdSubscribe` has not yet been frozen at the pure-Python `ctypes` boundary.

Current findings:

1. direct `ctypes` login is proven
2. two guessed `MdSubscribe` signatures caused access violations, so the subscribe ABI must not be guessed further
3. next step should freeze the subscribe signature from repository-owned wrapper code or from a trusted native declaration source, then resume `rb2610` tick verification
