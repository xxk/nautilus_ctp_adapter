# p002-nautilus-provider-production-readiness Phase Plan / 分阶段推进计划

**创建日期**：2026-06-03
**最后更新**：2026-06-08
**状态**：completed
**proposal-id**：`p002-nautilus-provider-production-readiness`
**关联提案**：[README.md](README.md)
**关联验收**：[acceptance.md](acceptance.md)

> 状态口径：本文件 `AI-PHASE-STATUS` 区块是 proposal 级唯一 machine-readable 主状态源；本页顶部 `**状态**` 与 `README.md` 顶部 `**状态**` 都只能作为投影。
>
> Topic 边界：topic 不作为 proposal 推进容器；本 proposal 的 phase 推进只看本文件与 child change `plan.md`，`topic-id` 只做分组标签。

---

## Artifact Trust Boundary

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - output/reports/p002-nautilus-provider-production-readiness/
  allowed_evidence_roots:
    - output/debug/change_evidence/p002-nautilus-provider-production-readiness/
    - output/reports/p002-nautilus-provider-production-readiness/
  source_issue_lists: []
  source_input_templates: []
  source_contract_templates:
    - docs/adr/ADR002 OpenCTP TTS Paper Simulation Test Environment.md
    - docs/changes/20260607__openctp-tts__test-baseline/runbook.md
    - docs/topics/nautilus-instrument-provider.md
    - docs/topics/nautilus-live-marketdata.md
    - docs/topics/nautilus-live-execution.md
    - docs/architecture/platform-neutral-ctp-runtime.md
    - docs/architecture/rust-python-adapter-split.md
    - docs/architecture/runtime-performance-guidelines.md
    - C:/Users/Administrator/anaconda3/Lib/site-packages/nautilus_trader/adapters/interactive_brokers/providers.py
    - C:/Users/Administrator/anaconda3/Lib/site-packages/nautilus_trader/adapters/interactive_brokers/data.py
    - C:/Users/Administrator/anaconda3/Lib/site-packages/nautilus_trader/adapters/interactive_brokers/execution.py
  ctp_account_profile: openctp-paper
  ctp_config_path: cfgs/local/ctp.openctp.tts.7x24.local.json
  ctp_evidence_class: paper-simulation
