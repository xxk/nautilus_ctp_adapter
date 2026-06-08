# OpenCTP TTS 7x24 Simulation Provider Readiness Runbook

**change-id**：`20260608__ctp-paper-provider-readiness__paper-ops-closeout`
**account profile**：`openctp-tts-7x24-simulation`
**scope**：OpenCTP TTS 7x24 simulation development and rehearsal only. Do not use this runbook to claim formal broker / Live readiness.

## Inputs

| Item | Required value |
| --- | --- |
| Config | `cfgs/local/ctp.openctp.tts.7x24.local.json` |
| Secret storage | `.env` or ignored local config only |
| Evidence root | `output/reports/p003-ctp-live-trading-provider-readiness/` |
| Account profile | `openctp-tts-7x24-simulation` |
| Evidence class | `openctp-tts-7x24-simulation` |

Tracked docs and reports must not contain raw account id, password, auth code, broker private fields, or unredacted private front data.

## Command Matrix

| Phase | Purpose | Command |
| --- | --- | --- |
| 1 | Config-only paper preflight | `python scripts/ctp_paper_session_preflight.py --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-session-preflight-config-only.json` |
| 1 | TD/MD paper session preflight | `python scripts/ctp_paper_session_preflight.py --connect-paper --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-session-preflight-connect.json` |
| 2 | Config-only read-only snapshot | `python scripts/ctp_paper_readonly_snapshot.py --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-config-only.json` |
| 2 | Connected read-only truth snapshot | `python scripts/ctp_paper_readonly_snapshot.py --connect-paper --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-connect.json` |
| 3 | Guarded paper order dry-run | `python scripts/ctp_guarded_paper_order_loop.py --pre-snapshot output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-connect.json --instrument TEST --side BUY --quantity 1 --limit-price 1 --client-order-id paper-order-contract --output-json output/reports/p003-ctp-live-trading-provider-readiness/guarded-paper-order-dry-run.json` |
| 3 | Armed-send safety blocker | `python scripts/ctp_guarded_paper_order_loop.py --pre-snapshot output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-connect.json --instrument TEST --side BUY --quantity 1 --limit-price 1 --client-order-id paper-order-armed-blocker --arm-paper-send --output-json output/reports/p003-ctp-live-trading-provider-readiness/guarded-paper-order-armed-blocker.json` |
| 4 | Recovery/idempotency evidence | `python scripts/ctp_paper_recovery_idempotency.py --run-id paper-recovery-acceptance --attempt 1 --evidence-root output/reports/p003-ctp-live-trading-provider-readiness/paper-recovery-idempotency --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-recovery-idempotency.json` |

## Pass / Blocker Semantics

| Result | Meaning | Operator action |
| --- | --- | --- |
| `status=passed` | The simulation/repo-only scenario produced complete redacted evidence | Keep artifact under the P003 report root |
| `status=blocked`, `blocker_type=paper-resource` | OpenCTP TTS 7x24 account/front/window/native resource or explicit send arm is unavailable | Keep typed blocker; do not convert to pass |
| `status=blocked`, `blocker_type=paper-safety` | Pre-snapshot/profile/guardrail is unsafe | Fix local input before any send attempt |
| `disposition=typed_blocker` | Recovery/reconnect cannot pass safely | Carry the blocker into closeout with next action |

## Correctness Checklist

| Capability | Required correctness signal |
| --- | --- |
| Contract query | `display_symbol`, `venue_symbol`, `exchange_id`, `product_kind`, `price_tick`, `volume_multiple` present and contract issues empty |
| Position query | long/short direction, total position, yesterday/today split and no-position disposition are distinct |
| Order preflight | intent maps to command side, qty, price, position effect, order ref, front id and session id |
| Order callback | duplicate fills are deduped; overfill and negative leaves qty are contract failures |
| Recovery | MD resubscribes each active symbol once; TD reconnect keeps `paper_send_armed=false`; historical residue is not current fill |

## Closeout Boundary

P003 closes OpenCTP TTS 7x24 simulation development readiness only. It does not close:

1. formal broker account readiness
2. real production trading window readiness
3. broker-specific front certification
4. unattended strategy trading approval

Those require a successor proposal or explicit formal-trading phase.
