---
status: accepted
owner: architecture
adr_id: "ADR003"
decision_status: accepted
landing_status: completed
---

# ADR003 Doc Harness Capability Replication And Strategies Alignment / 文档 Harness 能力复制与 strategies 对齐

- 日期：`2026-06-07`
- ADR 类型：governance
- 决策状态：accepted
- 落地状态：completed
- 落地摘要：completed via `20260610__governance__adr003-landing-closeout`；本地 harness 入口、workflow 绑定口径与 ADR/docs gate 已收口
- 覆盖摘要：decision 4/4, implementation 4/4, retirement 1/1
- 适用范围：`D:\Nautilus\nautilus_ctp_adapter`
- 决策问题：当本仓 doc / harness 能力缺失或落后时，应以哪个仓库和哪类能力作为对齐基线。
- 当前倾向：采用 `D:\Nautilus\nautilus_strategies` 的 doc / harness 能力作为本仓补齐参照，同时继续以本仓 Route B frontier 为执行状态源。
- 最终决策：accepted；本仓缺失 doc / harness 能力时，默认向 `nautilus_strategies` 的已落地治理能力对齐，但不得复制其业务 owner、策略运行时或 GitHub issue lane 作为本仓状态源。

---

## 1. Problem Frame / 问题框架

本仓已经采用 Route B：`docs/changes/*/plan.md` 是默认 executable frontier，proposal 负责多 phase 方案，ADR / architecture 负责稳定决策。但当前仓库仍存在明显的 doc / harness 能力缺口：

1. `docs/README.md` 和 `AGENTS.md` 指向 `docs/doc_harness_kit/README.md`，而本地 `docs/doc_harness_kit/` 当前缺失。
2. 本仓已有 `check_harness.py`、`check_change_docs.py`、`check_proposal_docs.py`、`autopilot.py` 和 `show_current_frontier.py`，但缺少 `nautilus_strategies` 已具备的 `check_adr_docs.py`、`docs/workflows/` fragments/gates、profile-aware workflow validation、blocker / Work Item Contract 等可复用能力。
3. `ADR002` 已存在但 ADR 索引滞后，说明 ADR discovery 与 ADR gate 仍未形成足够强的机器约束。
4. 本仓是 CTP adapter workspace，不应复制 `nautilus_strategies` 的业务策略 owner 或 GitHub issue lane；需要复制的是治理能力、模板能力、gate 能力与持续推进纪律。

本 ADR 的目标是冻结一个长期口径：当本仓 doc / harness 能力不足时，默认以 `D:\Nautilus\nautilus_strategies` 作为能力参照，按本仓边界裁剪复制，而不是临时手写第二套规则。

### 1.1 Hard Constraints / 硬约束

1. 本仓 executable frontier 继续以 `docs/changes/*/plan.md`、`scripts/autopilot.py --root .` 和 `scripts/show_current_frontier.py --root .` 为本地 authority。
2. `nautilus_strategies` 只能作为 doc / harness capability baseline，不得成为本仓执行状态源、业务 truth source 或 runtime owner。
3. 从 `nautilus_strategies` 复制能力时，必须裁剪掉策略业务、portfolio、paper/live UI、GitHub issue lane 等不属于本仓 adapter 责任的内容。
4. 新增能力必须落到本仓长期目录、脚本或 change/proposal 模板，并通过本仓 gate 验证；不得只留在聊天结论中。

### 1.2 Explicit Non-Goals / 明确不做

1. 本 ADR 不直接复制 `nautilus_strategies` 的全部 `docs/` 或 `scripts/`。
2. 本 ADR 不把 `nautilus_strategies` 的 GitHub issues 作为本仓正式状态源。
3. 本 ADR 不改变 ADR001 的 native-first runtime 决策，也不改变 ADR002 的 OpenCTP TTS paper simulation 决策。
4. 本 ADR 不要求恢复已删除的本地 `docs/doc_harness_kit/` 副本；是否恢复本地 kit 或改指上游路径由后续 change 决定。

### 1.3 Owner / Canonical Entry Impact

