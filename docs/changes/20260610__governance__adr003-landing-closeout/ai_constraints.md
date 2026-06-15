# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260610__governance__adr003-landing-closeout
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认验收目标，再进入实现
2. 开发计划必须围绕验收场景、出口条件与证据展开
3. 治理 closeout 必须以 checked-in docs 与 gate 为准，不能只停留在聊天说明
4. 正式验收必须走本仓真实入口：文档、脚本 gate、frontier 命令

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`
2. 再读取 `plan.md`
3. 锁定阻塞 ADR003 completed 的最小缺口
4. 再开始修改、验证和回填状态

## 每轮迭代 / Per-Round

1. 一次只解决一个最小阻塞
2. 每轮必须完成：修改、最小验证、判断是否推进了验收状态
3. 若阻塞来自本地入口缺失，必须补本仓入口或本仓 gate，不能只引用外部路径规避

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界
2. 不得把 mock、假文档、外部 issue 状态写成正式验收通过
3. 不得把 `nautilus_strategies` 作为本仓状态源

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源
2. 更新 YAML 后必须同步 Dashboard 派生字段
3. ADR003 `landing_status=completed` 前，不得把最终结论写成“已验收”

## 收尾 / Wrap-up

1. 收尾前检查 ADR003、ADR index、AGENTS 和 docs README 是否已同步
2. 收尾前执行 `python scripts/autopilot.py --root . --backfill`
