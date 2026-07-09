# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__ctp-paper-provider-readiness__guarded-paper-order-loop
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. 当前 change 只能使用 `openctp-paper` profile。
2. 不连接 formal-trading / Live，不要求正式交易账号，不发正式实盘单。
3. Paper order 必须 explicit arm，默认 request-only/dry-run。
4. 不写 `.env`、`cfgs/local/` 或账号凭据。
5. 不把 OpenCTP paper evidence 写成 formal-trading pass。
6. 所有 order lifecycle output 必须 redacted。

## 收尾 / Wrap-up

1. 回填当前 change acceptance。
2. 回填 P003 Phase 3 状态。
3. 执行 docs checks、focused guards 和必要 paper evidence。
