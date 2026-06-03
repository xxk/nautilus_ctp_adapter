# Change Map Fragment

**fragment-id**：`change_map`
**适用场景**：多个 child change 需要映射追踪。

---

## Phase Map

| Phase | Child Change | 依赖 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| Phase 0 Proposal convergence | `proposal-only planning` | ADR001 已创建 | completed | proposal scaffold + proposal docs write-back |
| Phase 1 Batch boundary freeze | `20260529__runtime-performance__p1` | Phase 0 | completed | batch contract source evidence、rust gate 与 focused pytest 已 closeout |
| Phase 2 Hot-path owner inventory / cutover boundary | `20260529__runtime-performance__p2-native-hot-path-ownership-cutover` | Phase 1；current vendor-bridge change 保持原 scope | completed | owner inventory / migration boundary 已 formalize |
| Phase 3 Thin Python host glue contract | `20260529__runtime-performance__p3-thin-python-host-glue-contract-lock` | Phase 2 | completed | contract-lock allowlist / forbidden-list / guard path 已创建 |
| Phase 4 Benchmark gate and daemon trigger policy | `20260529__runtime-performance__p4-benchmark-gate-and-daemon-decision` | Phase 1-3 | completed | benchmark command、threshold、artifact boundary 与 daemon trigger policy 已 formalize |

## 顺序规则

1. 每个 child change 必须能追溯到一个 proposal phase。
2. 若 phase 目标变化，应先更新 `phase-plan.md`，再更新本映射。
3. completed child change 不等于 proposal closeout，proposal closeout 仍以 `acceptance.md` 为准。
4. 当前 active change `20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff` 不是本 proposal 的 Phase 1-4 child change；它只作为当前 runtime / vendor-bridge 背景依赖。
5. Phase 1 不得吸收 Phase 2 owner inventory；Phase 2 不得吸收 Phase 3 thin-shell contract；Phase 4 必须单独冻结 benchmark 命令、阈值、artifact boundary 与 daemon trigger policy。
