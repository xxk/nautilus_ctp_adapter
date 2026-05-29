# p001-ADR001-native-first-runtime-rollout Phase Plan / 分阶段推进计划

**创建日期**：2026-05-29
**最后更新**：2026-05-29
**状态**：in_progress
**proposal-id**：`p001-ADR001-native-first-runtime-rollout`
**关联提案**：[README.md](README.md)
**关联验收**：[acceptance.md](acceptance.md)

> 状态口径：本文件 `AI-PHASE-STATUS` 区块是 proposal 级唯一 machine-readable 主状态源；本页顶部 `**状态**` 与 `README.md` 顶部 `**状态**` 都只能作为投影。

---

## Artifact Trust Boundary

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - 未冻结
  allowed_evidence_roots:
    - output/debug/change_evidence/p001-ADR001-native-first-runtime-rollout/
    - output/reports/p001-ADR001-native-first-runtime-rollout/
  source_contract_templates:
    - docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md
    - docs/architecture/platform-neutral-ctp-runtime.md
    - docs/architecture/rust-python-adapter-split.md
    - docs/architecture/runtime-performance-guidelines.md
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
6. 当前 active change `20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff` 只负责 vendor-bridge readiness；本 proposal 不得把其改写成性能 rollout 主承接面。

---

## AI 跟踪状态（AI Tracking Status）

<!-- AI-PHASE-STATUS-BEGIN
reviewed_at: 2026-05-29
reviewer: GitHub Copilot
overall_status: in_progress
phases:
  - id: phase_0_proposal_convergence
    status: completed
    ai_progress: 100
    evidence: "proposal scaffold created; phase split, acceptance boundary, ADR landing map, and docs gate evidence converged"
  - id: phase_1_batch_boundary_freeze
    status: in_progress
    ai_progress: 25
    evidence: "Phase 1 child change created at docs/changes/20260529__runtime-performance__p1; boundary evidence and guards not yet closed"
  - id: phase_2_hot_path_owner_cutover
    status: planned
    ai_progress: 0
    evidence: "owner inventory / migration-boundary child change not yet created"
  - id: phase_3_thin_python_shell_contract
    status: planned
    ai_progress: 0
    evidence: "thin host-glue contract child change not yet created"
  - id: phase_4_benchmark_gate_and_daemon_decision
    status: planned
    ai_progress: 0
    evidence: "benchmark command, threshold, artifact boundary, and daemon trigger policy are not yet frozen"
AI-PHASE-STATUS-END -->

---

## Phase 状态表（Phase Status Board）

| Phase / 阶段 | Revised Goal / 修订后目标 | Current Status / 当前状态 | AI Progress / AI 完成度 | Evidence / Current Facts / 证据 / 当前事实 | Next Action / 下一步 |
| --- | --- | --- | ---: | --- | --- |
| Phase 0 Proposal convergence / 阶段 0 提案收敛 | 冻结 proposal docs、phase split、artifact boundary 与 current-change scope freeze | `completed` | 100% | proposal bundle created；phase split、acceptance boundary、ADR landing map 与 docs gate evidence 已收敛 | 新建 Phase 1 batch-boundary child change |
| Phase 1 Batch boundary freeze / 阶段 1 批量边界冻结 | 冻结 adapter-facing batch runtime contract 与 child change 骨架 | `in_progress` | 25% | Phase 1 child change 已创建：`docs/changes/20260529__runtime-performance__p1/`；boundary source evidence 与 focused guard 尚未收口 | 执行 `20260529__runtime-performance__p1` |
| Phase 2 Hot-path owner inventory / cutover boundary / 阶段 2 热路径 owner 清单与迁移边界 | 冻结 query / market / trading hot path 的 owner inventory、暂留 Python 项与迁移边界 | `planned` | 0% | Python adapter 仍有 runtime bootstrap/placeholder ownership，且迁移边界未 formalize | 新建 owner-inventory child change |
| Phase 3 Thin Python host glue contract / 阶段 3 Python 宿主薄壳契约 | 用 contract lock 约束合法 host shell，并阻止 runtime logic 回流到 Python adapter | `planned` | 0% | thin-shell allowlist / forbidden-list / guard path 尚未 formalize | 新建 thin-shell contract change |
| Phase 4 Benchmark gate and daemon trigger policy / 阶段 4 Benchmark 门槛与 daemon 触发策略 | 冻结 benchmark gate child change 的命令、阈值、formal artifact boundary 与 daemon trigger policy | `planned` | 0% | benchmark gate、threshold、artifact boundary、daemon trigger policy 均未冻结 | 新建 benchmark-gate change 或 future proposal |

