# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. 当前 change 只能使用 `openctp-paper` profile。
2. 只读查询不发送订单。
3. 不连接 formal-trading / Live，不要求正式交易账号。
4. 不写 `.env`、`cfgs/local/` 或账号凭据。
5. 不把 OpenCTP paper evidence 写成 formal-trading pass。
6. Snapshot output 必须 redacted。

## 收尾 / Wrap-up

1. 回填当前 change acceptance。
2. 回填 P003 Phase 2 状态。
3. 执行 docs checks 和 focused guards。
