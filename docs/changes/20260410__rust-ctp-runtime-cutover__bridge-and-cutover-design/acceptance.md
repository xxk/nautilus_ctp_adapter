# Bridge And Cutover Design 验收方案

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已验收
**日期**：2026-04-10
**范围**：Rust workspace crate 结构、PyO3 bridge foundation、build system 切换
**change-id**：20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/rust_ctp/rust-ctp-runtime-cutover/README.md

## 一、验收目标

1. Rust workspace 中存在独立 `ctp_py` crate，类型为 `cdylib`，PyO3 可正常构建。
2. `CtpMdSession` 与 `CtpTdSession` 最小骨架 PyO3 class 可从 Python 导入。
3. `pyproject.toml` 使用 maturin，`maturin develop` 构建成功。
4. `scripts/check_rust_gate.py` 通过，包含 `ctp_py` artifact 检查。
5. 既有 6 条 Python contract tests 继续通过（实际 85 条全部通过）。
6. `docs/architecture/pyo3-bridge-design.md` 存在并记录核心设计决策。

## 二、验收场景

| 场景 | 执行方式 | 结论 | 证据备注 |
| --- | --- | --- | --- |
| `ctp_py` crate cargo build | `cargo build -p ctp_py` | ✅ 通过 | `_ctp_runtime.dll` 产生于 `rust/target/debug/` |
| PyO3 module Python import | `python -c "import ctp_runtime; print('ok')"` | ✅ 通过 | `maturin develop` 安装后正常导入 |
| maturin develop | `maturin develop` | ✅ 通过 | `nautilus-ctp-adapter-0.1.0` 安装；`import ctp_runtime` → ok |
| Rust gate | `python scripts/check_rust_gate.py` | ✅ 通过 | `PASS rust-gate: ctp_py-build extension=…\_ctp_runtime.dll` |
| 全部 contract tests | `python -m pytest tests/ -q` | ✅ 通过 | 85 passed，包含 4 条新 PyO3 bridge CONTRACT-LOCK tests |
| pyo3-bridge-design.md | 文件存在且内容完整 | ✅ 通过 | `docs/architecture/pyo3-bridge-design.md` 已创建 |

## 三、不作为验收证据的内容

1. 仅 `cargo check` 通过不算验收。
2. PyO3 module 构建成功但 Python 导入失败不算验收。
3. maturin develop 仅在 vendor DLL 存在时才允许测试 live 功能；本 change 只要 import 不报错即可通过。
