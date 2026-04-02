# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：{{change-id}}
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
4. 正式验收必须走真实入口、真实环境、真实数据或真实产物路径

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`
2. 再读取 `plan.md`
3. 锁定阻塞总体验收的最小缺口
4. 再开始修改、验证和回填状态

## 每轮迭代 / Per-Round

1. 一次只解决一个最小阻塞
2. 每轮必须完成：修改、最小验证、判断是否推进了验收状态
3. 若阻塞来自代码行为未满足验收条件，必须修代码，不能只改文档规避

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界
2. 不得把 test、mock、fake、stub、假数据、测试输出写成正式验收通过
3. 若遇到真实阻塞，必须写清楚缺什么权限、证据或环境

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源
2. 更新 YAML 后必须同步 Dashboard 派生字段
3. 阻塞场景全部通过前，不得把最终结论写成“已验收”

## 收尾 / Wrap-up

1. 若 `plan.md` 声明了 `long_term_target`，收尾前检查是否已回写或已记录暂不回写原因
