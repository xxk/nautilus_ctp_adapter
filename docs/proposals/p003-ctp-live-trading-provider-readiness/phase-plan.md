# p003-ctp-live-trading-provider-readiness Phase Plan / 分阶段推进计划

**创建日期**：2026-06-08
**最后更新**：2026-06-08
**状态**：completed
**proposal-id**：`p003-ctp-live-trading-provider-readiness`
**关联提案**：[README.md](README.md)
**关联验收**：[acceptance.md](acceptance.md)

> 状态口径：本文件 `AI-PHASE-STATUS` 区块是 proposal 级唯一 machine-readable 主状态源；本页顶部 `**状态**` 与 `README.md` 顶部 `**状态**` 都只能作为投影。
>
> 当前执行口径：继续使用 `openctp-tts-7x24-simulation` 补齐 24 小时 API 调试能力；formal-trading / Live 暂停。

---

## Artifact Trust Boundary

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - output/reports/p003-ctp-live-trading-provider-readiness/
  allowed_evidence_roots:
    - output/debug/change_evidence/p003-ctp-live-trading-provider-readiness/
    - output/reports/p003-ctp-live-trading-provider-readiness/
  source_issue_lists: []
  source_input_templates: []
  source_contract_templates:
    - docs/adr/ADR002 OpenCTP TTS Paper Simulation Test Environment.md
    - docs/changes/20260607__openctp-tts__test-baseline/runbook.md
    - docs/proposals/p002-nautilus-provider-production-readiness/
    - docs/topics/live-session-order-query-hardening.md
    - docs/topics/live-ops-truth-snapshot.md
    - docs/architecture/platform-neutral-ctp-runtime.md
    - docs/architecture/rust-python-adapter-split.md
    - docs/architecture/runtime-performance-guidelines.md
  ctp_account_profile: openctp-tts-7x24-simulation
  ctp_config_path: cfgs/local/ctp.openctp.tts.7x24.local.json
  ctp_evidence_class: openctp-tts-7x24-simulation
