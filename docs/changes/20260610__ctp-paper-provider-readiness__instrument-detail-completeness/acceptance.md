# Paper Instrument Detail Completeness 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-06-10
**范围**：paper instrument detail C1 completeness and preflight consumption
**change-id**：20260610__ctp-paper-provider-readiness__instrument-detail-completeness
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/proposals/p003-ctp-live-trading-provider-readiness/

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-10 12:30"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: false }
  A7: { exec: true, result: passed, blocking: false }
  A8: { exec: true, result: passed, blocking: false }
  A9: { exec: true, result: passed, blocking: true }
  A10: { exec: true, result: passed, blocking: true }
  A11: { exec: true, result: passed, blocking: false }
  A12: { exec: true, result: passed, blocking: false }
  A13: { exec: true, result: passed, blocking: true }
  A14: { exec: true, result: passed, blocking: true }
  A15: { exec: true, result: passed, blocking: false }
  A16: { exec: true, result: passed, blocking: false }
  A17: { exec: true, result: passed, blocking: true }
  A18: { exec: true, result: passed, blocking: true }
  A19: { exec: true, result: passed, blocking: false }
  A20: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 通过 | passed |
| AI 建议宣告通过 | 是 | focused pytest、真实 paper evidence 与 docs/proposal gates 均已通过 |

## 一、验收目标 / Goals

1. 证明 C1 instrument detail fields 进入 paper readonly snapshot 正式 contract。
2. 证明 trading status、delivery window、min/max volume 等字段能驱动 guarded paper order preflight。
3. 证明字段缺失、冲突、未知 product kind 不会被静默接受为 pass。
4. 证明 margin / product relation / lifecycle detail 至少能稳定进入 snapshot contract 或留下 typed disposition。
5. 证明真实 paper evidence、repo-only guard 和 carry-forward / blocker 口径彼此一致。
6. 证明 C1 contract 不会在后续 snapshot、evidence 或 preflight 演进中静默漂移。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `InstrumentName`
2. `OpenDate`, `ExpireDate`, `StartDelivDate`, `EndDelivDate`, `IsTrading`
3. `LongMarginRatio`, `ShortMarginRatio`
4. `MaxMarketOrderVolume`, `MinMarketOrderVolume`, `MaxLimitOrderVolume`, `MinLimitOrderVolume`
5. `ProductID`, `UnderlyingInstrID`, `DeliveryYear`, `DeliveryMonth`
6. C1 completeness / correctness summary and typed issue taxonomy
7. margin preview / product relation / lifecycle details 对下游 preflight 的最小可消费规则
8. evidence schema、account profile boundary 和 carry-forward / blocker discipline
9. anti-drift contract for field names, dispositions, downstream consumption and evidence schema

### 不覆盖（Out of Scope）

