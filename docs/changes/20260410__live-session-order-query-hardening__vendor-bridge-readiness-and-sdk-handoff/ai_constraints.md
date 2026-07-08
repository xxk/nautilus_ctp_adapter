# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认 vendor-bridge readiness 的验收口径，再进入实现或文档回写
2. 开发计划必须围绕 `check_rust_gate.py`、formal live smoke 与 repo-only probe 的统一术语展开
3. test 只能锁定 contract 与 function，不能替代正式 readiness 结论
4. 私有 SDK/live DLL 缺失时必须写 blocked 证据，不能靠文案把 blocked 写成 ready

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`
2. 再读取 `plan.md`
3. 锁定当前最小缺口：ready/blocker/handoff 术语是否已冻结
4. 再开始修改、验证和回填状态

## 每轮迭代 / Per-Round

1. 一次只解决一个最小 readiness/handoff 缺口
2. 每轮必须完成：修改、最小验证、判断是否推进了 unblock 交接状态
3. 若阻塞来自私有输入缺失，必须记录为 blocked，不得继续调 auth/front/credential

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界
2. 不得把 compat pack 误写成 live bridge ready
3. 不得提交、复制或伪造私有 SDK/live DLL

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源
2. 更新 YAML 后必须同步 Dashboard 派生字段
3. 私有输入未补齐前，不得把最终结论写成“已验收”

## 收尾 / Wrap-up

1. 收尾前检查 topic README 与 `scripts/README.md` 是否已同步同一术语
2. 收尾前检查是否已写清进入 C2 的触发条件