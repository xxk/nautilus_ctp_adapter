# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__openctp-tts-simulation-provider__nautilus-engine-harness
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. Harness 必须经过 Nautilus-facing provider entrypoint。
2. Script-only smoke 只能作为辅助诊断，不能关闭 engine harness 验收。
3. Simulation order 仍必须 obey explicit arm and redaction。
