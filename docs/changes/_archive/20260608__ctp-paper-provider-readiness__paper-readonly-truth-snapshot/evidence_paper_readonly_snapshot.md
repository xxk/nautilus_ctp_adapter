# Evidence: Paper Read-only Truth Snapshot

**change-id**：`20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot`
**日期**：2026-06-08
**account profile**：`openctp-paper`
**evidence class**：`paper-simulation`

## Commands

```powershell
python -m pytest tests/test_paper_readonly_snapshot.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/ctp_paper_readonly_snapshot.py --help
python scripts/ctp_paper_readonly_snapshot.py --config cfgs/ctp.openctp.tts.7x24.example.json
python scripts/ctp_paper_readonly_snapshot.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-config-only.json
python scripts/ctp_paper_readonly_snapshot.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --connect-paper --timeout-seconds 30 --output-json output/reports/p003-ctp-live-trading-provider-readiness/paper-readonly-snapshot-connect.json
```

## Result

| Check | Result | Notes |
| --- | --- | --- |
| Focused tests | passed | 6 tests passed |
| Help command | passed | command surface available |
| Example config | typed blocker | missing account fields returned `paper-resource`, no traceback |
| Local config-only snapshot | passed | redacted request-only summary emitted |
| Paper connect snapshot | passed | account, position, instrument, and order/trade read-only snapshot emitted |

## Correctness Coverage

1. Account identity is redacted to presence and fingerprint fields.
2. Position correctness covers direction, total quantity, today/yesterday split and malformed values.
3. Instrument correctness covers display symbol, venue symbol, exchange, product kind, price tick and volume multiple.
4. Order/trade section is read-only callback observation only; this change does not send orders.