1. `OptionsType`, `StrikePrice`, `UnderlyingMultiple`, `CombinationType`
2. formal-trading / Live readiness
3. 自动策略或跨品种策略层风控

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| Phase 2 paper readonly snapshot baseline exists | 仓库事实 | 是 | 是 | ✅ | `20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot` completed |
| Guarded paper order preflight baseline exists | 仓库事实 | 是 | 是 | ✅ | `20260608__ctp-paper-provider-readiness__guarded-paper-order-loop` completed |
| OpenCTP simulation profile remains canonical | 规则 | 是 | 是 | ✅ | P003/P004 boundary unchanged |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 不得把字段设计说明写成完成证据。
2. 若上游 paper query 不返回某些 C1 字段，只能留下 typed `data-contract` 或 `paper-resource` blocker。
3. 不得为了补齐 C1 字段而放宽 paper order safety boundary。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success: snapshot emits visible C1 fields in redacted detail payload | readonly snapshot command + tests | C1 字段进入 `raw_detail` / `detail_fields` | redacted output contains named C1 fields | query visible but snapshot silently drops fields | current change evidence |
| A2 | Success: correctness summary distinguishes covered, planned, out_of_scope and failed | schema tests / evidence review | summary stable | counts and issue lists are deterministic | summary absent or ambiguous | current change evidence |
| A3 | Success: `IsTrading` / delivery window blocks non-tradable contract before native send | guarded order preflight tests | no native send | typed blocker such as `instrument_not_tradable` / `delivery_window_blocked` | non-tradable contract still passes preflight | focused pytest + dry-run evidence |
| A4 | Success: min/max order volume fields drive qty preflight | guarded order preflight tests | qty outside range blocked | typed min/max volume issue | qty violation reaches native send | focused pytest + dry-run evidence |
| A5 | Success: margin/product relation fields are preserved for provider/cache/preflight consumption | snapshot / provider tests | fields reusable downstream | margin/product metadata retained in normalized record | fields lost or inconsistent across snapshot/provider | focused pytest |
| A6 | Failure: unknown product kind or conflicting contract fields are silently accepted | negative tests | typed `data-contract` issue | no silent pass | conflict / unknown collapsed into pass | focused pytest |
| A7 | Failure: missing C1 field is marked complete without evidence or disposition | negative tests / evidence review | incomplete field is `planned`, `missing`, or typed issue | no fake completeness claim | missing field treated as covered | current change evidence |
| A8 | Regression: C0 baseline and current paper trading path remain green | focused regression commands | existing snapshot/order tests still pass | no regression in C0 or guarded loop | C1 work breaks current paper path | focused pytest |
| A9 | Success: margin ratio fields are preserved in snapshot and can drive conservative risk preview | readonly snapshot + tests | long/short margin ratio is visible or typed missing | normalized detail contains redacted margin fields or explicit missing disposition | margin fields silently dropped | current change evidence |
| A10 | Success: product relation fields support contract month / underlying interpretation | readonly snapshot + provider tests | `ProductID`, `UnderlyingInstrID`, `DeliveryYear`, `DeliveryMonth` are reusable downstream | normalized detail and summary preserve product relation fields | product relation fields visible upstream but lost in normalized record | focused pytest |
| A11 | Failure: lifecycle fields are malformed but contract still treated as tradable | negative tests | malformed dates / flags produce typed issue or conservative block | no fake tradable pass | invalid lifecycle data still allows preflight pass | focused pytest |
| A12 | Regression: real paper query missing some C1 fields stays typed and does not block repo-only guards | optional paper evidence + docs review | missing external fields become typed `data-contract` / `paper-resource` disposition | repo-only tests remain green; real evidence is honest about missing fields | missing real query fields force fake pass or break repo-only validation | current change evidence |
| A13 | Success: snapshot and preflight consume the same normalized instrument identity | snapshot + preflight tests | `venue_symbol` / `display_symbol` / exchange identity are stable across both paths | one contract identity drives snapshot and order guard | snapshot identity and preflight identity diverge | focused pytest |
| A14 | Success: real paper evidence keeps canonical simulation profile and redaction contract | optional paper snapshot evidence | evidence includes run id, scenario id, account profile, evidence class and redaction statement | no stale alias / no secret / no private front leak | evidence lacks canonical profile or leaks secret | current change evidence |
| A15 | Failure: C1 field unsupported by current upstream query is silently marked covered instead of carry-forward/out_of_scope | docs/evidence review + negative tests | unsupported field remains typed `missing`, `out_of_scope_current`, or explicit carry-forward | no fake full-coverage claim | unsupported field appears as passed without source evidence | current change evidence |
| A16 | Regression: introducing C1 completeness does not weaken typed blocker discipline for external paper-resource gaps | docs review + optional paper evidence | external query/front gap remains `paper-resource` or `data-contract`, never traceback or fake pass | blocker schema remains reusable | external gap becomes untyped failure or implied pass | current change evidence |
| A17 | Anti-drift success: C1 field names and normalized detail keys stay stable across snapshot revisions | focused schema tests | canonical keys remain fixed | `detail_fields` / `raw_detail` keys match documented contract | later code renames or drops keys without contract update | focused pytest |
| A18 | Anti-drift success: preflight consumes the same C1 semantics the snapshot emits | snapshot + preflight contract tests | same field meanings drive both layers | `IsTrading`, delivery window, min/max volume and margin fields are interpreted consistently | snapshot says one thing, preflight guards another | focused pytest |
| A19 | Anti-drift failure: disposition vocabulary expands or changes silently | negative tests / docs review | only documented typed outcomes are allowed | new outcome requires explicit docs/test backfill before pass | ad hoc blocker/error label appears in evidence | focused pytest + docs review |
| A20 | Anti-drift regression: evidence schema remains stable enough for P003 successor backfill | evidence review / optional paper evidence | proposal/change/scenario/run/profile/verdict/redaction fields remain present | old and new evidence can be compared mechanically | C1 rollout changes evidence shape without migration note | current change evidence |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | focused pytest | `python -m pytest tests/test_paper_readonly_snapshot.py tests/test_guarded_paper_order_loop.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider` | contract and regression guard |
| 2 | snapshot evidence | `output/reports/p003-ctp-live-trading-provider-readiness/instrument-detail-completeness/` | redacted C1 snapshot / blocker evidence |
| 3 | docs gate | `python scripts/check_change_docs.py --root .` | current change docs pass |
| 4 | proposal gate | `python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness` | P003 carry-forward wording remains consistent when backfilled |
| 5 | optional real paper evidence | `python scripts/ctp_paper_readonly_snapshot.py ...` successor command | if external query is available, captures redacted C1 detail or typed blocker |
| 6 | anti-drift schema evidence | focused pytest + evidence review | proves field-name, disposition and evidence-shape stability |

