# CTP Paper-first Provider Capability Readiness

<!-- PROPOSAL-ANTI-DRIFT-GATE:v1 -->
<!-- PROPOSAL-SCAFFOLD: profile=multi_phase; fragments=change_map,decision_log -->
<!-- PROPOSAL-ADR-CARRIER-GATE:v1 -->

**proposal-id**：`p003-ctp-live-trading-provider-readiness`
**状态**：completed
**范围**：继续使用 `openctp-tts-7x24-simulation` 账号补齐 CTP provider 能力；暂不推进 formal-trading / Live 实盘验证。

| 顶部状态块 / Top Status Block | 值 |
| --- | --- |
| ADR carrier | no |
| Primary ADR | not_applicable |
| Carrier naming note | not_applicable |
| Tracer input case dir | not_applicable |
| Tracer case id | not_applicable |
| Tracer case ref | not_applicable |
| Work item type | delivery |
| Work item layer | proposal |
| Surface mode | console |
| Action mode | request_only |
| CTP account profile | openctp-tts-7x24-simulation |
| CTP config path | `cfgs/local/ctp.openctp.tts.7x24.local.json` |
| CTP evidence class | openctp-tts-7x24-simulation |

> 状态口径：本页顶部 `**状态**` 只是 human-readable projection；proposal 级唯一 machine-readable 主状态源是 `phase-plan.md` 中 `AI-PHASE-STATUS` 区块的 `overall_status`。
>
> Topic 边界：topic 不作为 proposal 推进容器；`topic-id` 只允许作为 child change `plan.md` frontmatter 标签和 `--by-topic` 分组维度。
>
> Live 边界：本 proposal 当前不使用正式交易账号、不发正式实盘单、不关闭 formal broker acceptance。正式交易 readiness 只作为未来 proposal 或 future phase carry-forward。

---

## 一句话结论

P003 改为 OpenCTP TTS 7x24 simulation-first 能力补齐路线：在 24 小时可调试 API 的 OpenCTP TTS 7x24 模拟账户中继续补 provider 的行情、查询、订单链路、回报、恢复、证据和 runbook 能力；正式 Live 暂停。

## Paper Capability GAP Table

| GAP | 当前事实 | Paper 开发目标 | 证据层级 | 下一步建议 |
| --- | --- | --- | --- | --- |
| Paper session readiness | OpenCTP paper baseline 已通 | 固化 TD/MD 登录、结算、交易日、front/session summary 和 redacted evidence | L5 paper-simulation | Phase 1 paper session preflight |
| Paper 合约与交易窗口 guardrails | 已有单合约/数量 guardrail 思路 | 用 paper 环境验证合约、交易窗口、qty、net-position、explicit arm 统一 preflight | L2/L5 | Phase 1 + Phase 3 |
| Paper 报单/撤单/成交回报链路 | P002 已有 repo-only report translation | 在 paper 账号验证 submit/cancel/fill/reject/timeout 回报分类 | L5 paper-simulation | Phase 3 guarded paper order loop |
| 查询与对账 truth snapshot | repo-only account/position report translation 已完成 | 用 paper 查询 account/position/order/trade/instrument 并形成对账 JSON | L4/L5 | Phase 2 readonly truth snapshot |
| 风控与 kill switch | live-send 默认禁止仍需统一入口 | 即使是 paper，也必须 explicit arm + guardrails；未来可迁移到 formal | L2/L5 | Phase 1 + Phase 3 |
| reconnect / replay / idempotency | paper smoke 有连接证据，恢复矩阵不足 | 在 paper/repo-only 中验证断线重连、重复 callback、历史残留处理 | L2/L5 | Phase 4 recovery-idempotency |
| 合约 universe 与 trading status | provider cache 已具备基础能力 | paper 查询结果驱动 instrument metadata、subscription 和 order preflight | L2/L5 | Phase 2 |
| 可观测性和证据留存 | runbook 已有 paper baseline | 每次 paper run 有 run id、flow path、session label、JSON summary、evidence root | L0/L5 | Phase 5 ops closeout |
| 性能、背压、超时语义 | runtime gate 可过 | callback queue drain、timeout/retry/backoff 在 paper/repo 中可观测 | L2/L5 | Phase 4 |
| Proposal 推进口径 | P002 completed，formal changes parked | 后续开发优先 paper 能力补齐；formal/live 不参与当前验收 | L0 | Phase 0 closeout |

## Paper Development Backlog

| 顺序 | Child change | 待开发能力 | 当前状态 |
| --- | --- | --- | --- |
| 1 | `20260608__ctp-paper-provider-readiness__paper-session-preflight` | Paper 配置、redaction、TD/MD login readiness、settlement、trading day、front/session summary | completed |
| 2 | `20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot` | Paper account/position/order/trade/instrument 只读快照、empty/timeout/query-failed disposition、Phase 3 reconciliation input | completed |
| 3 | `20260608__ctp-paper-provider-readiness__guarded-paper-order-loop` | Explicit-arm guarded paper order、submit/cancel/fill/reject/timeout 分类、pre/post snapshot reconciliation | completed |
| 4 | `20260608__ctp-paper-provider-readiness__paper-recovery-idempotency` | Reconnect/resubscribe、duplicate callback、historical residue、timeout/backpressure、idempotent reports | completed |
| 5 | `20260608__ctp-paper-provider-readiness__paper-ops-closeout` | Operator command matrix、evidence retention、redaction policy、runbook/architecture backfill、P003 closeout | completed |