```

规则：

1. proposal 全部文档若引用 formal artifact，只能引用本节声明的 `trusted_artifact_roots`。
2. 若尚未冻结唯一 artifact root，不得把 proposal 外部 artifact 写成当前 proposal 的完成证据。
3. `allowed_evidence_roots` 只允许做 repo-local 诊断留痕，不得替代 formal artifact root。
4. 作为模板来源的历史 proposal、input、cfg 或 contract 不等于当前 proposal 的 pass evidence。
5. 若某个 child change 继承本 proposal 的 artifact boundary，应在 change `plan.md` 再次显式落成自己的 `artifact_boundary`。
6. P002 development phases use `ctp_account_profile=openctp-paper` by default. Formal broker/trading evidence must switch the phase or child change to `ctp_account_profile=formal-trading` and cannot reuse paper simulation evidence.

---

## 执行原则

1. 先冻结输入、身份、artifact boundary 和验收入口，再执行 runtime 或 closeout。
2. 每个 phase 必须有明确 child change 或 proposal-only 交付物，不得只停留在对话记录。
3. 若依赖历史 proposal / tracer / artifact，只能把它们写成 template source 或 regression reference，不得写成当前 proposal 完成证据。
4. 任一 fail-fast 条件命中时，phase 状态必须写为 `blocked` 或 `reframing_required`，不得用 warning 或文字解释绕过。
5. 修改 shared module、gateway、orchestration、validation plan 或 cross-tracer 能力时，必须从 registry 推导 affected capability/tracer 并执行对应 gate。
6. 本 proposal 不属于 tracer/cross-tracer 研发，因此不维护 `issue-list.md`；后续若转为 tracer，必须先更新 README scaffold metadata 和 docs gate 预期。
7. CTP provider readiness 只能对齐 IB 的 Nautilus-facing contract，不得复制 IB/TWS client lifecycle 或多资产细节作为 CTP 架构约束。
8. proposal-specific naming、writer path、owner shortcut 或临时 schema 不得直接毕业为 stable runtime truth；若确认可复用，必须通过 child change 显式收敛到 canonical owner。
9. P002 live-capable development 默认使用 `openctp-paper`；正式交易账号只用于 `formal-trading` final pre-go-live evidence。
10. 任何 guarded order/report/live evidence 若要用于 P002 closeout，必须标明 account profile：`repo-only`, `openctp-paper`, or `formal-trading`。

---

## ADR Decision Coverage Mapping

Primary ADR: `not_applicable`
Covered decisions: `not_applicable`

本 proposal 不承载 ADR 落地；ADR001 的 native-first runtime 边界作为继承规则存在，但 P002 不新增 ADR decision coverage。

| ADR decision item | ADR section / successor scenario | Phase | Child change or proposal-only work | Acceptance row |
| --- | --- | --- | --- | --- |
| not_applicable | not_applicable | not_applicable | not_applicable | not_applicable |

---

## Blocker Handling Discipline

1. `code/contract blocker`: if the blocker is repo-local implementation, test, docs-gate, schema, writer path, or contract-lock work, keep working and fix it in the current proposal slice; do not stop at a blocker note.
2. `data blocker`: if the blocker is missing artifact, catalog, verifier output, or generated evidence, first try the official owner/runner/import path and record the command plus result. If the data cannot be generated inside the current authority boundary, materialize typed `blocked` evidence with `next_action`.
3. `governance blocker`: if the blocker requires an external owner, real approval, production authority, or human approval, never fabricate pass evidence. Implement the typed waiting/blocked state, fail-fast guard, acceptance row, and carry-forward entry.
4. `unknown blocker`: reduce it to the smallest test, inventory artifact, or reproducible command result, classify it as code/contract blocker, data blocker, or governance blocker, then apply the matching rule.
5. A proposal may close as `blocked` only when all repo-local repairable work has been attempted and the remaining blocker depends on external owner, real data, or human approval.
6. For this proposal, missing OpenCTP paper account credentials, paper trade window, SDK/DLL readiness, or disconnect-storm stability are external OpenCTP paper blockers; missing provider/cache/report tests are repo-local repairable blockers.
7. If only a formal-trading CTP credential is available, do not use it for development closeout; record a typed blocker or wait for OpenCTP paper account input.

---

## AI 跟踪状态（AI Tracking Status）

<!-- AI-PHASE-STATUS-BEGIN
reviewed_at: 2026-06-03
reviewer: Codex
overall_status: completed
phases:
  - id: phase_0_proposal_convergence
    status: completed
    ai_progress: 100
    evidence: "proposal docs gate passed for P002; README, phase-plan, acceptance, change-map, and decision-log converged"
  - id: phase_1_instrument_provider_cache_hydration
    status: completed
    ai_progress: 100
    evidence: "20260608__nautilus-provider-readiness__instrument-provider-cache-hydration completed for repo-only scope; focused tests pass for shared CTP-aware provider, metadata staging, FuturesContract hydration, and incomplete metadata negative path"
  - id: phase_2_marketdata_provider_live_loop
    status: completed
    ai_progress: 100
    evidence: "20260608__nautilus-provider-readiness__marketdata-provider-live-loop completed for repo-only scope; focused tests pass for provider-backed tick resolution, unknown diagnostics, no .CTP fabrication, and provider-backed subscription symbols; OpenCTP paper baseline is now available through C8 for later L5 provider evidence"
  - id: phase_3_execution_event_reporting
    status: completed
    ai_progress: 100
    evidence: "20260608__nautilus-provider-readiness__execution-event-reporting completed; fake CTP order/trade callbacks map to Nautilus order/fill reports and report APIs return cached CTP reports"
  - id: phase_4_query_report_generation
    status: completed
    ai_progress: 100
    evidence: "20260608__nautilus-provider-readiness__query-report-generation completed; fake CTP position rows map to PositionStatusReport and account rows map to AccountState"
  - id: phase_5_live_ops_evidence_readiness
    status: completed
    ai_progress: 100
    evidence: "20260608__nautilus-provider-readiness__live-ops-evidence-readiness completed; C8 OpenCTP paper baseline is reusable for P002, formal-trading remains final evidence only"
AI-PHASE-STATUS-END -->

---

## Phase 状态表（Phase Status Board）

| Phase / 阶段 | 目标 / Goal | Current Status / 当前状态 | AI Progress / AI 完成度 | Evidence / Current Facts / 证据 / 当前事实 | 下一动作 / Next Action |
| --- | --- | --- | ---: | --- | --- |
| Phase 0 Proposal convergence / 阶段 0 提案收敛 | 收敛 proposal 文档、边界、phase 拆分与验收矩阵 | `completed` | 100% | P002 proposal docs gate passed | 创建并执行 Phase 1 child change |
| Phase 1 InstrumentProvider cache hydration / 阶段 1 合约 provider 与缓存灌入 | 把 CTP instrument query 结果转成 Nautilus InstrumentProvider/cache 可消费对象 | `completed` | 100% | `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration` repo-only scope passed；factories 已返回 CTP-aware provider，metadata staging 和 FuturesContract hydration tests passed | 进入 Phase 2 marketdata provider live loop |
| Phase 2 Marketdata provider live loop / 阶段 2 行情 provider 生产闭环 | 用 Phase 1 provider 支撑 subscribe、tick handling、restore 和 unknown-instrument failure | `completed` | 100% | `20260608__nautilus-provider-readiness__marketdata-provider-live-loop` repo-only 通过；known tick 通过 provider metadata 解析到 `rb2610.SHFE`，unknown tick 有 diagnostic，missing metadata 不伪造 `.CTP` | 完成 |
| Phase 3 Execution event reporting / 阶段 3 执行事件与报告 | 把 TD order/trade callbacks 转成 Nautilus order/fill report 与 report API | `completed` | 100% | `20260608__nautilus-provider-readiness__execution-event-reporting` 通过；fake order/trade callback 生成 OrderStatusReport/FillReport，report API 返回缓存报告 | 完成 |
| Phase 4 Query report generation / 阶段 4 查询与报告生成 | position/account reports 使用 provider resolution 和 CTP query truth | `completed` | 100% | `20260608__nautilus-provider-readiness__query-report-generation` 通过；fake position row 生成 PositionStatusReport，account row 生成 AccountState | 完成 |
| Phase 5 OpenCTP paper / formal account evidence readiness / 阶段 5 账号证据就绪 | 固定 `openctp-paper` smoke、formal-trading final smoke、evidence-root/output-json、blocked semantics 与 operator playbook | `completed` | 100% | C8 已证明 OpenCTP paper account baseline 可用：TTS 6.6.9、本地 `.env` config、TD/MD/query/dry-run/live smoke evidence 已留存；formal-trading 仍是最终证据路径 | 完成 |

---

## Continuous Advancement Rule / 持续推进规则

Phase 0 `completed` 只表示 proposal 文档、边界、phase split 与验收缺口已经收敛，不表示后续 phase 已完成。若 `Next Action` 指向本地可完成的 child change 创建、proposal 映射回填、ADR landing map 回填或 runbook 索引同步，AI 必须继续执行该动作，或在 `acceptance.md` 写入 typed blocker；不得把 `Next Action` 本身当成完成证据。

---

## Phase 0: Proposal Convergence

### 目标

完成 provider readiness proposal 的正式收敛，冻结 IB parity 参照边界、phase split、acceptance matrix 和第一批 child change 方向。

### 依赖

1. 当前仓库 proposal scaffold 和 docs gate 可用。
2. 当前安装的 Nautilus package 可作为 IB provider source reference。

### Child Change

`proposal-only planning`

### 交付物

1. `docs/proposals/p002-nautilus-provider-production-readiness/README.md`
2. `docs/proposals/p002-nautilus-provider-production-readiness/phase-plan.md`
3. `docs/proposals/p002-nautilus-provider-production-readiness/acceptance.md`
4. `docs/proposals/p002-nautilus-provider-production-readiness/change-map.md`
5. `docs/proposals/p002-nautilus-provider-production-readiness/decision-log.md`

### Runtime / Command Freeze

1. 本 phase 不冻结 runtime command；runtime command 必须在实际执行 phase 中冻结。
2. 本 phase 冻结 proposal docs gate 入口：`python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness`。
3. 本 phase 冻结开发账户口径：P002 的 live-capable development account layer is `openctp-paper`; OpenCTP TTS is `openctp-paper`; `formal-trading` is final broker evidence only.

### 退出条件

1. Proposal docs gate 通过。
2. README、phase-plan、acceptance、change-map、decision-log 不含占位符或互相矛盾的状态。
3. Phase 1 first executable child change 的目标、依赖和验收口径已明确。

### Fail-fast / Negative Cases

1. 若 proposal 把 IB/TWS client architecture 写成 CTP runtime 约束，必须标记 `reframing_required`。
2. 若 proposal 把 OpenCTP paper evidence 缺失写成 repo-only work 的停止理由，必须修正 blocker 分类。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness
```

