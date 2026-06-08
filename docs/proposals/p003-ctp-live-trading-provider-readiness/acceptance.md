# Acceptance / 验收基线

**proposal-id**：`p003-ctp-live-trading-provider-readiness`
**状态**：completed

---

## 验收范围 / Scope

当前 proposal 验收以下内容：

1. OpenCTP paper provider capability 的 GAP、phase split、child change mapping 和 acceptance matrix 是否清晰。
2. Paper-simulation evidence 与 future formal-trading evidence 是否严格分离。
3. Paper preflight、read-only truth snapshot、guarded order loop、recovery/idempotency 和 ops closeout 是否都有可判定 pass/fail/blocker。
4. Paper order 是否默认 request-only，且只能在 explicit arm、trade window、instrument、qty、net position、rate limit、kill switch 和 account profile 全部通过后执行。

当前 proposal 不验收以下内容：

1. 正式交易账号 / Live 实盘 readiness。
2. OpenCTP paper 已经证明正式柜台 readiness。
3. 自动策略、组合下单、期权链、多品种全覆盖或全天候无人值守。
4. 将账号、密码、auth code 或 broker private fields 写入仓库。

---

## Artifact Root Rule

本文件引用的 paper artifact、projection、report、verdict 必须属于 sibling `phase-plan.md` 中声明的 `Artifact Trust Boundary`。

Formal-trading / Live evidence is out of current scope and must not be required by P003 acceptance rows。

---

## 验收层级 / Acceptance Layers

| Layer | 名称 | 说明 | 默认命令或证据 |
| --- | --- | --- | --- |
| L0 | Docs/governance | proposal/change/frontier 一致性 | `check_proposal_docs.py`, `check_change_docs.py`, `check_harness.py` |
| L1 | Static/API contract | import、factory、report、guardrail public surface | focused pytest |
| L2 | Repo-only behavior | fake callback、duplicate callback、guardrail negative path | `tests/test_nautilus_integration.py` |
| L3 | Runtime/Rust gate | PyO3、Rust、native bridge build/test | `python scripts/check_rust_gate.py` |
| L4 | Local smoke/read-only | repo debug smoke and dry/read-only diagnostics | `ctp_repo_debug_smoke.py` or successor |
| L5 | OpenCTP paper development evidence | OpenCTP TTS paper simulation | paper smoke/successor command |
| L6 | Formal trading final evidence | 正式交易账号 / broker front 的上线前确认 | out_of_scope_for_p003 |

---

## Account Profile Matrix

| Account profile | 用途 | May close P003 current acceptance | May be used for | Must fail if |
| --- | --- | --- | --- | --- |
| `repo-only` | Local contract and negative-path tests | yes for repo-only rows only | guardrail/report/idempotency tests | claims external CTP connectivity |
| `openctp-tts-7x24-simulation` | OpenCTP TTS 7x24 development/rehearsal/regression | yes | 24h API debug, session, order-chain, recovery, query evidence | used to claim formal broker readiness |
| `formal-trading` | Future pre-go-live broker evidence | no | future successor proposal only | requested by P003 current child change |

---

## Capability Coverage Index

| Capability | Phase | Child change | Scenario IDs | Repo-only gate | Paper pass signal |
| --- | --- | --- | --- | --- | --- |
| Paper session preflight | Phase 1 | `20260608__ctp-paper-provider-readiness__paper-session-preflight` | P3-A1, P3-A2, P3-F1 | config validation and redaction tests passed | paper TD/MD login/settlement/trading-day evidence passed |
| Paper read-only truth snapshot | Phase 2 | `20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot` | P3-A3, P3-F2, P3-A8, P3-A12, P3-A13 | query/report/correctness repo tests passed | paper account/position/order/trade/instrument snapshot passed |
| Guarded paper order lifecycle | Phase 3 | `20260608__ctp-paper-provider-readiness__guarded-paper-order-loop` | P3-A4, P3-A5, P3-F3 | guardrail negative tests | paper one-hand lifecycle evidence |
| Paper recovery/idempotency | Phase 4 | `20260608__ctp-paper-provider-readiness__paper-recovery-idempotency` | P3-A6, P3-F4 | duplicate/reconnect repo tests | paper recovery evidence or typed paper-resource blocker |
| Paper ops/runbook closeout | Phase 5 | `20260608__ctp-paper-provider-readiness__paper-ops-closeout` | P3-A7, P3-R1 | docs gates and runbook review | operator matrix and redacted evidence retention |

---

## 场景矩阵 / Scenario Matrix

