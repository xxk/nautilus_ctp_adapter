---
status: accepted
owner: architecture
adr_id: "ADR001"
decision_status: accepted
landing_status: completed
---

# ADR001 高性能优先原生主线适配边界 / High-Performance Native-First Adapter Boundary

- 日期：`2026-05-29`
- ADR 类型：standard
- 决策状态：accepted
- 落地状态：completed
- 落地摘要：completed via `p001-ADR001-native-first-runtime-rollout`; Phase 1-4 boundary child changes are completed; current active vendor-bridge change remains a separate prerequisite slice only
- 覆盖摘要：decision 1/1, boundary implementation 4/4, retirement policy 2/2
- 适用范围：`D:\Nautilus\nautilus_ctp_adapter`
- 决策问题：在继续作为 Nautilus provider / live client 接入层的前提下，仓库应采用哪条正式高性能主线，以及 Python、Rust、C/C++ 各自应保留到什么边界。
- 当前倾向：采用 native-first runtime + thin Python host glue；只有在测量证明 batch bridge 已成为瓶颈时，才评估 external native daemon。
- 最终决策：accepted；正式主线采用 native-first runtime + thin Python host glue，external native daemon 只保留为受 benchmark gate 约束的 future proposal。

---

## 1. Problem Frame / 问题框架

1. 当前仓库已经形成三条稳定事实：runtime core 应保持 platform-neutral，性能敏感逻辑应优先落 Rust，Nautilus host integration 仍位于 Python adapter layer。
2. 用户目标是最高性能，但当前讨论容易滑向“是否彻底删除 Python 文件”；这会混淆“语言数量”和“热路径 ownership”两个不同问题。
3. 本 ADR 要决定的是正式高性能主线，而不是单次 child change 的执行进度；它需要明确什么是允许的 Python 宿主壳，什么是必须下沉到 native runtime 的热路径，以及什么时候才允许切到 external daemon 模式。
4. 本 ADR 不允许为了追求表面上的纯 native 而重新引入第二套 mainline、managed bridge 中心化、或 Python-side fallback 逻辑。
5. 当前仓库事实：
   - [docs/architecture/platform-neutral-ctp-runtime.md](../architecture/platform-neutral-ctp-runtime.md) 已冻结 runtime host-neutral 方向。
   - [docs/architecture/rust-python-adapter-split.md](../architecture/rust-python-adapter-split.md) 已冻结 Rust runtime + Python adapter split。
   - [docs/architecture/runtime-performance-guidelines.md](../architecture/runtime-performance-guidelines.md) 已冻结“先优化 runtime，再薄化 host adapter”的性能口径。
   - 当前 active change [20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff](../changes/20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff/plan.md) 只负责 vendor bridge / SDK handoff readiness，不承担本 ADR 的长期架构裁决。

### 1.1 Hard Constraints / 硬约束

1. 只要本仓仍以 Nautilus provider / live client 形态接入，正式宿主协议必须兼容 Nautilus 当前 Python-facing config / factory / provider / client boundary。
2. 高吞吐热点不得依赖 Python per-event crossing；native callback、normalize、state machine、buffering、query lifecycle 必须优先收口到 Rust 或 repository-owned native boundary。
3. 不得把 temporary C# / managed bridge 重新抬升为长期 mainline，不得引入 fallback / compat / retry / silent downgrade 风格兜底路径。

### 1.2 Explicit Non-Goals / 明确不做

1. 本 ADR 不直接实现 SmartQuant adapter，也不重新定义多宿主 rollout 顺序。
2. 本 ADR 不把 direct-to-EventBus native integration 作为当前 primary path。
3. 本 ADR 不要求立即把当前仓库整体改造成独立 daemon 产品；daemon 化仅作为后续可选扩展路线。

### 1.3 Owner / Canonical Entry Impact

