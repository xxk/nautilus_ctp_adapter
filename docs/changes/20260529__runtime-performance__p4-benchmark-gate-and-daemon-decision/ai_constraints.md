# Benchmark Gate And Daemon Trigger Policy AI Constraints

**change-id**：20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision
**关联 plan**：./plan.md
**关联 acceptance**：./acceptance.md

## 必读上下文

1. P001 proposal bundle.
2. ADR001.
3. Phase 1-3 child changes.
4. `scripts/check_runtime_performance_gate.py`.
5. `docs/architecture/runtime-performance-guidelines.md`.

## 允许

1. Run the repo-local performance gate.
2. Update benchmark gate docs and daemon trigger policy.
3. Backfill P001 / ADR001 / architecture / scripts README.

## 禁止

1. Do not claim live performance pass from synthetic benchmark output.
2. Do not approve daemon or IPC implementation inside P001.
3. Do not write generated benchmark JSON into ADR body.
4. Do not silently lower the threshold to pass a regression.

## 验收纪律

1. Completed means the gate and trigger policy are frozen and executable.
2. Daemon remains future proposal only.
3. Missing live benchmark is not a blocker for P001 closeout because P001 closes the policy boundary, not daemon implementation.