| ID | 类型 | 场景 | 验收方式 | 通过信号 | 状态 |
| --- | --- | --- | --- | --- | --- |
| P3-A1 | success | OpenCTP paper local config preflight is available and redacted | Phase 1 child change | missing config/secret produces typed blocker; present config produces redacted fingerprint | passed |
| P3-A2 | success | Paper TD/MD login readiness can be judged | Paper preflight command | login, settlement, trading day, front/session disposition are recorded without secret leak | passed |
| P3-A3 | success | Paper read-only truth snapshot is reproducible | Phase 2 command | account/position/order/trade/instrument summary exists under trusted root | passed |
| P3-A4 | success | Paper order send is blocked until explicit arm and all guardrails pass | Phase 3 tests and command dry path | unsafe conditions fail before native order send | passed |
| P3-A5 | success | Guarded paper one-hand order lifecycle is classified | Paper Phase 3 evidence | submit/cancel/fill/reject/timeout and post-trade reconciliation are typed | passed |
| P3-A6 | success | Paper recovery and idempotency behavior is covered | Phase 4 tests/evidence | duplicate callback and reconnect do not create duplicate or stale reports | passed |
| P3-A7 | success | Operator can run the paper readiness path without chat context | Phase 5 runbook review | command matrix, pass/fail/blocker semantics, evidence roots and redaction policy are documented | passed |
| P3-A8 | success | Paper snapshot schema contains run id, flow path, session label and account profile | Phase 2 schema tests/evidence | JSON summary is reusable by Phase 3 reconciliation without chat context | passed |
| P3-A9 | success | Guarded paper order loop requires a Phase 2-compatible pre-order snapshot | Phase 3 tests | command fails before order send when snapshot is missing or stale | passed |
| P3-A10 | success | Paper recovery handles historical residue separately from current session events | Phase 4 tests/evidence | historical callbacks are tagged and do not mutate current session reports | passed |
| P3-A11 | success | P003 closeout keeps formal-trading as future carry-forward only | Phase 5 docs gate/review | closeout does not claim formal broker readiness | passed |
| P3-A12 | success | 合约查询正确性：paper instrument query fields match provider/cache requirements | Phase 2 schema/provider tests | symbol、exchange、product kind、price tick、volume multiple、display id 可用于 provider/cache hydration | passed |
| P3-A13 | success | 持仓查询正确性：paper position query preserves direction and today/yesterday split | Phase 2 query/report tests | long/short、position qty、yd/td qty、cost、no-position disposition 可复核 | passed |
| P3-A14 | success | 下单正确性：paper order intent maps to expected CTP order command before native send | Phase 3 dry-run/preflight tests | instrument、side、qty、price mode、position effect、order ref、front/session identity are deterministic | passed |
| P3-A15 | success | 下单回报正确性：paper order/trade callbacks map to Nautilus reports once | Phase 3 lifecycle tests/evidence | order status, fill qty/price, leaves qty, reject reason and cancel result are typed and idempotent | passed |
| P3-A16 | success | 合约明细查询完整性：C0/C1/C2 字段分层和 evidence shape 明确 | Phase 2 acceptance design | C0 covered；C1 lifecycle/market limits/product relation planned；C2 options-specific out of current scope | passed |
| P3-A17 | success | 合约明细查询正确性：tick/multiplier/product/trading status/order volume rules drive Phase 3 preflight | Phase 2 + Phase 3 successor tests | malformed or non-tradable contract blocks provider/cache or paper order preflight | passed |
| P3-A18 | success | 断点恢复：paper recovery command can resume from checkpoint without duplicating evidence or reports | Phase 4 repo/paper tests | same run id, monotonic attempt, completed/pending step split, no duplicate reports | passed |
| P3-A19 | success | MD 重连：disconnect is detected and subscribed paper symbols are restored once | Phase 4 reconnect evidence | disconnect reason, reconnect attempt, login success and resubscribed symbols are recorded | passed |
| P3-A20 | success | TD 重连：login/settlement readiness recovers while order send remains disarmed | Phase 4 reconnect evidence | account profile/guardrails preserved and `paper_send_armed=false` after reconnect | passed |
| P3-F1 | failure | Formal-trading config is requested by current P003 path | Phase 1 validation | validation rejects formal profile for current paper evidence | passed |
| P3-F2 | failure | Valid empty paper position is treated as timeout | Phase 2 tests | empty/no-position/timeout/login-failed are separate dispositions | passed |
| P3-F3 | failure | Paper order command bypasses trade-window or risk guardrails | Phase 3 negative tests | no native order send occurs and error is typed | passed |
| P3-F4 | failure | Duplicate trade callback creates duplicate fill report | Phase 4 tests | duplicate callback is idempotent or typed duplicate | passed |
| P3-F5 | failure | Snapshot or order evidence emits raw account id, password, auth code or private front | redaction tests/review | tests or review fail before acceptance can pass | passed |
| P3-F6 | failure | 合约查询返回字段缺失但仍进入 provider/cache | Phase 2 negative tests | malformed instrument metadata is rejected with typed data-contract disposition | passed |
| P3-F7 | failure | 持仓方向或数量解析错误仍被标记为可对账 | Phase 2 negative tests | invalid direction/qty split fails correctness acceptance | passed |
| P3-F8 | failure | 下单 intent 与 native command 不一致 | Phase 3 negative tests | mismatch blocks send and records typed order-contract failure | passed |
| P3-F9 | failure | 合约明细字段冲突或未知 product kind 被静默合并为 pass | Phase 2 successor negative tests | conflict/unknown fields produce typed `data-contract` disposition | passed |
| P3-F10 | failure | 断点恢复把 partial snapshot 当作完整 pre-order evidence | Phase 4 negative tests | incomplete checkpoint/snapshot blocks Phase 3 order preflight | passed |
| P3-F11 | failure | TD 重连后的历史 callback 被当作 current session fill | Phase 4 idempotency tests | callback is tagged historical/residue and does not mutate current reports | passed |
| P3-R1 | regression | P002 paper/repo baseline is weakened while adding paper capability work | regression gates | P002 focused provider tests and Rust gate remain pass | passed |
| P3-R2 | regression | Repo-only tests stop running because paper front is unavailable | Phase 2-4 verification | repo-only gates still run and paper dependency becomes typed blocker only | passed |
| P3-B1 | blocker | OpenCTP paper account, SDK, trade window, or front is unavailable | child change blocker evidence | status is typed paper-resource blocker with next action and repo-only fallback | passed |
| P3-B2 | blocker | Paper order trade window is closed or contract is not tradable | Phase 3 preflight evidence | order loop records typed blocker and does not send | passed |

