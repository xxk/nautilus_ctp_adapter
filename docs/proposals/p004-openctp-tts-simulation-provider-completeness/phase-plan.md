# p004-openctp-tts-simulation-provider-completeness Phase Plan / 分阶段推进计划

**创建日期**：2026-06-08
**最后更新**：2026-06-08
**状态**：completed
**proposal-id**：`p004-openctp-tts-simulation-provider-completeness`
**关联提案**：[README.md](README.md)
**关联验收**：[acceptance.md](acceptance.md)

> 状态口径：本文件 `AI-PHASE-STATUS` 区块是 proposal 级唯一 machine-readable 主状态源；本页顶部 `**状态**` 与 `README.md` 顶部 `**状态**` 都只能作为投影。
>
> 当前执行口径：只使用 `openctp-tts-7x24-simulation` 补齐 simulation provider 能力；formal-trading / Live 继续暂停。

---

## Artifact Trust Boundary

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - output/reports/p004-openctp-tts-simulation-provider-completeness/
  allowed_evidence_roots:
    - output/debug/change_evidence/p004-openctp-tts-simulation-provider-completeness/
    - output/reports/p004-openctp-tts-simulation-provider-completeness/
  source_issue_lists: []
  source_input_templates: []
  source_contract_templates:
    - docs/adr/ADR002 OpenCTP TTS Paper Simulation Test Environment.md
    - docs/changes/20260607__openctp-tts__test-baseline/runbook.md
    - docs/proposals/p003-ctp-live-trading-provider-readiness/
    - docs/proposals/p002-nautilus-provider-production-readiness/
  ctp_account_profile: openctp-tts-7x24-simulation
  ctp_config_path: cfgs/local/ctp.openctp.tts.7x24.local.json
  ctp_evidence_class: openctp-tts-7x24-simulation
