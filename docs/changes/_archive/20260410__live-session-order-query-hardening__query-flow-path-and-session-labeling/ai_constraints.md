# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__live-session-order-query-hardening__query-flow-path-and-session-labeling
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 方法论 / Working Mode

1. 先统一参数名和默认语义，再补 evidence naming。
2. 优先复用现有脚本参数，不为统一而新建重复入口。
3. test 只锁定 CLI / payload / naming contract，不替代真实 offhours 运行。

## 边界 / Boundaries

1. 不得修改真实 flow 文件内容，只能规范路径与命名口径。
2. 不得把 session labeling 扩成交易态 session 管理。
3. 不得把 evidence 导出到仓库根目录。