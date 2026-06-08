# Order Type And Price Boundary 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-06-08
**范围**：simulation order type and price boundary
**change-id**：20260608__openctp-tts-simulation-provider__order-type-price-boundary
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/openctp-tts-simulation-provider-completeness.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 21:34"
concluded_by: "codex"
exit_conditions: { E1_success_scenarios: passed, E2_failure_scenarios: passed, E3_verification_cmds: passed, E4_evidence_collected: passed, E5_real_acceptance_only: passed, E6_minimum_scenarios: passed }
scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed_with_caveat, blocking: true }
  A7: { exec: true, result: passed, blocking: true }
  A8: { exec: true, result: passed, blocking: true }
  A9: { exec: true, result: passed, blocking: true }
  A10: { exec: true, result: passed, blocking: true }
  A11: { exec: true, result: passed, blocking: false }
  A12: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | order type/tick/price/quantity boundary passed |
| AI 建议宣告通过 | 是 | limit-boundary source caveat recorded |

## 一、验收目标 / Goals

证明 order type 和 price boundary 在 native send 前可判定。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Limit order mapping | dry-run/simulation | native payload typed | limit preserved | payload missing | evidence |
| A2 | FAK/FOK mapping | dry-run/simulation or typed blocker | no silent downgrade | time condition typed | silently limit | evidence |
| A3 | Tick-aligned price | preflight | accepted | price aligned | false reject | test/evidence |
| A4 | Off-tick price blocked | negative test | no native send | typed issue | native send | test |
| A5 | Unsupported order type blocked | negative test | no silent fallback | typed unsupported | downgrade | test |
| A6 | Upper/lower limit price boundary | instrument/market data + preflight | price inside limit accepted; outside blocked or typed unknown | limit source recorded | outside-limit sent silently | evidence |
| A7 | Zero/negative price blocked | negative test | no native send | typed invalid price | native send | test output |
| A8 | Quantity lot and min/max volume boundary | instrument metadata preflight | quantity respects volume rules | min/max/lot rules typed | invalid volume sent | test/evidence |
| A9 | Exchange-specific unsupported order type | dry-run/simulation blocker | exchange/front limitation typed | no silent fallback | maps to wrong native type | evidence |
| A10 | Contract metadata missing blocks price preflight | malformed instrument test | no native send | data-contract issue typed | default tick used silently | test output |
| A11 | Evidence schema and redaction | evidence review | scenario id/run id/profile present; secrets absent | row can close | evidence leak | evidence |
| A12 | P003 guarded order regression | focused tests | pass | no regression | baseline broken | command output |

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| Boundary evidence | `docs/changes/20260608__openctp-tts-simulation-provider__order-type-price-boundary/evidence_order_type_price_boundary_20260608.md` | A1-A12 evidence recorded |
| LIMIT/GFD dry-run | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/limit_gfd_dry_run_c2609.json` | passed |
| FAK dry-run | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/limit_fak_dry_run_c2609.json` | passed |
| FOK dry-run | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/limit_fok_dry_run_c2609.json` | passed |
| Off-tick blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_off_tick_c2609.json` | `off_tick_price`, no native send |
| Zero price blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_zero_price_c2609.json` | `invalid_limit_price`, no native send |
| Invalid quantity blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_invalid_quantity_c2609.json` | `invalid_quantity`, no native send |
| Missing metadata blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_missing_metadata.json` | `instrument_metadata_missing`, no native send |
| Unsupported order type blocker | `output/reports/p004-openctp-tts-simulation-provider-completeness/order-type-price-boundary/blocked_unsupported_order_type_c2609.json` | `unsupported_order_type:STOP_LIMIT`, no `submit_order` command |
| Focused verification | `python -m pytest tests/test_guarded_paper_order_loop.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider` | `106 passed` |

## Verdict

Passed. Unsupported order types no longer silently downgrade, FAK/FOK mapping is explicit, and snapshot metadata blocks off-tick, zero-price, invalid-quantity and missing-metadata cases before native send.

Caveat: upper/lower limit prices are not present in the current read-only snapshot schema, so the limit-boundary source is recorded as `not_available/unknown`; outside-limit behavior is covered by simulation reject evidence in the post-order reconciliation child change.