## 目标 / Goals

1. 固定 `openctp-tts-7x24-simulation` 为当前 24 小时 API 调试开发账号 profile，后续 child change 默认使用该 profile。
2. 补齐 paper session preflight、read-only truth snapshot、guarded paper order loop、recovery/idempotency 和 evidence/runbook。
3. 把 paper 环境中的 request-only/guarded order 能力做成可迁移到 formal 的接口和证据形状。
4. 确保所有敏感信息只在 ignored `.env.d/`、`.env` 或 local config，proposal/runbook/evidence 只保留 redacted 字段。
5. 明确 formal-trading / Live 暂停，不作为 P003 当前验收条件。

## 非目标 / Non-Goals

1. 不连接正式交易账号，不发正式实盘单，不把 formal-trading 作为当前目标。
2. 不用 paper 证据宣称 formal broker readiness。
3. 不做自动策略、组合下单、期权链、多品种全覆盖或无人值守实盘。
4. 不把账号、密码、auth code 或 broker private fields 写入仓库。

## 评审结论 / Review Verdict

**当前结论**：completed

| 项 | 结论 |
| --- | --- |
| 是否进入正式 proposal | 是；P002 已完成开发基线，P003 聚焦 paper 环境中的能力补齐 |
| 是否需要 child change | 是；每个 phase 都应拆成 `docs/changes/<change-id>/` 执行切片 |
| 是否有 artifact trust boundary | 有；见 `phase-plan.md` |

## 当前状态快照 / Reality Snapshot

| 维度 | 当前事实 | 证据 |
| --- | --- | --- |
| P002 provider baseline | InstrumentProvider/cache、marketdata provider resolution、execution order/fill reports、position/account report translation 已完成 repo-only baseline | `docs/proposals/p002-nautilus-provider-production-readiness/` |
| OpenCTP TTS 7x24 baseline | OpenCTP TTS 7x24 可作为 24 小时 API 调试账户；账号敏感信息进入 ignored `.env.d/` 或 `cfgs/local/`，不写入仓库 | `docs/changes/20260607__openctp-tts__test-baseline/runbook.md`; ADR002 |
| Current execution policy | P003 继续 paper 能力补齐，formal/live 暂停 | 本 proposal README/phase-plan/acceptance |
| 验收边界 | P003 final acceptance 使用 `openctp-tts-7x24-simulation` evidence；formal-trading 只做 future carry-forward | `acceptance.md`; `phase-plan.md` |

## Graduation / Closeout Matrix

> 当 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status` 进入 `completed`，且 `reviewed_at >= 2026-05-22` 时，本节由 `python scripts/check_proposal_docs.py --root .` 检查。

No formal-trading graduation in P003; only paper development rules may graduate after closeout.

| Graduation item | Policy | Target | Status |
| --- | --- | --- | --- |
| ADR backfill | not_applicable | not_applicable | not_applicable |
| Architecture / ownership backfill | proposal_local | Stable paper-only rules remain in P003 and Phase 5 runbook until formal successor proposal | completed |
| Operator/runbook backfill | required | `docs/changes/20260608__ctp-paper-provider-readiness__paper-ops-closeout/paper_ops_runbook.md` | completed |
| Proposal-local evidence | archive_only | `acceptance.md` and `output/reports/p003-ctp-live-trading-provider-readiness/` | completed |

## 文档地图 / Document Map

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | proposal 概览、GAP 表、评审结论、现实状态快照 | 必需 |
| `phase-plan.md` | phase 状态板、artifact trust boundary、child change 入口 | 必需 |
| `acceptance.md` | proposal 级验收基线和 paper/formal 分层矩阵 | 必需 |
| `change-map.md` | proposal phase 到 child change 的映射 | 已启用 |
| `decision-log.md` | proposal 评审判断和 scope freeze 记录 | 已启用 |

## 稳定化规则 / Stabilization Rules

1. P003 当前完成只看 OpenCTP paper evidence；formal-trading / Live 不作为当前验收目标。
2. Paper order 也必须默认 request-only，只有 explicit arm、paper account profile、trade window、instrument preflight、qty cap、net-position cap 全部通过后才能触发。
3. 所有账号输出必须 redacted；不得在 proposal、change、evidence 或日志中复制账号、密码、认证码等敏感信息。
4. 若 OpenCTP paper 账号、SDK、交易窗口或 front 不可用，必须写 typed blocker 和 next action；不得伪造 pass。
5. P003 产生的可迁移长期规则必须在 closeout 时回流到 architecture 或 runbook，不能只留在 proposal-local 文本。
