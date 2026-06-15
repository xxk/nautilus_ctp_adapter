# Proposal Acceptance Template / 提案验收模板

**创建日期**：YYYY-MM-DD
**状态**：初版（Preliminary Baseline）
**所属 proposal**：[README.md](README.md)
**关联执行计划**：[phase-plan.md](phase-plan.md)

---

## 一句话结论

本文件定义 proposal 级验收口径，用于回答“当前 proposal 按现有执行范围是否已经完成初步验收”；若后续需要更严格或跨仓验收，应另开 `acceptance_stricter.md`。

> Artifact Root Rule / Artifact 根规则：本文件引用的 formal artifact、projection、report、verdict 必须属于 sibling `phase-plan.md` 中声明的 `Artifact Trust Boundary`。未冻结唯一受信根前，只允许记录“待冻结”或 repo-local 诊断留痕，不得把 proposal 外部 artifact 写成当前 proposal 的完成证据。

---

## 0. 当前验收状态

### 状态词典

| 状态 | 含义 |
| --- | --- |
| `not_run` | 尚未执行，也没有可复用的正式证据 |
| `documented_pass` | 已有 change / phase / issue closeout evidence 支撑通过，但本文件未额外重跑更严格链路 |
| `passed` | 已按本文件列出的命令完成复核并通过 |
| `failed` | 已知未通过 |

### Proposal 状态板

<!-- PROPOSAL-ACCEPTANCE-STATUS-BEGIN
reviewed_at: YYYY-MM-DD
reviewer: Codex
overall_status: not_run
stricter_acceptance_status: not_run
scenarios:
  - id: A1
    status: not_run
    evidence_source: ""
  - id: A2
    status: not_run
    evidence_source: ""
  - id: A3
    status: not_run
    evidence_source: ""
PROPOSAL-ACCEPTANCE-STATUS-END -->

## 1. 验收边界

当前 proposal 只验收以下内容：

1. <当前 proposal 的 in-scope 执行目标 1>
2. <当前 proposal 的 in-scope 执行目标 2>
3. <当前 proposal 的 in-scope 执行目标 3>

当前 proposal 不验收以下内容：

1. <明确 out-of-scope 1>
2. <明确 out-of-scope 2>
3. <明确 out-of-scope 3>

---

## 2. 验收场景

| ID | 当前状态 | 场景 | 验证命令 | 通过信号 | 当前证据来源 |
| --- | --- | --- | --- | --- | --- |
| A1 | `not_run` | <场景 1> | `<command>` | <通过信号> | <证据来源或留空> |
| A2 | `not_run` | <场景 2> | `<command>` | <通过信号> | <证据来源或留空> |
| A3 | `not_run` | <场景 3> | `<command>` | <通过信号> | <证据来源或留空> |

---

## 3. 详细验收场景（Scenario Cards）

> 本节是给人工 review 和后续 AI 施工看的主验收面。每个 proposal 至少保留 3 类场景：正向完成、负向拒绝、出口不干净回归。不要只写“运行测试通过”。

### A1. <正向完成场景名称>

**目的**：证明 proposal 的核心 happy path 已按当前 contract 完成，而不是只靠文档声称完成。

**前置数据 / 输入**：

1. <输入 artifact / fixture / command input 1>
2. <输入 artifact / fixture / command input 2>

**执行步骤**：

1. 运行 `<command>`。
2. 打开或读取 `<output path>`。
3. 核对 `<field / section / artifact>`。

**通过信号**：

1. <机器可读通过信号 1>
2. <人工可见通过信号 2>
3. <证据路径或日志片段>

**失败 / 拒绝信号**：

1. <缺字段 / 缺 artifact / 错误状态>
2. <不应出现的 fallback / 旧字段 / 弱证据>

**证据落点**：

```text
<docs/changes/.../acceptance.md evidence section>
<output/... artifact path, if applicable>
```

补充要求：若这里填的是正式 artifact 路径，而不是 repo-local debug 输出，该路径必须位于 `phase-plan.md` 声明的 `trusted_artifact_roots` 内。

### A2. <负向拒绝场景名称>

**目的**：证明 proposal 不会在缺关键证据、旧字段、错误 owner 或错误状态下误判通过。

**前置数据 / 输入**：

1. <故意缺失或错误的输入>
2. <旧字段 / retired field / invalid state>

**执行步骤**：

1. 运行 `<command>`。
2. 读取 `<error / gap / projection path>`。

**通过信号**：

1. 输出明确 fail-fast error 或 machine-readable gap。
2. 不生成 clean public output。
3. 不写入 formal truth / verdict / gate passed。

**失败 / 拒绝信号**：

1. 缺证据仍通过。
2. 使用 fallback / compat / old field 继续生成 clean output。
3. 只在 UI 文案里提示缺口，但机器状态仍是 pass。

**证据落点**：

```text
<negative test path>
<docs/changes/.../acceptance.md evidence section>
```

### A3. <出口不干净回归场景名称>

**目的**：证明 proposal 完成后，旧语义不会从 public artifact、HTML、template、docs、CLI help、error hint 或 tests fixture 回流。

**前置数据 / 输入**：

1. <retired terms / fields list>
2. <需要 grep 的目录或 surface>

**执行步骤**：

1. 运行代码 / 文档 grep。
2. 对每个命中分类：`active_contract`、`retired_historical`、`diagnostic_bridge`、`test_negative_case`、`false_positive`。
3. 修正不允许的 `active_contract` 命中。

**通过信号**：

1. 新写出的 public JSON 不含 retired field。
2. rendered HTML 不含 retired label，或明确标记 historical / diagnostic。
3. docs / templates 不把 retired field 写成当前推荐路径。
4. tests 不 assert retired field 是 clean expected output。

**失败 / 拒绝信号**：

1. grep 命中未分类。
2. active docs / active tests / current surface 仍要求旧字段。
3. closeout 没有记录 residual legacy boundary。

**建议命令**：

```powershell
Get-ChildItem -Recurse -File docs,dslresearch,tests -Include *.md,*.py,*.j2 |
  Select-String -Pattern '<retired-term-1>|<retired-term-2>|<retired-term-3>' |
  ForEach-Object { "{0}:{1}:{2}" -f $_.Path,$_.LineNumber,$_.Line.Trim() }
```

**证据落点**：

```text
<docs/changes/.../acceptance.md grep classification>
```

---

## 4. Clean Exit Checklist

Proposal closeout 前必须逐项回答：

1. 每个 in-scope 目标是否至少有一个正向验收场景？
2. 每个 P0 / P1 风险是否至少有一个负向拒绝场景？
3. 是否有出口不干净回归场景，覆盖 docs / code / tests / surface / CLI 或相关出口？
4. 是否记录了命令、输出、证据路径，而不是只写“已验证”？
5. 是否明确 out-of-scope，不把未验收能力写成已完成？
6. 若存在历史语义残留，是否标记为 `retired_historical`、`legacy_loader_only` 或 `diagnostic_bridge`？
7. 是否同步更新 `phase-plan.md` 的 AI-PHASE-STATUS？
8. 是否确认所有 formal artifact 引用都位于 proposal 已声明的受信 artifact roots 内？
