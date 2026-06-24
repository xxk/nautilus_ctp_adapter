---
status: accepted
owner: architecture
adr_id: "ADR004"
decision_status: accepted
landing_status: active
---

# ADR004 Adapter Governance Owner Truth Retirement Boundary / Adapter 治理 Owner、Truth 与退役边界

- 日期：`2026-06-23`
- ADR 类型：governance
- 决策状态：accepted
- 落地状态：active
- 落地摘要：active via local architecture governance gate; code migration is staged with guarded transitional retirement, not chat-only
- 覆盖摘要：decision 5/5, implementation 5/5, retirement 4/4 guarded_transitional
- 适用范围：`D:\Nautilus\nautilus_ctp_adapter`
- 决策问题：如何治理 CTP adapter 架构 owner、唯一 truth source、防 fork 规则和旧代码安全退役。
- 当前倾向：采用 owner registry + truth-source matrix + retirement ledger + executable governance gate。
- 最终决策：accepted；本仓必须以 repo-local owner registry 约束 runtime、native loading、adapter glue、diagnostics 和 governance，禁止新增第二 runtime、第二 live verdict、第二 evidence truth 或 forked owner。

---

## 1. Problem Frame / 问题框架

当前代码已经能支撑 CTP adapter 研发与验证，但 `adapters/ctp` 与 `scripts/` 长期吸收 smoke、evidence、policy、diagnostics、runtime pack lineage 等职责，导致正式 adapter、诊断工具和治理证据边界变厚。若不先建立 owner 与 truth 规则，后续拆分容易制造第二套入口、第二份 live-ready 结论、第二套 runtime pack truth，或者让旧代码在迁移后继续作为隐性正式路径。

本 ADR 的目标不是一次性重构代码，而是先冻结治理边界：谁拥有 canonical implementation，谁只能读 truth，谁可以写 evidence，哪些 legacy path 只能临时存在，以及每次退役必须如何被机器检查证明。

### 1.1 Hard Constraints / 硬约束

