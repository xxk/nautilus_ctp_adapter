# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260401__ctp-live-connectivity__nautilus-live-smoke-baseline
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 必须先读取 sibling `acceptance.md` 与 `plan.md`。
2. 启动前必须确认 `20260401__ctp-live-connectivity__td-auth-and-login-readiness` 已完成。
3. 必须同时阅读当前 topic roadmap 与 `docs/README.md`，避免把 baseline 和 docs index 写成两套口径。

## 方法论 / Working Mode

1. 本 change 只冻结 Nautilus smoke baseline，不得扩展成完整数据或交易实现。
2. 重点是正式入口、成功信号和证据格式统一。
3. 优先收口唯一正式 baseline，再清理 diagnostics 和正式入口的边界。

## 每轮迭代 / Per-Round

1. 一次只解决一个最小不一致点。
2. 每轮都要同时检查：入口是否唯一、成功信号是否唯一、证据路径是否唯一。
3. 若仍存在多个 competing 入口，不得宣告 baseline 已冻结。

## 边界 / Boundaries

1. 禁止顺手实现完整 adapter、完整市场数据、或完整 execution。
2. 禁止把临时诊断脚本包装成正式 baseline，除非文档中明确标注其仅为 diagnostics。
3. 禁止在没有证据格式定义的情况下宣告 Topic 1 可关闭。

## 收尾 / Wrap-up

1. 收尾前必须回写 `docs/README.md` 与当前 topic roadmap。
2. Topic 1 只有在 `C1` acceptance 也完成收口后才能整体关闭。
