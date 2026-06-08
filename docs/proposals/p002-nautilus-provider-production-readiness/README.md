# Nautilus Provider Production Readiness

<!-- PROPOSAL-ANTI-DRIFT-GATE:v1 -->
<!-- PROPOSAL-SCAFFOLD: profile=multi_phase; fragments=change_map,decision_log -->
<!-- PROPOSAL-ADR-CARRIER-GATE:v1 -->

**proposal-id**：`p002-nautilus-provider-production-readiness`
**状态**：completed
**范围**：以 Nautilus Interactive Brokers provider 已证明的 host-facing contract 为参照，使用 OpenCTP paper 账号作为 live-capable development account，并保留 formal trading 账号作为上线前最终证据，补齐 CTP adapter 从 smoke baseline 到 TradingNode 可消费 provider 的生产能力。

| 顶部状态块 / Top Status Block | 值 |
| --- | --- |
| ADR carrier | no |
| Primary ADR | not_applicable |
| Carrier naming note | not_applicable |
| Tracer input case dir | not_applicable |
| Tracer case id | not_applicable |
| Tracer case ref | not_applicable |
| CTP account profile | openctp-paper for development; formal-trading only for final broker evidence |
| CTP config path | `cfgs/local/ctp.openctp.tts.7x24.local.json` for development; formal config only when final evidence phase asks for it |
| CTP evidence class | paper-simulation during development; formal-broker only for final acceptance |

> 适用前提：proposal 用于“很多步骤、需要多 phase 推进”的正式任务容器；若单个 child change 就能完整闭环，不必建立 proposal。
>
> 状态口径：本页顶部 `**状态**` 只是 human-readable projection；proposal 级唯一 machine-readable 主状态源是 `phase-plan.md` 中 `AI-PHASE-STATUS` 区块的 `overall_status`。
>
> Topic 边界：topic 不作为 proposal 推进容器；`topic-id` 只允许作为 child change `plan.md` frontmatter 标签和 `--by-topic` 分组维度。

---

## 一句话结论

本 proposal 把当前 CTP adapter 的能力缺口收敛为一条可由 AI/autopilot 持续推进的生产就绪路线：先补 `InstrumentProvider` 与 Nautilus cache hydration，再补行情、执行、查询报告和 live ops evidence。IB provider 只作为 Nautilus-facing 能力参照，不作为 CTP runtime 架构约束。

开发账户口径：P002 的 live-capable development 默认使用 `openctp-paper`。OpenCTP TTS 7x24 按 ADR002 作为 paper simulation / development test environment；正式交易账号使用 `formal-trading`，只保留为上线前最终 broker-facing evidence，不作为本 proposal 的日常开发账户。

## 目标 / Goals

1. 建立 `IB-provider-parity baseline`：对齐 Nautilus provider/client 的可消费行为，而不是复制 IB 的 broker-specific 细节。
2. 把 `CtpInstrumentProvider` 从 standalone smoke/result holder 推进成 TradingNode data/execution client 共享的真实 Nautilus provider。
3. 补齐行情与执行 wrapper 的生产缺口：cache hydration、订阅解析、order/trade/position report、失败语义和 reconnect/readiness evidence。
4. 为每个能力面建立 repo-only acceptance 与 live acceptance 的分离矩阵，允许 AI 在缺 live 条件时继续推进本地可验证工作。
5. 明确哪些结论需要在 proposal closeout 后回流到 architecture/runbook，哪些只保留为 proposal-local evidence。
6. 冻结 `openctp-paper` 为 provider production readiness 的开发账户基线：行情、查询、guarded order/report evidence 优先在 OpenCTP paper 上验证，`formal-trading` 不得用于日常开发闭环。

## 非目标 / Non-Goals

1. 不把 CTP runtime 改成 IB/TWS 风格的 client architecture；CTP 仍继承 Rust/native runtime + thin Python Nautilus glue。
2. 不在本 proposal 中新增外部 daemon、C# managed bridge 或第二套 runtime API。
3. 不要求一次补齐 CTP 全品种、全交易所、期权链、组合合约和历史行情；这些只能按 phase/child change 渐进承接。
4. 不用 mock、stub、历史截图或聊天结论替代 L5 OpenCTP paper account evidence。
5. 不用生产实盘账户承担日常开发、调试或 guardrail 试错；生产账户只允许作为 final pre-go-live evidence path。

## 评审结论 / Review Verdict

**当前结论**：completed

| 项 | 结论 |
| --- | --- |
| 是否进入正式 proposal | 是；当前能力缺口跨 provider、data、execution、query/report 与 live ops，单个 child change 无法闭环 |
| 是否需要 child change | 是；每个 phase 都必须拆成一个或多个 `docs/changes/<change-id>/` 执行切片 |
| 是否有 artifact trust boundary | 有；见 `phase-plan.md` |

