# Acceptance / 验收基线

**proposal-id**：`p004-openctp-tts-simulation-provider-completeness`
**状态**：completed

---

## 验收范围 / Scope

当前 proposal 验收以下内容：

1. OpenCTP TTS 7x24 simulation 账户上的主动撤单、撤单失败和撤单 report 映射。
2. `OPEN`、`CLOSE`、`CLOSETODAY`、`CLOSEYESTERDAY` 的 provider 语义、CTP command 映射和模拟账户证据。
3. 每笔模拟下单后的 pre/post account、position、order、trade reconciliation。
4. 限价、FAK/FOK、tick 规整、涨跌停/不可交易合约阻断等订单类型和价格边界。
5. 资金、保证金、净持仓、重复 order id、频率限制、kill switch 等风控前置。
6. 真实模拟环境下 MD/TD reconnect、resubscribe、historical residue 隔离和 idempotency。
7. Nautilus engine harness 级下单、撤单、回报、账户和持仓报告闭环。

当前 proposal 不验收以下内容：

1. 正式交易账号、正式 broker front、实盘生产 readiness。
2. 自动策略、无人值守交易、组合单、套利或跨品种策略级风控。
3. 期权链、复杂组合保证金、做市或高频低延迟优化。
4. 将账号、密码、auth code 或 broker private fields 写入仓库。

---

## Artifact Root Rule

本文件引用的 formal artifact、projection、report、verdict 必须属于 sibling `phase-plan.md` 中声明的 `Artifact Trust Boundary`。

P004 trusted artifact root 为 `output/reports/p004-openctp-tts-simulation-provider-completeness/`。模拟账户运行证据必须 redacted；不得包含 raw account id、password、auth code、broker private fields 或未脱敏 private front。

---

## Acceptance Evidence Boundary

1. `pytest`、`unittest`、mock、stub、monkeypatch 或其他 test-only 输出，只能作为 contract/function guard evidence，不得单独充当 proposal 正式验收证据。
2. 需要模拟账户实证的场景，必须至少包含一次真实 OpenCTP TTS 7x24 simulation 命令输出、JSON report 或 child change evidence。
3. 若外部 front、合约交易窗口或账号状态不可用，只能记录 typed `paper-resource` blocker，不得伪造 pass。
4. 若命中本地代码、contract、redaction、guardrail 或 docs gate blocker，必须继续修复；不得把 repo-local blocker 写成最终阻塞。
5. 所有下单类验收都必须证明 explicit arm、profile、allowlist、qty cap、risk preflight 和 kill switch 处于可判定状态。

---

## Acceptance Layers

| Layer | 名称 | 说明 | 默认证据 |
| --- | --- | --- | --- |
| L0 | Docs/governance | proposal/change/frontier 一致性 | `check_proposal_docs.py`, `check_change_docs.py`, `check_harness.py` |
| L1 | Contract tests | command mapping、callback mapping、guardrail negative path | focused pytest |
| L2 | Repo smoke | dry-run、snapshot、recovery/idempotency local diagnostics | repo smoke scripts |
| L3 | OpenCTP TTS simulation | 真实 7x24 simulation front 上的 query/order/cancel/reconnect evidence | `output/reports/p004-openctp-tts-simulation-provider-completeness/` |
| L4 | Nautilus engine harness | 通过 Nautilus command 触发 provider 行为并生成 reports | engine harness output |
| L5 | Formal trading | 正式 broker / 实盘 readiness | out_of_scope_for_p004 |

---

## Capability Coverage Index

