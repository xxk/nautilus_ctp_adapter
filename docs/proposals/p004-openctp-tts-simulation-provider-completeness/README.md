# OpenCTP TTS Simulation Provider Completeness

<!-- PROPOSAL-ANTI-DRIFT-GATE:v1 -->
<!-- PROPOSAL-SCAFFOLD: profile=multi_phase; fragments=change_map,decision_log -->
<!-- PROPOSAL-ADR-CARRIER-GATE:v1 -->

**proposal-id**：`p004-openctp-tts-simulation-provider-completeness`
**状态**：completed
**范围**：在 P003 已完成的 OpenCTP TTS 7x24 模拟账户 API 调试闭环上，继续补齐 CTP simulation trading provider 的撤单、平仓、对账、风控、重连和 Nautilus engine 级验收能力。

| 顶部状态块 / Top Status Block | 值 |
| --- | --- |
| ADR carrier | no |
| Primary ADR | not_applicable |
| Carrier naming note | successor of P003 paper-first provider readiness |
| Tracer input case dir | not_applicable |
| Tracer case id | not_applicable |
| Tracer case ref | not_applicable |
| Work item type | delivery |
| Work item layer | proposal |
| Surface mode | console |
| Action mode | execution_capable |
| CTP account profile | openctp-tts-7x24-simulation |
| CTP config path | cfgs/local/ctp.openctp.tts.7x24.local.json |
| CTP evidence class | openctp-tts-7x24-simulation |

> 状态口径：本页顶部 `**状态**` 只是 human-readable projection；proposal 级唯一 machine-readable 主状态源是 `phase-plan.md` 中 `AI-PHASE-STATUS` 区块的 `overall_status`。
>
> Topic 边界：topic 不作为 proposal 推进容器；`topic-id` 只允许作为 child change `plan.md` frontmatter 标签和 `--by-topic` 分组维度。
>
> Workflow 边界：`docs/workflows/` 只定义 reusable fragments / gate specs；本 proposal 的 phase、queue、acceptance 和 evidence 仍由本目录与 child changes 承载。

---

## 一句话结论

P003 已证明 OpenCTP TTS 7x24 模拟账户可以用于 24 小时 API 调试、查询、行情和受保护下单；P004 继续把它推进为更完整的 simulation trading provider 验收面。

P004 不恢复 formal-trading，也不把模拟账户证据用作正式 broker readiness。

## 目标 / Goals

1. 补齐模拟账户上的撤单、平仓、订单类型、风控前置和 post-order reconciliation。
2. 补齐真实模拟环境下的 MD/TD 重连、重订阅、历史回报 residue 隔离和幂等 evidence。
3. 补齐 Nautilus engine harness：通过 Nautilus command 触发 CTP provider 行为，并收到可复核的 order、fill、account、position report。
4. 固化 OpenCTP TTS 7x24 simulation 账户类型、runbook、evidence root 和安全边界。

## 非目标 / Non-Goals

1. 不使用 `formal-trading`，不推进正式 broker / 实盘交易账号 readiness。
2. 不开发自动策略、无人值守交易、组合交易或跨品种策略风控。
3. 不把账号、密码、auth code、broker private field 或未脱敏 front 信息写入仓库。
4. 不以 mock、unit test 或 dry-run 单独关闭需要模拟账户实证的 acceptance row。

## 评审结论 / Review Verdict

**当前结论**：completed

| 项 | 结论 |
| --- | --- |
| 是否进入正式 proposal | 是，作为 P003 successor proposal |
| 是否需要 child change | 是，按撤单、平仓/订单类型、对账/风控、重连和 engine harness 分阶段推进 |
| 是否有 artifact trust boundary | 见 `phase-plan.md` |

## 当前状态快照 / Reality Snapshot

以下状态以本地代码、测试、已完成 changes 与相关文档为准，而不是只按 proposal 正文判断：

| 维度 | 当前事实 | 证据 |
| --- | --- | --- |
| P003 状态 | P003 completed，已具备 OpenCTP TTS 7x24 simulation API 调试和 guarded order loop 基线 | `docs/proposals/p003-ctp-live-trading-provider-readiness/` |
| 模拟下单证据 | `zn2610 BUY 2` 已成交；`c2609 SELL OPEN 3` 已提交并被分类为 rejected | `docs/changes/20260608__ctp-paper-provider-readiness__guarded-paper-order-loop/` |
| 当前缺口 | 无当前 P004 缺口；real reconnect row 已用 process-scoped controlled front proxy evidence 关闭 | `docs/changes/20260608__openctp-tts-simulation-provider__real-reconnect-evidence/` |
| 文档状态 | P004 child changes 已执行；proposal closeout 投影为 completed | 本目录 |
| 验收状态 | P004 acceptance rows 均已通过或作为历史 typed evidence 留档 | `acceptance.md` |

## Graduation / Closeout Matrix

> 当 `phase-plan.md` 的 `AI-PHASE-STATUS.overall_status` 进入 `completed`，且 `reviewed_at >= 2026-05-22` 时，本节由 `python scripts/check_proposal_docs.py --root .` 检查。

P004 已产生长期 provider runbook、simulation account safety boundary、controlled reconnect harness 和 Nautilus provider harness 入口；real reconnect evidence 通过 process-scoped controlled front proxy 关闭。

| Graduation item | Policy | Target | Status |
| --- | --- | --- | --- |
| ADR backfill | required | docs/adr/ADR002 OpenCTP TTS Paper Simulation Test Environment.md | completed |
| Architecture / ownership backfill | required | docs/architecture/openctp-tts-simulation-provider-completeness.md | completed |
| Runbook backfill | required | docs/changes/20260607__openctp-tts__test-baseline/runbook.md | completed |
| Proposal-local evidence | archive_only | acceptance.md | completed |

## 文档地图 / Document Map

| 文件 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | proposal 概览、评审结论、现实状态快照 | 必需 |
| `phase-plan.md` | phase 状态板与 artifact trust boundary | 必需 |
| `acceptance.md` | proposal 级验收基线和场景矩阵 | 必需 |
| `change-map.md` | proposal phase 到 child change 的映射 | 必需 |
| `decision-log.md` | 影响后续执行边界的决策记录 | 必需 |

## 稳定化规则 / Stabilization Rules

1. P004 只承载 OpenCTP TTS 7x24 simulation provider completeness，不等于 formal trading readiness。
2. 模拟账户证据必须使用 `ctp_account_profile=openctp-tts-7x24-simulation` 和 `ctp_evidence_class=openctp-tts-7x24-simulation`。
3. 所有模拟下单必须保留 explicit arm、instrument allowlist、qty cap、kill switch 和 redaction。
4. 若 P004 产生稳定 provider 入口、runbook 或 safety rule，closeout 前必须回写到长期文档。
