# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260608__openctp-tts-simulation-provider__cancel-lifecycle
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 先读取 sibling `acceptance.md` 与 `plan.md`。
2. 不得要求用户重复提供 P004 scope；以 `docs/proposals/p004-openctp-tts-simulation-provider-completeness/` 为准。
3. 只有缺 OpenCTP TTS front、SDK、账号或交易窗口时，才允许记录 typed `paper-resource` blocker。

## 方法论 / Working Mode

1. 先写/跑 contract tests，再运行 simulation command。
2. Test 只能锁定 contract；真实通过必须有 simulation evidence 或 typed external blocker。
3. 下单/撤单前必须确认 `openctp-tts-7x24-simulation`、explicit arm、allowlist、qty cap 和 kill switch。

## 边界 / Boundaries

1. 不得使用 `formal-trading`。
2. 不得泄漏 raw account id、password、auth code、broker private fields。
3. 不得把 script-only shortcut 伪装成 Nautilus engine provider evidence。
