---
change-id: "20260529__runtime-performance__p2-native-hot-path-ownership-cutover"
dependencies:
  hard_blocking:
    - id: "p001-ADR001-native-first-runtime-rollout"
      reason: "Phase 2 继承 P001 Phase 0-1 已冻结的 proposal carrier 与 batch runtime boundary"
      expected_status: in_progress
    - id: "20260529__runtime-performance__p1"
      reason: "owner inventory 必须建立在已冻结的 submit_command / drain_events batch boundary 上"
      expected_status: completed
  soft_dependency:
    - id: "20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff"
      reason: "vendor bridge readiness 仍是背景依赖，但不成为本 change 的 owner inventory carrier"
      expected_status: in_progress
  blocked_by: []
---

# Hot-Path Owner Inventory / Cutover Boundary 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-05-29
**范围**：P001 Phase 2、runtime / adapter owner inventory、migration boundary
**topic-id**：adr001-native-first-runtime-rollout
**execution_order**：2
**change-id**：20260529__runtime-performance__p2-native-hot-path-ownership-cutover
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 承接 P001 Phase 2，冻结 query / market / trading hot path 的 owner inventory。
2. 明确哪些 Python 项只是暂留 host glue 或 transitional runtime placeholder，哪些必须向 Rust/native 迁出。
3. 不执行真实 runtime cutover，不宣称 hot path 已全部 native 化。
4. 用 source evidence、architecture write-back 与 focused tests 入口证明后续 child changes 有明确迁移边界。

## 二、能力映射 / Capability Mapping

```text
- capability_id: native-hot-path-owner-inventory
- capability_name: Hot-path owner inventory and cutover boundary
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md, /D:/Nautilus/nautilus_ctp_adapter/docs/proposals/p001-ADR001-native-first-runtime-rollout/phase-plan.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change bundle、P001 proposal 文档、ADR001 landing map、runtime architecture docs。
2. 禁止修改：live trading config、vendor SDK/DLL、current vendor-bridge active change scope、Phase 3/4 的实际实现。
3. 当前正式入口与主要落点：
   - owner inventory：当前 `design.md`
   - long-term rule：`docs/architecture/runtime-performance-guidelines.md`
   - proposal projection：P001 `phase-plan.md` / `change-map.md` / `acceptance.md`
4. AI 开始前必须阅读：P001、ADR001、runtime performance docs、`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/`。
5. 改完后必须执行：
   - `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout`
   - `python scripts/check_change_docs.py --root .`
   - `python scripts/check_harness.py`

## 四、设计方案

Phase 2 冻结 owner inventory，不移动代码。正式 owner 规则见 sibling `design.md`：

1. Runtime truth / state / lifecycle target owner：Rust/native runtime。
2. Python adapter allowed owner：Nautilus host integration, config/factory/provider/client shell, source-to-host translation。
3. Transitional Python runtime placeholders must not grow new runtime ownership.
4. Phase 3 will add thin-shell contract lock; Phase 4 will add benchmark / daemon trigger policy.

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立 Phase 2 child change bundle | P001 A7 | 当前 bundle | plan / acceptance / ai_constraints / design | docs review | P001 | child change 有明确 scope | 已完成 |
| P2 | 冻结 hot-path owner inventory | ADR001 D1/D2 | design.md | owner inventory table | source review | architecture docs | query / market / trading owner 和暂留项清楚 | 已完成 |
| P3 | 冻结 migration boundary | P001 A7/A8 | design.md | cutover boundary | docs gate | P001 / ADR001 | 不宣称 full cutover | 已完成 |
| P4 | 回写 proposal / architecture | P001 closeout | P001 / ADR001 / architecture | 状态与 landing map | proposal gate | long-term docs | A7/A8 completed | 已完成 |

## 六、验证动作

```powershell
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
```

## 七、完成定义

1. owner inventory 和 migration boundary 已在 `design.md` 冻结。
2. P001 Phase 2 指向当前 child change。
3. ADR001 / architecture docs 只回写稳定 owner rule，不写一次性 evidence。
4. 没有把真实 hot-path cutover、thin-shell lock 或 benchmark gate 写进 Phase 2 完成定义。

## 八、长期规则增量摘要 / Long-Term Rule Delta Summary

本次新增规则：query / market / trading hot path 的 truth、state、lifecycle 与 performance owner 必须向 native/Rust runtime 收口；Python adapter 只保留 host integration 与显式 transitional placeholders。

## 九、回写与相关变更 / Write-back & Related Changes

1. 已回写 P001 Phase 2 映射。
2. 已回写 ADR001 landing matrix。
3. 已回写 runtime performance architecture docs。

## 十、阻塞项

无。真实代码迁移和 live cutover evidence 属于后续 implementation changes，不是本边界冻结 change 的 blocker。

## 十一、进度记录

1. 2026-05-29：创建 Phase 2 child change，冻结 owner inventory / migration boundary。
