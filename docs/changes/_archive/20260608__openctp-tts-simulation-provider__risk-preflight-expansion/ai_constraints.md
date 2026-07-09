# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__openctp-tts-simulation-provider__risk-preflight-expansion
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. Guardrail fail 必须发生在 native send 前。
2. Kill switch 默认关闭。
3. Risk evidence 必须 redacted。
