# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__nautilus-provider-readiness__execution-event-reporting
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 边界 / Boundaries

1. 不写 `.env`、`cfgs/local/` 或账号凭据。
2. 不默认武装 live-send。
3. 不用 `.CTP` fallback 掩盖 provider metadata 缺失。
4. 不引入第二套 execution truth owner；只把已有 CTP normalized payload 翻译成 Nautilus report。

## 收尾 / Wrap-up

1. 回填当前 change acceptance。
2. 回填 P002 Phase 3 状态。
3. 执行 focused tests 和 docs checks。
