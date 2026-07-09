# OpenCTP TTS 7x24 Runbook

**change-id**: `20260607__openctp-tts__test-baseline`
**last updated**: 2026-06-08

## Scope

This runbook is the account-profile authority for CTP local execution. It fixes
the default 24h API debug account as `openctp-tts-7x24-simulation`, separates
OpenCTP 仿真, broker paper, and formal trading account paths, and covers config
generation, TTS CTPAPI runtime preparation, login smoke, and evidence capture.
It must not contain account passwords or local secret values.

## Default Selection Rule

If the task says "debug API", "24h debug", "development smoke", "provider API
debug", "login/query/order dry-run debug", or does not explicitly request
broker-specific 仿真 / final broker evidence, use:

```text
account_profile: openctp-tts-7x24-simulation
config_path: cfgs/local/ctp.openctp.tts.7x24.local.json
evidence_class: openctp-tts-7x24-simulation
default_symbol: TEST
```

Do not ask which account to use for 24h API debugging. Ask only when the user
explicitly requests broker-specific 仿真, broker paper, or formal final evidence
and the required local config is missing.

## Account Profile Matrix

Every proposal, child change, runbook command, and evidence file that touches a
live CTP front must declare exactly one account profile.

| Profile | Purpose | Secret source | Local config | Evidence use | Must not be used for |
| --- | --- | --- | --- | --- | --- |
| `repo-only` | Contract tests, fake normalized CTP payloads, docs gates | none | none | repo-only guard/reference | any external front or account evidence |
| `openctp-tts-7x24-simulation` | Default 24h API debugging: login, MD, TD, query, dry-run, guarded simulated send | `.env.d/openctp-tts-7x24-simulation.env` keys prefixed `OPENCTP_TTS_7X24_` | `cfgs/local/ctp.openctp.tts.7x24.local.json` | 24h TTS simulation evidence | formal broker readiness or broker-specific 仿真 claims |
| `openctp-simenv` | OpenCTP 仿真环境 validation when the task explicitly asks for simenv rather than 7x24 replay/debug | `.env.d/openctp-simenv.env` keys prefixed `OPENCTP_SIMENV_` | `cfgs/local/ctp.openctp.simenv.local.json` | OpenCTP 仿真 evidence | default 24h API debug or final broker evidence |
| `broker-paper` | Futures-company / broker-provided paper or 仿真 account validation | `.env.d/broker-paper.env` keys prefixed `CTP_BROKER_PAPER_` | `cfgs/local/ctp.broker.paper.local.json` or approved ignored broker paper config | broker-specific paper evidence | 24h CI-like debug or formal final evidence |
| `formal-trading` | Broker-facing formal validation before production use | `.env.d/formal-trading.env` keys prefixed `CTP_FORMAL_` or existing ignored formal local config | `cfgs/local/ctp.live.formal.local.json` or approved broker-specific ignored config | final broker-facing evidence | 24h dev loop, weekend CI, OpenCTP simulation acceptance, or ordinary development closeout |

Legacy alias: historical docs/evidence may contain `openctp-paper`. Treat it as
an alias for `openctp-tts-7x24-simulation` when reading old evidence, but write
new runbook commands and new evidence with `openctp-tts-7x24-simulation`.

Selection rules:

1. Proposal `README.md` and `phase-plan.md` must name the intended profile before any live CTP command is accepted as evidence.
2. If no profile is declared, only repo-only tests, mock/scaffold checks, and dry-run commands are allowed.
3. `openctp-tts-7x24-simulation` evidence can unblock 24h development loops, but it cannot satisfy OpenCTP 仿真, broker paper, or formal broker/trading readiness.
4. `openctp-simenv` and `broker-paper` commands may run only when the proposal, child change, or user request explicitly asks for that account class.
5. `formal-trading` commands may only run when the proposal or child change explicitly asks for formal broker evidence and guardrails are reviewed for the current account state.
5. Never copy secrets from `.env.d/`, `.env`, or `cfgs/local/` into proposal docs, change docs, evidence markdown, stdout snapshots, or tracked config examples.
6. `TEST` belongs to `openctp-tts-7x24-simulation`; real broker symbols such as `c2609` belong to broker-specific paper/formal profiles. Do not mix instruments or guardrails across profiles.

