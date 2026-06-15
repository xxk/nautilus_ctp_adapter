# Acceptance / 验收基线

**proposal-id**：`p002-nautilus-provider-production-readiness`
**状态**：completed

---

## 验收范围 / Scope

当前 proposal 验收以下内容：

1. CTP provider production readiness 的 phase split、child change mapping 和 acceptance matrix 是否清晰。
2. IB provider parity 是否被正确限定为 Nautilus-facing capability reference，而不是 CTP architecture copy。
3. InstrumentProvider/cache hydration、marketdata live loop、execution event/reporting、query report generation、account evidence readiness 五个能力面是否都有 repo-only、openctp-paper 和 formal-trading acceptance 分层。
4. AI/autopilot 是否能复用已完成的 OpenCTP paper baseline，同时在 paper provider-specific 条件缺失时继续推进 repo-local repairable work，并把外部条件写成 typed blocker。
5. P002 是否明确使用 `openctp-paper` 作为 live-capable development account，并把 `formal-trading` 正式交易账号保留为 final broker-facing evidence。

当前 proposal 不验收以下内容：

1. CTP 已覆盖所有品种、期权、组合、历史行情和全交易所特殊规则。
2. formal-trading final smoke 已经通过。
3. CTP provider 已覆盖所有品种、期权、组合、历史行情和全交易所特殊规则。
4. 新 ADR 已经产生；当前没有新增 ADR decision。
5. formal-trading 正式交易账号已经可以用于日常开发；正式交易账号只作为 final pre-go-live evidence path。

---

## Artifact Root Rule

本文件引用的 formal artifact、projection、report、verdict 必须属于 sibling `phase-plan.md` 中声明的 `Artifact Trust Boundary`。

未冻结唯一受信根前，只允许记录“待冻结”或 repo-local 诊断留痕，不得把 proposal 外部 artifact 写成当前 proposal 的完成证据。

---

## Acceptance Evidence Boundary

1. `pytest`、`unittest`、`dotnet test`、mock、stub、monkeypatch 或其他 test-only 输出，只能作为 contract/function guard evidence，不得单独充当 proposal 正式验收证据。
2. proposal 验收场景若要写成 `passed`、`completed` 或等价完成结论，至少还需要一类非 test-only 证据：真实命令执行结果、受信 formal artifact、projection/read-model 结果、live/rendered surface 证据，或可复核的 source evidence。
3. 若当前只有 test/mock 结果，而没有真实入口、真实 artifact 或真实 consumer 证据，只能记录为 guard/reference，不得把该 proposal 场景写成正式收口完成。
4. A repo-local repairable blocker must not be used as a reason to stop; it needs a repair attempt, focused gate result, and updated acceptance evidence.
5. A blocker that depends on an external owner, real data, or human approval must not be faked; it must produce typed waiting/blocked evidence, blockers, next_action, and carry-forward mapping.
6. A proposal closeout may remain `blocked` only after code/contract blockers have been handled and the remaining blocker is outside the current authority boundary.

---

## 验收层级 / Acceptance Layers

| Layer | 名称 | 说明 | 默认命令或证据 |
| --- | --- | --- | --- |
| L0 | Docs/governance | proposal/topic/change/frontier 一致性 | `check_proposal_docs.py`, `check_harness.py`, `autopilot.py` |
| L1 | Static/API contract | import、类型继承、factory 签名、public surface | `tests/test_nautilus_integration.py` |
| L2 | Repo-only behavior | fake normalized CTP inputs 验证 provider/cache/data/exec/report behavior | focused pytest |
| L3 | Runtime/Rust gate | PyO3、Rust、native bridge build/test | `python scripts/check_rust_gate.py` |
| L4 | Local smoke | repo debug smoke / formal smoke dry path | `python scripts/ctp_repo_debug_smoke.py` |
| L5 | OpenCTP paper account evidence | OpenCTP paper config、front、paper simulation evidence output | `ctp_nautilus_live_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json` 或 successor command |
| L6 | Formal trading final evidence | 正式交易账号 / broker account 的上线前确认 | final pre-go-live runbook / successor command only |

