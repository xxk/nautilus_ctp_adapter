# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__openctp-tts-simulation-provider__post-order-reconciliation
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. 不得把 stale、partial 或 account-mismatched snapshot 写成 pass evidence。
2. Test-only evidence 只能作为 guard。
3. Simulation evidence 必须 redacted。
