# Cancel Lifecycle Repo-only Contract Evidence

**change-id**: `20260608__openctp-tts-simulation-provider__cancel-lifecycle`
**proposal-id**: `p004-openctp-tts-simulation-provider-completeness`
**account_profile**: `openctp-tts-7x24-simulation`
**evidence_class**: `openctp-tts-7x24-simulation`
**scenario_ids**: `A1`, `A2`, `A3`, `A4`, `A5`, `A6`, `A7`, `A8`, `A9`, `A10`, `A11`, `A12`
**captured_at**: 2026-06-08
**last_updated**: 2026-06-08 18:55

## Scope

This evidence covers repo-only and dry-run cancel lifecycle contracts. It does not claim that a real OpenCTP TTS staged order was cancelled.

## Commands

```powershell
python -m pytest tests/test_guarded_paper_cancel_loop.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python -m pytest tests/test_guarded_paper_cancel_loop.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python -m pytest tests/test_smoke_import.py -q --basetemp output/pytest-tmp -p no:cacheprovider -k "check_rust_gate or pyo3_internal_td_live_session"
python scripts/check_rust_gate.py
python scripts/check_proposal_docs.py --root . --proposal-id p004-openctp-tts-simulation-provider-completeness
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
python -m pytest tests/test_paper_readonly_snapshot.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_paper_readonly_snapshot.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --connect-paper --timeout-seconds 20 --process-timeout-seconds 5 --completion-grace-seconds 2 --observation-grace-seconds 2 --flow-path output/ctp-flow/p004-cancel-pre --session-label p004-cancel-pre-20260608 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/pre_cancel_snapshot_live_timeout_blocker.json
Invoke-WebRequest -Uri 'http://www.openctp.cn/simenv.html' -UseBasicParsing -TimeoutSec 20
python scripts/ctp_td_login_smoke.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_TEST.local.json --timeout-seconds 30 --flow-path output/ctp-flow/p004-td-login-tts669-test --session-label p004-td-login-tts669-test --evidence-root output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle
python scripts/ctp_paper_readonly_snapshot.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_TEST.local.json --connect-paper --timeout-seconds 30 --process-timeout-seconds 45 --completion-grace-seconds 2 --observation-grace-seconds 2 --flow-path output/ctp-flow/p004-pre-cancel-tts669-test --session-label p004-pre-cancel-tts669-test --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/pre_cancel_snapshot_tts669_TEST.json
python scripts/ctp_guarded_paper_order_loop.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_c2609.armed.local.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/pre_cancel_snapshot_tts669_TEST.json --instrument c2609 --side BUY --quantity 1 --limit-price 2300 --client-order-id p004-cancel-stage-c2609-20260608-03 --arm-paper-send --timeout-seconds 20 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/stage_order_c2609_buy_2300.json
python scripts/ctp_guarded_paper_cancel_loop.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_c2609.armed.local.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/pre_cancel_snapshot_tts669_TEST.json --instrument c2609 --client-order-id p004-cancel-stage-c2609-20260608-03 --order-ref 2 --front-id 1 --session-id -1169162043 --exchange-id DCE --arm-cancel-send --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/cancel_order_c2609_ref2.json
python scripts/ctp_guarded_paper_order_loop.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_c2609.armed.local.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/post_cancel_snapshot_final_c2609.json --instrument c2609 --side BUY --quantity 1 --limit-price 2350 --client-order-id p004-fill-race-c2609-20260608-02 --arm-paper-send --timeout-seconds 20 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/fill_race_order_c2609_buy_2350.json
python scripts/ctp_guarded_paper_cancel_loop.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_c2609.armed.local.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/post_cancel_snapshot_final_c2609.json --instrument c2609 --client-order-id p004-fill-race-c2609-20260608-02 --order-ref 2 --front-id 1 --session-id -1153171226 --exchange-id DCE --arm-cancel-send --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/cancel_fill_race_pending_c2609_ref2_second.json
python scripts/ctp_paper_readonly_snapshot.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_c2609.readonly.local.json --connect-paper --timeout-seconds 30 --process-timeout-seconds 45 --completion-grace-seconds 2 --observation-grace-seconds 2 --flow-path output/ctp-flow/p004-post-cancel-cleanup-c2609 --session-label p004-post-cancel-cleanup-c2609 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/post_cancel_snapshot_cleanup_c2609.json
python scripts/ctp_query_adapter_smoke.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/tts_7x24_c2609.readonly.local.json --instrument-symbol c2609 --include-order-trade-snapshot --timeout-seconds 30 --flow-path output/ctp-flow/p004-order-trade-cleanup-c2609 --session-label p004-order-trade-cleanup-c2609 --evidence-root output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle
python scripts/ctp_guarded_paper_cancel_loop.py --config output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/redacted_cancel_fixture_config.json --pre-snapshot output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/redacted_pre_cancel_snapshot.json --instrument rb2610 --client-order-id cancel-dry-run-contract-20260608 --order-ref 42 --front-id 7 --session-id 8 --exchange-id SHFE --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/cancel_dry_run_contract.json
```

## Result