---

## IB Provider Parity Baseline

| Capability | IB provider reference | CTP readiness target | Repo-only acceptance | OpenCTP paper / live acceptance | Status |
| --- | --- | --- | --- | --- | --- |
| Shared provider | Data/exec client receive the same `InteractiveBrokersInstrumentProvider` | CTP data/exec factories share a real CTP-aware provider | factory tests prove same provider instance and no blank `InstrumentProvider()` | OpenCTP paper stack uses same provider in formal smoke | repo-only passed |
| Startup loading | provider `initialize()` may load configured ids/contracts | CTP provider can load configured symbols into Nautilus provider/cache | fake CTP instrument hydrates provider/cache | OpenCTP paper instrument query hydrates provider/cache | repo-only passed |
| Dynamic lookup | provider can load/request by `InstrumentId` or contract | CTP provider can resolve configured CTP symbols and Nautilus `InstrumentId` | metadata lookup and provider-backed symbol resolution tests passed | OpenCTP paper query for configured symbol | repo-only passed |
| Contract metadata map | IB keeps `InstrumentId -> IBContract/ContractDetails` | CTP keeps `InstrumentId -> CTP instrument metadata` | metadata map present after fake load | OpenCTP paper metadata captured in evidence | repo-only passed |
| Data dependency | subscriptions look up provider contract/instrument | CTP subscribe/tick path requires provider/cache resolution | known tick resolves through provider metadata; unknown diagnostic and no-fabrication paths passed | OpenCTP paper tick for known instrument does not get dropped | repo-only passed; L5 provider evidence deferred |
| Execution dependency | reports and position updates resolve instruments through provider | CTP order/fill/position reports use provider resolution | fake exec/position/account inputs produce reports/state | guarded OpenCTP paper order/query evidence maps to reports | repo-only passed |

## CTP Development Account Baseline

| Account profile | Purpose | May close P002 development scenarios | Must not do | Evidence wording |
| --- | --- | --- | --- | --- |
| `repo-only` | L1/L2 contract and negative-path tests | yes for repo-only rows only | claim external CTP connectivity | `repo-only guard/reference` |
| `openctp-paper` | ADR002 7x24 paper simulation / development test environment | yes for paper simulation development rows | claim formal broker/trading readiness | `OpenCTP paper simulation evidence` |
| `formal-trading` | final pre-go-live broker confirmation | no for daily development closeout | replace paper development loop or CI-like testing | `formal broker/trading evidence` |

---

## Capability Coverage Index

| Capability | Phase | Child change | Scenario IDs | Repo-only gate | OpenCTP paper / live gate |
| --- | --- | --- | --- | --- | --- |
| Shared provider | Phase 1 | `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration` | C1-S1, C1-F1, C1-R1 | factory/provider identity tests; no blank base `InstrumentProvider()` | OpenCTP paper stack trace proves data/exec share provider |
| Startup loading | Phase 1 | `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration` | C2-S1, C2-F1, C2-R1 | fake normalized instruments hydrate provider/cache | OpenCTP paper instrument query hydrates cache |
| Dynamic lookup | Phase 1 | `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration` | C3-S1, C3-F1, C3-R1 | known/unknown symbol request tests | configured OpenCTP paper symbol resolves through live query |
| Contract metadata map | Phase 1 | `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration` | C4-S1, C4-F1, C4-R1 | metadata map stores CTP fields and rejects malformed payloads | OpenCTP paper evidence captures CTP contract metadata |
| Data dependency | Phase 2 | `20260608__nautilus-provider-readiness__marketdata-provider-live-loop` | C5-S1, C5-F1, C5-R1 | fake cached/unknown tick behavior tests | first known OpenCTP paper tick is not dropped |
| Marketdata live loop | Phase 2 | `20260608__nautilus-provider-readiness__marketdata-provider-live-loop` | C6-S1, C6-F1, C6-B1 | provider-backed subscription symbol tests; OpenCTP baseline separated for Phase 5 | OpenCTP paper login, subscribe, first tick, and restore evidence |
| Execution dependency | Phase 3 | `20260608__nautilus-provider-readiness__execution-event-reporting` | C7-S1, C7-F1, C7-R1 | fake order/fill paths require provider resolution | guarded OpenCTP paper order/query maps instruments through provider |
| Execution event reporting | Phase 3 | `20260608__nautilus-provider-readiness__execution-event-reporting` | C8-S1, C8-F1, C8-R1 | TD exec events emit Nautilus reports or typed diagnostics | guarded OpenCTP paper TD event evidence is captured |
| Query report generation | Phase 4 | `20260608__nautilus-provider-readiness__query-report-generation` | C9-S1, C9-F1, C9-R1 | fake position/account query inputs produce reports/state | OpenCTP paper query evidence maps to Nautilus reports/state |
| OpenCTP paper evidence readiness | Phase 5 | `20260608__nautilus-provider-readiness__live-ops-evidence-readiness` | C10-S1, C10-F1, C10-B1 | C8 smoke command emits structured evidence schema | OpenCTP paper account smoke emits pass/fail/blocker evidence |
| Governance and AI autopilot | Phase 0-5 | all child changes | C11-S1, C11-F1, C11-R1 | harness/proposal/change-doc checks pass | typed blockers and carry-forward mapping remain visible |
| Development account boundary | Phase 0-5 | all child changes | C12-S1, C12-F1, C12-R1 | docs gate proves account-layer wording is present | OpenCTP paper evidence is separated from formal-trading evidence |

