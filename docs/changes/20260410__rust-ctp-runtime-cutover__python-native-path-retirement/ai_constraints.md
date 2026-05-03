# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__rust-ctp-runtime-cutover__python-native-path-retirement
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库/IDE 工作区内运行时，必须主动读取 sibling `acceptance.md` 与 `plan.md`。
2. 只要 sibling 文件可读，就不得停下来要求用户重复发送。
3. 只有在文档缺失、目标冲突、缺权限、或缺关键外部依赖时，才允许先停止并汇报阻塞。

## 方法论 / Working Mode

1. 先确认验收目标，再进入实现。
2. 本 change 要按 consumer cutover 顺序推进：先 read-only，再 order-truth，再 guarded live order。
3. test 只能锁定 contract 与 function，不能单独替代正式验收。
4. 正式验收必须走真实入口、真实环境、真实产物路径。

## 启动步骤 / Kickoff

1. 先读取 `acceptance.md`。
2. 再读取 `plan.md`。
3. 再读取 `design.md`，锁定 C4 cutover 顺序与保留边界。
4. 先解决一个最小阻塞 consumer，再推进下一条路径。

## 每轮迭代 / Per-Round

1. 一次只解决一个最小阻塞。
2. 每轮必须完成：修改、最小验证、判断是否推进了验收状态。
3. 若阻塞来自“剩余 consumer 仍走 ctypes 主路径”，必须修正式代码，不能只改文档或测试规避。

## 边界 / Boundaries

1. 不允许越过 `plan.md` 中已声明的修改边界。
2. 不得引入运行时 fallback 到 `CtpTdApi`。
3. 不得提前改 public `CtpTdSession` scaffold 的 `-9000/-9001` contract。
4. 不得弱化 execution guardrails 或扩大真实交易副作用面。

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源。
2. 更新 YAML 后必须同步 Dashboard 派生字段。
3. 阻塞场景全部通过前，不得把最终结论写成“已验收”。

## 收尾 / Wrap-up

1. 收尾前必须检查 `docs/architecture/pyo3-bridge-design.md` 是否已回写最终 ctypes retirement 口径。
2. 收尾前必须同步 `docs/README.md`、`docs/topics/README.md`、`docs/changes/README.md` 的 active change。
