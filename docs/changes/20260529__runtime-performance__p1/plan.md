---
change-id: "20260529__runtime-performance__p1"
dependencies:
  hard_blocking:
    - id: "p001-ADR001-native-first-runtime-rollout"
      reason: "Phase 1 必须继承 ADR001 rollout carrier 已冻结的 phase split、artifact boundary 与 daemon gate 口径"
      expected_status: in_progress
  soft_dependency:
    - id: "20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff"
      reason: "vendor bridge / SDK handoff 仍是 live-ready 背景依赖，但不得成为本 change 的性能 rollout carrier"
      expected_status: blocked-completed
  blocked_by: []
---

# Batch Runtime Boundary Freeze 开发计划

**状态**：进行中
**进度**：25%
**日期**：2026-05-29
**范围**：`docs/proposals/p001-ADR001-native-first-runtime-rollout/`、`docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md`、`docs/architecture/runtime-performance-guidelines.md`、`src/nautilus_ctp_adapter/runtime/`、`rust/ctp_runtime_core/src/`
**topic-id**：adr001-native-first-runtime-rollout
**execution_order**：1
**change-id**：20260529__runtime-performance__p1
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 承接 P001 Phase 1，只冻结 adapter-facing batch runtime boundary。
2. 明确当前唯一主线接口是 command submission + bounded event draining，而不是 Python per-event callback mainline。
3. 明确本 change 不做 hot-path owner inventory、不做 thin Python shell contract、不做 benchmark / daemon 判定。
4. 用 source evidence、proposal evidence 和 focused guard 入口证明后续实现只能围绕同一 batch boundary 推进。

## 二、能力映射 / Capability Mapping

```text
- capability_id: runtime-batch-boundary-freeze
- capability_name: Adapter-facing batch runtime boundary freeze
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/proposals/p001-ADR001-native-first-runtime-rollout/phase-plan.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md, /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/proposals/p001-ADR001-native-first-runtime-rollout/design.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change bundle、P001 proposal 文档、ADR001 landing map、runtime performance architecture 文档、必要的 focused tests。
2. 禁止修改：vendor 私有 SDK / DLL、live trading config、当前 vendor-bridge active change 的 scope、Phase 2-4 的执行内容。
3. 当前正式入口与主要落点：
   - 文档入口：P001 `phase-plan.md` / `change-map.md` / `acceptance.md`
   - Runtime source evidence：`src/nautilus_ctp_adapter/runtime/bridge.py`、`rust/ctp_runtime_core/src/native.rs`
   - Guard evidence：focused pytest around bridge batching if code/test changes are needed
4. AI 开始前必须阅读：
   - P001 全部文件
   - ADR001
   - `docs/architecture/runtime-performance-guidelines.md`
   - `src/nautilus_ctp_adapter/runtime/bridge.py`
   - `rust/ctp_runtime_core/src/native.rs`
5. 改完后必须执行：
   - `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout`
   - `python scripts/check_harness.py`
   - 若新增或修改 focused tests，再执行对应 pytest。

## 四、背景与约束

P001 已完成 proposal convergence，并把 Phase 1 定义为 batch boundary freeze。当前 Python placeholder bridge 和 Rust native runtime 都已存在 `submit_command(...)` / `drain_events(limit)` 形态，但该 contract 还没有作为 Phase 1 child change 的唯一边界正式冻结。

本 change 的关键是把“后续只能围绕 batch contract 前进”写成可验收执行包，避免继续在 Python per-event callback、第二套 adapter-facing API 或 daemon 默认化方向漂移。

## 五、设计方案

1. Canonical batch boundary：
   - command ingress：`submit_command(command)`
   - event egress：`drain_events(limit)`
   - diagnostic / transitional command drain：`drain_submitted_commands(limit)` 只作为 repo-local guard / bridge inspection surface，不成为 host-facing long-term second API。
2. Python adapter 允许调用 batch boundary 做 host integration，但不得新增逐 tick / 逐 callback Python mainline。
3. Runtime side 后续实现可以在 Rust/native 内部拆分 queue、buffer、normalize、state machine，但 adapter-facing public boundary 不应扩张成第二套 API。
4. Phase 2 owner inventory、Phase 3 thin-shell contract、Phase 4 benchmark gate 只能引用本 boundary，不能反向改写 Phase 1 完成定义。

## 六、阶段划分

1. P1：创建 Phase 1 child change bundle，冻结 scope 和验收场景。
2. P2：回写 P001，使 Phase 1 指向本 change，并把 P001 状态推进到 `in_progress`。
3. P3：确认 source evidence 中已存在 batch-shaped bridge，并记录 focused guard 入口。
4. P4：必要时补充最小 focused tests，锁定 `limit` 语义和 per-event callback 不成为正式主线。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立 Phase 1 child change bundle | P001 Phase 1 | 当前 change bundle | plan / acceptance / ai_constraints / design | 文档审阅 | P001 | change scope 清楚，不混入 Phase 2-4 | 进行中 |
| P2 | 回写 P001 Phase 1 状态与 change map | P001 Phase 1 | P001 phase-plan / change-map / acceptance | Phase 1 指向本 change | `check_proposal_docs` | P001 | P001 进入 in_progress，Phase 1 有真实 child change | 未开始 |
| P3 | 冻结 batch boundary source evidence | ADR001 D3 | `design.md`、必要 architecture docs | source evidence table | source review / targeted tests | ADR001 / architecture | `submit_command` / `drain_events(limit)` 为唯一主线 | 未开始 |
| P4 | 补 focused guard 或记录现有 guard | A5/A6 | tests 或 evidence section | guard evidence | targeted pytest if touched | acceptance | 第二套 API / per-event mainline 被阻断 | 未开始 |

## 八、验证动作

```powershell
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
python scripts/check_harness.py
```

若修改 tests：

```powershell
python -m pytest tests/test_smoke_import.py -q
```

## 九、完成定义

### 开发完成

1. 当前 change bundle 已建立并冻结 Phase 1 scope。
2. P001 Phase 1 已指向当前 change。
3. batch boundary 的 source evidence 与 focused guard 入口已记录。

### 交付完成

1. `acceptance.md` 中 A1-A6 均有证据。
2. P001 docs gate 通过。
3. 未把 Phase 2 owner inventory、Phase 3 thin-shell contract 或 Phase 4 benchmark gate 混入本 change 的完成定义。

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

本次新增长期规则：adapter-facing runtime boundary 默认收敛到 command submission + bounded event draining；不得引入 Python per-event callback mainline 或第二套 host-facing runtime API。

## 十一、回写与相关变更 / Write-back & Related Changes

1. 必须回写 P001 `phase-plan.md`、`change-map.md`、`acceptance.md`。
2. 若本 change 完成后形成稳定长期规则，应回写 ADR001 和 `runtime-performance-guidelines.md`。

## 十二、阻塞项

无真实外部依赖阻塞。若后续要证明 live performance，则属于 Phase 4 benchmark gate，不属于本 change。

## 十三、进度记录

1. 2026-05-29：基于 P001 Phase 0 closeout，创建 Phase 1 batch-boundary child change，先冻结执行边界与验收面。
