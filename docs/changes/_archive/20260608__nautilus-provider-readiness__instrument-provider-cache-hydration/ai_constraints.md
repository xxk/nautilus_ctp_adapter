# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__nautilus-provider-readiness__instrument-provider-cache-hydration
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 先读 sibling `acceptance.md` 与 `plan.md`。
2. 再读 P002 `README.md`、`phase-plan.md`、`acceptance.md`。
3. 不得要求用户重复提供账号；账号 profile 规则来自 OpenCTP runbook。

## 方法论 / Working Mode

1. 先锁 repo-only contract，再接 OpenCTP paper evidence。
2. test 只能证明 repo-only contract，不能写成 L5/L6 pass。
3. OpenCTP paper baseline 只能作为后续 L5 evidence 输入，不能伪造成本 repo-only change pass。

## 边界 / Boundaries

1. 不写 `.env` 或 `cfgs/local/`。
2. 不提交 downloaded runtime/SDK。
3. 不默认武装 live-send。
4. 不用 formal-trading 账号推进日常 development closeout。

## 收尾 / Wrap-up

1. 回填当前 change acceptance。
2. 回填 P002 Phase 1 状态。
3. 执行 focused tests 和 docs checks。
