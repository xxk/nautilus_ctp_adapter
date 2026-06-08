# P003 Change Map / Child Change 映射

**fragment-id**：`change_map`
**适用场景**：多个 child change 需要映射追踪。

---

## Phase Map

| Phase | Child Change | 依赖 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| Phase 0 | proposal-only planning | P002 completed baseline and OpenCTP paper runbook | completed | P003 paper-first proposal docs |
| Phase 1 | `20260608__ctp-paper-provider-readiness__paper-session-preflight` | Phase 0 | completed | redacted config-only and paper connect preflight evidence passed |
| Phase 2 | `20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot` | Phase 1 | completed | redacted account/position/instrument/order-trade snapshot evidence passed |
| Phase 3 | `20260608__ctp-paper-provider-readiness__guarded-paper-order-loop` | Phase 1 + Phase 2 + paper trade window | completed | guarded paper order dry-run/order contract/callback contract passed; armed paper send typed blocker recorded |
| Phase 4 | `20260608__ctp-paper-provider-readiness__paper-recovery-idempotency` | Phase 2 + Phase 3 | completed | checkpoint/reconnect/idempotency repo-only evidence passed |
| Phase 5 | `20260608__ctp-paper-provider-readiness__paper-ops-closeout` | Phase 1-4 | completed | paper runbook/backfill and closeout boundary completed |

## 顺序规则

1. Phase 1 是 first executable slice；它不发送任何订单。
2. Phase 3 只能在 Phase 1/2 通过，且 explicit arm、paper trade window、risk guardrails 全部通过后执行。
3. P003 child change 必须默认标记 `ctp_account_profile=openctp-tts-7x24-simulation`，不得要求 formal-trading。
4. OpenCTP paper blocker 必须写成 typed blocker，并保留 repo-only fallback 的可推进项。
5. 每个 completed child change 必须回填 proposal acceptance row。
6. Formal-trading / Live 只允许作为 future carry-forward，不参与 P003 当前验收。