---

## Phase 0: Proposal Convergence

### 目标

完成 ADR001 的 proposal carrier 收敛，冻结 proposal 边界、phase 拆分、artifact boundary、change map 和 acceptance baseline，使后续 AI 可以按 `proposal + change` 持续推进。

### 依赖

1. ADR001 已存在并给出架构主线。
2. proposal scaffold 和 docs gate 可用。

### Child Change

`proposal-only planning`

### 交付物

1. `docs/proposals/p001-ADR001-native-first-runtime-rollout/README.md`
2. `docs/proposals/p001-ADR001-native-first-runtime-rollout/phase-plan.md`
3. `docs/proposals/p001-ADR001-native-first-runtime-rollout/acceptance.md`
4. `docs/proposals/p001-ADR001-native-first-runtime-rollout/design.md`
5. `docs/proposals/p001-ADR001-native-first-runtime-rollout/change-map.md`
6. `docs/proposals/p001-ADR001-native-first-runtime-rollout/decision-log.md`

### Runtime / Command Freeze

1. 本 phase 不冻结 runtime command；runtime command 必须在实际执行 phase 中冻结。

### 退出条件

1. proposal 边界、phase 与验收入口已冻结。
2. `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout` 通过并回填到 `acceptance.md`。

### Fail-fast / Negative Cases

1. proposal 状态投影与 `AI-PHASE-STATUS.overall_status` 不一致。
2. formal artifact root 未冻结却把外部 artifact 当作 closeout evidence。
3. proposal 把当前 active vendor-bridge change 重写成性能 rollout carrier。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
```

---

## Phase 1: Batch Boundary Freeze

### 目标

只冻结 adapter-facing batch runtime boundary，明确后续 child change 应围绕哪些命令、事件批次和测试锁推进，而不是继续在 Python per-event callback 语义上漂移。本 phase 不承担 hot-path owner inventory，也不承担 thin-shell contract lock。

### 依赖

1. Phase 0 completed.
2. ADR001 继续维持 `native-first runtime + thin Python host glue` 为主线。

### Child Change

`20260529__runtime-performance__p1`

### 交付物

1. `docs/changes/20260529__runtime-performance__p1/` child change bundle
2. adapter-facing batch contract surface inventory
3. focused validation entry list for batch submission and drain behavior

### Runtime / Command Freeze

1. `python scripts/check_rust_gate.py`
2. targeted tests for touched runtime/adapter boundary

### 退出条件

1. batch boundary child change 已创建并写清唯一主线接口。
2. proposal 不再允许把 per-event callback 当成默认长期 boundary。
3. hot-path owner inventory 仍明确保留给 Phase 2，不在本 phase 提前完成定义。

### Fail-fast / Negative Cases

1. 新设计引入第二套 adapter-facing runtime API。
2. 新设计默许 Python per-event callback 成为正式长期路径。
3. 在 Phase 1 内混入 hot-path owner inventory 或 thin-shell contract 作为完成条件。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
```

---

## Phase 2: Hot-Path Owner Inventory / Cutover Boundary

### 目标

只冻结 query / market / trading hot path 的 owner inventory、暂留 Python 项和迁移边界，明确后续 child change 应如何向 native/Rust 收口。实际代码迁移、运行时 cutover 证据与 moved-path tests 属于后续 child change 执行，不由本 phase 预先伪造完成。