```

规则：

1. P004 evidence must use `ctp_account_profile=openctp-tts-7x24-simulation` and `ctp_evidence_class=openctp-tts-7x24-simulation`。
2. Formal-trading / Live evidence is out of current scope and must not be requested by P004 child changes。
3. `cfgs/local/ctp.openctp.tts.7x24.local.json` 是 ignored local config slot；不得把账号、密码、auth code、broker 私密参数写入仓库。
4. 任何 simulation 账号输出必须 redacted，保留 run id、scenario id、front type、session/trading-day disposition、pass/fail/blocker，不保留 secret。
5. 若未来恢复 formal-trading，需要 successor proposal 或显式 future phase，不得复用本 proposal 的 simulation pass 关闭 formal readiness。

---

## 执行原则

1. 每个下单类 phase 都先跑 read-only snapshot，再触发 armed simulation order。
2. Simulation order 默认 dry-run/request-only；必须通过 explicit arm、account profile、trade window、instrument、qty、net position、rate limit 和 kill switch preflight。
3. 每个 phase 必须有明确 child change；聊天记录、手工截图或未 redacted 日志不能作为完成证据。
4. repo-local blocker 继续修；OpenCTP TTS 账号、SDK、front、交易窗口不可用才允许 typed `paper-resource` blocker。
5. P004 继承 P003 作为 baseline 和 regression reference，但 P003 completed 不等于 P004 pass。

---

## ADR Decision Coverage Mapping

Primary ADR: `not_applicable`
Covered decisions: `not_applicable`

本 proposal 不承载新 ADR 落地；它继承 ADR002 的 OpenCTP TTS simulation profile 规则，并把 formal-trading 明确排除在当前执行范围外。

| ADR decision item | ADR section / successor scenario | Phase | Child change or proposal-only work | Acceptance row |
| --- | --- | --- | --- | --- |
| not_applicable | not_applicable | not_applicable | not_applicable | not_applicable |

---

## Blocker Handling Discipline

1. `code/contract blocker`: local implementation、test、docs-gate、schema、redaction、guardrail 和 mapping blocker 都是 repo-local repairable blocker，必须继续推进。
2. `paper-resource blocker`: OpenCTP TTS 账号、SDK、front、交易窗口或合约状态不可用时，写 typed blocker、next action 和 repo-only fallback。
3. `evidence blocker`: evidence root、JSON summary、redaction、run id 或 scenario id 缺失时先补工具链，不允许用 console-only 输出关闭验收。
4. `safety blocker`: 任何 simulation order 前置条件不明确时，phase 必须保持 blocked，不得降级为 warning。

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
    evidence: "P004 proposal, acceptance matrix, phase map and child change mapping were created"
  - id: phase_1_cancel_lifecycle
    status: completed
    ai_progress: 100
    evidence: "docs/changes/20260608__openctp-tts-simulation-provider__cancel-lifecycle/"
  - id: phase_2_close_position_semantics
    status: completed
    ai_progress: 100
    evidence: "docs/changes/20260608__openctp-tts-simulation-provider__close-position-semantics/"
  - id: phase_3_post_order_reconciliation
    status: completed
    ai_progress: 100
    evidence: "docs/changes/20260608__openctp-tts-simulation-provider__post-order-reconciliation/"
  - id: phase_4_order_type_price_boundary
    status: completed
    ai_progress: 100
    evidence: "docs/changes/20260608__openctp-tts-simulation-provider__order-type-price-boundary/"
  - id: phase_5_risk_preflight_expansion
    status: completed
    ai_progress: 100
    evidence: "docs/changes/20260608__openctp-tts-simulation-provider__risk-preflight-expansion/"
  - id: phase_6_real_reconnect_evidence
    status: completed
    ai_progress: 100
    evidence: "docs/changes/20260608__openctp-tts-simulation-provider__real-reconnect-evidence/; controlled front proxy reconnect evidence passed"
  - id: phase_7_nautilus_engine_harness
    status: completed
    ai_progress: 100
    evidence: "docs/changes/20260608__openctp-tts-simulation-provider__nautilus-engine-harness/"
AI-PHASE-STATUS-END -->

---

## Phase 状态表（Phase Status Board）

| Phase / 阶段 | 目标 / Goal | Current Status / 当前状态 | AI Progress / AI 完成度 | Evidence / Current Facts / 证据 / 当前事实 | 下一动作 / Next Action |
| --- | --- | --- | ---: | --- | --- |
| Phase 0 Proposal convergence | 收敛 P004 scope、artifact boundary、phase split、acceptance matrix 和 child change mapping | `completed` | 100% | proposal docs created | 执行 Phase 1 |
| Phase 1 Cancel lifecycle | 补齐挂单、主动撤单、撤单回报、撤单失败和 cancel report 映射 | `completed` | 100% | cancel lifecycle child change passed | 无 |
| Phase 2 Close position semantics | 补齐 `CLOSE` / `CLOSETODAY` / `CLOSEYESTERDAY` provider 语义 | `completed` | 100% | close semantics child change passed | 无 |
| Phase 3 Post-order reconciliation | 每笔下单后自动对账 pre/post account、position、order、trade | `completed` | 100% | post-order reconciliation child change passed | 无 |
| Phase 4 Order type and price boundary | 覆盖限价、FAK/FOK、tick 规整、涨跌停和不可交易合约阻断 | `completed` | 100% | order type / price boundary child change passed | 无 |
| Phase 5 Risk preflight expansion | 扩展资金、保证金、净持仓、频率、重复 order id、kill switch | `completed` | 100% | risk preflight child change passed | 无 |
| Phase 6 Real reconnect evidence | 补齐受控 MD/TD reconnect、resubscribe、historical residue 隔离 | `completed` | 100% | controlled front proxy evidence passed; process-scoped disconnect avoids public front disruption | 无 |
| Phase 7 Nautilus engine harness | 通过 Nautilus command 触发 provider 下单、撤单和 reports | `completed` | 100% | `ctp_nautilus_engine_harness.py` emits provider reports through `CtpLiveExecutionClient` | evidence: `output/reports/p004-openctp-tts-simulation-provider-completeness/nautilus-engine-harness/engine_harness_provider_reports.json` |

---

## Continuous Advancement Rule / 持续推进规则

Phase 0 `completed` 只表示 proposal 文档、边界、phase split 与验收缺口已经收敛，不表示后续 phase 已完成。若 `Next Action` 指向本地可完成的 child change 创建、proposal 映射回填或 runbook 索引同步，AI 必须继续执行该动作，或在 `acceptance.md` 写入 typed blocker。

---

## Phase 0: Proposal Convergence

### 目标

建立 P004 successor proposal，冻结 simulation-provider-completeness 范围、artifact boundary、phase split、验收矩阵和 child change mapping。

### 依赖

1. P003 completed。
2. OpenCTP TTS 7x24 simulation 账户已作为 24 小时 API 调试默认账户。

### Child Change

`proposal-only planning`

### 交付物

1. `docs/proposals/p004-openctp-tts-simulation-provider-completeness/README.md`
2. `docs/proposals/p004-openctp-tts-simulation-provider-completeness/phase-plan.md`
3. `docs/proposals/p004-openctp-tts-simulation-provider-completeness/acceptance.md`
4. `docs/proposals/p004-openctp-tts-simulation-provider-completeness/change-map.md`
5. `docs/proposals/p004-openctp-tts-simulation-provider-completeness/decision-log.md`

### Runtime / Command Freeze

1. 本 phase 不冻结 runtime command；runtime command 必须在实际执行 phase 中冻结。
2. Proposal docs gate: `python scripts/check_proposal_docs.py --root . --proposal-id p004-openctp-tts-simulation-provider-completeness`。

### 退出条件

1. Proposal docs gate 通过。
2. README、phase-plan、acceptance、change-map、decision-log 不含占位符或互相矛盾状态。
3. Phase 1 first executable child change 的目标、依赖和验收口径已明确。

### Fail-fast / Negative Cases

1. 若 proposal 把 simulation evidence 写成 formal pass，必须失败。
2. 若 proposal 要求 formal-trading / Live 作为当前 phase 依赖，必须失败。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p004-openctp-tts-simulation-provider-completeness
```

