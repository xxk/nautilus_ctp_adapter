# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260610__ctp-paper-provider-readiness__instrument-detail-completeness
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞

## 方法论 / Working Mode

1. 先确认 C1 completeness / correctness 验收目标，再进入实现
2. 优先扩展现有 readonly snapshot / guarded preflight contract，不新建第二套 snapshot shape
3. test 只能锁定 contract 与 negative path，不能替代真实 paper evidence
4. formal-trading / Live 继续 out-of-scope

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`
2. 再读取 `plan.md`
3. 再读取 `docs/proposals/p003-ctp-live-trading-provider-readiness/acceptance.md`
4. 再读取 `docs/changes/20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot/acceptance.md`
5. 再开始修改、验证和回填状态

## 每轮迭代 / Per-Round

1. 一次只解决一个最小阻塞
2. 每轮必须完成：修改、最小验证、判断是否推进了验收状态
3. 若字段来自上游 query，但当前 wrapper 丢弃，必须补 runtime/adapter contract，不能只改文档

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界
2. 不得把 options-specific 字段混入当前 futures baseline
3. 不得因补 C1 字段而放宽 explicit arm、trade window、qty cap、kill switch 等 guardrail
4. 若字段缺失来自外部 front/query，不得伪造 pass

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源
2. 更新 YAML 后必须同步 Dashboard 派生字段
3. 未有真实或 typed blocker evidence 前，不得宣告 C1 completeness 已通过

## 收尾 / Wrap-up

1. 若完成了稳定 contract，回写 `paper-readonly-truth-snapshot` 相关 acceptance
2. 至少执行 `python scripts/check_change_docs.py --root .`
