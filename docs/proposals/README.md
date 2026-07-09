# Proposal Index / 提案目录索引

**创建日期**：2026-05-26
**最后更新**：2026-06-08
**状态**：生效

---

## 分类导航索引 / Classified Navigation Index

> 本索引置于顶部供第一屏命中；完整策略说明见下方各节。

### Active / Current Proposals

| Proposal | 目录 | 状态 | 说明 |
| --- | --- | --- | --- |
| p001 | [p001-ADR001-native-first-runtime-rollout](./p001-ADR001-native-first-runtime-rollout/) | completed | ADR001 rollout carrier；Phase 1-4 boundary child changes 已完成，不扩张当前 vendor-bridge active change |
| p002 | [p002-nautilus-provider-production-readiness](./p002-nautilus-provider-production-readiness/) | completed | CTP provider paper/repo development baseline；以 IB provider parity 为能力参照，补齐 Nautilus provider/cache/data/execution/report/live-capable evidence |
| p003 | [p003-ctp-live-trading-provider-readiness](./p003-ctp-live-trading-provider-readiness/) | completed | CTP OpenCTP TTS 7x24 simulation paper-first capability readiness；session truth、read-only snapshot、guarded paper order loop、recovery/idempotency 与 ops closeout 已完成，暂不推进 Live |
| p004 | [p004-openctp-tts-simulation-provider-completeness](./p004-openctp-tts-simulation-provider-completeness/) | completed | P003 successor；已补齐 OpenCTP TTS 7x24 simulation provider 的撤单、平仓、post-order 对账、订单类型、风控、controlled reconnect evidence 与 Nautilus engine harness |

---

## 一句话结论

`docs/proposals/` 用于承载**很多步骤、需要多 phase 持续推进**的任务容器；当一条方案已经不是单个 child change 能说清，而要拆成多个 phase / 多个 child change 连续推进时，默认优先建立 proposal canonical path。

它不替代 `docs/architecture/`，而是把“仍在推进中的正式方案”从“已经接受的稳定架构结论”里分离出来。

它也不是第三种独立执行模式；只有当 proposal 与 child change 配对时，才形成正式执行面 `proposal + change`。

当 proposal 已完成且代码/规则趋于稳定时，proposal 的默认退役路径不是删除目录，而是 `closeout -> graduation -> optional archive`。

Topic 不作为 proposal 推进容器。`topic-id` 只允许作为 child change `plan.md` frontmatter 标签和 `python scripts/show_current_frontier.py --by-topic` 的分组维度。

---

## 适用场景

下列内容应优先放在 `docs/proposals/`：

1. 一项任务明显有很多步骤，需要按多个 phase 持续推进，而不是单个 change 一次闭环。
2. 一份方案需要多个 child change 分阶段落地，并且 phase 之间存在顺序或依赖关系。
3. 文档本身仍在评审、收敛、拆 phase，而不是稳定结论。
4. 需要把 proposal 主文档、phase 状态、child change 映射与决策日志放在同一个目录内维护。
5. 需要保留 proposal canonical path，但不希望继续把它混在 `docs/architecture/` 里。

## 不适用场景

下列内容不应放在 `docs/proposals/`：

1. 已接受、当前生效且应长期稳定维护的架构结论。
2. 回答“为什么选这个方案”的 ADR。
3. 单次执行单元的计划、验收与证据；这类内容仍应放到 `docs/changes/`。
4. 步骤不多、单个 child change 就能完整说清并闭环的任务。
5. 只做历史回溯、不再推进的冷归档内容。

---

## 与其他目录的边界

1. `docs/architecture/`
   - 存放稳定长期架构结论。
   - 重点回答“当前正式口径是什么”。
2. `docs/proposals/`
   - 存放待推进或待收敛的正式提案。
   - 重点回答“这条方案如何拆 phase、如何映射 change、当前还在评审什么”。
3. `docs/changes/`
   - 存放单次可执行 child change。
   - 重点回答“本次改什么、验收什么、证据在哪里”。
4. `docs/adr/`
   - 存放架构决策记录。
   - 重点回答“为什么接受这个方向，以及哪些稳定决策必须被后续 proposal / change 覆盖”。
5. `docs/topics/`
   - 只保留 legacy roadmap 与 `--by-topic` grouped projection。
   - 不替代 proposal phase plan，不作为 proposal 推进容器，也不选择默认 executable frontier。

---

## 模板入口 / Template Entry

优先使用本仓 proposal scaffold：

```powershell
python scripts/new_proposal.py --root . --id <proposal-id> --profile multi_phase
```

校验 proposal 文档闭环：

```powershell
python scripts/check_proposal_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id <proposal-id>
```

模板结构位于 `docs/proposals/_template/`：

1. `base/`：每个 proposal 必需文件。
2. `fragments/`：可选附加片段。
3. `profiles/`：常见片段组合。
4. `meta/`：模板使用说明与 fragment registry。

---

## 规则 / Rules

1. proposal 顶部 `**状态**` 只能投影自 `phase-plan.md` 里的 `AI-PHASE-STATUS.overall_status`。
2. 若 proposal 已产生稳定架构、owner 或 runtime 规则，必须回流到 `docs/adr/`、`docs/architecture/` 或等价长期文档。
3. proposal 验收必须落在 `acceptance.md`，不能只停留在聊天或 issue 备注。
4. proposal 允许承接多个 child change；proposal 完成只由 proposal `phase-plan.md` 与 `acceptance.md` 判断，不等待 topic closeout，也不得由 topic queue 推进。
5. proposal phase 状态、artifact boundary、change map、decision log 与 acceptance evidence 必须位于同一个 proposal canonical path 或其明确声明的受信 artifact roots。
6. 任何需要 CTP 外部账号或 live front 的 proposal 必须显式声明 `ctp_account_profile`，取值只能是 `openctp-tts-7x24-simulation`、`formal-trading` 或 `repo-only`。未声明 profile 时，proposal 只能使用 repo-only/mock/dry-run 证据。
7. `openctp-tts-7x24-simulation` 只能形成 simulation evidence，不得关闭 formal broker/trading acceptance；`openctp-paper` 只允许作为历史 alias 出现在兼容说明或旧证据引用中；`formal-trading` 只能在 proposal/change 明确要求正式交易账号证据时使用。
8. CTP 账号 profile 的具体 runbook authority 是 `docs/changes/20260607__openctp-tts__test-baseline/runbook.md`；proposal 只引用 profile 和 config path，不复制 secret。

