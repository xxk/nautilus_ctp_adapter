---
change-id: "20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision"
dependencies:
  hard_blocking:
    - id: "20260529__runtime-performance__p1"
      reason: "benchmark gate 必须围绕已冻结的 batch boundary 量测"
      expected_status: completed
    - id: "20260529__runtime-performance__p2-native-hot-path-ownership-cutover"
      reason: "daemon trigger policy 需要先知道 hot-path owner inventory"
      expected_status: completed
    - id: "20260529__runtime-performance__p3-thin-python-host-glue-contract-lock"
      reason: "daemon trigger policy 需要先冻结 Python host glue 边界"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Benchmark Gate And Daemon Trigger Policy 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-05-29
**范围**：P001 Phase 4、runtime performance gate、daemon trigger policy
**topic-id**：adr001-native-first-runtime-rollout
**execution_order**：4
**change-id**：20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 承接 P001 Phase 4，冻结 benchmark gate 命令、阈值、artifact boundary 和 daemon trigger policy。
2. 新增 repo-local runtime performance gate，作为当前可复跑的 lower-bound gate。
3. 明确该 gate 不等于 live performance benchmark；daemon 仍不得默认化。
4. 若后续要走 external daemon，必须新建 proposal，并提供 formal/live benchmark evidence。

## 二、能力映射 / Capability Mapping

```text
- capability_id: runtime-benchmark-gate-and-daemon-trigger-policy
- capability_name: Runtime benchmark gate and daemon trigger policy
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR001 高性能优先原生主线适配边界_High-Performance Native-First Adapter Boundary.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：current change bundle、P001、ADR001、runtime performance docs、scripts README、repo-local benchmark gate script。
2. 禁止修改：live trading config、vendor DLL/SDK、external daemon implementation。
3. 必须执行：
   - `python scripts/check_runtime_performance_gate.py --events 5000 --limit 1000 --min-events-per-sec 1000`
   - proposal docs gate
   - change docs gate
   - harness gate

## 四、设计方案

1. Current gate command:
   `python scripts/check_runtime_performance_gate.py --events 5000 --limit 1000 --min-events-per-sec 1000`
2. Formal artifact boundary:
   `output/reports/p001-ADR001-native-first-runtime-rollout/runtime_performance_gate.json`
3. Threshold:
   synthetic runtime bridge batch drain must process at least `1000` events/sec and drain all submitted events.
4. Daemon trigger policy:
   this gate can block obvious local regressions, but it can never approve daemon by itself. Daemon requires a successor proposal with live/formal benchmark evidence proving the in-process batch bridge is the bottleneck.

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 创建 Phase 4 child change bundle | P001 A10/A11 | 当前 bundle | 四件套 | docs review | P001 | scope 清楚 | 已完成 |
| P2 | 新增 repo-local performance gate | P001 A10 | `scripts/check_runtime_performance_gate.py` | benchmark command | script execution | scripts README | command 可复跑 | 已完成 |
| P3 | 冻结 artifact boundary / threshold | P001 A10 | design.md / acceptance | gate contract | command output | P001 / ADR001 | 阈值与输出路径清楚 | 已完成 |
| P4 | 冻结 daemon trigger policy | ADR001 D4 | design.md / ADR001 | no-daemon-default rule | docs review | ADR001 / architecture | daemon 仍需 separate proposal | 已完成 |

## 六、验证动作

```powershell
python scripts/check_runtime_performance_gate.py --events 5000 --limit 1000 --min-events-per-sec 1000
python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
```

## 七、完成定义

1. Benchmark command, threshold and artifact boundary are frozen.
2. Daemon trigger policy is explicit and keeps daemon as separate proposal.
3. P001 A10/A11 are completed without declaring live performance pass.

## 八、长期规则增量摘要 / Long-Term Rule Delta Summary

External daemon is forbidden by default. It can only be proposed after formal benchmark evidence shows the in-process batch bridge is the bottleneck after Phase 1-3 boundaries are satisfied.

## 九、阻塞项

无。Live performance proof is intentionally out of scope for P001 closeout and must be handled by a successor proposal if needed.
