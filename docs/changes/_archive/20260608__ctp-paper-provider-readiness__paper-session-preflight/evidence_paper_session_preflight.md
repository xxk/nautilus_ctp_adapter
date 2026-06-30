# Evidence: Paper Session Preflight

**change-id**：`20260608__ctp-paper-provider-readiness__paper-session-preflight`
**日期**：2026-06-08
**account profile**：`openctp-paper`
**evidence class**：`paper-simulation`

## Commands

```powershell
python -m pytest tests/test_openctp_env_config.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_paper_session_preflight.py --help
python scripts/ctp_paper_session_preflight.py --config cfgs/ctp.openctp.tts.7x24.example.json
python scripts/ctp_paper_session_preflight.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-session-preflight-config-only.json
python scripts/ctp_paper_session_preflight.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --connect-paper --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-session-preflight-connect.json
```

## Result

| Check | Result | Notes |
| --- | --- | --- |
| Focused tests | passed | 7 tests passed |
| Help command | passed | command surface available |
| Example config | typed blocker | missing account fields returned `paper-resource`, no traceback |
| Local config-only preflight | passed | redacted request-only summary emitted |
| Paper connect preflight | passed | TD/MD login, settlement confirmation, first tick and bridge events recorded |

## Redaction Boundary

1. Evidence records only presence/fingerprint/disposition fields for account identity.
2. Raw account id, password, auth code and private front values must not be copied into tracked docs.
3. `--connect-paper` does not send orders; it only checks paper TD/MD session readiness.