| Capability | Phase | Planned child change | Scenario IDs | Repo-only gate | Simulation pass signal |
| --- | --- | --- | --- | --- | --- |
| Account/runbook profile cleanup | Phase 0 | proposal-only / runbook cleanup | P4-A1, P4-F1 | docs gate | P003/P004 profile wording is canonical |
| Cancel lifecycle | Phase 1 | `20260608__openctp-tts-simulation-provider__cancel-lifecycle` | P4-A2, P4-A3, P4-F2, P4-F3 | cancel mapping tests | passive order can be cancelled or typed reject is explained |
| Close position semantics | Phase 2 | `20260608__openctp-tts-simulation-provider__close-position-semantics` | P4-A4, P4-A5, P4-F4, P4-F5 | command mapping tests | close today/yesterday evidence or typed blocker |
| Post-order reconciliation | Phase 3 | `20260608__openctp-tts-simulation-provider__post-order-reconciliation` | P4-A6, P4-A7, P4-F6 | reconciliation tests | pre/post snapshot explains fill/reject/cancel result |
| Order type and price boundary | Phase 4 | `20260608__openctp-tts-simulation-provider__order-type-price-boundary` | P4-A8, P4-A9, P4-F7, P4-F8 | price/order-type tests | FAK/FOK/tick/limit boundary is typed |
| Risk preflight expansion | Phase 5 | `20260608__openctp-tts-simulation-provider__risk-preflight-expansion` | P4-A10, P4-F9, P4-F10, P4-F11 | guardrail tests | unsafe send is blocked before native command |
| Real reconnect evidence | Phase 6 | `20260608__openctp-tts-simulation-provider__real-reconnect-evidence` | P4-A11, P4-A12, P4-F12 | recovery tests | reconnect/resubscribe/relogin evidence is redacted |
| Nautilus engine harness | Phase 7 | `20260608__openctp-tts-simulation-provider__nautilus-engine-harness` | P4-A13, P4-A14, P4-F13, P4-R1 | integration tests | Nautilus command path emits provider reports |
| Cross-phase startup and evidence contract | All phases | all P004 child changes | P4-A15, P4-A16, P4-A17, P4-F14, P4-F15, P4-B3 | docs and redaction gates | every child change can run from runbook without chat context |
| Cross-phase sequencing and safety | All order phases | all order-capable child changes | P4-A18, P4-A19, P4-F16, P4-F17, P4-F18 | guardrail tests | unsafe or out-of-order execution is blocked |
| Account state cleanup and carry-forward | All phases | all P004 child changes | P4-A20, P4-A21, P4-F19, P4-F20, P4-R2 | snapshot/reconciliation tests | residual positions/orders are visible and mapped forward |

---

## 场景矩阵 / Scenario Matrix

