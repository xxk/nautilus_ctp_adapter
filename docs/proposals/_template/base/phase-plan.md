# <proposal-id> Phase Plan / 分阶段推进计划

**创建日期**：<YYYY-MM-DD>
**最后更新**：<YYYY-MM-DD>
**状态**：draft
**proposal-id**：`<proposal-id>`
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
    - <正式 artifact root；未冻结时写 "未冻结">
  allowed_evidence_roots:
    - output/debug/change_evidence/<proposal-id>/
    - output/reports/<proposal-id>/
  source_issue_lists:
    - <持续曳光弹 / tracer proposal 的来源 issue list；无则写 []>
  source_input_templates:
    - <允许作为模板来源的 input；无则写 []>
  source_contract_templates:
    - <允许作为模板来源的 proposal / cfg / contract；无则写 []>
  ctp_account_profile: repo-only | openctp-paper | formal-trading | not_applicable
  ctp_config_path: <cfgs/local/... or not_applicable>
  ctp_evidence_class: repo-only | paper-simulation | formal-broker | not_applicable
```

规则：

1. proposal 全部文档若引用 formal artifact，只能引用本节声明的 `trusted_artifact_roots`。
2. 若尚未冻结唯一 artifact root，不得把 proposal 外部 artifact 写成当前 proposal 的完成证据。
3. `allowed_evidence_roots` 只允许做 repo-local 诊断留痕，不得替代 formal artifact root。
4. 作为模板来源的历史 proposal、input、cfg 或 contract 不等于当前 proposal 的 pass evidence。
5. 若某个 child change 继承本 proposal 的 artifact boundary，应在 change `plan.md` 再次显式落成自己的 `artifact_boundary`。
6. `source_issue_lists` 只表示“来源问题账本”或“下一枚曳光弹的验收输入”，不等于当前 proposal 已完成；每条 issue 仍需映射到当前 acceptance 或下一枚 tracer 的 carry-forward contract。
7. 若 `ctp_account_profile=openctp-paper`，证据只能作为 paper simulation；若 `ctp_account_profile=formal-trading`，证据只能来自正式交易账号 local config；若未声明 profile，不得引用外部 CTP live front 证据。

---

## 执行原则

1. 先冻结输入、身份、artifact boundary 和验收入口，再执行 runtime 或 closeout。
2. 每个 phase 必须有明确 child change 或 proposal-only 交付物，不得只停留在对话记录。
3. 若依赖历史 proposal / tracer / artifact，只能把它们写成 template source 或 regression reference，不得写成当前 proposal 完成证据。
4. 任一 fail-fast 条件命中时，phase 状态必须写为 `blocked` 或 `reframing_required`，不得用 warning 或文字解释绕过。
5. 修改 UI surface、report context 或 HTML 模板时，必须同步补 CONTRACT-LOCK 测试。
6. 修改 shared module、gateway、orchestration、validation plan 或 cross-tracer 能力时，必须从 registry 推导 affected capability/tracer 并执行对应 gate。
7. 若 proposal 属于持续曳光弹 / tracer / cross-tracer 研发，执行期间必须持续回填 `issue-list.md`，把“本轮已修复”“本轮仍打开”“必须在下一枚 tracer 验收”的问题分开记账。
8. proposal-specific naming、writer path、owner shortcut 或临时 schema 不得直接毕业为 stable runtime truth；若确认可复用，必须通过 child change 显式收敛到 canonical owner，并把 proposal id 只保留在 artifact identity 或文档 traceability 边界。
9. 需要 CTP 外部账号时，先声明 `ctp_account_profile`，再运行任何 live smoke；不得把 OpenCTP paper evidence 用作 formal broker/trading readiness。

---

## ADR Decision Coverage Mapping

> 仅当 README 顶部状态块 `ADR carrier` 为 `yes` 时必填；否则写 `not_applicable` 并说明本 proposal 不承载 ADR 落地。

Primary ADR: `<ADR-00xx or not_applicable>`
Covered decisions: `<D1, D2, ... or not_applicable>`

ADR-carrier proposal 必须把 Primary ADR 的 Decision Coverage IDs 映射到 phase / child change / 验收行；不能只写 ADR 链接。

| ADR decision item | ADR section / successor scenario | Phase | Child change or proposal-only work | Acceptance row |
| --- | --- | --- | --- | --- |
| D1 | <ADR Section 6.2 successor scenario or section anchor> | <Phase N> | <change id or proposal-only> | <A-ADR-1> |

---

## Blocker Handling Discipline

1. `code/contract blocker`: if the blocker is repo-local implementation, test, docs-gate, schema, writer path, or contract-lock work, keep working and fix it in the current proposal slice; do not stop at a blocker note.
2. `data blocker`: if the blocker is missing artifact, catalog, verifier output, or generated evidence, first try the official owner/runner/import path and record the command plus result. If the data cannot be generated inside the current authority boundary, materialize typed `blocked` evidence with `next_action`.
3. `governance blocker`: if the blocker requires an external owner, real approval, production authority, or human approval, never fabricate pass evidence. Implement the typed waiting/blocked state, fail-fast guard, acceptance row, and carry-forward entry.
4. `unknown blocker`: reduce it to the smallest test, inventory artifact, or reproducible command result, classify it as code/contract blocker, data blocker, or governance blocker, then apply the matching rule.
5. A proposal may close as `blocked` only when all repo-local repairable work has been attempted and the remaining blocker depends on external owner, real data, or human approval.

---

## AI 跟踪状态（AI Tracking Status）

<!-- AI-PHASE-STATUS-BEGIN
reviewed_at: <YYYY-MM-DD>
reviewer: <agent-or-human>
overall_status: draft
phases:
  - id: phase_0_proposal_convergence
    status: planned
    ai_progress: 0
    evidence: "<proposal docs not yet verified>"
AI-PHASE-STATUS-END -->

---

## Phase 状态表（Phase Status Board）

| Phase / 阶段 | 目标 / Goal | Current Status / 当前状态 | AI Progress / AI 完成度 | Evidence / Current Facts / 证据 / 当前事实 | 下一动作 / Next Action |
| --- | --- | --- | ---: | --- | --- |
| Phase 0 Proposal convergence / 阶段 0 提案收敛 | <收敛 proposal 文档、边界、phase 拆分与验收缺口 / Converge proposal docs, boundaries, phase split, and acceptance gaps> | `planned` | 0% | <Current evidence / 当前证据> | <下一动作 / Next action> |

---

## Continuous Advancement Rule / 持续推进规则

Phase 0 `completed` 只表示 proposal 文档、边界、phase split 与验收缺口已经收敛，不表示后续 phase 已完成。若 `Next Action` 指向本地可完成的 child change 创建、proposal 映射回填、ADR landing map 回填或 runbook 索引同步，AI 必须继续执行该动作，或在 `acceptance.md` 写入 typed blocker；不得把 `Next Action` 本身当成完成证据。

通用执行口径见 `docs/runbooks/Proposal_ADR_Runbook连续推进手册_Proposal ADR Runbook Continuous Advancement Runbook.md`。

---

## Phase 0: Proposal Convergence

### 目标

<本 phase 想完成什么；说明它为什么是正式执行前的必要收敛。>

### 依赖

1. <依赖 1；无则写“无外部依赖”。>
2. <依赖 2。>

### Child Change

`proposal-only planning` 或 `<YYYYMMDD__domain__change-id>`

### 交付物

1. `docs/proposals/<proposal-id>/README.md`
2. `docs/proposals/<proposal-id>/phase-plan.md`
3. `docs/proposals/<proposal-id>/acceptance.md`
4. <其他 fragment 或设计文件>
5. 若是 tracer / cross-tracer proposal：`docs/proposals/<proposal-id>/issue-list.md`

### Runtime / Command Freeze

若本 phase 不运行 runtime，写：

1. 本 phase 不冻结 runtime command；runtime command 必须在实际执行 phase 中冻结。

若本 phase 需要运行 runtime，必须写清：

1. command 可在当前仓库复跑，且入口自检或 `--help` 通过。
2. command 显式绑定当前 proposal 的 case identity 与 artifact root。
3. command 输出的 summary / manifest / report 路径。
4. command 的失败判定和不可降级项。

### 退出条件

1. <条件 1>
2. <条件 2>

### Fail-fast / Negative Cases

1. <失败条件 1；命中时必须 blocked / failed。>
2. <失败条件 2。>

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id <proposal-id>
```

