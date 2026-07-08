# Batch Runtime Boundary Freeze 设计

**状态**：进行中
**日期**：2026-05-29
**范围**：adapter-facing runtime batch boundary
**关联 plan**：./plan.md

## 一、现状

P001 已把 ADR001 rollout 拆成 Phase 1-4。Phase 1 的唯一职责是冻结 adapter-facing batch runtime boundary，避免实现继续在 Python per-event callback 语义上漂移。

当前 source 已有两个 batch-shaped evidence：

1. Python placeholder bridge：`src/nautilus_ctp_adapter/runtime/bridge.py`
2. Rust native runtime：`rust/ctp_runtime_core/src/native.rs`

两者都已经围绕 command queue 和 event queue 工作，但这条边界还没有作为 Phase 1 child change 的正式 contract 冻结。

## 二、正式入口与实现落点

正式 boundary：

1. Command ingress：`submit_command(command)`
2. Event egress：`drain_events(limit)`

允许的辅助面：

1. `drain_submitted_commands(limit)` 可作为 repo-local diagnostic / test inspection surface。
2. `pending_command_count` / `pending_event_count` 可作为 diagnostic counter。
3. Adapter-local helpers such as `drain_marketdata_event_batch(limit)` may package already-drained runtime events for Nautilus consumption, but they must not become a second runtime API.

非正式主线：

1. Python per-event callback mainline
2. one Python crossing per tick as default host boundary
3. second adapter-facing runtime API parallel to command submission + bounded event draining
4. daemon / IPC path without Phase 4 benchmark gate

## 三、设计方案

本 change 冻结的 contract 是：

```text
adapter submits normalized runtime commands in batches or discrete command objects
  -> runtime/native side owns queueing, callback ingress, normalization, state updates
  -> adapter drains normalized runtime events with an explicit limit
```

Phase 1 只冻结这个 contract 和 guard 口径。后续 Rust/native implementation 可以优化 queue、buffer、allocator、event representation 或 internal module split，但不能要求 host adapter 改用另一套 long-term API。

Phase 2 将在该 boundary 之上冻结 owner inventory。Phase 3 将在该 boundary 之上冻结 Python host glue allowlist / forbidden list。Phase 4 将在该 boundary 量测后判断 daemon 是否需要进入 future proposal。

## 四、接口与输入输出

| 接口 | 输入 | 输出 | Phase 1 约束 |
| --- | --- | --- | --- |
| `submit_command(command)` | normalized runtime command | no direct event return | command ingress 主线 |
| `drain_events(limit)` | optional non-negative limit | list / vector of normalized events | event egress 主线；`limit` 必须 bounded |
| `drain_submitted_commands(limit)` | optional non-negative limit | submitted commands | diagnostic / guard only，不是 host long-term API |

失败语义：

1. `limit < 0` 一类非法输入必须 fail fast。
2. API 扩展若形成第二套 host-facing runtime path，必须进入 reframing，不得静默合并。

## 五、AI 实现约束

1. 不得新增 callback-per-event host boundary。
2. 不得把 adapter-local helper 写成 runtime-wide second API。
3. 不得把 Phase 2 owner inventory、Phase 3 thin-shell contract 或 Phase 4 benchmark gate 写成当前已完成。
4. 不得为了“先跑通”增加 fallback / compat / silent downgrade path。

## 六、备选方案

| 方案 | 结论 | 原因 |
| --- | --- | --- |
| 继续允许 Python per-event callback | 拒绝 | 与 ADR001 / runtime performance guidelines 冲突，且会把 hot path 留在 Python crossing 上 |
| 直接切 daemon / IPC | 拒绝作为本 phase 内容 | 需要 Phase 4 benchmark gate 证明 batch bridge 是瓶颈 |
| 先冻结 batch boundary，再做 owner inventory | 采用 | 先稳定 host-facing contract，后续迁移不再反复改 adapter API |

## 七、风险与影响面

1. 若只写文档不补 guard，后续实现仍可能引入第二套 API。
2. 若 Phase 1 混入 owner inventory，Phase 2 会失去独立验收边界。
3. 若把 adapter-local batch helper 当成 runtime boundary，可能导致 Nautilus-specific fast path 泄漏进 shared runtime design。

## 八、发布回滚与退出策略

本 change 是文档/contract freeze，不涉及部署回滚。若后续发现 boundary 不足，应通过 P001 Phase 1 reframing 修改 contract，而不是在实现中静默新增旁路。

## 九、需要沉淀为长期规则的内容

1. Adapter-facing runtime boundary defaults to command submission + bounded event draining.
2. Python per-event callback is not a long-term performance mainline.
3. External daemon requires Phase 4 benchmark gate and a separate proposal.