| Check | Result |
| --- | --- |
| Cancel contract tests | `4 passed` |
| Nautilus integration regression and duplicate callback idempotency | `70 passed` |
| Combined P004 cancel + Nautilus regression | `74 passed` |
| Rust gate / native bridge | `PASS rust-gate: cargo-check`, `PASS rust-gate: cargo-build`, `PASS rust-gate: ctp_py-build`, `PASS rust-gate: cargo-test` |
| Gate regression tests | `9 passed, 204 deselected` for check-rust-gate and PyO3 TD live-session visibility |
| Read-only snapshot watchdog tests | `7 passed` |
| Proposal/change/harness docs | `PROPOSAL_DOCS_CHECK_OK`, `CHANGE_DOCS_CHECK_OK`, `HARNESS_CHECK_OK` |
| Real simulation pre-cancel snapshot attempt | typed blocker: `failure_reason=connect_process_timeout`, `blocker_type=paper-resource`, `snapshot_complete=false` |
| OpenCTP server status page check | `http://www.openctp.cn/simenv.html` returned HTTP 200; target TTS fronts reported running/connected |
| Environment recovery | official TTS 6.6.9 runtime/SDK restored; TD login/account/position/instrument query passed |
| Pre-cancel connected snapshot | `pre_cancel_snapshot_tts669_TEST.json`: `success=true`, account/position/instrument/order-trade snapshot passed |
| Passive order staging | `stage_order_c2609_buy_2300.json`: `disposition=accepted`, `leaves_qty=1`, native identity captured |
| Active cancel command | `cancel_order_c2609_ref2.json`: native cancel `accepted=true`, `native_code=0`; no disconnects |
| Post-cancel residual check | `post_cancel_snapshot_final_c2609.json` and `p004-order-trade-final-c2609/aggregated_query.json`: no current-session order/trade residual |
| Fill-before-cancel race | `fill_race_order_c2609_buy_2350.json` followed by `cancel_fill_race_pending_c2609_ref2_second.json`; final cleanup snapshot shows c2609 LONG 1 and no current-session order residual |
| Dry-run cancel contract | `success=true`, `status=passed`, `action_mode=dry_run`, `cancel_send_armed=false` |
| Dry-run native send boundary | `command_kinds=[]`; no runtime cancel command submitted |
| Command contract | `disposition=cancel_contract_passed`, no issues |

## Native Runtime Loader Finding

Before the gate fix, `python scripts/check_rust_gate.py` failed at `cargo-test` with `STATUS_ENTRYPOINT_NOT_FOUND` while launching `_ctp_runtime-*.exe`. Root cause was stale CTP runtime DLLs under Cargo target output directories taking precedence over the repo `vendor/ctp/bin` runtime pack during test process loading.

The gate now synchronizes `thostmduserapi_se.dll` and `thosttraderapi_se.dll` from `vendor/ctp/bin` into Cargo `debug` and `debug/deps` loader directories before `cargo test`. The Python package loader also registers all repo native candidate directories so `ctp_runtime._ctp_runtime` resolves the repo-built `ctp_native.dll` before fallback vendor copies.

The local Python 3.12 editable extension was refreshed from `rust/target/debug/_ctp_runtime.dll`; `CtpTdLiveSession.order_action` is import-visible.

## Simulation Pre-cancel Snapshot Attempt

The first connected pre-cancel snapshot command exceeded the outer shell timeout and produced no payload. To prevent live API debugging from hanging without evidence, `ctp_paper_readonly_snapshot.py` now runs connected snapshots behind a process-level watchdog.

The guarded retry wrote:

```text
output/reports/p004-openctp-tts-simulation-provider-completeness/cancel-lifecycle/pre_cancel_snapshot_live_timeout_blocker.json
```

The payload is redacted and records `connect_process_timeout` as a typed `paper-resource` blocker. Because the pre-cancel snapshot did not complete, no staged order or armed cancel was attempted.

## Timeout Server Status Check

Before treating the timeout as an OpenCTP service outage, the public monitoring page was checked:

```text
http://www.openctp.cn/simenv.html
```

Observed rows for the target TTS system:

| Environment | Front | Status |
| --- | --- | --- |
| `openctp-7x24` | TD `tcp://trading.openctp.cn:30001` | `running`, `connected`, response time `0 milliseconds` |
| `openctp-7x24` | MD `tcp://trading.openctp.cn:30011` | `running`, `connected`, response time `1 milliseconds` |
| `openctp-仿真` | TD `tcp://trading.openctp.cn:30002` | `running`, `connected`, response time `0 milliseconds` |
| `openctp-vip仿真` | TD `tcp://vip.openctp.cn:30003` | `running`, `connected`, response time `0 milliseconds` |

Conclusion: the observed `connect_process_timeout` should not be recorded as "OpenCTP target front down" for the 7x24 profile. Next diagnosis should focus on local native session lifecycle, login/query callback completion, account/session state, or front/protocol mismatch.

## Redaction

The generated fixture config and snapshot use redacted placeholder credentials only. No raw account id, password, auth code, broker private field, or private front is present in this tracked evidence.

## Simulation Completion Notes

The real OpenCTP TTS simulation path required restoring the official TTS 6.6.9 runtime/SDK and putting `rust/target/debug` first on `PATH`. Before that recovery, TD login returned repeated disconnect reason `4097` even though the OpenCTP monitor page showed target fronts running.

The cancel action returned `native_code=0` but did not emit an order callback in the cancel session. Post-cancel snapshots and order-trade snapshots were therefore used as the residual-order truth source. Final cleanup evidence showed no current-session order or trade residual. The fill-race attempt resulted in c2609 LONG 1 before cancel, and the subsequent cleanup snapshot still showed no current-session order residual.
