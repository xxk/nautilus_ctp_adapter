# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__live-session-order-query-hardening__aggregated-query-evidence-export
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 方法论 / Working Mode

1. 先补最小聚合 contract，再补 evidence export。
2. 不新增独立实现层，优先复用当前 `query_adapter` 与现有 smoke 入口。
3. test 只锁定 contract 与 function，不替代真实 offhours evidence。

## 边界 / Boundaries

1. 不得引入 live-send 或 trade-window 语义。
2. 不得把 evidence export 写到仓库根目录，必要产物必须落在 `output/` 或 change bundle evidence 路径。
3. 不得把仓外敏感配置写入仓库。