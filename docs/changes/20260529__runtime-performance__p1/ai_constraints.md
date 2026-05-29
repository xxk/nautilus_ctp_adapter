# Batch Runtime Boundary Freeze AI Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260529__runtime-performance__p1
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 先读取 sibling `acceptance.md`。
2. 再读取 sibling `plan.md`。
3. 再读取 P001 proposal 全部文件和 ADR001。
4. 只要 sibling 文件可读，就不得停下来要求用户重复发送。

## 方法论 / Working Mode

1. 本 change 只承接 P001 Phase 1 batch boundary freeze。
2. 先锁定验收场景，再修改 proposal / architecture / tests。
3. test 只能作为 focused guard evidence，不能替代 source evidence。
4. 正式验收必须包含真实 repo source、真实 docs gate 或真实 guard 命令。

## 边界 / Boundaries

1. 不得完成或宣告完成 Phase 2 hot-path owner inventory。
2. 不得完成或宣告完成 Phase 3 thin Python host glue contract。
3. 不得完成或宣告完成 Phase 4 benchmark gate / daemon trigger policy。
4. 不得把 current vendor-bridge change 改写为本 change 的性能 rollout carrier。
5. 不得新增 Python per-event callback mainline 或第二套 adapter-facing runtime API。

## 必读上下文 / Required Context

1. `docs/proposals/p001-ADR001-native-first-runtime-rollout/README.md`
2. `docs/proposals/p001-ADR001-native-first-runtime-rollout/phase-plan.md`
3. `docs/proposals/p001-ADR001-native-first-runtime-rollout/acceptance.md`
4. `docs/proposals/p001-ADR001-native-first-runtime-rollout/design.md`
5. `docs/proposals/p001-ADR001-native-first-runtime-rollout/change-map.md`
6. `docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md`
7. `docs/architecture/runtime-performance-guidelines.md`
8. `src/nautilus_ctp_adapter/runtime/bridge.py`
9. `rust/ctp_runtime_core/src/native.rs`

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是当前 change 的唯一 AI 执行状态源。
2. 更新 YAML 后必须同步 Dashboard 派生字段。
3. A1-A6 全部通过前，不得把最终结论写成 passed。

## 收尾 / Wrap-up

1. 必须回写 P001 Phase 1 mapping。
2. 必须执行 proposal docs gate 和 harness gate。
3. 若触及 source/tests，必须执行最小 targeted pytest。