1. 本 ADR 不新增第二套 public entry；正式 runtime owner 仍在 `rust/` 与 repository-owned native boundary，Nautilus host entry 仍在 `src/nautilus_ctp_adapter/adapters/ctp/`。
2. 本 ADR 收紧 owner 边界：Python adapter 只拥有 host integration，不再允许继续扩张 native/runtime ownership。
3. canonical adapter-facing runtime boundary 继续收口到 `submit_command(command)` / `drain_events(limit)` 一类批量接口，后续扩展也必须围绕这一层，而不是新增逐 tick Python callback mainline。

### 1.4 概念判重 / Canonical Naming Check

| Candidate term | Layer / Owner | Existing nearby term | Collision risk | Decision | Guard / Evidence |
| --- | --- | --- | --- | --- | --- |
| `native-first runtime` | runtime / architecture | `Rust core`, `platform-neutral runtime`, `rust-ctp` | 容易被误读成“必须删除所有 Python” | 采纳为“hot path owner 在 native/Rust，不等于删除宿主壳” | 本 ADR + split doc + successor contract lock |
| `thin Python host glue` | host adapter / Nautilus integration | `Python glue`, `adapter layer`, `host integration` | 容易被误读成可继续承载 state machine 或 callback parse | 采纳为“只保留 config/factory/provider/client shell 与 host translation” | 本 ADR + successor thin-shell tests |
| `external native daemon` | future extension / runtime deployment | `native bridge`, `vendor bridge`, `IPC runtime` | 容易和当前 in-process runtime mainline 混淆 | 降级为 future extension，只有量测越线后才可进入 proposal | 本 ADR + future proposal gate |
| `pure native plugin` | host integration / fork path | `plugin`, `in-process native host` | 容易被误当成默认高性能解 | 明确拒绝为当前长期主线 | 本 ADR |
| `C++ full-stack rewrite` | implementation language choice | `Rust runtime`, `repository-owned native boundary` | 容易把语言替换误当成性能主因 | 明确拒绝为当前默认路径 | 本 ADR |

---

## 2. 与既有 ADR / Architecture 的关系 / Relationship To Existing Decisions

1. 本 ADR 补充并收紧 [platform-neutral-ctp-runtime](../architecture/platform-neutral-ctp-runtime.md) 的“host-neutral runtime”结论，增加对高性能主线和 crossing budget 的明确裁决。
2. 本 ADR 具体化 [rust-python-adapter-split](../architecture/rust-python-adapter-split.md) 中“Rust core + Python glue”的边界，把“Python glue 允许存在，但不得拥有热路径”写成正式待评审决策。
3. 本 ADR 继承 [runtime-performance-guidelines](../architecture/runtime-performance-guidelines.md) 的性能排序，但进一步加入“何时允许 daemon 化、何时拒绝纯 native in-process fork”这类方案裁决。
4. 本 ADR 不是 rollout 文档；执行面仍应下沉到当前 active change 和后续 runtime child changes，而不是把验证进度回写到 ADR 本体。

---

## 3. 方案对比 / Options Comparison

本次对比不只比较“能不能做”，还比较性能、truth-source 分层、长期扩展性、治理成本与退役成本。这里的关键不是仓库里有没有 Python 文件，而是 hot path 由谁拥有、边界 crossing 是否可批量化、以及是否会引入第二条 mainline。

