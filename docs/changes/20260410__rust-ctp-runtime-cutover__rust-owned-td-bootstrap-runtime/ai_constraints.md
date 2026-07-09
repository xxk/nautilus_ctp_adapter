# Rust-Owned TD Bootstrap Runtime AI 约束 / AI Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

1. 只推进 TD bootstrap/readiness 主路径，不提前把真实 order send mainline 一并切过去。
2. 不得破坏 execution guardrails 或把 host event shaping 下沉到 Rust。
3. 可沿用“单个活跃 TD session”限制，但必须显式文档化。
4. 收尾前必须回填 topic/docs frontier。
