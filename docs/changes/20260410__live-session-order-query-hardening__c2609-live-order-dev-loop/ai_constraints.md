# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__live-session-order-query-hardening__c2609-live-order-dev-loop
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认 trade-window 验收目标，再进入实现
2. 开发计划必须围绕 A1/A2/A5 的 preflight、live-send 与 guardrail 展开
3. test 只能锁定 contract 与 function，不能替代正式交易时段证据
4. vendor-bridge 未 ready 时不得伪造 live-send 通过

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`
2. 再读取 `plan.md`
3. 锁定当前最小阻塞：preflight、guardrail 还是 live-send 输出语义
4. 再开始修改、验证和回填状态

## 每轮迭代 / Per-Round

1. 一次只解决一个最小交易路径缺口
2. 每轮必须完成：修改、最小验证、判断是否推进了交易时段验收状态
3. 若阻塞来自交易窗口或私有输入缺失，必须写明 blocked，不得改文档硬过

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界
2. 不得放宽 `c2609 / 1 手 / 5 手上限` guardrails
3. 不得在未满足前置条件时执行真实 live-send

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源
2. 更新 YAML 后必须同步 Dashboard 派生字段
3. 阻塞成功场景未通过前，不得把最终结论写成“已验收”

## 收尾 / Wrap-up

1. 若形成真实交易证据，必须写回当前 change bundle
2. 收尾前检查是否已向 C4 交接 evidence 路径