| 方案 | 核心思路 | 适用场景 | 优点 | 缺点 / 风险 | 架构一致性 | 实施成本 | 结论 | 采纳与落地 / Decision + Landing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. Native-first runtime + thin Python host glue | Rust / C boundary 拥有热路径，Python 仅保留 Nautilus config/factory/provider/client 壳 | 继续作为 Nautilus provider / live client | 性能与现有宿主兼容性平衡最好；能保持单一 mainline | 仍需维护少量 Python 层；需要严格防止热路径回流 | 高 | 中 | 推荐 | proposed + planned |
| B. Native daemon + IPC bridge | 把 CTP runtime 做成独立 native 进程，Nautilus 通过 IPC 接入 | batch bridge 已被测量证明成为瓶颈，且需要更强隔离 | 可把热路径完全移出 Python 进程；跨宿主复用更强 | 架构和运维复杂度明显上升；需要自建时序、一致性、恢复 contract | 中 | 高 | 未来扩展 | future extension |
| C. Pure native in-process plugin / host fork | 直接绕开当前 Python-host contract，把 native plugin 嵌到宿主内部 | 只有在宿主提供稳定 native ABI 或明确接受 fork 时 | 理论上 crossing 最少 | 对当前 Nautilus 形态侵入最大；长期维护风险最高 | 低 | 高 | 拒绝 | rejected |
| D. C++ full-stack rewrite | 用 C++ 替代 Rust 作为主要 runtime 实现语言 | 团队明确放弃 Rust 工具链并接受重写成本 | 可直接贴 CTP SDK | 不能天然解决 crossing / batching / ownership 问题；重写成本高 | 低 | 高 | 拒绝作为当前默认路线 | rejected |

### 3.1 Landing Evidence / 落地证据

| 方案 | decision_state | landing_state | evidence_state | evidence_ref | residual_risk |
| --- | --- | --- | --- | --- | --- |
| A | included | not_implemented | docs_only | 本 ADR + architecture docs + active change | 仍需后续 runtime child change 把 batching / buffer / state machine 下沉完毕 |
| B | future | not_implemented | docs_only | 本 ADR | 需要真实测量证明 Python batch bridge 已成为主瓶颈 |
| C | rejected | not_started | docs_only | 本 ADR | 宿主耦合和维护风险过高 |
| D | rejected | not_started | docs_only | 本 ADR | 语言替换不能代替主线边界优化 |

### 3.2 架构一致性分析 / Architecture Consistency Analysis

1. 方案 A 与当前 [platform-neutral-ctp-runtime](../architecture/platform-neutral-ctp-runtime.md)、[rust-python-adapter-split](../architecture/rust-python-adapter-split.md) 和 [runtime-performance-guidelines](../architecture/runtime-performance-guidelines.md) 最一致：它保留单一 runtime owner、单一 host adapter 层，并把性能优化放在 runtime 内部和 batch crossing 上，而不是重写宿主协议。
2. 方案 B 只有部分一致。它仍保持 native-first，但会把当前 in-process adapter split 扩展成跨进程架构，因此只有在量测证明 batch bridge 已经成为主瓶颈时，才值得承受额外的 IPC、一致性、运维和 recovery contract 成本。
3. 方案 C 与当前架构明显冲突：它会把当前 Python-facing Nautilus entry 绕开或 fork 掉，形成第二 host integration truth，等价于以“最高性能”名义引入第二 mainline。
4. 方案 D 与现有“Rust 已是正式 runtime 主线”冲突较大。它既不能自动消除 crossing，也不能自动消除 owner 分叉；如果仅以语言替换推进，会把当前已收敛的 Rust runtime ownership 打散成新的重写工程。
5. 因此，本 ADR 的一致性结论是：优先收紧 A，而不是以 C/D 的结构性重写来替代 A 的边界治理；B 只能在量测证据充分后作为后续 proposal 进入评审。

### 3.3 取舍说明 / Trade-Off Notes

1. 方案 B 不是被否决，而是被降级为 future extension。它只有在 `submit_command/drain_events` 批量边界、runtime queue、buffer 复用都已落地后，仍被 benchmark 证明不足时才允许进入正式 proposal。
2. 方案 C 不能作为长期正式方案，因为它会把性能优化建立在宿主 fork 或第二 host ABI 上，代价是长期维护和接口稳定性显著恶化。
3. 方案 D 不能作为默认性能路线，因为“语言切换”无法替代“owner 边界、批量 crossing、runtime state 收口”这些真正决定性能的因素；只有在组织层面明确放弃 Rust 工具链时，才值得单独立项讨论。