---

## Phase N: <Phase Name>

### 目标

<本 phase 的具体目标。>

### 依赖

1. <前置 phase 或外部能力。>

### Child Change

`<YYYYMMDD__domain__change-id>`

### 交付物

1. `<exact/path/to/file-or-artifact>`
2. `<exact/path/to/test-or-contract>`

### Runtime / Command Freeze

1. <若需要 runtime，写正式命令冻结要求。>
2. <若不需要 runtime，明确写“不适用”。>

### 退出条件

1. <可判定条件 1>
2. <可判定条件 2>

### Fail-fast / Negative Cases

1. <必须拒绝的失败路径 1>
2. <必须拒绝的失败路径 2>

### 验证方式

```bash
<exact command>
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
8. 若 proposal 属于持续曳光弹 / tracer / cross-tracer 研发，`issue-list.md` 已回填：每条遗留问题都有当前状态、acceptance 映射，以及是否 carry-forward 到下一枚 tracer 的明确口径。
9. `README.md` 的 `Graduation / Closeout Matrix` 已声明稳定结论回流或 `archive_only` 收口；所有 `required` target 均存在，且 status 为 `verified`、`passed` 或 `completed`。
10. proposal-specific 命名、writer、owner path 或 schema 若被证明应长期保留，已在 canonical owner / ADR / architecture 中去 proposal 化；若仍保留 proposal 语义，只能留在 evidence、fixture 或 artifact traceability 边界。

---

## 状态词典

| 状态 | 含义 |
| --- | --- |
| `planned` | 已定义，尚未开始 |
| `in_progress` | 正在推进 |
| `blocked` | 命中真实阻塞 |
| `completed` | 已满足退出条件并留下证据 |
| `reframing_required` | proposal 方向仍有效，但 owner / scope / interface 需要先修订 |
