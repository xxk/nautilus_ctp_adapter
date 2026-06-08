# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__openctp-tts-simulation-provider__close-position-semantics
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 先读取 sibling `acceptance.md` 与 `plan.md`。
2. 以 P004 acceptance rows P4-A4/P4-A5/P4-F4/P4-F5 为验收边界。

## 边界 / Boundaries

1. 不得使用 formal-trading。
2. 不得在没有可平仓位时发送 native close。
3. 不得把 SHFE/INE 今昨仓规则折叠成静默 generic close。