```

规则：

1. P003 final pass evidence must use `ctp_account_profile=openctp-tts-7x24-simulation` and `ctp_evidence_class=openctp-tts-7x24-simulation`。
2. Formal-trading / Live evidence is out of current scope and must not be requested by P003 child changes。
3. `cfgs/local/ctp.openctp.tts.7x24.local.json` 表示 ignored local config slot；不得把账号、密码、auth code、broker 私密参数写入仓库。
4. 任何 paper 账号输出必须 redacted，保留 run id、front type、session/trading-day disposition、scenario id 和 pass/fail/blocker，不保留 secret。
5. 若未来恢复 formal-trading，需要建立 successor proposal 或显式 future phase，不得复用本 proposal 的 paper pass 关闭 formal readiness。

---

## 执行原则

1. 先完成 paper config/preflight/read-only truth snapshot，再触发任何 paper order send。
2. Paper order 默认 request-only；必须通过 explicit arm、account profile、trade window、instrument、qty、net position、rate limit 和 kill switch preflight。
3. 每个 phase 必须有明确 child change；只做聊天记录、手工截图或未 redacted 日志都不能作为完成证据。
4. repo-local blocker 继续修；OpenCTP paper 账号、SDK、front、交易窗口不可用才允许 typed blocker。
5. P003 不继承 P002 的 completed 结论；它只继承 P002 作为开发基线和 regression reference。

---

## ADR Decision Coverage Mapping

Primary ADR: `not_applicable`
Covered decisions: `not_applicable`

本 proposal 不承载新 ADR 落地；它继承 ADR002 的 OpenCTP paper profile 规则，并把 formal-trading 明确排除在当前执行范围外。

| ADR decision item | ADR section / successor scenario | Phase | Child change or proposal-only work | Acceptance row |
| --- | --- | --- | --- | --- |
| not_applicable | not_applicable | not_applicable | not_applicable | not_applicable |

---

## Blocker Handling Discipline

1. `code/contract blocker`: local preflight、guardrail、report mapping、reconnect simulation、docs gate、test gap 都是 repo-local repairable blocker，必须继续推进。
2. `paper-resource blocker`: OpenCTP paper 账号、SDK、front、交易窗口不可用时，写 typed blocker、next action 和 repo-only fallback。
3. `evidence blocker`: evidence root、JSON summary、redaction 或 run id 缺失时先补工具链，不允许用 console-only 输出关闭验收。
4. `safety blocker`: 任何 paper order 前置条件不明确时，phase 必须保持 blocked，不得降级为 warning。

---

## AI 跟踪状态（AI Tracking Status）

<!-- AI-PHASE-STATUS-BEGIN
reviewed_at: 2026-06-08
reviewer: Codex
overall_status: completed
phases:
  - id: phase_0_proposal_convergence
    status: completed
    ai_progress: 100
    evidence: "P003 proposal docs adjusted to paper-first scope and proposal docs gate passed"
  - id: phase_1_paper_session_preflight
    status: completed
    ai_progress: 100
    evidence: "20260608__ctp-paper-provider-readiness__paper-session-preflight completed; redacted config-only and connect-paper evidence passed"
  - id: phase_2_paper_readonly_truth_snapshot
    status: completed
    ai_progress: 100
    evidence: "20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot completed; redacted account/position/instrument/order-trade snapshot evidence passed"
  - id: phase_3_guarded_paper_order_loop
    status: completed
    ai_progress: 100
    evidence: "20260608__ctp-paper-provider-readiness__guarded-paper-order-loop completed; dry-run/order contract/reconciliation contract passed and unarmed paper send recorded typed blocker"
  - id: phase_4_paper_recovery_idempotency
    status: completed
    ai_progress: 100
    evidence: "20260608__ctp-paper-provider-readiness__paper-recovery-idempotency completed; checkpoint/reconnect/idempotency repo-only evidence passed"
  - id: phase_5_paper_ops_closeout
    status: completed
    ai_progress: 100
    evidence: "20260608__ctp-paper-provider-readiness__paper-ops-closeout completed; paper operator runbook and closeout boundary documented"
AI-PHASE-STATUS-END -->

---

## Phase 状态表（Phase Status Board）

| Phase / 阶段 | 目标 / Goal | Current Status / 当前状态 | AI Progress / AI 完成度 | Evidence / Current Facts / 证据 / 当前事实 | 下一动作 / Next Action |
| --- | --- | --- | ---: | --- | --- |
| Phase 0 Proposal convergence | 收敛 P003 paper-first GAP、phase split、artifact boundary 和 no-Live scope | `completed` | 100% | proposal docs gate passed | 完成 |
| Phase 1 Paper session preflight | OpenCTP paper 配置、redaction、TD/MD login readiness、settlement/trading-day truth | `completed` | 100% | `20260608__ctp-paper-provider-readiness__paper-session-preflight` passed；config-only 和 `--connect-paper` evidence 均已 redacted | 进入 Phase 2 paper readonly truth snapshot |
| Phase 2 Paper read-only truth snapshot | account/position/order/trade/instrument read-only snapshot 和对账 schema | `completed` | 100% | `20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot` passed；account/position/instrument/order-trade redacted snapshot 已留证 | 进入 Phase 3 guarded paper order loop |
| Phase 3 Guarded paper order loop | paper 一手 guarded submit/cancel/fill/reject/timeout/post-trade reconciliation | `completed` | 100% | dry-run/order contract/callback contract/reconciliation contract passed；unarmed paper send recorded typed blocker | 完成 |
| Phase 4 Paper recovery and idempotency | reconnect、resubscribe、duplicate callback、historical residue、backpressure | `completed` | 100% | checkpoint/reconnect/idempotency evidence passed；paper uncontrollable disconnect remains typed fallback | 完成 |
| Phase 5 Paper ops closeout | runbook、operator matrix、evidence retention、architecture/runbook backfill | `completed` | 100% | paper ops runbook and closeout boundary completed | 完成 |

---

## Phase 0: Proposal Convergence

### 目标

建立 P003 paper-first proposal，冻结 GAP 表、no-Live boundary、phase split 和验收矩阵。

### 依赖

1. P002 provider baseline 已完成。
2. OpenCTP paper baseline 可作为 development reference。

### Child Change

`proposal-only planning`

### 交付物

1. `docs/proposals/p003-ctp-live-trading-provider-readiness/README.md`
2. `docs/proposals/p003-ctp-live-trading-provider-readiness/phase-plan.md`
3. `docs/proposals/p003-ctp-live-trading-provider-readiness/acceptance.md`
4. `docs/proposals/p003-ctp-live-trading-provider-readiness/change-map.md`
5. `docs/proposals/p003-ctp-live-trading-provider-readiness/decision-log.md`

### Runtime / Command Freeze

1. 本 phase 不冻结 runtime command；runtime command 必须在实际执行 phase 中冻结。
2. Proposal docs gate: `python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness`。

### 退出条件

1. Proposal docs gate 通过。
2. README、phase-plan、acceptance、change-map、decision-log 不含占位符或互相矛盾状态。
3. Phase 1 first executable child change 的目标、依赖和验收口径已明确。

### Fail-fast / Negative Cases

1. 若 proposal 把 OpenCTP paper evidence 写成 formal pass，必须失败。
2. 若 proposal 要求 formal-trading / Live 作为当前 phase 依赖，必须失败。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness
```