---

## 4. 决策 / Decision

### 4.1 决策结论 / Decision Summary

1. 拟采用方案 A 作为正式高性能主线：native-first runtime + thin Python host glue。
2. 拟拒绝方案 C 进入当前长期主线；在没有稳定 native host ABI 或用户明确批准 fork 的前提下，不得把 pure native in-process plugin 作为默认方向。
3. 拟拒绝把方案 D 作为默认性能答案；除非后续有明确组织级理由，否则“改写成 C++”不构成当前仓库的首选性能优化路径。
4. 方案 B 保留为未来扩展，但前置条件是已有 batch bridge 主线被测量证明成为瓶颈，而不是基于猜测提前重构。

### 4.2 决策边界 / Decision Boundaries

1. 正式 truth source 仍是 repository-owned native boundary + Rust runtime mainline；Python adapter 不是 runtime truth source。
2. Python 层允许保留 `config`、`factory`、`InstrumentProvider`、`LiveDataClient`、`LiveExecutionClient` 等宿主整合外壳，但这些外壳不得继续积累 callback parsing、state machine、query lifecycle ownership、或 per-event hot loop。
3. adapter-facing runtime contract 应维持小而稳定的批量边界，例如 `submit_command(command)`、`drain_events(limit)`，以及后续在同一抽象层上的 batch query / batch event draining；不得新增第二套逐事件 Python callback mainline。
4. `ctp_native` / vendor bridge / callback registration / normalized event queue / login-reconnect-settlement / order lifecycle / query lifecycle 等热路径应继续向 Rust 或 repository-owned native boundary 收口。

### 4.3 Design Kernel / 设计内核

1. 稳定组件边界：
   - repository-owned native boundary：最薄 C ABI、vendor DLL 对接、raw callback ingress
   - Rust runtime：normalize、buffer、state machine、query/trading/market separation、adapter-facing batch bridge
   - Python host glue：Nautilus config/factory/provider/client 壳与最薄 host translation
2. 数据流方向：`CTP native callback -> native boundary -> Rust runtime queue -> normalized batch event -> Python adapter -> Nautilus host`。
3. owner 边界：runtime correctness、performance、state、query truth 均归 native/Rust；Python 不得成为第二 owner。
4. negative constraints：
   - 不允许 Python per-tick mainline
   - 不允许 managed bridge 重新成为生产中心
   - 不允许为了“纯 native”口号引入第二条正式路径
   - 不允许以 fallback 形式保留旧 host-specific runtime ownership

### 4.4 推荐产物 / Recommended Deliverables

1. 明确 runtime batch contract 的后续 child change。
2. 明确 market data / trading / query 分队列或分模块的 runtime 设计文档与测试锁。
3. 明确 Python adapter thin-shell contract，防止 runtime logic 回流。
4. 同步更新 README、architecture docs、相关 runbook，使 operator 能区分 repo-only probe、formal live verdict、runtime performance path。

### 4.5 决策覆盖与落地矩阵 / Decision Coverage And Landing Matrix

