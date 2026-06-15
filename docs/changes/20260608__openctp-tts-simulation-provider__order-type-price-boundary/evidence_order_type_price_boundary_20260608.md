# Order Type And Price Boundary Evidence - 2026-06-08

## Scope

- Proposal: `p004-openctp-tts-simulation-provider-completeness`
- Change: `20260608__openctp-tts-simulation-provider__order-type-price-boundary`
- Account profile: `openctp-tts-7x24-simulation`
- Evidence class: `openctp-tts-7x24-simulation`
- Formal trading: not used

## Repo Contract Evidence

Command:

```powershell
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Result: `106 passed`.

Covered contracts:

- `LIMIT/GFD` keeps CTP limit order mapping.
- `FAK` maps to IOC time condition and any-volume condition.
- `FOK` maps to IOC time condition and complete-volume condition.
- Unsupported order type and unsupported time-in-force fail before native command construction.
- Snapshot instrument metadata drives tick validation.
- Off-tick price, zero price, invalid quantity and missing metadata block before native send.

## Positive Dry-run Evidence

All positive cases use `post_cleanup_snapshot_c2609.json` as the redacted pre-order snapshot. No native send was armed.

| Scenario | Evidence | Result |
| --- | --- | --- |
| LIMIT/GFD | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/limit_gfd_dry_run_c2609.json` | `success=true`, `order_boundary_passed`, `time_in_force=GFD` |
| LIMIT/FAK | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/limit_fak_dry_run_c2609.json` | `success=true`, `order_boundary_passed`, `time_in_force=FAK` |
| LIMIT/FOK | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/limit_fok_dry_run_c2609.json` | `success=true`, `order_boundary_passed`, `time_in_force=FOK` |

The instrument metadata source is `c2609.DCE`, `price_tick=1.0`, `volume_multiple=10`.

## Negative Boundary Evidence

| Scenario | Evidence | Blocker |
| --- | --- | --- |
| Off-tick price | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_off_tick_c2609.json` | `paper-safety`, `off_tick_price`, no `mapped_submit` |
| Zero price | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_zero_price_c2609.json` | `paper-safety`, `invalid_limit_price`, no `mapped_submit` |
| Invalid quantity | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_invalid_quantity_c2609.json` | `paper-safety`, `invalid_quantity`, no `mapped_submit` |
| Missing metadata | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_missing_metadata.json` | `paper-safety`, `instrument_metadata_missing`, no `mapped_submit` |
| Unsupported order type | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_unsupported_order_type_c2609.json` | `mapped_submit.error=unsupported_order_type:STOP_LIMIT`, no `submit_order` command |

## Limit Boundary Caveat

The current read-only snapshot contains instrument tick and volume metadata but does not contain exchange upper/lower limit prices. The order-boundary payload records `limit_boundary.source=not_available` and `status=unknown`. Outside-limit behavior is therefore evidenced through a simulation reject from the post-order reconciliation child change, while this child prevents known unsafe local cases before native send.
