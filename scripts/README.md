# Scripts

Put smoke tests, local diagnostics, and one-off bootstrap helpers here.

Current planned entrypoints:

1. `python scripts/sync_ctp_native.py`
2. `python scripts/ctp_md_login_smoke.py --config <path>`
3. `python scripts/ctp_td_login_smoke.py --config <path>`
4. `python scripts/ctp_nautilus_live_smoke.py --config <path>`

## Formal Baseline

The formal Nautilus-facing live smoke baseline is:

1. `python scripts/ctp_nautilus_live_smoke.py --config <path>`
2. It must be the default live smoke entrypoint reused by later topics.
3. The MD-only and TD-only scripts remain diagnostics helpers.

## Legacy Note

`scripts/ctp_live_smoke_host/` is legacy verification residue only.

1. It is not the current mainline.
2. Do not extend it for new work.
3. New smoke and adapter work must prefer the repository-owned local C wrapper path.
