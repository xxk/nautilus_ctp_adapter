# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__nautilus-provider-readiness__query-report-generation
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. 不写 `.env`、`cfgs/local/` 或账号凭据。
2. 不重新解析 raw CTP structs。
3. 不把 AccountState 误写成 formal broker final evidence。
4. 不改变 existing query adapter 的 truth owner。

## 收尾 / Wrap-up

1. 回填当前 change acceptance。
2. 回填 P002 Phase 4 状态。
3. 执行 focused tests 和 docs checks。