---

## Phase 1: Paper Session Preflight

### 目标

建立 OpenCTP paper local config slot、redacted config fingerprint、TD/MD login readiness、结算确认、trading day、session id 和 front disposition。

### 依赖

1. Phase 0 completed。
2. OpenCTP TTS 7x24 local config 存在，且敏感字段只在 ignored `.env.d/`、`.env` 或 local config。

### Child Change

`20260608__ctp-paper-provider-readiness__paper-session-preflight`

### 交付物

1. Paper config preflight command or extension。
2. Redacted evidence JSON schema。
3. Paper TD/MD login/settlement/readiness runbook row。

### Runtime / Command Freeze

1. `python scripts/check_rust_gate.py`
2. `python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json --md-timeout-seconds 30 --td-timeout-seconds 30`
3. Paper preflight command to be frozen by the child change。

### 退出条件

1. Missing paper config/secret produces typed blocker, not traceback。
2. Paper TD/MD readiness can be judged pass/fail/blocker with redacted evidence。
3. No formal-trading / Live path is invoked。

### Fail-fast / Negative Cases

1. Secret appears in tracked files or evidence。
2. Formal config is requested by this phase。

### 验证方式

```bash
python scripts/check_rust_gate.py
python scripts/check_change_docs.py --root .
```

---

## Phase 2: Paper Read-only Truth Snapshot

### 目标

用 OpenCTP paper 只读查询建立 account、position、order、trade、instrument truth snapshot 和 reconciliation disposition。

### 依赖

1. Phase 1 paper session preflight completed or typed paper-resource blocker recorded。
2. P002 query/report translation remains valid。

### Child Change

`20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot`

### 交付物

1. Paper read-only truth snapshot command。
2. Account/position/order/trade/instrument JSON summary。
3. Empty/no-position/timeout/login-failed typed disposition。

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. Paper read-only snapshot command to be frozen by the child change。

### 退出条件

1. Startup truth snapshot is redacted and reproducible。
2. Query timeout, valid empty result, and login failure are distinguishable。
3. Snapshot can be used as pre/post order reconciliation input for Phase 3。

### Fail-fast / Negative Cases