| ID | 类型 | 场景 | 验收方式 | 通过信号 | 状态 |
| --- | --- | --- | --- | --- | --- |
| P4-A1 | success | P003/P004 runbook and proposal wording use canonical `openctp-tts-7x24-simulation` profile | docs review and proposal docs gate | no stale `openctp-paper` / `paper-simulation` pass boundary remains except explicitly marked legacy alias | passed |
| P4-A2 | success | Passive simulation order can be submitted without immediate full fill when cancel scenario requires it | cancel lifecycle child change | order accepted or typed market/resource blocker explains why passive order cannot be staged | passed |
| P4-A3 | success | Active cancel command maps to CTP cancel request and Nautilus cancel report | simulation cancel command and callback evidence | cancel accepted/rejected status, native order ref, front/session identity and report mapping are recorded | passed |
| P4-A4 | success | Existing simulation position can be selected as close candidate without leaking account identity | close semantics child change | side, exchange, today/yesterday qty, available close qty and redacted account fingerprint are recorded | passed |
| P4-A5 | success | Close command maps to expected CTP position effect | dry-run plus simulation evidence | `CLOSE`, `CLOSETODAY`, or `CLOSEYESTERDAY` is deterministic for exchange/position split | passed |
| P4-A6 | success | Filled simulation order triggers automatic post-order snapshot | post-order reconciliation child change | pre/post position/account/order/trade delta matches fill qty and leaves qty | passed |
| P4-A7 | success | Rejected or cancelled simulation order still produces post-order reconciliation | post-order reconciliation child change | no-position-delta and order/trade status explain final lifecycle disposition | passed |
| P4-A8 | success | Order type mapping covers limit and FAK/FOK where CTP front supports them | order type child change | native command payload records order type and time condition without silent fallback | passed |
| P4-A9 | success | Price tick and limit boundary are enforced before native send | price boundary tests and simulation blocker evidence | malformed price, off-tick price, non-tradable status or limit-boundary issue blocks or types the order | passed |
| P4-A10 | success | Expanded risk preflight reads account/position truth before armed send | risk preflight child change | available funds, margin, net position and configured caps are checked and recorded redacted | passed |
| P4-A11 | success | MD disconnect/reconnect restores subscribed symbols once | real reconnect child change | disconnect reason, reconnect attempt, login success and resubscribe count are recorded | passed |
| P4-A12 | success | TD reconnect preserves profile and leaves order send disarmed | real reconnect child change | relogin/settlement readiness is restored and `paper_send_armed=false` after reconnect | passed |
| P4-A13 | success | Nautilus engine command can submit a simulation order through provider entrypoint | engine harness child change | Nautilus command path emits order accepted/fill/reject report without using script-only shortcut | passed |
| P4-A14 | success | Nautilus engine command can cancel or classify cancel failure | engine harness child change | cancel command path emits cancel report or typed cancel reject through provider event flow | passed |
| P4-A15 | success | Operator can start any P004 child change without chat context | child change docs review | `plan.md`/`acceptance.md`/`ai_constraints.md` name commands, evidence roots, account profile and fail-fast boundaries | passed |
| P4-A16 | success | Simulation environment preflight records local readiness before order-capable scenarios | preflight command in each order-capable child change | config fingerprint, profile, instrument allowlist, `AllowLiveOrderSmoke`, trading day and front/session readiness are redacted and recorded | passed |
| P4-A17 | success | Evidence schema is stable across all P004 child changes | JSON/evidence review and docs gate | every evidence file includes proposal id, change id, scenario id, run id, account profile, evidence class, command, verdict and redaction statement | passed |
| P4-A18 | success | Child change order respects frontier and phase dependencies | `show_current_frontier.py` and change-map review | active change is the lowest execution order unfinished P004 child change unless a typed blocker permits carry-forward | passed |
| P4-A19 | success | Order-capable scenario can run in dry-run mode with the same contract as armed simulation send | focused command/test | dry-run emits native payload contract, guardrail verdict and no native send; armed path reuses the same contract | passed |
| P4-A20 | success | Residual open orders and positions from previous simulation runs are visible before new sends | read-only snapshot before each order-capable child change | preflight lists or fingerprints residual orders/positions and maps them to close/cancel/carry-forward action | passed |
| P4-A21 | success | P004 closeout can distinguish completed, typed-blocked and carried-forward scenarios | proposal closeout review | every scenario is `passed`, typed `paper-resource` blocker, or explicit carry-forward with next action | passed |
| P4-A22 | success | Close position handles opposite-side order direction correctly | close semantics child change | long positions close with sell-side command and short positions close with buy-side command | passed |
| P4-A23 | success | Post-order reconciliation covers partial fill and timeout states | post-order reconciliation child change | fill qty, leaves qty, timeout status and query truth are all typed without ambiguous final state | passed |
| P4-A24 | success | Order type and price boundary includes volume lot/min/max checks | order type child change | invalid quantity lot/min/max blocks before native send and records instrument metadata source | passed |
| P4-A25 | success | Risk preflight includes session-level send budget | risk preflight child change | repeated sends are capped, typed and redacted | passed |
| P4-A26 | success | Reconnect evidence covers in-flight order state | real reconnect child change | in-flight order after reconnect is recovered, reconciled or typed as conservative blocker | passed |
| P4-A27 | success | Nautilus engine harness covers rejected and filled reports idempotently | engine harness child change | engine emits one stable report per logical order/fill and maps reject reason | passed |
| P4-F1 | failure | Stale alias is used as canonical profile in new P004 evidence | docs gate / review | evidence is rejected unless alias is explicitly marked legacy compatibility | passed |
| P4-F2 | failure | Cancel is attempted without native order ref/front/session identity | cancel lifecycle negative test | no native cancel command is sent; typed `cancel_contract_failed` is recorded | passed |
| P4-F3 | failure | Duplicate cancel callback creates duplicate report | callback idempotency test | duplicate native callback is ignored or typed duplicate | passed |
| P4-F4 | failure | Close command is sent when no matching available position exists | close semantics preflight | no native order send occurs; typed no-position/insufficient-position blocker is recorded | passed |
| P4-F5 | failure | SHFE/INE today/yesterday split is collapsed into generic close | close semantics negative test | command is rejected before native send or maps to explicit close today/yesterday | passed |
| P4-F6 | failure | Post-order reconciliation accepts stale or partial snapshot | reconciliation negative test | stale run id, mismatched account fingerprint or partial snapshot blocks closeout | passed |
| P4-F7 | failure | Unsupported order type silently downgrades to limit | order type negative test | command fails fast with typed unsupported order type disposition | passed |
| P4-F8 | failure | Off-tick or limit-boundary price is sent to native bridge | price boundary negative test | order is blocked before native send and issue is typed | passed |
| P4-F9 | failure | Quantity, max net position or frequency cap is bypassed | risk preflight negative tests | no native command is submitted | passed |
| P4-F10 | failure | Kill switch is off but armed send still proceeds | risk preflight negative tests | command exits before order mapping and records `paper-safety` blocker | passed |
| P4-F11 | failure | Reused client order id creates ambiguous lifecycle | risk/idempotency test | duplicate id is rejected before native send or explicitly correlated to existing order | passed |
| P4-F12 | failure | Reconnect classifies historical callback as current fill | reconnect/idempotency test | callback is tagged residue/historical and current session report remains unchanged | passed |
| P4-F13 | failure | Engine harness bypasses provider entrypoint and calls script internals only | engine harness review/test | harness evidence is rejected as non-provider evidence | passed |
| P4-F14 | failure | Evidence omits scenario id, run id or account profile | docs/evidence review | evidence cannot close the row and child change remains pending | passed |
| P4-F15 | failure | Evidence leaks raw account id, password, auth code, broker private fields or private front | redaction review/test | evidence is rejected and must be regenerated redacted | passed |
| P4-F16 | failure | Order-capable scenario skips pre-order read-only snapshot | guardrail negative test/review | native send is blocked and typed `pre_snapshot_missing` or equivalent issue is recorded | passed |
| P4-F17 | failure | Armed simulation send proceeds when `AllowLiveOrderSmoke=false` | guardrail negative test | no native send occurs and `paper-safety` blocker is recorded | passed |
| P4-F18 | failure | A later P004 child change is closed while an earlier hard dependency is neither completed nor typed-blocked | frontier/change-map review | closeout is rejected until dependency is resolved or carry-forward is explicit | passed |
| P4-F19 | failure | Residual open order is ignored before a new cancel/close/order scenario | preflight negative test/review | new send is blocked or residual order is explicitly carried forward | passed |
| P4-F20 | failure | Proposal closeout claims provider completeness with only repo-only tests and no simulation evidence/blocker | proposal review | closeout is rejected; test-only evidence remains guard/reference | passed |
| P4-F21 | failure | Close direction opens more exposure instead of reducing position | close semantics negative test | command is rejected before native send | passed |
| P4-F22 | failure | Partial fill is reconciled as full fill | reconciliation negative test | leaves qty and fill qty mismatch blocks acceptance | passed |
| P4-F23 | failure | Invalid quantity lot/min/max is sent to native bridge | order type/price negative test | order is blocked before native send | passed |
| P4-F24 | failure | Session-level send budget is not enforced across repeated commands | risk preflight negative test | repeated sends stop at configured budget | passed |
| P4-F25 | failure | In-flight order state is lost across reconnect | reconnect negative test or typed blocker review | reconnect evidence cannot pass without recovery, reconciliation or conservative blocker | passed |
| P4-F26 | failure | Engine emits duplicate fill/order reports for one logical event | engine harness idempotency test | duplicate event is ignored or typed duplicate | passed |
| P4-R1 | regression | P003 guarded order and readonly snapshot baseline regresses | focused regression commands | existing P003 tests and proposal docs gate remain pass | passed |
| P4-R2 | regression | P004 child changes weaken redaction or account-profile rules established by ADR002/P003 | docs and focused tests | canonical profile and redaction rules remain enforced | passed |
| P4-B1 | blocker | OpenCTP TTS front, account, SDK or trade window is unavailable | child change evidence | typed `paper-resource` blocker includes next action and repo-only fallback | passed: front/SDK available; controlled reconnect covered separately |
| P4-B2 | blocker | Simulation account cannot stage passive order because market fills immediately | cancel lifecycle evidence | typed blocker records attempted symbols/prices and alternative staging plan | passed |
| P4-B3 | blocker | A required simulation contract is unavailable or suspended for the 7x24 front | instrument query and child change evidence | typed blocker records contract, exchange, query result, next candidate-selection action and no native send | passed |

