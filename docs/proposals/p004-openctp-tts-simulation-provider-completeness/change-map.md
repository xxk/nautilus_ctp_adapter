# P004 Change Map

**fragment-id**：`change_map`
**proposal-id**：`p004-openctp-tts-simulation-provider-completeness`
**状态**：completed

---

## Phase Map

| Phase | Child Change | 依赖 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| Phase 0 Proposal convergence | proposal-only planning | P003 completed | completed | P004 docs created |
| Phase 1 Cancel lifecycle | `20260608__openctp-tts-simulation-provider__cancel-lifecycle` | P003 guarded order baseline | completed | acceptance rows P4-A2/P4-A3/P4-F2/P4-F3 |
| Phase 2 Close position semantics | `20260608__openctp-tts-simulation-provider__close-position-semantics` | read-only position snapshot | completed | acceptance rows P4-A4/P4-A5/P4-F4/P4-F5 |
| Phase 3 Post-order reconciliation | `20260608__openctp-tts-simulation-provider__post-order-reconciliation` | guarded order loop and readonly snapshot | completed | acceptance rows P4-A6/P4-A7/P4-F6 |
| Phase 4 Order type and price boundary | `20260608__openctp-tts-simulation-provider__order-type-price-boundary` | instrument query metadata | completed | acceptance rows P4-A8/P4-A9/P4-F7/P4-F8 |
| Phase 5 Risk preflight expansion | `20260608__openctp-tts-simulation-provider__risk-preflight-expansion` | account/position snapshot and guardrails | completed | acceptance rows P4-A10/P4-F9/P4-F10/P4-F11 |
| Phase 6 Real reconnect evidence | `20260608__openctp-tts-simulation-provider__real-reconnect-evidence` | recovery/idempotency baseline | completed | acceptance rows P4-A11/P4-A12/P4-F12; controlled front proxy evidence passed |
| Phase 7 Nautilus engine harness | `20260608__openctp-tts-simulation-provider__nautilus-engine-harness` | P002 provider baseline and P004 previous phases | completed | acceptance rows P4-A13/P4-A14/P4-F13/P4-R1 |

## 顺序规则

1. 每个 child change 必须能追溯到一个 proposal phase。
2. 若 phase 目标变化，应先更新 `phase-plan.md`，再更新本映射。
3. Completed child change 不等于 proposal closeout，proposal closeout 仍以 `acceptance.md` 为准。
4. Phase 1 是 P004 first executable change；后续 phase 可在不共享 runtime state 时并行，但下单类场景必须保留 explicit arm 和 redaction。