1. Empty position is treated as timeout。
2. Paper query evidence leaks account secret。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
```

---

## Phase 3: Guarded Paper Order Loop

### 目标

在 OpenCTP paper 账号上关闭一手 guarded order lifecycle：preflight、submit、cancel/fill/reject/timeout、callback report 和 post-trade reconciliation。

### 依赖

1. Phase 1 completed。
2. Phase 2 snapshot can produce pre-order account/position truth。
3. Paper 交易窗口、合约、数量、净持仓和 explicit arm 全部通过。

### Child Change

`20260608__ctp-paper-provider-readiness__guarded-paper-order-loop`

### 交付物

1. Guarded paper order command。
2. Preflight checklist and fail-fast guard evidence。
3. Submit/cancel/fill/reject/timeout typed lifecycle evidence。
4. Post-trade account/position/order/trade reconciliation summary。

### Runtime / Command Freeze

1. `python scripts/check_rust_gate.py`
2. `python -m pytest tests/test_nautilus_integration.py -q`
3. Paper guarded order command to be frozen by the child change。

### 退出条件

1. Paper order send cannot run without explicit arm and paper account profile。
2. One-hand paper lifecycle result is classified and redacted。
3. Post-trade reconciliation proves position/account/order/trade truth or records typed blocker。

### Fail-fast / Negative Cases

1. Command sends paper order outside configured trade window。
2. Command bypasses qty/net-position/rate/kill-switch guardrails。
3. Command tries to use formal-trading / Live profile。

### 验证方式

```bash
python scripts/check_rust_gate.py
python -m pytest tests/test_nautilus_integration.py -q
```

---

## Phase 4: Paper Recovery And Idempotency

### 目标

补齐 paper provider 的 reconnect、resubscribe、duplicate callback、historical residue、timeout retry、backpressure 和 idempotent report semantics。

### 依赖

1. Phase 2 read-only snapshot completed。
2. Phase 3 lifecycle command exists or paper order blocker is typed。

### Child Change

`20260608__ctp-paper-provider-readiness__paper-recovery-idempotency`

### 交付物

1. Repo-only duplicate callback/idempotency tests。
2. Paper recovery rehearsal evidence。
3. Failure disposition matrix for reconnect and residue handling。

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. Paper recovery rehearsal command to be frozen by the child change。

### 退出条件

1. Duplicate callback does not duplicate fill/order reports。
2. Historical residue is not classified as current session fill。
3. Reconnect/resubscribe evidence can be judged pass/fail/blocker。

### Fail-fast / Negative Cases

1. Duplicate trade callback creates duplicate fill report。
2. Reconnect clears paper guardrails or account profile。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
```

---

## Phase 5: Paper Ops Closeout

### 目标

完成 paper operator runbook、evidence retention、redaction policy、architecture/runbook backfill 和 closeout checklist。

### 依赖

1. Phase 1-4 completed or typed blocker rows are explicitly carried forward。

### Child Change

`20260608__ctp-paper-provider-readiness__paper-ops-closeout`

### 交付物

1. OpenCTP paper runbook / successor doc。
2. Pass/fail/blocker operator matrix。
3. Evidence retention and redaction checklist。
4. Architecture/runbook graduation updates for paper capability rules。

### Runtime / Command Freeze

1. `python scripts/check_harness.py`
2. `python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness`
3. `python scripts/check_change_docs.py --root .`

### 退出条件

1. Operator can run paper readiness path without chat context。
2. All paper evidence rows are redacted and under trusted roots。
3. Stable rules are backfilled or explicitly marked proposal-local。

### Fail-fast / Negative Cases

1. Runbook tells operator to use paper evidence as formal pass。
2. Secret handling is implicit or undocumented。

### 验证方式

```bash
python scripts/check_harness.py
python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness
python scripts/check_change_docs.py --root .
```

---

## Closeout Checklist

1. Phase 状态表和 `AI-PHASE-STATUS` 块均已回填为真实状态。
2. README 顶部 `**状态**` 与本页顶部 `**状态**` 投影自 `AI-PHASE-STATUS.overall_status`。
3. 每个 OpenCTP TTS 7x24 scenario 都有 redacted simulation evidence 或 typed paper-resource blocker。
4. Formal-trading / Live 不作为 P003 当前验收目标。
5. Proposal docs gate、change docs gate、targeted tests、Rust gate 和必要 paper smoke 已执行并回填。
6. Stable runbook/architecture rules 已回流，或明确保持 proposal-local evidence。