---

## Per-Capability Acceptance Scenarios

### C1 Shared Provider / 共享 Provider

| ID | 类型 | 场景 | Repo-only 验收 | OpenCTP paper / live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C1-S1 | success | data 和 execution factories 使用同一个 CTP-aware provider 实例 | factory test proves provider identity/cache key reuse | OpenCTP paper stack reports same provider identity or equivalent trace id | factories still create blank `InstrumentProvider()` | repo-only passed |
| C1-F1 | failure | provider config 不完整 | config validation returns missing fields before live connection | OpenCTP paper smoke emits typed config blocker | missing config reaches TD/MD session as ad hoc failure | planned |
| C1-R1 | regression | provider sharing does not break existing Nautilus config inheritance | `tests/test_nautilus_integration.py` still proves config classes inherit Nautilus base configs | not_applicable | config public surface changes without focused tests | planned |

### C2 Startup Loading / 启动加载

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C2-S1 | success | configured CTP symbols load into Nautilus provider/cache on startup | fake normalized instrument hydrates provider and cache, then `list_all()` exposes it | OpenCTP paper instrument query hydrates cache for configured symbol | startup leaves cache empty for configured symbol | repo-only passed |
| C2-F1 | failure | startup query returns no instruments | load result marks empty/no-match explicitly | OpenCTP paper evidence records no-instrument/no-match, not success | empty result is silently treated as loaded success | planned |
| C2-R1 | regression | startup loading remains optional/config-controlled | repo-only tests cover enabled and disabled startup loading | OpenCTP paper smoke records selected config mode | provider always queries live TD even when disabled | planned |

### C3 Dynamic Lookup / 动态查询

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C3-S1 | success | known `InstrumentId` or CTP symbol can be loaded on demand | `load_async`/request path hydrates a fake known symbol | OpenCTP paper query resolves configured symbol | request path only works after load-all | planned |
| C3-F1 | failure | unknown symbol requested | returns explicit not-found diagnostic and does not mutate cache | OpenCTP paper evidence records not-found or query timeout distinctly | unknown symbol is added as partial instrument | planned |
| C3-R1 | regression | dynamic lookup reuses the same normalization rules as startup loading | tests compare startup and dynamic normalized IDs | OpenCTP paper evidence shows same `InstrumentId` format | dynamic path invents different symbol/exchange mapping | planned |