---

## Phase 1: InstrumentProvider Cache Hydration

### 目标

把 standalone `CtpInstrumentProvider` 的 normalized instrument result 推进成 Nautilus `InstrumentProvider` / cache 可消费的真实 provider，使 data 和 execution factories 共享同一 provider 实例，并让 tick 进入前 instrument 已可解析。

### 依赖

1. Phase 0 completed。
2. 当前 `CtpInstrumentProvider` instrument query contract 和 normalization helper 继续有效。

### Child Change

`20260608__nautilus-provider-readiness__instrument-provider-cache-hydration`

### 交付物

1. CTP Nautilus provider wrapper or hydration helper。已部分完成：`CtpNautilusInstrumentProvider`
2. Factory shared-provider contract update。已完成
3. Repo-only tests for provider cache hydration and data/exec provider sharing。已部分完成：shared provider + metadata staging
4. Docs update mapping this phase back to P002。已部分完成

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. `python -m pytest tests/test_smoke_import.py -q`
3. `python scripts/check_proposal_docs.py --root . --proposal-id p002-nautilus-provider-production-readiness`

### 退出条件

1. Data and execution factories share a real CTP-aware Nautilus provider, not a blank `InstrumentProvider()`。
2. Fake normalized CTP futures instrument can hydrate a Nautilus instrument/cache entry in repo-only tests。
3. Unknown-instrument tick path has a focused negative test.

