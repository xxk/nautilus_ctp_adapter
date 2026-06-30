# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 必须先读取 sibling `acceptance.md` 与 `plan.md`
2. 只要文档可读，就默认进入执行，不得停留在纯分析

## 方法论 / Working Mode

1. 先冻结仓内 native ownership 规则，再做实现补位
2. 不得把临时 C# host 固化为长期方案
3. test 只能锁定 contract/function，不能代替正式验收

## 每轮迭代 / Per-Round

1. 一次只解决一个最小阻塞
2. 优先冻结边界，再补最小实现或同步机制
3. 结束时回填当前 change 与 topic roadmap 状态