---

## Phase 1: Cancel Lifecycle

### 目标

在 OpenCTP TTS simulation 账户上补齐 passive order staging、主动撤单、撤单 accepted/rejected callback、duplicate cancel idempotency 和 Nautilus cancel report 映射。

### 依赖

1. Phase 0 completed。
2. P003 read-only snapshot 和 guarded order baseline 可作为 regression reference。

### Child Change

`20260608__openctp-tts-simulation-provider__cancel-lifecycle`

### 交付物

1. Cancel lifecycle command or extension。
2. Cancel command contract tests。
3. Simulation cancel evidence or typed paper-resource blocker。

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. Cancel lifecycle command to be frozen by the child change。

### 退出条件

1. Cancel cannot run without native order ref、front id、session id 和 explicit profile。
2. Cancel accepted、cancel rejected、duplicate callback 都有 typed disposition。
3. Evidence redacted and mapped to P4-A2/P4-A3/P4-F2/P4-F3。

### Fail-fast / Negative Cases

1. Missing front/session/order ref still sends native cancel。
2. Duplicate cancel callback creates duplicate report。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
```

---

## Phase 2: Close Position Semantics

### 目标

补齐 `CLOSE`、`CLOSETODAY`、`CLOSEYESTERDAY` 的 provider 语义、交易所差异、position availability preflight 和模拟账户 evidence。

### 依赖

1. Phase 1 completed or explicitly not required for close dry-run。
2. Read-only position snapshot can identify long/short and today/yesterday split。

### Child Change

`20260608__openctp-tts-simulation-provider__close-position-semantics`

### 交付物

1. Close position preflight and command mapping。
2. Close semantics tests for SHFE/INE and non-SHFE exchanges。
3. Simulation close evidence or typed blocker。

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. Close semantics simulation command to be frozen by the child change。

### 退出条件

1. No matching position blocks native send。
2. SHFE/INE today/yesterday split is explicit。
3. Close evidence includes redacted pre/post position truth。

### Fail-fast / Negative Cases

1. Generic close silently replaces close today/yesterday where split is required。
2. Close sends when available position is insufficient。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
```

---

## Phase 3: Post-order Reconciliation

### 目标

让每笔 simulation order 自动产生 pre/post account、position、order、trade snapshot，并把 fill/reject/cancel/timeout 解释为可复核 reconciliation verdict。

### 依赖

1. P003 read-only snapshot command。
2. Phase 1/2 order lifecycle outputs。

### Child Change

`20260608__openctp-tts-simulation-provider__post-order-reconciliation`

### 交付物

1. Post-order reconciliation command or guarded order extension。
2. Snapshot freshness/account identity checks。
3. Evidence for filled、rejected、cancelled or typed blockers。

### Runtime / Command Freeze

1. `python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py -q`
2. Reconciliation command to be frozen by the child change。

### 退出条件

1. Stale or partial snapshot cannot close acceptance。
2. Filled orders explain account/position/order/trade delta。
3. Rejected/cancelled orders explain no-delta and lifecycle final state。

### Fail-fast / Negative Cases

1. Account fingerprint mismatch is accepted。
2. Snapshot from another run id is accepted as post-order truth。

### 验证方式

```bash
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py -q
```

---

## Phase 4: Order Type And Price Boundary

### 目标

覆盖限价、FAK/FOK、tick 规整、涨跌停、不可交易合约和 unsupported order type fail-fast。

### 依赖

1. Instrument query exposes tick, volume multiple, exchange and trading constraints。
2. Guarded order command can block before native send。

### Child Change

`20260608__openctp-tts-simulation-provider__order-type-price-boundary`

### 交付物

1. Order type mapping contract。
2. Price boundary preflight。
3. Simulation evidence for supported cases or typed blocker for unsupported cases。

### Runtime / Command Freeze

