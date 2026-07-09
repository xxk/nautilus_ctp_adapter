# Evidence: Guarded Paper Order Dry-run

**change-id**：`20260608__ctp-paper-provider-readiness__guarded-paper-order-loop`
**日期**：2026-06-08
**account profile**：`openctp-paper`
**evidence class**：`paper-simulation`

## Commands

```powershell
python -m pytest tests/test_guarded_paper_order_loop.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_guarded_paper_order_loop.py --help
python scripts/ctp_guarded_paper_order_loop.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --pre-snapshot output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-connect.json --instrument TEST --side BUY --quantity 1 --limit-price 1 --client-order-id paper-dry-run-1 --output-json output/reports/p003-ctp-live-trading-provider-readiness/guarded-paper-order-dry-run.json
python scripts/ctp_guarded_paper_order_loop.py --pre-snapshot output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-connect.json --instrument TEST --side BUY --quantity 1 --limit-price 1 --client-order-id paper-order-armed-blocker --arm-paper-send --output-json output/reports/p003-ctp-live-trading-provider-readiness/guarded-paper-order-armed-blocker.json
```

## Result

| Check | Result | Notes |
| --- | --- | --- |
| Focused tests | passed | 7 tests passed |
| Help command | passed | command surface available |
| Dry-run command | passed | `paper_send_armed=false`; no native paper send requested; lifecycle verdict is `dry_run_preflight` |
| Intent command contract | passed | side/qty/price/effect/order ref/front/session validation covered by tests |
| Callback lifecycle contract | passed | duplicate fill, overfill and negative leaves qty are typed contract failures |
| Armed send without config arm | typed blocker | `guarded-paper-order-armed-blocker.json` records `paper-resource` RuntimeError before native send |

## Remaining

1. Real paper submit/cancel/fill/reject/timeout remains a successor paper-send evidence path that requires explicit local config arm.
2. This change is closed by repo-only lifecycle contract evidence plus typed `paper-resource` blocker for unarmed paper send.
3. No formal-trading / Live evidence is claimed.