### C4 Contract Metadata Map / 合约元数据映射

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C4-S1 | success | provider keeps CTP metadata | fake metadata map contains exchange, venue symbol, tick size, multiplier, product kind | OpenCTP paper evidence records same fields for paper-account contract | provider only stores Nautilus instrument without CTP metadata | repo-only passed |
| C4-F1 | failure | required metadata missing or malformed | invalid tick/multiplier/product kind produces typed validation diagnostic | OpenCTP paper malformed payload is recorded as data blocker | malformed metadata hydrates usable instrument silently | planned |
| C4-R1 | regression | metadata map is host glue, not runtime raw callback owner | review/test proves raw callback parsing stays outside Nautilus wrapper | not_applicable | Python host glue reparses raw CTP structs as runtime truth | planned |

### C5 Data Dependency / 行情依赖 Provider

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C5-S1 | success | known tick becomes Nautilus `QuoteTick` after provider/cache hydration | fake tick resolution reuses hydrated provider instrument and returns `rb2610.SHFE` | OpenCTP paper first tick for known symbol is not dropped | tick path bypasses provider/cache resolution | repo-only passed |
| C5-F1 | failure | tick arrives for unknown instrument | explicit `ctp_metadata_missing` diagnostic and no false data emission | OpenCTP paper evidence records unknown-instrument if encountered | tick is silently dropped with no evidence field | repo-only passed |
| C5-R1 | regression | subscription uses selected configured symbols, not every related instrument | provider-backed subscription helper filters unknown symbols | OpenCTP paper evidence records selected subscription set | provider result causes unintended chain-wide subscription | repo-only passed |

### C6 Marketdata Live Loop / 行情生产闭环

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C6-S1 | success | MD connect/subscribe/restore uses provider-backed symbols | provider-backed active symbols are available for restore/resubscribe consumption | OpenCTP paper smoke records login, subscribe, first tick, restore evidence where applicable | restore loses provider symbol set | repo-only passed |
| C6-F1 | failure | MD login/subscribe fails | failure result includes error id/message and selected symbols | OpenCTP paper evidence records login/subscribe failure distinctly | failure is collapsed into generic timeout | planned |
| C6-B1 | carry-forward | provider-specific OpenCTP paper evidence not yet in Phase 2 scope | repo-only tests still pass; L5 row is deferred to Phase 5 | evidence includes account profile and next action | paper unavailable blocks Phase 1-4 closeout | deferred_to_phase_5 |

### C7 Execution Dependency / 执行依赖 Provider

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C7-S1 | success | submit/cancel/report paths resolve instrument through provider | fake order intent for cached instrument maps to order command/report identity | guarded OpenCTP paper order/query maps to same instrument id | execution uses raw symbol with no provider-backed identity | planned |
| C7-F1 | failure | execution requested for unknown instrument | explicit reject or not-found diagnostic before order send | OpenCTP paper order is not armed for unknown instrument | unknown instrument reaches native `order_send` | planned |
| C7-R1 | regression | execution guardrails remain effective | tests keep `c2609`, qty, net-position, rate and live-arm checks | OpenCTP paper evidence records guardrail precheck before send | provider readiness weakens live-order guardrails | planned |

### C8 Execution Event Reporting / 执行事件与报告

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C8-S1 | success | known order callback yields Nautilus-facing order status report/event | fake order callback with provider-backed instrument produces deterministic report/event | guarded OpenCTP paper callback evidence maps to report/event | `_handle_td_exec_event` remains debug-log-only | planned |
| C8-S2 | success | known trade callback yields fill report/event | fake trade callback produces deterministic fill report/event | guarded OpenCTP paper fill or no-fill evidence is classified | trade callback is only stored as raw runtime event | planned |
| C8-F1 | failure | callback cannot be matched to current order/session | report marks unmatched/historical/delayed boundary | OpenCTP paper evidence distinguishes historical residue from current session | unmatched callback is treated as current order fill | planned |

### C9 Query Report Generation / 查询报告生成