1. `python -m pytest tests/test_guarded_paper_order_loop.py tests/test_nautilus_integration.py -q`
2. Order type/price boundary simulation command to be frozen by the child change。

### 退出条件

1. Unsupported order type does not silently downgrade。
2. Off-tick price and limit-boundary issue block before native send。
3. Supported order type evidence includes native payload summary。

### Fail-fast / Negative Cases

1. FAK/FOK silently becomes normal limit。
2. Price not aligned to `price_tick` is sent。

### 验证方式

```bash
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_nautilus_integration.py -q
```

---

## Phase 5: Risk Preflight Expansion

### 目标

扩展资金、保证金、净持仓、重复 client order id、频率限制和 kill switch guardrails。

### 依赖

1. Account/position snapshot is available。
2. Guarded order command has explicit arm and config guardrails。

### Child Change

`20260608__openctp-tts-simulation-provider__risk-preflight-expansion`

### 交付物

1. Expanded risk preflight function。
2. Negative tests for each guardrail。
3. Simulation preflight evidence with redacted account metrics。

### Runtime / Command Freeze

1. `python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py -q`
2. Risk preflight command to be frozen by the child change。

### 退出条件

1. Unsafe order is blocked before native command。
2. Risk verdict records exact typed issue。
3. Kill switch default remains off after reconnect or command failure。

### Fail-fast / Negative Cases

1. Kill switch disabled but armed send proceeds。
2. Duplicate client order id creates ambiguous lifecycle。

### 验证方式

```bash
python -m pytest tests/test_guarded_paper_order_loop.py tests/test_paper_readonly_snapshot.py -q
```

---

## Phase 6: Real Reconnect Evidence

### 目标

补齐真实 simulation MD/TD reconnect、resubscribe、relogin、settlement readiness preserved 和 historical residue isolation evidence。

### 依赖

1. OpenCTP TTS front and SDK available。
2. Phase 4 repo-only recovery/idempotency baseline remains green。

### Child Change

`20260608__openctp-tts-simulation-provider__real-reconnect-evidence`

### 交付物

1. Reconnect rehearsal command or documented operator workflow。
2. MD resubscribe evidence。
3. TD reconnect evidence with `paper_send_armed=false`。

### Runtime / Command Freeze

1. `python -m pytest tests/test_paper_recovery_idempotency.py -q`
2. Reconnect simulation command to be frozen by the child change。

### 退出条件

1. MD resubscribes active symbols once。
2. TD relogin preserves profile and disarms order send。
3. Historical residue cannot mutate current session reports。

### Fail-fast / Negative Cases

1. Reconnect clears guardrails。
2. Historical callback is classified as current fill。

### 验证方式

```bash
python -m pytest tests/test_paper_recovery_idempotency.py -q
```

---

## Phase 7: Nautilus Engine Harness

### 目标

通过 Nautilus command path 触发 CTP provider submit/cancel/report 行为，避免只用 repo script shortcut 作为 provider evidence。

### 依赖

1. Phase 1-6 completed or typed blockers carried forward。
2. P002 Nautilus provider baseline remains green。

### Child Change

`20260608__openctp-tts-simulation-provider__nautilus-engine-harness`

### 交付物

1. Minimal Nautilus engine harness command。
2. Provider submit/cancel/report evidence。
3. Engine-level regression tests。

### Runtime / Command Freeze

1. `python -m pytest tests/test_nautilus_integration.py -q`
2. Engine harness command to be frozen by the child change。

### 退出条件

1. Harness uses provider entrypoint, not script internals only。
2. Order/fill/cancel/account/position reports are emitted through Nautilus-facing path。
3. Evidence maps to P4-A13/P4-A14/P4-F13/P4-R1。

### Fail-fast / Negative Cases

1. Harness bypasses provider and calls native smoke directly。
2. Engine evidence lacks account/position/report projection。

### 验证方式

```bash
python -m pytest tests/test_nautilus_integration.py -q
```

---

## Closeout Checklist

1. Phase 状态表和 `AI-PHASE-STATUS` 块均已回填为真实状态。
2. `README.md` 顶部 `**状态**` 与本页顶部 `**状态**` 已投影自 `AI-PHASE-STATUS.overall_status`。
3. proposal-level acceptance 中的每个 in-scope 场景都有 repo-local guard 和 simulation evidence，或 typed `paper-resource` blocker。
4. 所有 artifact references 都位于本文件声明的 `trusted_artifact_roots`。
5. Proposal docs gate、change docs gate、targeted tests、必要 guard 已执行并回填。
6. residual risk、non-goals 与 follow-up 已回填到 proposal、phase-plan 或 child change。
7. Graduation / Closeout Matrix 中 required target 均完成或写清 typed carry-forward。
