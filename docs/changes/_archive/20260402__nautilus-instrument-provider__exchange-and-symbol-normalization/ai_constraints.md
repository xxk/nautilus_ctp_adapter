# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260402__nautilus-instrument-provider__exchange-and-symbol-normalization
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认验收目标，再进入实现
2. 开发计划必须围绕验收场景、出口条件与证据展开
3. test 只能锁定 contract 与 function，不能替代正式验收
4. 本 change 必须继承 `C1` 已冻结的 query contract

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界
2. 不得把 mock、stub、假数据、测试输出来写成正式验收通过
3. 不得在本 change 中提前实现完整 `InstrumentProvider`
