# Close Position Semantics Evidence - 2026-06-08

## Scope

- Proposal: `p004-openctp-tts-simulation-provider-completeness`
- Change: `20260608__openctp-tts-simulation-provider__close-position-semantics`
- Account profile: `openctp-tts-7x24-simulation`
- Evidence class: `openctp-tts-7x24-simulation`
- Formal trading: not used

## Server Status Preflight

Source checked before connected/order-capable runs:

- `http://www.openctp.cn/simenv.html`
- HTTP status: `200`
- Generated at: `2026-06-08 21:02:00`
- `openctp-7x24` TD `tcp://trading.openctp.cn:30001`: `running`, `connected`, response time `0 ms`
- `openctp-7x24` MD `tcp://trading.openctp.cn:30011`: `running`, `connected`, response time `1 ms`

Conclusion: no upstream server outage was observed before close-position evidence collection.

## Repo Contract Evidence

Commands:

```powershell
python -m pytest tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider -k "ClosePositionSemantics"
python -m pytest tests/test_guarded_paper_order_loop.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Results:

- `7 passed, 70 deselected`
- `15 passed`

Covered contracts:

- `LONG` close maps to `SELL`; `SHORT` close maps to `BUY`.
- CTP offset mapping is explicit: `OPEN=0`, `CLOSE=1`, `CLOSETODAY=3`, `CLOSEYESTERDAY=4`.
- SHFE/INE generic `CLOSE` is not silently sent when today/yesterday split is ambiguous.
- DCE generic `CLOSE` remains allowed.
- no-position, insufficient-position and stale snapshot blockers prevent native send.
- CTP `YdPosition` is capped by current `Position` when calculating closable quantity.
- Windows stdout emits JSON as UTF-8 bytes so CTP replacement characters do not prevent evidence export.

## Simulation Snapshot Evidence

Pre-close c2609 snapshot:

- Path: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_c2609.json`
- Result: `success=true`
- Run id: `paper-readonly-1780923894816`
- Candidate positions:
  - `c2609 LONG position_qty=1 td=1 yd=0`
  - `c2609 SHORT position_qty=3 td=0 yd=3`
- Instrument query: `c2609.DCE`, tick `1.0`, multiplier `10`

Pre-close zn2610 snapshot:

- Path: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_zn2610.json`
- Result: `success=true`
- Run id: `paper-readonly-1780924051627`
- Candidate position: `zn2610 LONG position_qty=2 td=0 yd=2`
- Instrument query: `zn2610.SHFE`, tick `5.0`, multiplier `5`

## Dry-Run Mapping Evidence

DCE short close:

- Path: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_dry_run_c2609_short1_after_fix.json`
- Result: `success=true`
- Candidate: `c2609 SHORT position_qty=2 td=0 yd=3`
- Closable quantity after cap: `2`
- Intent: `BUY CLOSE 1 @ 2300`
- Native command: dry-run only, `submit_order` command contract passed, `paper_send_armed=false`

SHFE close-yesterday:

- Path: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_dry_run_zn2610_long1.json`
- Result: `success=true`
- Candidate: `zn2610 LONG position_qty=2 td=0 yd=2`, exchange recovered from instrument record as `SHFE`
- Intent: `SELL CLOSEYESTERDAY 1 @ 25000`
- Native command: dry-run only, `submit_order` command contract passed, `paper_send_armed=false`

## Negative Evidence

Insufficient close:

- Path: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_over_blocked_c2609_short3.json`
- Input state: `c2609 SHORT position_qty=2`, `yd_position_qty=3`
- Request: `BUY CLOSE 3`
- Result: `success=false`, `blocker_type=paper-safety`
- Issue: `insufficient_closable_position`
- Native send: no `mapped_submit`, no lifecycle command

Stale snapshot:

- Path: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/close_stale_snapshot_blocked_c2609.json`
- Result: `success=false`, `blocker_type=paper-safety`
- Issue: `pre_snapshot_run_id_mismatch`
- Native send: no `mapped_submit`, no lifecycle command

## Armed Close Evidence

An armed close command was attempted:

```powershell
python scripts\ctp_guarded_paper_order_loop.py `
  --config output\reports\p004-openctp-tts-simulation-provider-completeness\cancel-lifecycle\tts_7x24_c2609.armed.local.json `
  --pre-snapshot output\reports\p004-openctp-tts-simulation-provider-completeness\close-position\pre_close_snapshot_c2609.json `
  --instrument c2609 --side BUY --quantity 1 --limit-price 2350 `
  --position-effect CLOSE `
  --client-order-id p004-close-armed-c2609-short-20260608-01 `
  --timeout-seconds 18 `
  --close-from-pre-snapshot --close-position-direction SHORT `
  --expected-pre-snapshot-run-id paper-readonly-1780923894816 `
  --arm-paper-send `
  --output-json output\reports\p004-openctp-tts-simulation-provider-completeness\close-position\close_armed_c2609_short1.json
```

The command failed at stdout export with `UnicodeEncodeError` before the JSON file was written. This was a repo-local evidence exporter bug, not an upstream front outage. It was fixed by adding UTF-8 stdout bytes output and moving `output-json` write before stdout emission.

Post-attempt snapshot:

- Path: `output/reports/p004-openctp-tts-simulation-provider-completeness/close-position/pre_close_snapshot_c2609_after_stdout_fix.json`
- Result: `success=true`
- Run id: `paper-readonly-1780924164172`
- `c2609 SHORT position_qty` changed from `3` to `2`
- Delta: `-1`

Conclusion: the armed close reduced one c2609 short position before the stdout exporter crash. No second armed close was sent after discovering this, to avoid duplicate position changes.

## Residual State / Carry-Forward

Latest recorded simulation state after the close attempt:

- `c2609 LONG position_qty=1`
- `c2609 SHORT position_qty=2`
- `rb2609 LONG position_qty=1`
- `rb2609 LONG position_qty=4`
- `zn2610 LONG position_qty=2`

Residual positions are visible in the post snapshot and must be considered by later P004 order-capable child changes.
