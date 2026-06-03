---
change-id: "20260529__runtime-performance__p3-thin-python-host-glue-contract-lock"
dependencies:
  hard_blocking:
    - id: "20260529__runtime-performance__p2-native-hot-path-ownership-cutover"
      reason: "thin-shell contract 必须继承 Phase 2 owner inventory"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Thin Python Host Glue Contract Lock 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-05-29
**范围**：P001 Phase 3、Python adapter host-glue allowlist / forbidden-list、focused guard path
**topic-id**：adr001-native-first-runtime-rollout
**execution_order**：3
**change-id**：20260529__runtime-performance__p3-thin-python-host-glue-contract-lock
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 承接 P001 Phase 3，冻结 thin Python host glue contract。
2. 明确 Python adapter 的合法 allowlist 与禁止回流的 runtime logic forbidden-list。
3. 绑定 focused guard path，防止后续把 runtime truth 写回 Python adapter。
4. 不执行真实迁移，不修改 live config。

## 二、能力映射 / Capability Mapping

```text
- capability_id: thin-python-host-glue-contract-lock
- capability_name: Thin Python host glue contract lock
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change bundle、P001、ADR001、architecture docs、必要 focused guard references。
2. 禁止修改：runtime migration implementation、vendor SDK/DLL、live trading config、benchmark/daemon gate implementation。
3. 必须执行：proposal docs gate、change docs gate、harness gate、focused pytest if touched.

## 四、设计方案

Thin-shell contract 见 sibling `design.md`：

1. Allowlist：config/factory/provider/client shell、host translation、smoke orchestration、guardrail precheck、adapter-local event packaging。
2. Forbidden-list：callback parsing owner、state machine owner、query lifecycle owner、order lifecycle truth、per-event hot loop、fallback/compat bridge expansion。
3. Guard path：existing focused tests plus proposal/change docs gates.

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 创建 Phase 3 child change bundle | P001 A9 | 当前 bundle | 四件套 | docs review | P001 | scope 清楚 | 已完成 |
| P2 | 冻结 allowlist / forbidden-list | ADR001 D2 | design.md | contract lock | source review | architecture | 合法/非法 Python 职责清楚 | 已完成 |
| P3 | 绑定 focused guard path | P001 A8/A9 | design.md / acceptance | guard commands | pytest/gates | P001 | 有可复跑入口 | 已完成 |
| P4 | 回写 proposal / ADR / architecture | P001 closeout | P001 / ADR001 / architecture | stable contract pointer | docs gate | long-term docs | A8/A9 completed | 已完成 |

## 六、验证动作

```powershell
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
python -m pytest tests/test_smoke_import.py::test_runtime_bridge_submit_and_drain_contract -q
```

## 七、完成定义

1. Thin-shell allowlist / forbidden-list 已冻结。
2. Focused guard path 已写入 acceptance。
3. P001 Phase 3 映射到当前 child change。
4. 没有把 benchmark gate 或 daemon trigger policy 写入本 phase 完成定义。

## 八、长期规则增量摘要 / Long-Term Rule Delta Summary

Python adapter may remain as host glue, but cannot own runtime truth or hot-path lifecycle logic.

## 九、阻塞项

无。
