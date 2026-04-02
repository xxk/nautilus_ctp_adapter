# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260402__governance-harness__rust-validation-gate
**关联 acceptance**：[acceptance.md](./acceptance.md)
**关联 plan**：[plan.md](./plan.md)

## 单文档启动 / Standalone Kickoff

1. 在仓库内执行本 change 时，先读取 sibling `acceptance.md` 与 `plan.md`。
2. 不要求用户重复提供 Rust toolchain 状态；应先用脚本自行探测。
3. 只有在 `rust/Cargo.toml` 缺失或 Python 自身不可运行时，才允许直接阻塞。

## 方法论 / Working Mode

1. 先冻结 Rust gate 正式入口，再扩展文档与测试。
2. 不把“本机没装 cargo”伪装成 Rust workspace 代码失败。
3. 验收必须同时覆盖缺 toolchain 场景与成功路径 contract-lock。

## 边界 / Boundaries

1. 不修改 Rust 业务 crate 行为。
2. 不伪造真实 `cargo check` 成功证据。
3. fake cargo 仅允许出现在测试中，用于锁定 gate 成功分支。

## 收尾记录 / Wrap-up Notes

1. 已新增 `scripts/check_rust_gate.py` 作为正式 Rust gate。
2. 已将 `README.md`、`AGENTS.md`、`docs/README.md`、`scripts/README.md` 的官方验证入口统一改到该脚本。
3. 已留存当前命令证据于 sibling evidence 文件。
