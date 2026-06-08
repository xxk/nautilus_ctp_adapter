# Acceptance / 验收基线

**proposal-id**：`<proposal-id>`
**状态**：draft

---

## 验收范围 / Scope

当前 proposal 验收以下内容：

1. <in-scope 目标 1>
2. <in-scope 目标 2>

当前 proposal 不验收以下内容：

1. <out-of-scope 事项 1>
2. <out-of-scope 事项 2>

---

## Artifact Root Rule

本文件引用的 formal artifact、projection、report、verdict 必须属于 sibling `phase-plan.md` 中声明的 `Artifact Trust Boundary`。

未冻结唯一受信根前，只允许记录“待冻结”或 repo-local 诊断留痕，不得把 proposal 外部 artifact 写成当前 proposal 的完成证据。

---

## Acceptance Evidence Boundary

1. `pytest`、`unittest`、`dotnet test`、mock、stub、monkeypatch 或其他 test-only 输出，只能作为 contract/function guard evidence，不得单独充当 proposal 正式验收证据。
2. proposal 验收场景若要写成 `passed`、`completed` 或等价完成结论，至少还需要一类非 test-only 证据：真实命令执行结果、受信 formal artifact、projection/read-model 结果、live/rendered surface 证据，或可复核的 source evidence。
3. 若当前只有 test/mock 结果，而没有真实入口、真实 artifact 或真实 consumer 证据，只能记录为 guard/reference，不得把该 proposal 场景写成正式收口完成。
4. A repo-local repairable blocker must not be used as a reason to stop; it needs a repair attempt, focused gate result, and updated acceptance evidence.
5. A blocker that depends on an external owner, real data, or human approval must not be faked; it must produce typed waiting/blocked evidence, blockers, next_action, and carry-forward mapping.
6. A proposal closeout may remain `blocked` only after code/contract blockers have been handled and the remaining blocker is outside the current authority boundary.

---

## 场景矩阵 / Scenario Matrix

| ID | 类型 | 场景 | 验收方式 | 通过信号 | 状态 |
| --- | --- | --- | --- | --- | --- |
| A1 | success | 核心 happy path 完成 | <命令/检查> | <通过信号> | planned |
| A2 | failure | 缺关键证据时拒绝通过 | <命令/检查> | <拒绝信号> | planned |
| A3 | regression | 旧语义不会从公开入口回流 | <命令/检查> | <无回流> | planned |

---

## ADR Carrier Acceptance Matrix

> 仅当 README 顶部状态块 `ADR carrier` 为 `yes` 时必填；否则写 `not_applicable`。ADR carrier acceptance rows are incomplete until mapped.

ADR-carrier proposal 的验收矩阵必须逐项覆盖 `phase-plan.md` 中的 `Covered decisions`，并把每个 ADR decision item 映射到 ADR successor scenario、positive path、negative/fail-fast path、authority / retirement boundary 和最小证据。

| ID | Primary ADR | ADR decision item | ADR successor scenario | Positive path | Must fail if | Authority / retirement boundary | Minimal evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-ADR-1 | ADR-00xx | D1 | <ADR Section 6.2 successor scenario> | <expected accepted path> | <negative path that must reject> | <owner / authority / retirement boundary> | <command, artifact, projection, or source evidence> | planned |

---

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| <证据名称> | <路径或命令> | <结论> |

---

## Closeout Checklist

1. 所有 in-scope 场景都有证据。
2. 所有 formal artifact 引用都位于 proposal 已声明的受信 artifact roots 内。
3. residual risk 已回填到 proposal / phase-plan / follow-up child change。
4. 若属于持续曳光弹 / tracer proposal，`issue-list.md` 中每条未完全关闭的问题都已映射到当前验收行或下一枚 tracer 的 carry-forward 验收要求。
5. 任何 proposal 场景都不得仅凭 test/mock 结果写成正式验收通过；若 test 是当前唯一证据，必须显式标注为 guard/reference，而不是 closeout evidence。
