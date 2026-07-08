# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260607__openctp-tts__test-baseline
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`。
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送。
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞。

## 方法论 / Working Mode

1. 先确认 OpenCTP TTS 7x24 的官方前置与 `BrokerID/AuthCode/AppID` 口径，再改仓库。
2. 配置解析变更必须先有 failing test，再实现。
3. test 只能锁定 config/function contract，不能替代真实 OpenCTP 连通证据。

## 边界 / Boundaries

1. 不允许修改 `cfgs/local/`、`vendor/` 或仓外账号文件。
2. tracked 模板中不得把 `ExecutionGuardrails.AllowLiveOrderSmoke` 设为 true。
3. OpenCTP 7x24 的 `TEST` 调试路径不得覆盖 real-account `c2609` guardrail 口径；两者必须在文档中分层。

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源。
2. 更新 YAML 后必须同步 Dashboard 派生字段。
3. 真实 OpenCTP 连接未跑通前，不得把最终结论写成“已验收”。

## 收尾 / Wrap-up

1. 收尾前必须执行 targeted pytest 和 docs checks。
2. 若缺账号/runtime/SDK，必须记录为真实 blocker，而不是调低验收条件。
