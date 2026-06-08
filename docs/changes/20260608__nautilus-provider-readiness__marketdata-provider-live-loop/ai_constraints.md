# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__nautilus-provider-readiness__marketdata-provider-live-loop
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. 不写 `.env`、`cfgs/local/` 或账号凭据。
2. 不把 OpenCTP paper baseline 写成 repo-only pass，也不把 L5 provider evidence 混入本 change scope。
3. 不用 `.CTP` hardcode 掩盖 provider metadata 缺失。
4. 不引入第二套行情 truth owner；tick parsing stays in current data client boundary.