1. 新增治理 owner 口径：`nautilus_strategies` 是本仓 doc / harness capability baseline。
2. 本仓 canonical execution entries 不变：`scripts/autopilot.py`、`scripts/show_current_frontier.py`、`scripts/check_harness.py`、`scripts/check_change_docs.py --root .`、`scripts/check_proposal_docs.py --root .`。
3. 后续若新增 `check_adr_docs.py`、`docs/workflows/` 或 workflow validation，owner 应归本仓 governance harness，而不是归 `nautilus_strategies` 或共享外部仓。
4. 当前缺失的 `docs/doc_harness_kit/` 必须在后续 change 中收口为以下二选一：恢复本地副本并由本仓 gate 维护，或把入口改为 `D:\Nautilus\docs\doc_harness_kit\` / 等价上游位置。

### 1.4 概念判重 / Canonical Naming Check

| Candidate term | Layer / Owner | Existing nearby term | Collision risk | Decision | Guard / Evidence |
| --- | --- | --- | --- | --- | --- |
| `doc / harness capability baseline` | governance / architecture | `Doc Harness Kit`, Route B, harness | 可能被误读成外部仓状态源 | 采纳为能力参照，不是状态源 | ADR003 + future docs gate |
| `nautilus_strategies alignment` | cross-repo governance | downstream integration, strategies repo | 可能被误读成业务能力复制 | 采纳为治理能力对齐，排除业务 owner | ADR003 red lines |
| `capability replication` | governance rollout | template copy, harness adoption | 可能变成无差别目录复制 | 采纳为按能力族裁剪复制 | successor change acceptance |
| `docs/workflows/` | workflow spec layer | proposal/change templates, topics | 可能成为第三状态源 | 仅作为模板/gate spec，不承载 execution state | future gate based on strategies pattern |

---

## 2. 与既有 ADR / Architecture 的关系 / Relationship To Existing Decisions

1. 本 ADR 补充 [ADR001](./ADR001%20%E9%AB%98%E6%80%A7%E8%83%BD%E4%BC%98%E5%85%88%E5%8E%9F%E7%94%9F%E4%B8%BB%E7%BA%BF%E9%80%82%E9%85%8D%E8%BE%B9%E7%95%8C_High-Performance%20Native-First%20Adapter%20Boundary.md) 的治理外层，不改变 runtime 或 adapter owner。
2. 本 ADR 补充 [ADR002](./ADR002%20OpenCTP%20TTS%20Paper%20Simulation%20Test%20Environment.md) 的 ADR discovery 需求：新增 ADR 后必须能被 index/gate 发现。
3. 本 ADR 继承 `docs/README.md` 与 `docs/proposals/README.md` 的 Route B 口径：proposal/change/topic/ADR 继续分层，不让 workflow 或 harness 成为新的执行状态源。
4. 本 ADR 与跨仓文档 [任务分层与命名统一口径](../../../docs/harness/%E4%BB%BB%E5%8A%A1%E5%88%86%E5%B1%82%E4%B8%8E%E5%91%BD%E5%90%8D%E7%BB%9F%E4%B8%80%E5%8F%A3%E5%BE%84_Cross-Repo%20Work%20Item%20Layering%20And%20Naming.md) 一致：正式执行单元仍叫 `change`，task 只存在于 change 内部。

---

## 3. 方案对比 / Options Comparison

本次对比关注 governance capability 的来源、复制范围、长期维护成本和防分叉能力。

| 方案 | 核心思路 | 适用场景 | 优点 | 缺点 / 风险 | 架构一致性 | 实施成本 | 结论 | 采纳与落地 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. 以 `nautilus_strategies` 为能力基线，按本仓裁剪复制 | 缺什么补什么：ADR gate、workflow fragments、harness validation、autopilot policy 等 | 本仓 doc / harness 能力缺失或落后 | 有已验证参照；减少重新发明规则；便于跨仓一致 | 需要严格裁剪业务语义和 issue lane | 高 | 中 | 推荐 | accepted + planned |
| B. 恢复/复制完整 `doc_harness_kit` 本地副本 | 把上游 kit 重新放回本仓并维护本地副本 | 需要离线、自包含治理模板 | 自包含，读入口直接可用 | 容易长期分叉；当前已出现缺失/删除状态 | 中 | 中 | 过渡候选 | included as implementation option |
| C. 只引用共享上游 kit，不复制 strategies 能力 | 将本仓入口改指 `D:\Nautilus\docs\doc_harness_kit\` | 只需基础模板而不需要 advanced workflows | 减少本地副本维护 | 无法覆盖 strategies 已有的 ADR/workflow/autopilot 高阶能力 | 中 | 低 | 不足 | retained as partial source |
| D. 本仓独立重新设计 harness | 为 CTP adapter 从零设计新规则 | 有强烈本仓特化需求时 | 完全贴合本仓 | 高重复、高漂移，容易产生第二套口径 | 低 | 高 | 拒绝 | rejected |

### 3.1 Landing Evidence / 落地证据

| 方案 | decision_state | landing_state | evidence_state | evidence_ref | residual_risk |
| --- | --- | --- | --- | --- | --- |
| A | accepted | completed | docs_and_gate | `20260610__governance__adr003-landing-closeout` | 后续可继续增量补 profile-aware capability，但不阻断 ADR 落地完成 |
| B | included | not_selected | not_applicable | successor closeout chose minimal local entry instead of full mirror | 完整副本仍有长期分叉风险 |
| C | included | completed_as_entry | docs_and_gate | local `docs/doc_harness_kit/README.md` + harness gate | 基础入口已补，但 advanced capability 仍以本仓落地为准 |
| D | rejected | rejected_not_applicable | not_applicable | ADR003 Section 3 | 无 |

### 3.2 取舍说明 / Trade-Off Notes

1. 方案 A 是长期默认：以 `nautilus_strategies` 的能力族为参照，但按 `nautilus_ctp_adapter` 的 Route B、runtime owner 和 live smoke 边界裁剪。
2. 方案 B 可以作为恢复本地读入口的实现选项，但不能形成长期未同步副本；如果恢复，必须有 gate 或版本说明证明它没有漂移。
3. 方案 C 只解决基础 kit 指针，不足以覆盖 ADR gate、workflow fragments、profile-aware validation、continuous autopilot policy 等高阶能力。
4. 方案 D 拒绝为默认，因为它会制造跨仓第二套 governance vocabulary。

---

## 4. 决策 / Decision

### 4.1 决策结论 / Decision Summary

1. 采用方案 A：`D:\Nautilus\nautilus_strategies` 是本仓 doc / harness capability baseline。
2. 本仓能力欠缺时，优先查找 `nautilus_strategies` 已有实现、文档、fragment、gate 和 ADR，再按本仓事实裁剪落地。
3. 允许从共享上游 `D:\Nautilus\docs\doc_harness_kit\` 补基础 kit 入口，但不得因此跳过 `nautilus_strategies` 已沉淀的 advanced governance 能力。
4. 拒绝为本仓从零重写第二套 harness vocabulary、workflow taxonomy 或 ADR gate 体系。

### 4.2 决策边界 / Decision Boundaries

1. 正式 truth source：本仓 `docs/changes/*/plan.md`、proposal `phase-plan.md`、ADR/architecture 文档和本仓脚本 gate。
2. 能力参照源：`D:\Nautilus\nautilus_strategies` 的 `AGENTS.md`、`docs/adr/`、`docs/workflows/`、`scripts/check_adr_docs.py`、`scripts/check_harness.py`、`scripts/autopilot.py` 和 `scripts/autopilot_internal/`。
3. 复制边界：只复制 doc/harness 能力、模板、验证规则、状态恢复纪律和 anti-fork guard；不复制策略业务、portfolio semantics、PM UI、Paper/Live admission 业务规则或 GitHub issue state source。
4. 后续落地必须由本仓 governance change 或 proposal/change 承接，不得直接把外部仓路径作为运行时依赖硬编码进正式 gate，除非该 gate 明确声明它只是检查 cross-repo reference 可用性。

### 4.3 Design Kernel / 设计内核

稳定能力族如下：

1. ADR capability：ADR 模板契约、ADR 索引完整性、`check_adr_docs.py` 或等价 gate。
2. Workflow capability：`docs/workflows/` 作为模板/gate spec layer，不承载 execution state。
3. Harness validation capability：`scripts/harness/validation.py` 或等价分层 validator，`check_harness.py` 作为 aggregator。
4. Autopilot capability：持续推进、checkpoint、blocker 分类、frontier 输出和 trajectory，不改变本仓 state source。
5. Template capability：proposal/change fragments、profile-aware 模板和 acceptance evidence 规则。

数据流方向：

```text
nautilus_strategies capability baseline
  -> adapter-specific capability gap analysis
  -> local governance child change / proposal
  -> local docs/scripts/templates
  -> local harness/checks/autopilot evidence
```

Negative constraints:

1. 不得把 `nautilus_strategies` 的 GitHub issue lane 变成本仓状态源。
2. 不得把 workflow spec 写成第三执行队列。
3. 不得复制 portfolio / PM View / strategy owner 业务语义。
4. 不得让共享 kit、本仓副本、strategies 能力三者静默分叉；任一偏离必须写入本仓 ADR、architecture 或 successor change。

### 4.4 推荐产物 / Recommended Deliverables

1. 新增 `scripts/check_adr_docs.py` 或增强 `check_harness.py` 覆盖 ADR index completeness。
2. 建立或恢复 doc harness kit 入口：本地副本或明确指向 `D:\Nautilus\docs\doc_harness_kit\`。
3. 按需新增 `docs/workflows/`，至少承载 ADR/template/work-item/gate fragments，不承载状态。
4. 增强 proposal/change template fragments，对齐 `nautilus_strategies` 的 reusable fragment 和 gate 口径。
5. 更新 `AGENTS.md`、`docs/README.md`、`docs/changes/README.md`，使缺失能力的对齐路径可被 AI 直接执行。

### 4.5 决策覆盖与落地矩阵 / Decision Coverage And Landing Matrix

| 决策项 | 必须覆盖的落点 | 覆盖状态 | 承接 proposal / change | executable evidence | docs evidence | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
| D1. `nautilus_strategies` is capability baseline | ADR / AGENTS / docs README | implemented | ADR003 | docs gate after index update | ADR003 | 后续同步 AGENTS/docs README |
| D2. Local frontier remains local authority | autopilot / frontier / changes docs | implemented | ADR003 | `autopilot.py --root .` / `show_current_frontier.py --root .` | ADR003 + existing docs | 无 |
| D3. Copy governance capability, not business semantics | workflow/template/gate docs | implemented | `20260610__governance__adr003-landing-closeout` | docs/workflows + AGENTS/docs boundary + harness gate | ADR003 + successor change | 后续增量能力按本仓 change 推进 |
| D4. Missing harness kit entry must be closed | docs entry / harness gate | implemented | `20260610__governance__adr003-landing-closeout` | local `docs/doc_harness_kit/README.md` + checklist + harness gate | ADR003 + successor change | 无 |

---

## 5. Landing Map / 落地映射

### 5.0 Accepted Decision Boundary / 已接受决策边界

Accepted:

1. `nautilus_strategies` 是本仓 doc / harness 能力补齐的默认参照。
2. 本仓只复制治理能力，不复制外部仓业务 owner 或状态源。
3. 本仓 frontier、proposal、change、ADR 分层继续作为本地 authority。
4. 当前 `docs/doc_harness_kit/` 缺失是后续 governance change 必须收口的缺口。

### 5.0.1 Not Accepted By This ADR / 本 ADR 不接受

1. 不接受把 `nautilus_strategies` 作为本仓 execution frontier。
2. 不接受无差别复制 `nautilus_strategies` 全仓文档或脚本。
3. 不接受复制 portfolio / strategy / PM UI 业务概念。
4. 不接受在没有本仓 gate 的情况下声明能力已经完成。

### 5.0.2 Successor Proposal Boundary / 后续 Proposal 边界

| Phase | 目标 | 承接 proposal / change | 退出条件 | retirement 影响 | 承接状态 |
| --- | --- | --- | --- | --- | --- |
| Phase 0 | 冻结 ADR003 决策与索引 | ADR003 | ADR003 已创建并列入 ADR index | 无 | ADR-only completed |
| Phase 1 | 做 capability gap inventory | `20260610__governance__adr003-landing-closeout` | 已识别本仓当前最小缺口与裁剪边界 | 无 | completed |
| Phase 2 | 补 ADR / workflow / harness gates | `20260610__governance__adr003-landing-closeout` | ADR gate、workflow spec、harness entry/gate 已落地 | stale doc_harness 缺口关闭 | completed |
| Phase 3 | autopilot/blocker/template 能力补齐 | existing local harness + future incremental changes | 当前不再阻断 ADR003 closeout；后续按本仓 change 增量推进 | 聊天-only 行为已退役 | completed_for_adr_scope |
| Final | closeout distillation | `20260610__governance__adr003-landing-closeout` | AGENTS/docs README/ADR index 已同步稳定结论 | stale docs retired | completed |

### 5.1 旧代码退役与文档收口 / Legacy Retirement And Documentation Closure

| 旧项 / 路径 | 当前职责 | 新归宿 / 替代物 | 处理动作 | 暂留边界 | 最终移除条件 | 文档同步项 | 承接状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/doc_harness_kit/` missing local entry | 被 AGENTS/docs README 引用的 harness kit 入口 | local stable entry + upstream pointer | 已通过 successor change 收口 | 不再作为缺口保留 | 入口可读且 gate 通过 | AGENTS / docs README / check_harness | completed |
| ADR index stale behavior | ADR discovery 依赖人工记忆 | `check_adr_docs.py` + updated index discipline | 已有机器检查并回填索引 | 无 | ADR index completeness gate 通过 | docs/adr/README.md | completed |

---

## 6. Acceptance And Evidence / 验收与证据

### 6.0 ADR-Level Acceptance Only / 仅限 ADR 级验收

本 ADR accepted 的条件是治理决策被写入并可被 ADR index 发现，不要求后续 capability 已经全部复制完成。

### 6.1 General Acceptance Rules / 通用验收纪律

1. 能力复制必须有本仓落点、本仓 gate 和本仓 evidence。
2. 缺失能力不得只用聊天结论判定为完成。
3. 复制前必须先标明 `strategies` 对应能力、裁剪范围、排除业务语义和本仓 owner。
4. 后续 change 完成时，应回填 acceptance evidence，而不是把一次性命令输出复制进 ADR。

### 6.2 Successor Proposal Acceptance Scenario Requirements / 后续 Proposal 验收场景要求

| ADR decision item | Required acceptance scenario | Positive path | Must fail if | Authority / retirement boundary | Minimal evidence |
| --- | --- | --- | --- | --- | --- |
| D1 | strategies capability baseline is discoverable | ADR003 + AGENTS/docs README update | baseline only exists in chat | ADR owns decision; docs expose entry | ADR docs gate |
| D2 | local frontier remains local | `autopilot.py --root .` and `show_current_frontier.py --root .` still select local changes | strategies state affects adapter frontier | local plans remain state authority | frontier command evidence |
| D3 | governance-only copying is enforced | capability inventory marks included/excluded semantics | portfolio/PM/GitHub issue lane copied as adapter truth | adapter runtime/business owner unchanged | inventory + focused docs gate |
| D4 | harness kit missing entry is closed | local kit restored or upstream pointer is valid | AGENTS/docs point to missing path | docs entry no longer stale | check_harness / docs gate |

### 6.3 Architecture-Level Acceptance / 架构级验收

ADR003 is fully landed only when:

1. ADR index lists ADR003 as binding and completed.
2. ADR002 stale-index gap is fixed.
3. A successor governance change inventories the missing capabilities against `nautilus_strategies`.
4. ADR discovery, harness entry, and workflow/template capability gaps are implemented for the current repository scope.

### 6.4 ADR Closeout Distillation / ADR closeout 沉淀

Closeout 后只沉淀稳定结论：

1. `nautilus_strategies` remains the default doc / harness capability baseline.
2. 本仓 local frontier remains authoritative.
3. 具体复制结果、命令输出和 gap inventory 留在 successor change acceptance，不复制进 ADR。

---

## 7. Related Documents / 关联文档

1. [ADR001 Native-First Adapter Boundary](./ADR001%20%E9%AB%98%E6%80%A7%E8%83%BD%E4%BC%98%E5%85%88%E5%8E%9F%E7%94%9F%E4%B8%BB%E7%BA%BF%E9%80%82%E9%85%8D%E8%BE%B9%E7%95%8C_High-Performance%20Native-First%20Adapter%20Boundary.md)
2. [ADR002 OpenCTP TTS Paper Simulation Test Environment](./ADR002%20OpenCTP%20TTS%20Paper%20Simulation%20Test%20Environment.md)
3. [Adapter docs README](../README.md)
4. [`nautilus_strategies` AGENTS.md](../../../nautilus_strategies/AGENTS.md)
5. [`nautilus_strategies` workflows README](../../../nautilus_strategies/docs/workflows/README.md)
6. [`nautilus_strategies` ADR index](../../../nautilus_strategies/docs/adr/README.md)
7. [Cross-Repo Work Item Layering And Naming](../../../docs/harness/%E4%BB%BB%E5%8A%A1%E5%88%86%E5%B1%82%E4%B8%8E%E5%91%BD%E5%90%8D%E7%BB%9F%E4%B8%80%E5%8F%A3%E5%BE%84_Cross-Repo%20Work%20Item%20Layering%20And%20Naming.md)

---

## Optional Fragments / 可选片段

### A. Red Lines

1. Do not copy `nautilus_strategies` business owner semantics into this adapter repo.
2. Do not let external repo state choose this repo's active change.
3. Do not treat `docs/workflows/` as an execution state source.
4. Do not claim harness capability copied until local gate and local docs evidence exist.
5. Do not keep stale harness entrypoints without an explicit successor change or blocker.
