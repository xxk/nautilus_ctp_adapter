# P002 Change Map / Child Change 映射

**fragment-id**：`change_map`
**适用场景**：多个 child change 需要映射追踪。

---

## Phase Map

| Phase | Child Change | 依赖 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| Phase 0 | proposal-only planning | 本 proposal scaffold | completed | proposal docs gate |
| Phase 1 | `20260608__nautilus-provider-readiness__instrument-provider-cache-hydration` | Phase 0 | completed | shared CTP-aware provider + metadata staging + FuturesContract hydration repo-only evidence |
| Phase 2 | `20260608__nautilus-provider-readiness__marketdata-provider-live-loop` | Phase 1 | completed | provider-backed tick resolution, unknown diagnostic, no-fabrication, and provider-backed subscription symbol repo-only evidence |
| Phase 3 | `20260608__nautilus-provider-readiness__execution-event-reporting` | Phase 1 | completed | order/trade callbacks map to Nautilus reports; report APIs return cached CTP reports |
| Phase 4 | `20260608__nautilus-provider-readiness__query-report-generation` | Phase 1 / Phase 3 | completed | CTP position rows map to PositionStatusReport; account rows map to AccountState |
| Phase 5 | `20260608__nautilus-provider-readiness__live-ops-evidence-readiness` | Phase 2 / Phase 3 / OpenCTP paper account conditions | completed | C8 OpenCTP paper baseline reused; formal-trading remains final evidence only |

## 顺序规则

1. 每个 child change 必须能追溯到一个 proposal phase。
2. 若 phase 目标变化，应先更新 `phase-plan.md`，再更新本映射。
3. completed child change 不等于 proposal closeout，proposal closeout 仍以 `acceptance.md` 为准。
4. Phase 1 是优先 first executable slice；它不依赖 live CTP 条件，应该先被 autopilot 承接。
5. Phase 5 可以复用 C8 OpenCTP paper baseline；provider-specific OpenCTP paper evidence 缺失时只能 typed blocked，不能让 Phase 1-4 的 repo-only contract work 停止。
6. 生产 formal-trading evidence 只用于 final pre-go-live，不得作为 P002 日常开发账户闭环。