## Timeout Triage

When an OpenCTP TTS command times out, check the public environment monitor
before assigning the blocker:

```powershell
Invoke-WebRequest -Uri 'http://www.openctp.cn/simenv.html' -UseBasicParsing -TimeoutSec 20
```

Record the target rows in evidence:

1. `openctp-7x24` TD `tcp://trading.openctp.cn:30001`
2. `openctp-7x24` MD `tcp://trading.openctp.cn:30011`
3. `openctp-仿真` TD `tcp://trading.openctp.cn:30002` when a simenv task is in scope
4. `openctp-vip仿真` TD `tcp://vip.openctp.cn:30003` when a vip simenv task is in scope

If the monitor reports the target front as `running` and `connected`, do not
classify the blocker as server-down. Continue diagnosis under local native
session lifecycle, login/query callback completion, account/session state,
network path, runtime DLL mismatch, or front/profile mismatch.

2026-06-08 P004 timeout check observed `openctp-7x24` TD `30001` and MD
`30011` as `running`/`connected`; `openctp-仿真` `30002` and
`openctp-vip仿真` `30003` were also `running`/`connected`.

## Local Secrets

Create `.env` from `.env.example` for the selected profile only, then keep
account secrets in ignored `.env.d/<profile>.env`.

Base selector:

```powershell
CTP_ACCOUNT_PROFILE=openctp-tts-7x24-simulation
```

24h API debug secrets:

```powershell
# .env.d/openctp-tts-7x24-simulation.env
OPENCTP_TTS_7X24_USER_ID=<tts-7x24-account>
OPENCTP_TTS_7X24_PASSWORD=<tts-7x24-password>
OPENCTP_TTS_API_ROOT=output/openctp/tts-sdk/tts_6.6.9-win64-combined
OPENCTP_TTS_CONFIG=cfgs/local/ctp.openctp.tts.7x24.local.json
```

Optional OpenCTP 仿真 environment values, only when explicitly needed:

```powershell
# .env.d/openctp-simenv.env
CTP_ACCOUNT_PROFILE=openctp-simenv
OPENCTP_SIMENV_USER_ID=<openctp-simenv-account>
OPENCTP_SIMENV_PASSWORD=<openctp-simenv-password>
OPENCTP_SIMENV_CONFIG=cfgs/local/ctp.openctp.simenv.local.json
```

Optional broker paper / futures-company 仿真 values, only when explicitly needed:

```powershell
# .env.d/broker-paper.env
CTP_ACCOUNT_PROFILE=broker-paper
CTP_BROKER_PAPER_BROKER_ID=<broker-id>
CTP_BROKER_PAPER_USER_ID=<broker-paper-user>
CTP_BROKER_PAPER_PASSWORD=<broker-paper-password>
CTP_BROKER_PAPER_TD_FRONT=<tcp://td-front>
CTP_BROKER_PAPER_MD_FRONT=<tcp://md-front>
CTP_BROKER_PAPER_CONFIG=cfgs/local/ctp.broker.paper.local.json
```

For formal broker/trading validation, keep `.env.d/formal-trading.env` as the
secret source and fill the `CTP_FORMAL_` keys instead of asking for credentials
in chat:

```powershell
# .env.d/formal-trading.env
CTP_ACCOUNT_PROFILE=formal-trading
CTP_FORMAL_BROKER_ID=<broker-id>
CTP_FORMAL_USER_ID=<formal-user>
CTP_FORMAL_PASSWORD=<formal-password>
CTP_FORMAL_PRODUCT_INFO=<product-info>
CTP_FORMAL_APP_ID=<app-id>
CTP_FORMAL_AUTH_CODE=<auth-code>
CTP_FORMAL_TD_FRONT=<tcp://td-front>
CTP_FORMAL_MD_FRONT=<tcp://md-front>
CTP_FORMAL_CONFIG=cfgs/local/ctp.live.formal.local.json
```

Generate the ignored local config:

```powershell
python scripts/write_openctp_tts_config_from_env.py
```

Expected signals for 24h API debug config:

1. `account_profile: openctp-tts-7x24-simulation`
2. `password_present: true`
3. `path: cfgs\local\ctp.openctp.tts.7x24.local.json`
4. `allow_empty_broker_id: false`
5. `allow_live_order_smoke: false`

The current helper generates only the `openctp-tts-7x24-simulation` config.
`openctp-paper` in `.env` is accepted only as a legacy alias. OpenCTP simenv,
broker paper, and formal broker config generation remain follow-ups unless a
child change explicitly scopes them; until then, those account values stay in
`.env.d/`, `.env`, or ignored `cfgs/local/` files.

## Proposal Usage Rules

When a proposal needs CTP evidence, add an account-profile line to its scope or
phase plan:

```yaml
ctp_account_profile: repo-only | openctp-tts-7x24-simulation | openctp-simenv | broker-paper | formal-trading
ctp_config_path: cfgs/local/<selected-config>.json
ctp_evidence_class: repo-only | openctp-tts-7x24-simulation | openctp-simenv | broker-paper | formal-broker
```

Required mapping:

1. `repo-only` -> no external front, no account secret, no live broker evidence
2. `openctp-tts-7x24-simulation` -> `ctp_evidence_class: openctp-tts-7x24-simulation`
3. `openctp-simenv` -> `ctp_evidence_class: openctp-simenv`
4. `broker-paper` -> `ctp_evidence_class: broker-paper`
5. `formal-trading` -> `ctp_evidence_class: formal-broker`

Reject the proposal evidence if:

1. the profile is missing;
2. the config path points to the wrong account class;
3. OpenCTP TTS 7x24 evidence is used to close OpenCTP 仿真, broker paper, or formal broker acceptance rows;
4. formal account credentials appear in tracked files;
5. OpenCTP `TEST` evidence is mixed with real broker `c2609` guardrails.

## P004 Provider Completeness Commands

P004 adds these stable simulation-provider entrypoints on top of the baseline login/query commands. Keep all evidence under `output/reports/p004-openctp-tts-simulation-provider-completeness/`.

```powershell
python scripts/ctp_paper_readonly_snapshot.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --instrument c2609 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/<phase>/pre_snapshot.json
python scripts/ctp_guarded_paper_order_loop.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --pre-snapshot <pre-snapshot.json> --instrument c2609 --side BUY --quantity 1 --limit-price 2300 --client-order-id <id> --output-json <order-evidence.json>
python scripts/ctp_guarded_paper_cancel_loop.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --client-order-id <id> --instrument c2609 --order-ref <ref> --front-id <front> --session-id <session> --output-json <cancel-evidence.json>
python scripts/ctp_paper_recovery_idempotency.py --run-id p004-real-reconnect-rehearsal --attempt 1 --md-symbol c2609 --md-symbol zn2610 --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/real-reconnect-evidence/reconnect_rehearsal_pass.json
python scripts/ctp_nautilus_engine_harness.py --run-id p004-nautilus-engine-harness --output-json output/reports/p004-openctp-tts-simulation-provider-completeness/nautilus-engine-harness/engine_harness_provider_reports.json
```

P004 closeout status is `blocked` only because true forced MD/TD reconnect evidence cannot be generated safely against the public OpenCTP 7x24 front from this workspace. Do not convert the repo-only reconnect rehearsal into a real reconnect pass. The unblock condition is operator-controlled front disconnect/restart, process-scoped network interruption approval, or a dedicated simulation/broker paper environment where forced reconnect is allowed.

## Runtime / SDK

OpenCTP TTS requires replacing the standard CTP runtime DLLs with TTS-compatible
CTPAPI DLLs of the same API version. Keep downloaded SDK/runtime files under
`output/openctp/` or another ignored local path. Use the official TTS package,
not the generic CTPAPI-Python package, for the repository C++ bridge.

For the current Windows development path:

```powershell
$env:CTP_VENDOR_SDK_ROOT=(Resolve-Path output/openctp/tts-sdk/tts_6.6.9-win64-combined).Path
Copy-Item output/openctp/tts-sdk/tts_6.6.9-win64-combined/thostmduserapi_se.dll rust/target/debug/thostmduserapi_se.dll -Force
Copy-Item output/openctp/tts-sdk/tts_6.6.9-win64-combined/thosttraderapi_se.dll rust/target/debug/thosttraderapi_se.dll -Force
python scripts/check_rust_gate.py
Copy-Item rust/target/debug/_ctp_runtime.dll src/ctp_runtime/_ctp_runtime.cp312-win_amd64.pyd -Force
```

The final copy keeps the Python development package aligned with the latest Rust
build. Do not commit generated binaries or downloaded OpenCTP runtime files.

## Connectivity Gate

Before interpreting login failures as account or adapter failures, verify TCP
reachability:

```powershell
Test-NetConnection -ComputerName trading.openctp.cn -Port 30001
Test-NetConnection -ComputerName trading.openctp.cn -Port 30011
Test-NetConnection -ComputerName vip.openctp.cn -Port 30003
```

Expected: `TcpTestSucceeded: True` for TD `30001` and MD `30011`.

If these are false while `http://www.openctp.cn/` is reachable, record a network
blocker. Do not mark live smoke as passed.

## Login Smoke

Prepare environment:

```powershell
$env:CTP_VENDOR_SDK_ROOT=(Resolve-Path output/openctp/tts-sdk/tts_6.6.9-win64-combined).Path
$env:PATH=(Resolve-Path rust/target/debug).Path + ';' + $env:PATH
```

Run MD and TD login smokes:

```powershell
python scripts/ctp_md_login_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --timeout-seconds 30 --session-label openctp-tts-724-md --evidence-root output/debug/openctp-tts
python scripts/ctp_td_login_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --timeout-seconds 30 --session-label openctp-tts-724-td --evidence-root output/debug/openctp-tts
```

For formal broker evidence, replace the config path and session label with the
declared formal profile values, for example:

```powershell
python scripts/ctp_md_login_smoke.py --config cfgs/local/ctp.live.formal.local.json --timeout-seconds 30 --session-label formal-trading-md --evidence-root output/debug/formal-trading
python scripts/ctp_td_login_smoke.py --config cfgs/local/ctp.live.formal.local.json --timeout-seconds 30 --session-label formal-trading-td --evidence-root output/debug/formal-trading
```

Run formal broker commands only inside a proposal/change whose acceptance row
requires `ctp_account_profile: formal-trading`.

Evidence paths:

```text
output/debug/openctp-tts/openctp-tts-724-md/md_login_smoke.json
output/debug/openctp-tts/openctp-tts-724-td/td_login_smoke.json
```

Pass criteria:

1. MD login succeeds and at least one `TEST` tick is observed.
2. TD login succeeds and settlement confirmation succeeds.
3. No live order is submitted unless local config explicitly arms
   `ExecutionGuardrails.AllowLiveOrderSmoke=true`.

## Official Reference

OpenCTP public docs list TTS 7x24 as:

1. TD front: `tcp://trading.openctp.cn:30001`
2. MD front: `tcp://trading.openctp.cn:30011`
3. `BrokerID`: `9999`
4. `AppID` / `AuthCode`: empty for OpenCTP simulation
5. `TEST`, `BTC`, and `MINUS`: useful 7x24 customer-to-customer test symbols

Reference entries: `http://www.openctp.cn/simenv.html`, `http://www.openctp.cn/TTS-CTPAPI.html`

## Account Type Difference

1. `openctp-tts-7x24-simulation` is the default 24h API debugging profile. It is
   optimized for always-on development feedback and uses the OpenCTP TTS 7x24
   front with `TEST` by default.
2. `openctp-simenv` is OpenCTP's 仿真 environment profile. Use it when the task
   asks to validate against 仿真 rather than 7x24 replay/debug.
3. `broker-paper` is a broker/futures-company paper or 仿真 account. Use it for
   broker-specific compatibility evidence, not for default 24h debugging.
4. `formal-trading` is final broker/trading evidence. It must not be used for
   daily development or exploratory API debugging.
