# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__ctp-paper-provider-readiness__paper-recovery-idempotency
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. 当前 change 只能使用 `openctp-paper` profile。
2. 不连接 formal-trading / Live，不要求正式交易账号。
3. 不写 `.env`、`cfgs/local/` 或账号凭据。
4. 不把 OpenCTP paper evidence 写成 formal-trading pass。
5. Recovery/reconnect evidence 必须 redacted。

## 收尾 / Wrap-up

1. 回填当前 change acceptance。
2. 回填 P003 Phase 4 状态。
3. 执行 docs checks、focused guards 和必要 paper evidence。