### Fail-fast / Negative Cases

1. Returning blank provider from factories after Phase 1 is a failure。
2. Creating a second unmanaged provider cache with no factory sharing is a failure。
3. Relying on live CTP to prove repo-only cache hydration is a failure。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
python -m pytest tests/test_smoke_import.py -q
```

---

## Phase 2: Marketdata Provider Live Loop

### 目标

让 `CtpLiveDataClient` 以 Phase 1 provider 为唯一 instrument source，完成 subscribe/quote tick/restore 的 Nautilus-facing contract，并保留 CTP-specific failure diagnostics。

### 依赖

1. Phase 1 completed。
2. Existing MD PyO3 session and `CtpDataClient` bootstrap remain valid。

### Child Change

`20260608__nautilus-provider-readiness__marketdata-provider-live-loop`

### 交付物

1. Subscribe path uses provider-resolved instrument metadata。
2. QuoteTick construction has provider/cache contract tests。
3. Restore/resubscribe semantics reference active provider symbols。
4. OpenCTP paper smoke row for MD login/subscribe/first tick remains L5, not repo-only closeout。

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. `python scripts/check_rust_gate.py`
3. Optional L5: `python scripts/ctp_nautilus_live_smoke.py --config <ctp-paper-config-path>` when OpenCTP paper account config exists。

### 退出条件

1. Known instrument ticks are emitted as Nautilus data through the data client。
2. Unknown instrument and missing subscription cases produce explicit diagnostics。
3. Repo-only pass does not claim live marketdata readiness.

### Fail-fast / Negative Cases

1. Tick emission bypasses provider/cache resolution。
2. Subscribe silently succeeds when provider cannot resolve the instrument。
3. Live-only failure is written as repo-only test failure instead of typed blocker。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
python scripts/check_rust_gate.py
```

---

## Phase 3: Execution Event Reporting

### 目标

把 CTP TD callbacks and mapped order identity translated into Nautilus order/fill/position events and reports, using provider resolution and existing execution guardrails.

### 依赖

1. Phase 1 completed。
2. Existing `CtpExecutionClient` mapping, guardrails, and live order smoke baseline remain valid。

### Child Change

`20260608__nautilus-provider-readiness__execution-event-reporting`

### 交付物

1. `_handle_td_exec_event` maps order/trade callback payloads into Nautilus events or stable reports。
2. `generate_order_status_report(s)` and `generate_fill_reports` have non-empty repo-only contract paths。
3. Guardrail rejects still surface as stable errors。
4. Live order send remains gated by existing execution guardrails。

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. `python -m pytest tests/test_smoke_import.py -q`
3. Optional L5: guarded paper-account order smoke only when OpenCTP paper account config, paper trade window, and guardrails are explicitly satisfied。

### 退出条件

1. Repo-only fake exec callbacks produce deterministic Nautilus-facing order/fill report evidence。
2. Cancel and modify unsupported paths have explicit semantics。
3. Live send is not armed by default。

### Fail-fast / Negative Cases

