# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__openctp-tts-simulation-provider__order-type-price-boundary
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. Unsupported order type 必须 fail fast。
2. Off-tick price 不得进入 native send。
3. Simulation evidence 不得泄漏 secret。