| 决策项 | 必须覆盖的落点 | 覆盖状态 | 承接 proposal / change | executable evidence | docs evidence | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
| D1. Native owns hot path | runtime / native / tests | boundary_locked | `p001-ADR001-native-first-runtime-rollout` + `20260529__runtime-performance__p2-native-hot-path-ownership-cutover` | source inventory + docs gates | 本 ADR + performance docs + proposal p001 + Phase 2 child change | 真实代码迁移仍由后续 implementation changes 承接 |
| D2. Python stays thin host glue | adapter / tests / README | boundary_locked | `p001-ADR001-native-first-runtime-rollout` + `20260529__runtime-performance__p3-thin-python-host-glue-contract-lock` | focused guard path + docs gates | 本 ADR + rust/python split + proposal p001 + Phase 3 child change | 物理删除旧 helper 仍由后续 changes 承接 |
| D3. Batch boundary is canonical | runtime bridge / tests | completed | `p001-ADR001-native-first-runtime-rollout` + `20260529__runtime-performance__p1` | `check_rust_gate.py` + focused pytest | 本 ADR + runtime docs + proposal p001 + Phase 1 child change | 后续 Phase 2 仍需 owner inventory，不影响 D3 closeout |
| D4. Daemon path requires measurement gate | proposal / docs | boundary_locked | `p001-ADR001-native-first-runtime-rollout` + `20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision`; future proposal if needed | `check_runtime_performance_gate.py` lower-bound gate + policy | 本 ADR + proposal p001 + Phase 4 child change | live/formal benchmark 仍需 successor proposal 承接 |
| D5. Managed bridge remains non-mainline | docs / scripts / runbook | policy_locked | `20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff` | 当前 change 证据 | 本 ADR + existing architecture docs | vendor-bridge readiness change 仍独立推进，不由 P001 改 scope |

---

## 5. Landing Map / 落地映射

### 5.0 Accepted Decision Boundary / 已接受决策边界

（待决策后填写）

### 5.0.1 Not Accepted By This ADR / 本 ADR 不接受

1. 不接受把“删除 Python 文件数量”当成性能目标本身。
2. 不接受在没有量测证据的前提下直接切到 external daemon 或 pure native plugin。
3. 不接受以 managed bridge、compat path 或第二 host integration mainline 作为性能捷径。

### 5.0.2 Successor Proposal Boundary / 后续 Proposal 边界

| Phase | 目标 | 承接 proposal / change | 退出条件 | retirement 影响 | 承接状态 / Landing Status |
| --- | --- | --- | --- | --- | --- |
| Phase 0 | 冻结 vendor bridge readiness 与当前 runtime mainline 边界 | [20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff](../changes/20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff/plan.md) | 当前临时桥接路径、formal live verdict 与 blocker 口径已冻结 | 为后续 managed bridge / scaffold path retirement 建 inventory | active via change 20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff |
| Phase 1 | 只冻结 adapter-facing batch boundary | [p001-ADR001-native-first-runtime-rollout](../proposals/p001-ADR001-native-first-runtime-rollout/README.md) + [20260529__runtime-performance__p1](../changes/20260529__runtime-performance__p1/plan.md) | 唯一 batch runtime boundary 已冻结，且 per-event Python callback 不再是默认长期接口；hot-path owner inventory 仍保留给 Phase 2 | 为后续 owner inventory / migration boundary 提供唯一接口面 | completed via change 20260529__runtime-performance__p1 |
| Phase 2 | 只冻结 hot-path owner inventory 与 migration boundary | [p001-ADR001-native-first-runtime-rollout](../proposals/p001-ADR001-native-first-runtime-rollout/README.md) + [20260529__runtime-performance__p2-native-hot-path-ownership-cutover](../changes/20260529__runtime-performance__p2-native-hot-path-ownership-cutover/plan.md) | query / market / trading hot path 的 owner、暂留 Python 项与迁出边界已冻结；thin-shell contract 仍保留给 Phase 3 | 开始压缩 Python runtime ownership，但不把 thin-shell closeout 提前混入 | completed via change 20260529__runtime-performance__p2-native-hot-path-ownership-cutover |
| Phase 3 | 只冻结 thin Python host glue contract | [p001-ADR001-native-first-runtime-rollout](../proposals/p001-ADR001-native-first-runtime-rollout/README.md) + [20260529__runtime-performance__p3-thin-python-host-glue-contract-lock](../changes/20260529__runtime-performance__p3-thin-python-host-glue-contract-lock/plan.md) | Python adapter 的合法 host shell、禁止回流的 runtime logic 类别与 focused guard evidence 路径已冻结 | 进入旧 helper / legacy boundary retirement | completed via change 20260529__runtime-performance__p3-thin-python-host-glue-contract-lock |
| Phase 4 | 只冻结 benchmark gate 与 daemon trigger policy | [p001-ADR001-native-first-runtime-rollout](../proposals/p001-ADR001-native-first-runtime-rollout/README.md) + [20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision](../changes/20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision/plan.md)；future proposal if needed | benchmark 命令、阈值、formal artifact boundary 与 daemon trigger policy 已冻结 | 若进入 daemon 路线，旧 in-process assumptions 需文档收口 | completed via change 20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision |

### 5.1 旧代码退役与文档收口 / Legacy Retirement And Documentation Closure

| 旧项 / 路径 | 当前职责 | 新归宿 / 替代物 | 处理动作 | 暂留边界 | 最终移除条件 | 文档同步项 | 承接状态 / Landing Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temporary managed bridge wording | 历史临时 bootstrap / smoke 描述 | Rust-owned runtime + formal live verdict wording | 降级为 debug-only / reference-only 描述 | 在 vendor bridge readiness closeout 前仍可作为 blocker 背景 | formal live path 与 vendor bridge 全部稳定后 | README / runbook / topic docs | active via change 20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff |
| Python-side runtime ownership creep | 在 adapter 层继续放入 parse / state / query logic 的风险 | native-first runtime + thin-shell contract | 通过后续 change 收口并补 contract lock | 当前仓库仍有部分 placeholder / bootstrap logic | successor runtime changes verified | ADR / README / tests | planned via proposal p001 |

---

## 6. Acceptance And Evidence / 验收与证据

### 6.0 ADR-Level Acceptance Only / 仅限 ADR 级验收

本 ADR accepted 的条件是“正式架构边界已被评审确认”，不是“所有 runtime 实现已完成”。

### 6.1 通用规则 / General Rules

1. 每个 child change 在回填 `acceptance.md` 前，先补对应 `[CONTRACT-LOCK]` 测试。
2. 正式验收只认结构化证据：contract tests、定向行为测试、性能结果、文档回填与 evidence path。
3. 不得以人工点页面、口头结论或临时截图替代正式验收。

### 6.2 Architecture-Level Acceptance

1. 若本 ADR 被 accepted，正式主线必须明确写成“native owns hot path, Python owns host integration only”。
2. 任一后续实现若把 normalize、state machine、query lifecycle 或 per-event hot loop 放回 Python，应视为违反本 ADR。
3. 任一后续 proposal 若主张 external daemon，必须先给出 batch bridge 已成为主瓶颈的测量证据。
4. D1-D4 至少需要 successor change 的 executable evidence 后，才能从 `planned` 升到 `implemented/verified`。
5. D5 需要现有 active change closeout 与 runbook/README 同步，才能视为 retirement 闭环的一部分。

### 6.3 ADR Closeout Distillation / ADR closeout 沉淀

P001 closeout 后的稳定沉淀：

1. 正式高性能主线已接受为 `native-first runtime + thin Python host glue`。
2. Adapter-facing boundary 已锁定为 `submit_command(command)` / `drain_events(limit)`。
3. Hot-path owner inventory、thin-shell contract、benchmark gate 与 daemon trigger policy 已分别由 P001 Phase 2-4 child changes 收口。
4. 一次性 gate 输出和 generated benchmark JSON 留在 child change acceptance / output report，不复制进 ADR。

---

## 7. Related Documents / 关联文档

1. [Platform-neutral CTP runtime](../architecture/platform-neutral-ctp-runtime.md)
2. [Rust / Python adapter split](../architecture/rust-python-adapter-split.md)
3. [Runtime performance guidelines](../architecture/runtime-performance-guidelines.md)
4. [P001 ADR001 Native-First Runtime Rollout](../proposals/p001-ADR001-native-first-runtime-rollout/README.md)
5. [Vendor bridge readiness and SDK handoff plan](../changes/20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff/plan.md)