### 依赖

1. Phase 1 completed.
2. 当前 vendor-bridge readiness change 已保持原 scope，不被 proposal 抢占。

### Child Change

`待创建：runtime-performance__native-hot-path-ownership-cutover`

### 交付物

1. owner-cutover child change bundle
2. hot-path ownership inventory、暂留 Python 项与 retirement list
3. migration-boundary verification entry list

### Runtime / Command Freeze

1. 冻结 owner inventory 的 source-of-truth 触点与 review 入口。
2. moved-path runtime tests 由后续 child change 执行时冻结；本 phase 只冻结它们必须存在的验证入口。

### 退出条件

1. hot-path ownership inventory 完成并映射到 child change。
2. proposal 明确哪些逻辑仍允许暂留 Python，哪些必须迁出。
3. thin Python host glue contract 仍保留给 Phase 3，不在本 phase 提前 closeout。

### Fail-fast / Negative Cases

1. 为了赶进度把新的 state machine / query lifecycle 写回 Python。
2. 没有 owner inventory 就直接宣称 hot path 已完全 native 化。
3. 在 Phase 2 中把 thin-shell contract lock 或 benchmark gate 写成已完成前提。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
```

---

## Phase 3: Thin Python Host Glue Contract

### 目标

给 Python host glue 建立显式 contract lock，冻结合法 host shell、禁止回流的 runtime logic 类别与 focused guard 入口，防止后续开发把 runtime logic 重新塞回 adapter layer。

### 依赖

1. Phase 2 completed.

### Child Change

`待创建：runtime-performance__thin-python-host-glue-contract-lock`

### 交付物

1. thin-shell contract child change bundle
2. Python adapter contract-lock tests or equivalent focused guard plan
3. host-glue allowlist / forbidden-runtime-logic list 与 README / architecture write-back

### Runtime / Command Freeze

1. targeted adapter tests
2. `python scripts/check_harness.py`

### 退出条件

1. thin-shell contract lock 已存在。
2. 明确哪些 Python entry 仍属合法 host integration surface。
3. 明确哪些 runtime logic 类别禁止回流，以及对应 focused guard evidence 应如何产生。

### Fail-fast / Negative Cases

1. 允许在 Python adapter 中继续新增 callback parse/state ownership。
2. 只有文档说明，没有 focused guard evidence。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
```

---

## Phase 4: Benchmark Gate And Daemon Trigger Policy

### 目标

只冻结 benchmark gate child change 的边界：可复跑 benchmark 命令、阈值、formal artifact boundary 和 daemon trigger policy 必须在该 child change 中被显式冻结。当前 proposal 只冻结“必须建立这些门槛”，不提前把 external daemon 写成默认主线或已批准执行面。

### 依赖

1. Phase 1-3 completed.
2. 可复跑的 benchmark surface 或替代量测入口已冻结。

### Child Change

`待创建：runtime-performance__benchmark-gate-and-daemon-decision`

### 交付物

1. benchmark gate child change bundle
2. benchmark command / threshold / formal artifact boundary freeze checklist
3. daemon trigger policy skeleton or explicit no-daemon conclusion

### Runtime / Command Freeze

1. 精确 benchmark 命令在后续 child change 中冻结；当前 proposal 不声明最终 benchmark 命令。
2. 数值阈值、formal artifact boundary 与 daemon trigger policy 在后续 child change 中冻结；当前 proposal 只声明这些项属于必填门槛。

### 退出条件

1. benchmark gate child change 已创建，并显式承接 benchmark 命令、阈值、formal artifact boundary 与 daemon trigger policy 的冻结责任。
2. daemon 是否需要 proposal 化的触发条件已正式写清。

### Fail-fast / Negative Cases

1. 没有 benchmark 证据就直接把 daemon 升为默认主线。
2. 用主观“感觉更快”替代量测门槛。
3. 直接把 proposal 级 `allowed_evidence_roots` 当成 Phase 4 formal benchmark pass artifact root。

### 验证方式

```bash
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
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
