# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260411__architecture__windows-proxy-service-runbook
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限或缺关键环境能力时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认验收目标，再进入文档实现
2. 开发计划必须围绕服务化 runbook、索引可发现性与验证边界展开
3. 正式验收只声明仓内真实验证结果，不伪造目标机实跑

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`
2. 再读取 `plan.md`
3. 锁定最小缺口：长期文档、原始文档关联还是索引入口
4. 再开始修改、验证和回填状态

## 每轮迭代 / Per-Round

1. 一次只解决一个最小缺口
2. 每轮必须完成：修改、最小验证、判断是否推进了验收状态
3. 若当前环境没有目标机二进制或服务上下文，必须明确保留为待办，不得文案硬过

## 边界 / Boundaries

1. 不允许修改 `src/`、`scripts/`、`vendor/` 或 topic frontier 文档
2. 不得把 `3proxy` 或 `nssm` 已安装、服务已运行写成既成事实，除非当前环境真实执行过
3. 不得把仓内文档验证替代为目标机运行验证

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源
2. 更新 YAML 后必须同步 Dashboard 派生字段
3. 阻塞场景全部通过前，不得把最终结论写成“已验收”

## 收尾 / Wrap-up

1. 收尾前检查长期文档、原始文档和索引是否都已互相可发现
2. 收尾前检查是否已写清楚目标机实跑仍待执行的边界