1. 本仓不得产生第二个 CTP runtime core、第二个 native loader truth、第二个 Nautilus adapter owner、第二个 live-ready verdict source。
2. `rust/ctp_runtime_core/`、`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/native/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`scripts/`、`docs/` 必须有明确 owner role。
3. 旧代码退役必须有 successor owner、compat boundary、focused tests 或 governance gate；不得靠聊天结论、README 声明或人工记忆退役。
4. CTP credentials、raw fronts、broker secrets、account secrets 和 live trading authority 仍由 owner repo / local runtime owner 提供；本仓 governance 不得复制或内联秘密。
5. Live / paper / broker-facing acceptance 不得被 docs-only evidence、stdout-only evidence、screenshots 或 unverified human statements 判定为 pass。

### 1.2 Explicit Non-Goals / 明确不做

1. 本 ADR 不直接重写 `data_client.py`、`execution_client.py` 或 live smoke scripts。
2. 本 ADR 不改变 ADR001 native-first runtime 决策。
3. 本 ADR 不授权发送 live orders，不改变 execution guardrails。
4. 本 ADR 不把外部 repo 或 global docs 变成本仓 runtime truth source。
5. 本 ADR 不要求一次性删除所有 legacy diagnostics；它要求 staged retirement with gates。

### 1.3 Owner / Canonical Entry Impact

1. 新增 canonical governance owner：`docs/architecture/adapter-governance-owner-truth-retirement.md` 是 owner/truth/retirement 的人读 authority。
2. 新增 executable governance gate：`scripts/check_architecture_governance.py` 是 machine-checkable authority。
3. `src/nautilus_ctp_adapter/adapters/ctp/` 继续是 Nautilus adapter glue owner，但不得继续吸收长期 diagnostics/evidence policy owner。
4. `scripts/` 保留 CLI wrapper 与 local diagnostics entrypoint 职责；长期可复用业务逻辑必须迁入 package-owned diagnostics/governance modules。

### 1.4 概念判重 / Canonical Naming Check

| Candidate term | Layer / Owner | Existing nearby term | Collision risk | Decision | Guard / Evidence |
| --- | --- | --- | --- | --- | --- |
| `owner registry` | architecture governance | Directory Map, Official Entry Points | 可能被误读成 execution state | 采纳为 stable owner boundary | `check_architecture_governance.py` |
| `truth-source matrix` | governance / evidence | acceptance evidence, live smoke verdict | 可能形成第二 evidence ledger | 采纳为 authority map, not evidence store | architecture doc + gate |
| `retirement ledger` | migration governance | docs/changes acceptance | 可能被误读成 completed state | 采纳为 staged retirement contract | gate requires successor/gate fields |
| `fork-prevention guard` | architecture gate | harness gate, ADR gate | 可能与 tests 混淆 | 采纳为 architecture-level docs gate | pytest + script |
| `legacy-only path` | retirement boundary | diagnostics-only scripts | 可能继续被正式调用 | 采纳为 temporary compatibility state | retirement table + focused tests |

---

## 2. 与既有 ADR / Architecture 的关系 / Relationship To Existing Decisions

1. 本 ADR 收紧 ADR001：native-first runtime 仍是主线，但 Python host glue 必须保持 thin；diagnostics/evidence 不能继续膨胀 adapter owner。
2. 本 ADR 不替代 ADR002；OpenCTP TTS 仍是默认 simulation provider，但 live-ready verdict source 不能被新 smoke script fork。
3. 本 ADR 延续 ADR003：治理能力必须本仓落地、本仓验证，不依赖聊天结论。
4. 本 ADR 具体化 `AGENTS.md` 中 “must not create a second runtime, gateway, market data route, schema family, validator, artifact root, or CTP evidence truth” 的长期治理规则。

---

## 3. 方案对比 / Options Comparison

本次对比关注防 fork、truth-source 分层、长期维护成本和旧代码安全退役。

| 方案 | 核心思路 | 适用场景 | 优点 | 缺点 / 风险 | 架构一致性 | 实施成本 | 结论 | 采纳与落地 / Decision + Landing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. Owner registry + truth matrix + retirement ledger + gate | 先冻结治理，再分阶段迁移代码 | 当前仓库已有 live/diagnostics 历史积累 | 防 fork 明确；旧代码可安全退役；可机器检查 | 需要维护 registry 和 gate | 高 | 中 | 推荐 | accepted + active |
| B. 立即大重构 | 一次性拆分 adapter、diagnostics、scripts | 小仓库或低风险代码 | 代码结果干净 | live path 风险高；旧证据易断 | 中 | 高 | 拒绝为第一步 | rejected |
| C. 只写 README 规范 | 文档说明 owner，不加 gate | 临时沟通 | 成本低 | 无法防止第二 truth；AI 容易漂移 | 低 | 低 | 拒绝 | rejected |
| D. 保持现状 | 继续在 adapter/scripts 中堆叠 | 短期赶验证 | 不打断当前工作 | fork 和第二 truth 风险持续升高 | 低 | 低 | 拒绝 | rejected |

### 3.1 Landing Evidence / 落地证据

| 方案 | decision_state | landing_state | evidence_state | evidence_ref | residual_risk |
| --- | --- | --- | --- | --- | --- |
| A | accepted | active | contract_locked | ADR004 + architecture doc + governance gate | final physical removal remains staged |
| B | rejected | rejected_not_applicable | not_applicable | ADR004 Section 3 | may be revisited after gate baseline |
| C | rejected | rejected_not_applicable | not_applicable | ADR004 Section 3 | docs-only governance is insufficient |
| D | rejected | rejected_not_applicable | not_applicable | ADR004 Section 3 | current legacy code remains transitional |

### 3.2 取舍说明 / Trade-Off Notes

1. 方案 A 保留当前可运行路径，同时先建立边界与防回退 gate。
2. 方案 B 的最终代码形态可能更干净，但不适合作为第一步，因为 live adapter 迁移必须可回归、可阻断、可退役。
3. 方案 C 与 D 都无法防止 AI 或人工后续新增第二 truth。

---

## 4. 决策 / Decision

### 4.1 决策结论 / Decision Summary

1. 采用方案 A。
2. `docs/architecture/adapter-governance-owner-truth-retirement.md` 是长期 owner/truth/retirement 人读 authority。
3. `scripts/check_architecture_governance.py` 是 architecture governance executable gate，并纳入 `check_harness.py` 聚合检查。
4. 旧 diagnostics/smoke/policy 代码必须通过 retirement ledger 分阶段迁移；迁移前标记 legacy-only/transitional，迁移后用 focused tests 和 import/entry guards 防回退。
5. 禁止新增绕过 registry 的 runtime、native loader、adapter stack、live verdict、evidence artifact root 或 governance validator。

### 4.2 决策边界 / Decision Boundaries

1. Runtime implementation truth：`rust/ctp_runtime_core/` 与 `src/nautilus_ctp_adapter/runtime/`。
2. Native loading truth：`src/nautilus_ctp_adapter/native/`，但 import-time process mutation must be retired behind explicit bootstrap.
3. Nautilus adapter truth：`src/nautilus_ctp_adapter/adapters/ctp/`，只保留 host glue、mapping、thin orchestration。
4. Diagnostics truth：package-owned diagnostics/governance modules；`scripts/` only wrap CLI entrypoints.
5. Live-ready verdict truth：formal entry remains `python scripts/ctp_nautilus_live_smoke.py --config <path>` until successor ADR/change explicitly retires it.
6. Governance truth：ADR + architecture doc + executable gates, not chat-only statements.

### 4.3 Design Kernel / 设计内核

Stable owner flow:

```text
CTP SDK / runtime pack refs
  -> native loader owner
  -> Rust/PyO3 runtime owner
  -> Python runtime boundary
  -> Nautilus adapter glue
  -> diagnostics / evidence readers
  -> governance gates