---

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| Proposal scaffold | `docs/proposals/p003-ctp-live-trading-provider-readiness/` | P003 proposal container created |
| P002 baseline | `docs/proposals/p002-nautilus-provider-production-readiness/` | provider development baseline completed; P003 adds paper capability evidence |
| OpenCTP paper authority | `docs/changes/20260607__openctp-tts__test-baseline/runbook.md` | paper simulation profile available for development/rehearsal/regression |
| Current scope correction | User instruction on 2026-06-08 | Continue using paper account; temporarily no Live |
| Phase 1 paper preflight | `docs/changes/20260608__ctp-paper-provider-readiness__paper-session-preflight/evidence_paper_session_preflight.md` | redacted config-only and paper connect preflight passed |
| Phase 2 paper read-only snapshot | `docs/changes/20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot/evidence_paper_readonly_snapshot.md` | redacted account/position/instrument/order-trade read-only snapshot passed |
| Phase 3 guarded paper order loop | `docs/changes/20260608__ctp-paper-provider-readiness__guarded-paper-order-loop/evidence_guarded_paper_order_dry_run.md` | dry-run/order contract/callback contract passed; armed-send typed blocker recorded |
| OpenCTP TTS 7x24 zn2610 order send | `docs/changes/20260608__ctp-paper-provider-readiness__guarded-paper-order-loop/evidence_20260608_openctp_tts_zn2610_buy2.md` | simulated `zn2610` BUY 2 order filled; not formal-trading evidence |
| OpenCTP TTS 7x24 c2609 order send | `docs/changes/20260608__ctp-paper-provider-readiness__guarded-paper-order-loop/evidence_20260608_openctp_tts_c2609_sell3.md` | simulated `c2609` SELL OPEN 3 order was submitted and typed as rejected with no fill; not formal-trading evidence |
| Phase 4 paper recovery/idempotency | `docs/changes/20260608__ctp-paper-provider-readiness__paper-recovery-idempotency/evidence_paper_recovery_idempotency.md` | checkpoint/reconnect/idempotency repo-only evidence passed |
| Phase 5 paper ops closeout | `docs/changes/20260608__ctp-paper-provider-readiness__paper-ops-closeout/paper_ops_runbook.md` | operator command matrix, redaction, evidence retention and no-formal-pass boundary documented |

---

## Closeout Checklist

1. All in-scope paper scenarios have redacted paper-simulation evidence or typed paper-resource blocker。
2. Formal-trading / Live is not required or invoked by P003 current child changes。
3. Paper order requires explicit arm, paper profile, trade window and risk guardrails。
4. Proposal docs gate, change docs gate, Rust gate and focused tests are executed and backfilled。
5. Runbook and stable architecture rules are graduated or explicitly kept proposal-local。