---

## ADR Carrier Acceptance Matrix

not_applicable

| ID | Primary ADR | ADR decision item | ADR successor scenario | Positive path | Must fail if | Authority / retirement boundary | Minimal evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable |

---

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| P003 baseline | `docs/proposals/p003-ctp-live-trading-provider-readiness/` | P003 completed；P004 继承为 baseline，不作为 P004 pass evidence |
| P003 zn2610 simulation order | `docs/changes/20260608__ctp-paper-provider-readiness__guarded-paper-order-loop/evidence_20260608_openctp_tts_zn2610_buy2.md` | filled order proves submit/fill baseline only |
| P003 c2609 simulation order | `docs/changes/20260608__ctp-paper-provider-readiness__guarded-paper-order-loop/evidence_20260608_openctp_tts_c2609_sell3.md` | rejected order proves reject classification baseline only |
| P004 proposal docs gate | `python scripts/check_proposal_docs.py --root . --proposal-id p004-openctp-tts-simulation-provider-completeness` | passed |
| Change docs gate | `python scripts/check_change_docs.py --root .` | passed |

---

## Closeout Checklist

1. 所有 in-scope 场景都有 repo-local guard 和真实 simulation evidence，或 typed `paper-resource` blocker。
2. 所有下单类 evidence 均证明 explicit arm、profile、allowlist、qty cap、risk preflight 和 kill switch 状态。
3. `formal-trading` 不作为 P004 当前验收目标，也不得被 simulation evidence 关闭。
4. residual risk 已回填到 proposal、phase-plan、child change 或长期 runbook。
5. 任何 proposal 场景都不得仅凭 test/mock 结果写成正式验收通过；若 test 是当前唯一证据，必须显式标注为 guard/reference。
