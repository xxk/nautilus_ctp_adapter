# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260401__ctp-live-connectivity__python-rust-md-login-path
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 必须先读取 sibling `acceptance.md` 与 `plan.md`。
2. 开始前必须确认 `20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap` 已完成。
3. 必须把 `login-025292-and-subscribe-rb2610` 中的 `rb2610` 行情证据当作 inherited evidence，而不是当前 change 的通过证据。

## 方法论 / Working Mode

1. 本 change 只聚焦 MD 主线，不得顺手扩展成完整 `LiveDataClient`。
2. 优先把真实 MD 路径迁回 Python/Rust runtime，再补 bridge、证据和失败口径。
3. 只有当前 change 自身产出的主线证据，才允许推进 `acceptance.md` 中的阻塞场景状态。

## 每轮迭代 / Per-Round

1. 一次只解决一个最小阻塞。
2. 每轮至少完成：代码修改、最小验证、当前 bundle 留证或状态更新。
3. 若发现依然依赖临时宿主才能解释登录或订阅成功，则本轮不得宣告通过。

## 边界 / Boundaries

1. 禁止扩展到 TD 长链路、execution 或 Topic 3 的完整 `LiveDataClient`。
2. 禁止用 C1 的临时宿主证据直接替代本 change 的主线验证。
3. 若需要新增 smoke 入口，只能服务本 change 的 MD 主线留证，不得提前冻结 Nautilus 全局 smoke baseline。

## 收尾 / Wrap-up

1. 收尾前必须同步更新 `plan.md` 的任务状态。
2. 收尾前必须在 topic roadmap 中把当前 implementation next action 更新到 `C4`，但前提是本 change 的 acceptance 已可判定通过。