| ID | 类型 | 场景 | Repo-only 验收 | Live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C9-S1 | success | position query records become Nautilus position reports | fake position records map to long/short/flat reports with provider resolution | OpenCTP paper position query evidence maps to reports | known position query returns empty report list | planned |
| C9-S2 | success | account query records become account/balance evidence | fake account record maps to supported report/evidence shape | OpenCTP paper account query evidence captures balance/margin fields | account result is discarded because report API is incomplete | planned |
| C9-F1 | failure | query timeout/no result/no position are distinguishable | repo-only cases cover timeout, empty, and no-position separately | OpenCTP paper evidence records exact disposition | timeout and valid empty account/position share same status | planned |
| C9-R1 | regression | query lifecycle truth stays in runtime/query adapter | source review and focused tests confirm wrapper translates existing truth only | not_applicable | Nautilus wrapper owns a second query lifecycle state machine | planned |

### C10 OpenCTP paper evidence Readiness / Paper 账户证据就绪

| ID | 类型 | 场景 | Repo-only 验收 | OpenCTP paper / live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C10-S1 | success | formal provider-readiness smoke emits reproducible evidence | command help/schema/output-json contract test | OpenCTP paper account smoke emits flow path, session label, evidence root, output JSON | paper evidence only exists as console text | planned |
| C10-B1 | blocker | SDK/DLL/OpenCTP paper config/paper trading window missing | proposal/child change records typed blocker, repo-only tests remain valid | blocker evidence includes reason and next action | missing paper dependency is marked as implementation failure | planned |
| C10-R1 | regression | operator can decide current action without chat context | runbook/index review has action matrix and evidence matrix | OpenCTP paper operator evidence follows documented path | docs require unstated chat instructions | planned |

### C12 Development Account Boundary / 开发账户边界

| ID | 类型 | 场景 | Repo-only 验收 | OpenCTP paper / live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C12-S1 | success | P002 child changes know the development account layer | docs gate/review sees `openctp-paper` as live-capable development baseline | OpenCTP paper account config/evidence is tagged as paper | child change claims generic live account without account layer | planned |
| C12-F1 | failure | formal-trading is used for daily development closeout | docs/review rejects the wording | not_applicable | formal-trading evidence closes ordinary development rows | planned |
| C12-R1 | regression | OpenCTP TTS simulation and OpenCTP paper account stay separate | ADR002/P002 wording remains distinct | evidence row names the layer used | OpenCTP `TEST` evidence is claimed as broker OpenCTP paper or formal broker/trading readiness | planned |

### C11 Governance And AI Autopilot / 治理与 AI 自动推进

| ID | 类型 | 场景 | Repo-only 验收 | OpenCTP paper / live 验收 | Must fail if | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| C11-S1 | success | each phase has a child change or proposal-only closeout | `change-map.md`, child bundles, and `phase-plan.md` stay aligned | not_applicable | phase has no executable owner | planned |
| C11-S2 | success | completion backfills acceptance and frontier state | `check_proposal_docs.py`, `check_change_docs.py`, `autopilot.py --backfill` pass where applicable | OpenCTP paper evidence rows backfilled when L5 runs | completed phase has missing acceptance evidence | planned |
| C11-F1 | failure | AI stops on repo-local repairable blocker | blocker handling review | not_applicable | missing tests/docs/code are recorded as external blockers | planned |

---

## 场景矩阵 / Scenario Matrix

