# Scripts

Put smoke tests, local diagnostics, and one-off bootstrap helpers here.

Current planned entrypoints:

1. `python scripts/sync_ctp_native.py`
2. `python scripts/ctp_md_login_smoke.py --config <path>`

## Legacy Note

`scripts/ctp_live_smoke_host/` is legacy verification residue only.

1. It is not the current mainline.
2. Do not extend it for new work.
3. New smoke and adapter work must prefer the repository-owned local C wrapper path.