1. `_handle_td_exec_event` remains debug-log-only after this phase。
2. Reports return empty values for known fake callback inputs。
3. Implementation weakens `c2609 + 1 hand + 5 hand max` guardrails。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
python -m pytest tests/test_smoke_import.py -q
```

---

## Phase 4: Query Report Generation

### 目标

把 existing position/account/order-truth/reconciliation query truth connected to Nautilus report generation APIs without inventing a second query lifecycle owner.

### 依赖

1. Phase 1 completed。
2. Phase 3 report identity mapping completed or explicitly scoped。
3. Existing query/reconciliation adapters remain valid。

### Child Change

`20260608__nautilus-provider-readiness__query-report-generation`

### 交付物

1. Position status report generation from CTP position query records。
2. Account balance/margin report path where Nautilus API supports it。
3. Order/fill report generation from order truth snapshots。
4. Failure semantics for empty/no-position/no-callback/timeouts。

### Runtime / Command Freeze

1. `python -m pytest tests/test_smoke_import.py -q`
2. `python -m pytest tests/test_nautilus_integration.py -q`

### 退出条件

1. Known fake position/account/order-truth inputs produce stable reports or explicit unsupported semantics。
2. Query lifecycle truth remains in runtime/query adapters, not ad hoc Nautilus wrapper state。
3. Empty account/position cases are distinguishable from timeout or login failure。

### Fail-fast / Negative Cases

1. Query report generation reparses raw CTP callbacks in Python host glue。
2. Empty results are silently treated as success without evidence fields。
3. Reports use instrument IDs not backed by provider resolution。

### 验证方式

```bash
python -m pytest tests/test_smoke_import.py -q
python -m pytest tests/test_nautilus_integration.py -q
```

---

## Phase 5: OpenCTP paper evidence Readiness

### 目标

收口 provider production readiness 的 OpenCTP paper evidence shape：paper-account smoke command, flow path, session label, evidence root, output JSON, and typed blocked semantics.

### 依赖

1. Phase 1-4 repo-only contract work completed。
2. OpenCTP paper account config, SDK/DLL readiness, and stable paper connection window available。

### Child Change

`20260608__nautilus-provider-readiness__live-ops-evidence-readiness`

### 交付物

1. OpenCTP paper provider readiness smoke or extension to existing live smoke。
2. `--flow-path`, `--session-label`, `--evidence-root`, `--output-json` support where applicable。
3. Evidence matrix mapping repo-only pass vs OpenCTP paper pass vs typed blocker。
4. Runbook update for operator use。

### Runtime / Command Freeze

1. `python scripts/check_rust_gate.py`
2. `python scripts/ctp_nautilus_live_smoke.py --config <ctp-paper-config-path>` when OpenCTP paper account config exists。
3. Provider readiness smoke command once created by the child change。

### 退出条件

1. OpenCTP paper evidence can prove provider cache hydration, marketdata tick, execution readiness/reporting, or typed blocker per scenario。
2. Missing SDK/DLL/paper account/paper window/disconnect storm produces typed blocker evidence, not fake pass。
3. Operator can follow docs without relying on chat context。

### Fail-fast / Negative Cases

1. OpenCTP paper blocker is hidden as generic test failure。
2. Paper-account pass evidence does not include output JSON or reproducible flow path。
3. Reported pass relies on mock/stub data.

### 验证方式

```bash
python scripts/check_rust_gate.py
python scripts/ctp_nautilus_live_smoke.py --config <ctp-paper-config-path>
```

---

## Closeout Checklist

1. Phase 状态表和 `AI-PHASE-STATUS` 块均已回填为真实状态。
2. `README.md` 顶部 `**状态**` 与本页顶部 `**状态**` 已投影自 `AI-PHASE-STATUS.overall_status`，不存在独立状态语义。
3. proposal-level acceptance 中的每个 in-scope 场景都有 repo-local test 或受信 artifact evidence。
4. 所有 formal artifact references 都位于本文件声明的 `trusted_artifact_roots`。
5. Proposal docs gate、targeted tests、必要 guard 已执行并回填。
6. 若修改本仓 shared module、runtime、adapter glue 或治理脚本，应执行对应 focused guard；若本仓提供 anti-pattern / contract gate，结果必须为 0 failure。
7. residual risk、non-goals 与 follow-up 已回填到 proposal、phase-plan 或 child change。
8. `README.md` 的 `Graduation / Closeout Matrix` 已声明稳定结论回流或 `archive_only` 收口；所有 `required` target 均存在，且 status 为 `verified`、`passed` 或 `completed`。
9. proposal-specific 命名、writer、owner path 或 schema 若被证明应长期保留，已在 canonical owner / ADR / architecture 中去 proposal 化；若仍保留 proposal 语义，只能留在 evidence、fixture 或 artifact traceability 边界。

---

## 状态词典

| 状态 | 含义 |
| --- | --- |
| `planned` | 已定义，尚未开始 |
| `in_progress` | 正在推进 |
| `blocked` | 命中真实阻塞 |
| `completed` | 已满足退出条件并留下证据 |
| `reframing_required` | proposal 方向仍有效，但 owner / scope / interface 需要先修订 |





