# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260413__nautilus-host-integration__nautilus-live-data-client
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认验收目标，再进入实现
2. 实现必须严格按照冻结设计 `docs/architecture/nautilus-host-integration-design.md` 第三、五、七节
3. 不得修改现有 `data_client.py`、`config.py` 的签名和行为
4. 新文件使用 `nautilus_` 前缀

## 边界 / Boundaries

1. 不允许实现 ExecutionClient（C3 范围）
2. 不允许实现 Factory（C4 范围）
3. 现有 smoke 脚本不得被破坏