```

Negative constraints:

1. Diagnostics may read adapter/runtime truth but must not become adapter/runtime truth.
2. Scripts may call package functions but must not own long-lived business logic.
3. Architecture docs may define owner/truth boundaries but must not store live runtime evidence as pass/fail truth.
4. Legacy paths may remain only with declared successor owner and retirement gate.
5. Compatibility wrappers must fail loudly or delegate to canonical owner; silent fork behavior is forbidden.

### 4.4 推荐产物 / Recommended Deliverables

1. `docs/architecture/adapter-governance-owner-truth-retirement.md`
2. `scripts/check_architecture_governance.py`
3. `tests/test_architecture_governance.py`
4. `check_harness.py` aggregation
5. Future child changes for adapter diagnostics extraction and explicit native bootstrap retirement

### 4.5 决策覆盖与落地矩阵 / Decision Coverage And Landing Matrix

| 决策项 | 必须覆盖的落点 | 覆盖状态 | 承接 proposal / change | executable evidence | docs evidence | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
| D1. owner registry exists | architecture doc | verified | ADR004 local governance | `check_architecture_governance.py` | architecture doc | none for owner baseline |
| D2. truth-source matrix exists | architecture doc | verified | ADR004 local governance | `check_architecture_governance.py` | architecture doc | none for docs baseline |
| D3. fork-prevention rules exist | gate + AGENTS | verified | ADR004 local governance | `check_harness.py` | ADR004 + architecture doc | future checks can deepen |
| D4. legacy retirement ledger exists | architecture doc | verified | ADR004 local governance | `check_architecture_governance.py` | architecture doc | legacy code still staged |
| D5. old code safely retired | code/tests/import guards | guarded_transitional | diagnostics/native owner extraction | focused tests + architecture governance gate | retirement ledger | final physical removal remains staged |

---

## 5. Landing Map / 落地映射

### 5.0 Accepted Decision Boundary / 已接受决策边界

Accepted:

1. Owner registry, truth-source matrix, fork-prevention rules and retirement ledger are mandatory governance artifacts.
2. Legacy code may remain only as transitional compatibility with declared successor owner.
3. New validators must join the aggregate harness gate.

### 5.0.1 Not Accepted By This ADR / 本 ADR 不接受

1. 不接受新增第二 live smoke verdict source。
2. 不接受把 scripts 作为长期业务逻辑 owner。
3. 不接受 import-time native bootstrap 继续作为最终 architecture target。
4. 不接受 evidence artifacts 或 output/debug 成为 canonical truth store。

### 5.0.2 Successor Change Boundary / 后续 Change Boundary

| Phase | 目标 | 承接 proposal / change | 退出条件 | retirement 影响 | 承接状态 |
| --- | --- | --- | --- | --- | --- |
| Phase 0 | 建立治理 authority 与 gate | ADR004 local governance | ADR/index/architecture/gate/test pass | 无 | active |
| Phase 1 | 抽离 adapter diagnostics dataclasses/policy | diagnostics owner extraction | adapter files delegate diagnostics models/policy to package owners | data/execution diagnostics guarded transitional | active |
| Phase 2 | scripts logic 下沉 package modules | diagnostics owner extraction | scripts delegate reusable payload/verdict logic and keep CLI/safety arms | scripts business owner guarded transitional | active |
| Phase 3 | explicit native runtime bootstrap | native loader owner extraction | `ctp_runtime` delegates bootstrap to native owner | import-time bootstrap guarded transitional | active |
| Final | legacy path removal / compatibility guards | future cleanup | old imports either delegate or fail with successor message | old code physically retired | planned |

### 5.1 旧代码退役与文档收口 / Legacy Retirement And Documentation Closure

| 旧项 / 路径 | 当前职责 | 新归宿 / 替代物 | 处理动作 | 暂留边界 | 最终移除条件 | 文档同步项 | 承接状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `src/nautilus_ctp_adapter/adapters/ctp/data_client.py` embedded MD smoke/evidence/policy | adapter + diagnostics mixed | package diagnostics/policy module + thin adapter facade | split and delegate | legacy-only policy methods may remain temporarily | focused tests prove delegated canonical owner | architecture doc + tests | planned |
| `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py` embedded TD smoke/evidence/policy | adapter + execution diagnostics mixed | package diagnostics/policy module + thin adapter facade | split and delegate | live order guardrails remain canonical until extracted safely | focused tests prove no behavior drift | architecture doc + tests | planned |
| `scripts/ctp_*.py` long-lived logic | CLI + business logic mixed | package-owned diagnostics/governance functions | move reusable logic to package, keep script wrappers | scripts remain runnable entrypoints | tests import package owner, scripts smoke CLI only | scripts README + architecture doc | planned |
| `src/ctp_runtime/__init__.py` import-time DLL preload | implicit native bootstrap | explicit native runtime bootstrap API | add explicit bootstrap then retire import mutation | current behavior remains compatibility only | import test proves no process mutation without explicit bootstrap | architecture doc + tests | planned |

---

## 6. Acceptance And Evidence / 验收与证据

### 6.0 ADR-Level Acceptance Only / 仅限 ADR 级验收

ADR-level acceptance requires only that the owner/truth/retirement decision is indexed, documented and machine-checkable. It does not claim code retirement is complete.

### 6.1 General Acceptance Rules / 通用验收纪律

1. Every successor change must include a positive path and a must-fail path for fork prevention or retirement.
2. Every retired path must name successor owner and have either a delegating compatibility wrapper or explicit failure message.
3. No live-ready, broker, credential, account, capital or order-send claim may be accepted without runtime-owner evidence or typed blocker.
4. Documentation-only acceptance is sufficient for governance docs only when paired with validator script or harness gate.

### 6.2 Successor Proposal Acceptance Scenario Requirements / 后续 Proposal 验收场景要求

| ADR decision item | Required acceptance scenario | Positive path | Must fail if | Authority / retirement boundary | Minimal evidence |
| --- | --- | --- | --- | --- | --- |
| D1 owner registry | gate reads required owner IDs | owner IDs present | owner missing or duplicate canonical owner | architecture doc | governance gate |
| D2 truth matrix | gate reads required truth IDs | truth IDs present | live verdict or evidence truth missing | architecture doc | governance gate |
| D3 fork prevention | harness aggregates gate | harness pass includes architecture gate | gate omitted from harness | check_harness | pytest + command |
| D4 retirement ledger | legacy rows have successor and gate | rows complete | planned legacy path lacks successor | architecture doc | governance gate |
| D5 code retirement | future focused tests | new package owner used | old path remains canonical after retirement | successor change | focused pytest |

---

## 7. Related Documents / 关联文档

1. [Architecture governance boundary](../architecture/adapter-governance-owner-truth-retirement.md)
2. [ADR001 High-Performance Native-First Adapter Boundary](./ADR001%20%E9%AB%98%E6%80%A7%E8%83%BD%E4%BC%98%E5%85%88%E5%8E%9F%E7%94%9F%E4%B8%BB%E7%BA%BF%E9%80%82%E9%85%8D%E8%BE%B9%E7%95%8C_High-Performance%20Native-First%20Adapter%20Boundary.md)
3. [ADR003 Doc Harness Capability Replication And Strategies Alignment](./ADR003%20Doc%20Harness%20Capability%20Replication%20And%20Strategies%20Alignment.md)

### ADR Closeout Distillation

Closeout must summarize stable owner/truth/retirement results only. Do not paste live evidence, secrets, runtime output or one-off smoke logs into this ADR.
