# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260402__nautilus-live-execution__real-account-debug-guardrails
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`。
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送。
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞。

## 方法论 / Working Mode

1. 先确认验收目标，再进入实现。
2. 本 change 优先冻结 guardrails，再补配置和执行预检，不得先写“真发单能力”。
3. `pytest` 只能锁定 config / precheck contract，不能替代未来真实 execution 验收。
4. 任何可能触达真实 TD 的命令、脚本或 smoke 都不在本 change 允许范围内。

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`。
2. 再读取 `plan.md`。
3. 锁定阻塞总体验收的最小缺口。
4. 再开始修改、验证和回填状态。

## 每轮迭代 / Per-Round

1. 一次只解决一个最小阻塞。
2. 每轮必须完成：修改、最小验证、判断是否推进了验收状态。
3. 若 guardrails 仍只存在于文档或仍需人工记忆，则必须补配置或代码入口。

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界。
2. 不得把 mock、stub、测试输出来写成 execution 主线 ready。
3. 不得新增任何真实发单逻辑、自动下单脚本或直连 TD 的调试流程。
4. 若遇到“5 收”语义冲突，默认按 `5` 手保持保守冻结，并在文档中显式说明当前假设。

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源。
2. 更新 YAML 后必须同步 Dashboard 派生字段。
3. 阻塞场景全部通过前，不得把最终结论写成“已验收”。

## 收尾 / Wrap-up

1. 收尾前检查 `nautilus-live-execution` topic README 与 mainline roadmap 是否已同步回写。
2. 收尾前确认没有把任何真实发单入口带入当前提交。
