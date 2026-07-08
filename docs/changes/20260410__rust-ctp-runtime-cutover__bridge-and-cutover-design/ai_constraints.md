# Bridge And Cutover Design AI 约束

**日期**：2026-04-10
**change-id**：20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design

## 硬约束

1. 不得把 `InstrumentProvider`、`LiveDataClient`、`LiveExecutionClient` 任何逻辑下沉到 `ctp_py` 或 `ctp_runtime_core`。
2. 不得删除 `ctp_runtime_core` 的 cdylib 输出（`ctp_native.dll` 继续存在）；ctypes 路径继续有效。
3. 不得在 C1 阶段实际切换 Python adapter 主路径——C1 只建立 PyO3 骨架，主路径切换在 C2/C3 完成。
4. 不得改变已冻结的 error contract：`-9000 = NOT_IMPLEMENTED`，`-9001 = INVALID_HANDLE`。
5. 不得因 maturin 切换导致 `pip install -e .` 无法对纯 Python 路径安装生效。
6. `[CONTRACT-LOCK]` 测试行不得在未获用户明确确认前修改。

## 软约束

1. PyO3 API 形状以 plan.md 2.3 节为准；若需调整必须先更新 plan.md 再实现。
2. 既有 6 条 contract tests 全部保持通过。
3. 架构决策落入 `docs/architecture/pyo3-bridge-design.md`，不要停留在聊天记录里。
