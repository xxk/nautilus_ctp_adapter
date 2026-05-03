# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 方法论 / Working Mode

1. 先冻结 read-only taxonomy，再进入实现。
2. 优先复用当前 TD truth 与 runtime event contract，不新增交易路径。
3. test 只能锁定 payload 与 failure taxonomy，不能替代真实 offhours evidence。

## 边界 / Boundaries

1. 不得扩展成 order lifecycle live-send。
2. 不得把 callback truth 直接重命名成 query snapshot 而不做分层。
3. 不得提交真实 flow 文件或敏感配置。