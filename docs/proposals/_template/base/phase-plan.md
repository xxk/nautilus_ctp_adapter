# <proposal-id> Phase Plan / 分阶段推进计划

**创建日期**：<YYYY-MM-DD>
**最后更新**：<YYYY-MM-DD>
**状态**：draft
**proposal-id**：`<proposal-id>`
**关联提案**：[README.md](README.md)
**关联验收**：[acceptance.md](acceptance.md)

> 本文件 `AI-PHASE-STATUS` 区块是 proposal 级唯一 machine-readable 主状态源；顶部 `**状态**` 与 `README.md` 顶部 `**状态**` 只能作为投影。

---

## Artifact Trust Boundary

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - <正式 artifact root；未冻结时写 "未冻结">
  allowed_evidence_roots:
    - output/debug/proposals/<proposal-id>/
    - output/reports/<proposal-id>/
  source_contract_templates:
    - <允许作为模板来源的 proposal / cfg / contract；无则写 []>
```

规则：

1. formal artifact 只能引用本节声明的 `trusted_artifact_roots`。
2. `allowed_evidence_roots` 只能做 repo-local 诊断留痕，不替代 formal artifact root。
3. 历史 proposal、cfg 或 contract 只能作为 template source，不等于当前 proposal 完成证据。

---

## 执行原则

1. 先冻结输入、身份、artifact boundary 和验收入口，再执行 runtime 或 closeout。
2. 每个 phase 必须有明确 child change 或 proposal-only 交付物，不得只停留在对话记录。
3. 任一 fail-fast 条件命中时，phase 状态必须写为 `blocked` 或 `reframing_required`。
4. 不得引入 fallback / compat / silent downgrade 路径来伪造 proposal 完成。

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

| Phase / 阶段 | Revised Goal / 修订后目标 | Current Status / 当前状态 | AI Progress / AI 完成度 | Evidence / 证据 / 当前事实 | Next Action / 下一步 |
| --- | --- | --- | ---: | --- | --- |
| Phase 0 Proposal convergence / 阶段 0 提案收敛 | <收敛 proposal 文档、边界、phase 拆分与验收缺口> | `planned` | 0% | <当前证据> | <下一步> |

---

## Phase 0: Proposal Convergence

### 目标

<本 phase 想完成什么。>

### 依赖

1. <依赖 1；无则写“无外部依赖”。>

### Child Change

`proposal-only planning` 或 `<YYYYMMDD__domain__change-id>`

### 交付物

1. `docs/proposals/<proposal-id>/README.md`
2. `docs/proposals/<proposal-id>/phase-plan.md`
3. `docs/proposals/<proposal-id>/acceptance.md`

### Runtime / Command Freeze

1. 本 phase 不冻结 runtime command；runtime command 必须在实际执行 phase 中冻结。

### 退出条件

1. proposal 边界、phase 与验收入口已冻结。
2. `python scripts/check_proposal_docs.py --root . --proposal-id <proposal-id>` 通过。

### Fail-fast / Negative Cases

1. proposal 状态投影与 `AI-PHASE-STATUS.overall_status` 不一致。
2. formal artifact root 未冻结却把外部 artifact 当作 closeout evidence。

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

### Runtime / Command Freeze

1. <若需要 runtime，写正式命令冻结要求；若不需要 runtime，写“不适用”。>

### 退出条件

1. <可判定条件 1>
2. <可判定条件 2>

### Fail-fast / Negative Cases

1. <必须拒绝的失败路径 1>
2. <必须拒绝的失败路径 2>

### 验证方式

```bash
<exact command>
```# <proposal-id> Phase Plan / 分阶段推进计划

**创建日期**：<YYYY-MM-DD>
**最后更新**：<YYYY-MM-DD>
**状态**：draft
**proposal-id**：`<proposal-id>`
**关联提案**：[README.md](README.md)
**关联验收**：[acceptance.md](acceptance.md)

> 状态口径：本文件 `AI-PHASE-STATUS` 区块是 proposal 级唯一 machine-readable 主状态源；本页顶部 `**状态**` 与 `README.md` 顶部 `**状态**` 都只能作为投影。

---

## Artifact Trust Boundary

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - <formal artifact root; use "未冻结" when not frozen>
  allowed_evidence_roots:
    - output/debug/change_evidence/<proposal-id>/
    - output/reports/<proposal-id>/
  source_contract_templates:
    - <source proposal / cfg / contract; use [] when not applicable>
```

规则：

1. proposal 全部文档若引用 formal artifact，只能引用本节声明的 `trusted_artifact_roots`。
2. 若尚未冻结唯一 artifact root，不得把 proposal 外部 artifact 写成当前 proposal 的完成证据。
3. `allowed_evidence_roots` 只允许做 repo-local 诊断留痕，不得替代 formal artifact root。
4. 作为模板来源的历史 proposal、cfg 或 contract 不等于当前 proposal 的 pass evidence。
5. 若某个 child change 继承本 proposal 的 artifact boundary，应在 change `plan.md` 再次显式落成自己的 `artifact_boundary`。

---

## 执行原则

1. 先冻结输入、身份、artifact boundary 和验收入口，再执行 runtime 或 closeout。
2. 每个 phase 必须有明确 child change 或 proposal-only 交付物，不得只停留在对话记录。
3. 若依赖历史 proposal 或 artifact，只能把它们写成 template source 或 regression reference，不得写成当前 proposal 完成证据。
4. 任一 fail-fast 条件命中时，phase 状态必须写为 `blocked` 或 `reframing_required`，不得用 warning 或文字解释绕过。
5. 修改 shared runtime、adapter glue、native bridge、schema 或正式入口时，必须同步补 focused tests 或 repo guard evidence。

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

| Phase / 阶段 | Revised Goal / 修订后目标 | Current Status / 当前状态 | AI Progress / AI 完成度 | Evidence / Current Facts / 证据 / 当前事实 | Next Action / 下一步 |
| --- | --- | --- | ---: | --- | --- |
| Phase 0 Proposal convergence / 阶段 0 提案收敛 | <Converge proposal docs, boundaries, phase split, and acceptance gaps> | `planned` | 0% | <Current evidence> | <Next action> |

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

### Runtime / Command Freeze

若本 phase 不运行 runtime，写：

1. 本 phase 不冻结 runtime command；runtime command 必须在实际执行 phase 中冻结。

若本 phase 需要运行 runtime，必须写清：

1. command 可在当前仓库复跑，且入口自检或 `--help` 通过。
2. command 显式绑定当前 proposal 的 artifact root 或目标 surface。
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
6. residual risk、non-goals 与 follow-up 已回填到 proposal、phase-plan 或 child change。

---

## 状态词典

| 状态 | 含义 |
| --- | --- |
| `planned` | 已定义，尚未开始 |
| `in_progress` | 正在推进 |
| `blocked` | 命中真实阻塞 |
| `completed` | 已满足退出条件并留下证据 |
| `reframing_required` | proposal 方向仍有效，但 owner / scope / interface 需要先修订 |