| ID | 类型 | 场景 | 验收方式 | 通过信号 | 状态 |
| --- | --- | --- | --- | --- | --- |
| A1 | success | Proposal docs gate passes for P002 | `python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness` | docs gate returns OK | completed |
| A2 | failure | IB provider parity is treated as architecture copy | README/phase-plan review | Text says IB is capability reference only; no TWS lifecycle copied into CTP runtime | planned |
| A3 | regression | Existing native-first runtime boundary remains intact | `runtime-performance-guidelines.md` + phase review | no second runtime API, no C# bridge, no raw callback parse owner in Python host glue | planned |
| A4 | success | Phase 1 has first executable child change | `change-map.md` + child bundle | `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration` exists and maps to Phase 1 | completed |
| A5 | success | CTP factories share real provider | Phase 1 tests | data/exec factories do not return blank `InstrumentProvider()` | repo-only passed |
| A6 | failure | Unknown instrument tick is silently accepted or dropped without diagnostics | Phase 1/2 tests | unknown instrument produces explicit diagnostic path | repo-only passed |
| A7 | success | Marketdata uses provider/cache resolution | Phase 2 tests | known fake tick becomes Nautilus data after provider hydration | repo-only passed |
| A8 | success | Execution callbacks produce Nautilus-facing reports/events | Phase 3 tests | fake order/trade callback yields deterministic report/event | planned |
| A9 | failure | Execution reports remain empty for known fake inputs | Phase 3 tests | known fake callback no longer returns empty reports | planned |
| A10 | success | Query report generation uses existing query truth | Phase 4 tests | position/account/order-truth fake inputs map to reports or explicit unsupported semantics | planned |
| A11 | failure | Query lifecycle truth is re-owned by Python Nautilus wrapper | Phase 4 review/tests | wrapper only translates drained/query adapter truth; it does not parse raw callbacks | planned |
| A12 | success | OpenCTP paper evidence has reproducible output shape | Phase 5 command evidence | flow path, session label, evidence root, output JSON are present | planned |
| A13 | blocker | SDK/DLL/OpenCTP paper config/paper trade window/disconnect storm missing | Phase 5 typed blocker evidence | status is blocked/waiting with next_action, not failed/faked pass | planned |
| A14 | regression | Repo-only work stops because provider-specific OpenCTP paper evidence is unavailable | Phase review | Phase 1-4 continue with L1-L4 gates while L5 is deferred or blocked | planned |
| A15 | success | OpenCTP paper account is the P002 development account baseline | README/phase-plan/acceptance review | `openctp-paper` is explicit and formal-trading final evidence is separate | planned |

---

## ADR Carrier Acceptance Matrix

not_applicable：本 proposal 不是 ADR carrier，不承接 Primary ADR decision coverage。ADR001 仅作为继承的架构边界，P002 不新增 ADR successor scenario。

| ID | Primary ADR | ADR decision item | ADR successor scenario | Positive path | Must fail if | Authority / retirement boundary | Minimal evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable |

---

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| Proposal scaffold | `docs/proposals/p002-nautilus-provider-production-readiness/` | P002 proposal container created |
| IB provider reference | `C:/Users/Administrator/anaconda3/Lib/site-packages/nautilus_trader/adapters/interactive_brokers/providers.py` | IB provider offers Nautilus-facing parity reference |
| CTP current provider gap | `src/nautilus_ctp_adapter/adapters/ctp/nautilus_factories.py` | factories currently create blank `InstrumentProvider()` |
| Proposal docs gate | `python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness` | passed on 2026-06-03 and rerun passed after 2026-06-08 Phase 1 update |
| Development account baseline | `README.md`; `phase-plan.md`; `acceptance.md` | P002 uses OpenCTP paper account for live-capable development; OpenCTP TTS and formal-trading final evidence remain separate layers |
| Phase 1 repo-only provider contract | `docs/changes/20260608__nautilus-provider-readiness__instrument-provider-cache-hydration/evidence_repo_only_provider_contract.md` | shared CTP-aware provider, metadata staging, FuturesContract hydration, and incomplete metadata negative path tests passed |
| Phase 2 tick provider resolution | `docs/changes/20260608__nautilus-provider-readiness__marketdata-provider-live-loop/evidence_tick_provider_resolution.md` | known tick symbol resolves through CTP provider metadata to `rb2610.SHFE`; unknown diagnostic, no-fabrication, not-hydrated, and provider-backed subscription symbol guards passed |

---

## Closeout Checklist

1. 所有 in-scope 场景都有证据。
2. 所有 formal artifact 引用都位于 proposal 已声明的受信 artifact roots 内。
3. residual risk 已回填到 proposal / phase-plan / follow-up child change。
4. 任何 proposal 场景都不得仅凭 test/mock 结果写成正式验收通过；若 test 是当前唯一证据，必须显式标注为 guard/reference，而不是 closeout evidence。
5. Phase 1-5 每个 child change 都已回填 acceptance 状态，或留下 typed blocker 与 next_action。
6. 若 CTP provider readiness 产生长期规则，已回流到 architecture/runbook；若未产生长期规则，README closeout matrix 保持 proposal-local evidence only。