## 七、未通过处理 / On Failure

1. repo-local schema / mapping / preflight blocker 必须修代码，不得改文档绕过。
2. external field absence 必须 typed blocker 或 scoped carry-forward，不得伪造 complete。

## 八、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1-A5 | passed | real paper readonly snapshot with visible C1 fields | `python scripts/ctp_paper_readonly_snapshot.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --connect-paper --timeout-seconds 20 --process-timeout-seconds 40 --session-label instrument-detail-completeness --output-json output/reports/p003-ctp-live-trading-provider-readiness/instrument-detail-completeness/paper_readonly_snapshot_connect.json` | redacted evidence contains reusable C1 details and explicit missing-field list | none | `output/reports/p003-ctp-live-trading-provider-readiness/instrument-detail-completeness/paper_readonly_snapshot_connect.json` |

## 九、Contract/Function 锁定证据

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Snapshot contract | focused pytest | 锁定 C1 field mapping and issue taxonomy |
| Preflight contract | focused pytest | 锁定 trading status / volume / delivery-window guard behavior |
| Product relation contract | focused pytest | 锁定 contract month / underlying / product metadata preservation |
| Margin preview contract | focused pytest | 锁定 margin ratio preservation and conservative downstream consumption |
| Evidence schema contract | docs/evidence review | 锁定 scenario id / run id / account profile / redaction statement presence |
| Carry-forward contract | docs/evidence review | 锁定 unsupported or unavailable C1 fields must land as typed carry-forward / blocker |
| Anti-drift field contract | focused pytest | 锁定 C1 normalized field names and disposition vocabulary |
| Anti-drift downstream contract | focused pytest | 锁定 snapshot -> preflight consumption semantics 不发生静默漂移 |

## 十、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-06-10
- **执行人**：Codex
- **建议**：可以宣告通过
- **说明**：代码、focused pytest、真实 paper readonly snapshot 和 docs/proposal gates 均已完成；当前 OpenCTP query 对 C1 字段形成“部分覆盖 + typed missing”而非假完整通过。
