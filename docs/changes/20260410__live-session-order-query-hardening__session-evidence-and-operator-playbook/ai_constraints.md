# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__live-session-order-query-hardening__session-evidence-and-operator-playbook
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认 operator playbook 的验收目标，再进入文档实现
2. 开发计划必须围绕决策树、evidence matrix 与导航一致性展开
3. test 只能锁定治理与 contract，不能替代文档可执行性
4. sibling evidence 未齐全时必须保留缺口，不得伪造 closeout

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`
2. 再读取 `plan.md`
3. 锁定当前最小缺口：导航、索引还是术语冲突
4. 再开始修改、验证和回填状态

## 每轮迭代 / Per-Round

1. 一次只解决一个最小 playbook 缺口
2. 每轮必须完成：修改、最小验证、判断是否推进了 operator handoff 状态
3. 若缺的是 sibling evidence，必须写明 gap，而不是把 playbook 写成已闭环

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界
2. 不得新增业务能力代码来掩盖文档层缺口
3. 不得把 blocked topic/change 写成 ready-next

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源
2. 更新 YAML 后必须同步 Dashboard 派生字段
3. sibling 关键 evidence 未齐全前，不得把最终结论写成“已验收”

## 收尾 / Wrap-up

1. 收尾前检查 topic README、`docs/README.md` 与 `scripts/README.md` 是否已对齐
2. 收尾前检查是否已保留 blocked/gap 的可见性