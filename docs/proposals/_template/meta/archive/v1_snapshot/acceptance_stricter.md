# Proposal Stricter Acceptance Template / 提案更严格验收模板

**创建日期**：YYYY-MM-DD
**状态**：初版，已定义更严格验收场景但尚未执行（Stricter Acceptance Designed, Not Yet Run）
**所属 proposal**：[README.md](README.md)
**关联初步验收**：[acceptance.md](acceptance.md)
**关联执行计划**：[phase-plan.md](phase-plan.md)

---

## 一句话结论

本文件承接 proposal 级更严格验收，用来验证当前 proposal 是否已经具备更长链路、更多真实运行约束或更强 owner 边界要求下的通过证据。

> Artifact Root Rule / Artifact 根规则：更严格验收引用的真实 artifact、projection、report、verdict 路径，必须全部落在 sibling `phase-plan.md` 的 `Artifact Trust Boundary` 受信根内；若只能拿到 proposal 外部 artifact，本文件结论最多写为 blocker / gap，不得写 pass。

---

## 0. 当前验收状态

### 状态词典

| 状态 | 含义 |
| --- | --- |
| `not_run` | 尚未执行，也没有正式重跑记录 |
| `passed` | 已按本文件列出的命令重跑并通过 |
| `failed` | 已重跑但存在失败场景 |

### Proposal Stricter 状态板

<!-- PROPOSAL-STRICTER-ACCEPTANCE-STATUS-BEGIN
reviewed_at: YYYY-MM-DD
reviewer: Codex
overall_status: not_run
scenarios:
  - id: S1
    status: not_run
    evidence_source: ""
  - id: S2
    status: not_run
    evidence_source: ""
  - id: S3
    status: not_run
    evidence_source: ""
PROPOSAL-STRICTER-ACCEPTANCE-STATUS-END -->

## 1. 验收边界

本文件只验收以下内容：

1. <更严格链路目标 1>
2. <更严格链路目标 2>
3. <更严格链路目标 3>

本文件不验收以下内容：

1. <仍未正式落地的 owner / bridge lane>
2. <跨仓未来能力>
3. <超出当前 proposal 执行范围的事项>

---

## 2. 正式验收设计

| ID | 当前状态 | 场景 | 正式验收命令 | 通过信号 | 当前证据来源 |
| --- | --- | --- | --- | --- | --- |
| S1 | `not_run` | <场景 1> | `<real runtime command>` | <通过信号> | <证据来源或留空> |
| S2 | `not_run` | <场景 2> | `<real runtime command>` | <通过信号> | <证据来源或留空> |
| S3 | `not_run` | <场景 3> | `<real runtime command>` | <通过信号> | <证据来源或留空> |

---

## 3. 更严格验收场景（Stricter Scenario Cards）

> 本节用于长链路、真实 runtime、跨仓、或更强 owner 边界验收。每个场景必须说明真实输入、真实命令、通过信号、拒绝信号、证据落点。

### S1. <真实链路正向场景名称>

**目的**：证明 proposal 在真实或接近真实的正式入口下通过，而不是只通过 unit fixture。

**真实输入 / 环境**：

1. <真实 input package / artifact root / external repo ref；若为 artifact root，必须属于 phase-plan.md 已声明受信根>
2. <必要环境变量或本地资源>

**正式命令**：

```bash
<real runtime command>
```

**通过信号**：

1. <formal artifact / projection / report path exists>
2. <schema / gate / verdict / status field>
3. <human-readable surface signal, if relevant>

**拒绝信号**：

1. <缺 owner evidence 却通过>
2. <跨仓 contract 不一致却通过>
3. <旧字段 / fallback / compat 分支被使用>

**证据落点**：

```text
<docs/changes/.../acceptance.md evidence section>
<output/... artifact path>
```

补充要求：若证据落点指向正式 artifact，其路径必须位于 proposal 的受信 artifact roots；否则该场景应判为拒绝通过，而不是“先临时复用”。

### S2. <真实链路负向场景名称>

**目的**：证明真实入口在缺关键 artifact、错误 schema、错误 owner 或过期语义下会拒绝。

**故障注入 / 输入变体**：

1. <missing artifact / invalid schema / stale owner ref>
2. <retired field only / wrong role / weak URI evidence>

**正式命令**：

```bash
<real runtime command expected to fail or produce gap>
```

**通过信号**：

1. 命令 fail-fast，或生成 machine-readable blocker gap。
2. 不写 pass verdict。
3. 不生成 clean current-facing surface。

**失败信号**：

1. 缺关键 evidence 仍通过。
2. 使用 fallback /旧字段继续生成 current output。
3. 只在日志里 warning，但 formal status 是 pass。

**证据落点**：

```text
<negative evidence path>
```

### S3. <跨出口一致性场景名称>

**目的**：证明 code、docs、tests、UI、CLI、external verifier input 等出口对同一 contract 的语义一致。

**检查出口**：

1. <code owner>
2. <tests / fixtures>
3. <docs / runbooks>
4. <surface / rendered HTML>
5. <external manifest / verifier input>

**正式命令**：

```bash
<docs/code/surface verification commands>
```

**通过信号**：

1. 所有出口使用同一 current contract 字段。
2. historical / retired references 被明确隔离。
3. no active output uses retired field as current truth。

**失败信号**：

1. 任一出口仍把 retired field 当 current contract。
2. 任一出口存在未分类 grep 命中。
3. 任一出口使用 fallback / compat 文案或代码。

---

## 4. Stricter Clean Exit Checklist

1. 是否覆盖真实 runtime 正向场景？
2. 是否覆盖真实 runtime 负向拒绝场景？
3. 是否覆盖跨出口一致性场景？
4. 是否记录真实命令和输出路径？
5. 是否明确说明未跑的场景和原因？
6. 是否把 residual risk 回填到 proposal / phase-plan / follow-up child change？