## 当前状态快照 / Reality Snapshot

以下状态以本地代码、测试、已完成 changes 与相关文档为准，而不是只按 proposal 正文判断：

| 维度 | 当前事实 | 证据 |
| --- | --- | --- |
| 代码状态 | `CtpInstrumentProvider`、`CtpNautilusInstrumentProvider`、data/exec factories、marketdata provider-backed tick resolution、execution order/fill/position reports、account state evidence translation 均已形成 repo-only contract；OpenCTP paper baseline 已可复用 | `src/nautilus_ctp_adapter/adapters/ctp/nautilus_provider.py`; `src/nautilus_ctp_adapter/adapters/ctp/nautilus_factories.py`; `src/nautilus_ctp_adapter/adapters/ctp/nautilus_data.py`; `src/nautilus_ctp_adapter/adapters/ctp/nautilus_execution.py` |
| 文档状态 | instrument provider、marketdata、execution 主 topic 已完成最小 smoke baseline；live ops 和 session hardening 仍 blocked/parked | `docs/topics/nautilus-instrument-provider.md`; `docs/topics/nautilus-live-marketdata.md`; `docs/topics/nautilus-live-execution.md`; `docs/topics/live-ops-truth-snapshot.md`; `docs/topics/live-session-order-query-hardening.md` |
| 开发账户状态 | P002 的 live-capable development profile 是 `openctp-paper`；formal broker/trading account profile 是 `formal-trading`，只用于上线前最终证据 | ADR002; OpenCTP runbook; P002 README/phase-plan/acceptance |
| 参考基线 | Nautilus 官方 IB adapter 提供 `InteractiveBrokersInstrumentProvider`、data/execution client 共享 provider、provider initialize/load/dynamic lookup、contract map、cache hydration 和 reports 参照 | `C:/Users/Administrator/anaconda3/Lib/site-packages/nautilus_trader/adapters/interactive_brokers/providers.py`; Nautilus IB docs |
| 验收状态 | Phase 0-5 均已完成；formal-trading final evidence 仍作为独立上线前路径，不阻塞 P002 development closeout | `acceptance.md`; `phase-plan.md`; `change-map.md` |

## Graduation / Closeout Matrix

> 当 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status` 进入 `completed`，且 `reviewed_at >= 2026-05-22` 时，本节由 `python scripts/check_proposal_docs.py --root .` 检查。

若 proposal 产生稳定架构、owner、public entry、reader/writer、gate 或长期语义结论，必须用 `required` 行指向已经回流的 ADR、architecture、ownership、runbook 或等价长期文档。

ADR carrier proposal 还必须在 `phase-plan.md` 和 `acceptance.md` 中完成 Primary ADR 的 Decision Coverage IDs 与后续验收场景映射；ADR carrier acceptance rows are incomplete until mapped.

No stable rule graduation: proposal-local evidence only until closeout determines which provider-readiness rules graduate.

| Graduation item | Policy | Target | Status |
| --- | --- | --- | --- |
| ADR backfill | not_applicable | not_applicable | not_applicable |
| Architecture / ownership backfill | required | `docs/architecture/rust-python-adapter-split.md` or successor provider-readiness architecture doc | completed |
| Operator/runbook backfill | required | `docs/topics/live-session-order-query-hardening.md` and formal smoke runbooks where affected | completed |
| Proposal-local evidence | archive_only | `acceptance.md` | completed |

## 文档地图 / Document Map

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | proposal 概览、评审结论、现实状态快照 | 必需 |
| `phase-plan.md` | phase 状态板、artifact trust boundary、child change 入口 | 必需 |
| `acceptance.md` | proposal 级验收基线和 IB parity 能力矩阵 | 必需 |
| `change-map.md` | proposal phase 到 child change 的映射 | 已启用 |
| `decision-log.md` | proposal 评审判断和 scope freeze 记录 | 已启用 |

## 稳定化规则 / Stabilization Rules

1. 本目录承载的是 proposal，不等于 stable architecture。
2. proposal 中已经收敛为稳定结论的内容，应回写到 `docs/architecture/` 或 `docs/adr/`。
3. 本页顶部 `**状态**` 必须投影自 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status`，不得与 phase-plan 各自独立维护。
4. proposal 的 AI 追踪状态板只回答“这条 proposal 的收敛进度如何”，不替代 `proposal + change` 的正式执行状态源。
5. IB provider parity 是能力参照，不是架构搬运；任何 CTP 实现都必须继续遵守平台中立 runtime 与 thin Python host glue 边界。
6. repo-only acceptance 和 live acceptance 必须分离；live 条件缺失只能产生 typed blocker，不得阻塞 repo-local 可验证工作。
7. `openctp-paper` 是 P002 live-capable development 的默认账号 profile；`formal-trading` 是 final evidence path，两者不得混写成同一个 readiness 结论。
