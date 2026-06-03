# Benchmark Gate And Daemon Trigger Policy 设计

**状态**：completed
**日期**：2026-05-29
**范围**：P001 Phase 4 benchmark gate / daemon trigger policy
**关联 plan**：./plan.md

## 一、Gate Contract

Current repo-local gate:

```powershell
python scripts/check_runtime_performance_gate.py --events 5000 --limit 1000 --min-events-per-sec 1000
```

This gate measures synthetic batch drain throughput on `CtpRuntimeBridge`. It is a lower-bound regression gate, not a live performance benchmark.

## 二、Artifact Boundary

| Artifact | Path | Trust level |
| --- | --- | --- |
| runtime performance gate JSON | `output/reports/p001-ADR001-native-first-runtime-rollout/runtime_performance_gate.json` | repo-local benchmark artifact |
| proposal acceptance | `docs/proposals/p001-ADR001-native-first-runtime-rollout/acceptance.md` | proposal state |
| child change acceptance | current `acceptance.md` | change evidence |

The JSON artifact is generated output and is not the ADR authority. ADR001 may point to this gate, but must not copy benchmark output as architecture text.

## 三、Threshold

The default lower-bound threshold is:

1. All submitted synthetic events must be drained.
2. `events_per_sec >= 1000`.
3. The command must fail non-zero if the threshold is missed.

This low threshold is intentional: it only catches severe local regressions and proves the gate is executable. Production/live performance thresholds require a successor benchmark proposal.

## 四、Daemon Trigger Policy

Daemon remains forbidden by default.

A daemon proposal may only be opened when all conditions hold:

1. P001 Phase 1 batch boundary is completed.
2. P001 Phase 2 owner inventory is completed.
3. P001 Phase 3 thin-shell contract is completed.
4. A formal benchmark artifact shows the in-process batch bridge is the bottleneck.
5. The new proposal defines IPC semantics, recovery semantics, artifact boundary and operator runbook.

The repo-local gate in this change cannot satisfy item 4 by itself.

## 五、Failure Semantics

| Failure | Meaning | Required action |
| --- | --- | --- |
| gate command fails | local batch drain regression or environment issue | fix local regression before claiming P001 closeout |
| no live benchmark exists | daemon cannot be approved | keep daemon as future proposal only |
| benchmark output copied into ADR body | evidence / architecture mixed | move output to acceptance or generated report |

## 六、Relationship To P001

P001 is complete when this policy and gate are frozen. P001 does not assert that the runtime has reached final performance limits.
