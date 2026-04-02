# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260327__harness-adoption__minimal-5step-adoption
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`。
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送。
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞。

## 方法论 / Working Mode

1. 先确认验收目标，再进入实现。
2. 开发计划必须围绕验收场景、出口条件与证据展开。
3. test 只能锁定 contract 与 function，不能替代正式验收。
4. 正式验收必须走真实入口、真实环境、真实数据或真实产物路径。

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`。
2. 再读取 `plan.md`。
3. 锁定阻塞总体验收的最小缺口。
4. 再开始修改、验证和回填状态。

## 每轮迭代 / Per-Round

1. 一次只解决一个最小缺口。
2. 不允许把“目录已复制”直接当作接入完成。
3. 不允许保留示例仓验证命令占位而宣告通过。
4. 必须把当前 change 自身当作第一个真实试点 change 留证。

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界。
2. 不得把 test、mock、fake、stub、假数据、测试输出写成正式验收通过。
3. 若正式入口或验证入口不明确，先补文档，不要跳过。

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源。
2. 只有阻塞场景全部满足且真实证据齐全时，才允许把 `allow_declare_pass` 改成 `true`。
3. 只有真实执行与真实证据满足出口条件时，AI 才能把最终结论改为“已通过”。

## 收尾 / Wrap-up

1. 确认入口地图已可发现。
2. 确认 change 模板落点已存在。
3. 确认目标项目验证命令已替换为真实口径。
4. 确认当前 change 的证据已完整记录。
