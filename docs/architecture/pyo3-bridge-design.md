# PyO3 Bridge Design / PyO3 桥接设计

**更新日期**：2026-04-10
**状态**：C2 已完成首个 live mainline 切片（MD 主路径已切到 internal live session，C3–C4 待实现）
**关联 change**：`docs/changes/20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design/`

---

## 1. 目标 / Goal

用原生 PyO3 extension module（`.pyd`）替代当前 ctypes bridging（`ctp_native.dll` → `CtpMdApi` / `CtpTdApi`），
消除运行时 ctypes 符号解析的脆弱性，并为后续 `ctp_runtime_core` 向 MD/TD 真实会话迁移奠定类型安全完备基础。

---

## 2. Crate 架构 / Crate Architecture

```text
rust/
  ctp_runtime_core/   # rlib + cdylib
  │  Cargo.toml       # produces ctp_native.dll (ctypes compat path, kept until C4)
  │  src/lib.rs
  │
  ctp_py             # cdylib only — PyO3 extension module
     Cargo.toml      # produces _ctp_runtime.*.pyd via maturin
     src/lib.rs      # public scaffold sessions + internal live sessions + constants
```

**关键约束**：

- `ctp_runtime_core` 同时保留 `rlib`（被 `ctp_py` 引用）和 `cdylib`（仍产出 `ctp_native.dll`）。
- C4 之前，`ctypes` 路径（`CtpMdApi` / `CtpTdApi`）保持完整可用，不提前删除。
- `ctp_py` 是独立 crate，不污染 `ctp_runtime_core` 的 cdylib ABI。

---

## 3. 构建工具 / Build Tooling

| 工具 | 版本 | 用途 |
| --- | --- | --- |
| maturin | 1.13.1 | 以 `pyo3` crate 生成 Python wheel 并安装到 venv |
| PyO3 | 0.23.5 | Rust–Python FFI；支持 Python 3.13 |
| Python | 3.13.12 | 项目活跃 venv |

**pyproject.toml 核心配置**：

```toml
[build-system]
requires = ["maturin>=1.4,<2.0"]
build-backend = "maturin"

[tool.maturin]
python-source = "src"
manifest-path = "rust/ctp_py/Cargo.toml"
module-name = "ctp_runtime._ctp_runtime"
```

`module-name = "ctp_runtime._ctp_runtime"` 使 `.pyd` 落在 `src/ctp_runtime/` 内；
`src/ctp_runtime/__init__.py` 先注册 `vendor/ctp/bin` 的 Windows DLL 搜索目录，再从 `._ctp_runtime` 重导出公共符号。

---

## 4. Python API 冻结 / Frozen Python API

### CtpMdSession（public scaffold）

```python
CtpMdSession(front: str, broker: str, user: str, password: str)
# 方法
.init()                    -> int   # scaffold public contract
.login()                   -> int
.subscribe(symbols: list[str]) -> int
.dispose()                 -> None
```

### CtpTdSession（public scaffold）

```python
CtpTdSession(front: str, broker: str, user: str, password: str, appid: str, auth_code: str)
# 方法
.init()                    -> int
.authenticate()            -> int
.login()                   -> int
.query_instruments()       -> int
.query_account()           -> int
.query_positions()         -> int
.dispose()                 -> None
```

### 常量

| 名称 | 值 | 含义 |
| --- | --- | --- |
| `SCAFFOLD_NOT_IMPLEMENTED` | `-9000` | scaffold 占位返回码，与 ctypes manifest 保持一致 |
| `INVALID_HANDLE` | `-9001` | 会话已 dispose / handle 无效，与 ctypes manifest 保持一致 |

### CtpMdLiveSession（internal mainline helper, C2）

```python
from ctp_runtime._ctp_runtime import CtpMdLiveSession

session = CtpMdLiveSession("D:/repo/var/md_flow_smoke")
session.set_login_callback(callback)
session.set_tick_callback(callback)
session.set_front_disconnected_callback(callback)
session.init("tcp://...")
session.login("0155", "025292", "secret")
session.subscribe(["rb2610"])
session.dispose()
```

说明：为保持 C1 已验收的 public scaffold contract 不变，C2 不直接改变公开 `CtpMdSession` 语义，而是新增 internal `CtpMdLiveSession` 给 `CtpDataClient` 主路径使用。

---

## 5. C1–C4 Cutover 序列 / Cutover Sequence

| Phase | change slug | 目标 |
| --- | --- | --- |
| **C1** | `bridge-and-cutover-design` | 冻结 API 设计，搭建 ctp_py scaffold，确认 maturin 链路可用 |
| **C2** | `md-pyO3-live-path` | internal `CtpMdLiveSession` 接入真实 thost MD API，并让 `CtpDataClient` 替代 `CtpMdApi` ctypes path |
| **C3** | `td-pyO3-live-path` | TD bootstrap/readiness 切到 PyO3 internal live session |
| **C4** | `ctypes-retirement` | 删除 ctypes bridge (`native/md_ctypes.py`, `native/td_ctypes.py`)，archive ctypes-related tests |

---

## 6. 诊断兼容表 / Diagnostics Parity

C2、C3 完成后，以下诊断场景必须在 PyO3 path 下产出相同的可观测结论：

| 场景 | ctypes 当前行为 | PyO3 目标行为 |
| --- | --- | --- |
| Front 连通性失败 | `init()` 返回非 0 | `init()` 返回相同非 0 |
| 认证失败（TD） | `authenticate()` 返回错误码 | 同左 |
| 登录失败 | `login()` 返回错误码 | 同左 |
| MD 断链 4097 | 回调 `front_disconnected` | PyO3 internal live session 暴露 disconnect callback |
| Dispose 后调用 | 段错误或 -9001 | 必须返回 `-9001`（INVALID_HANDLE）不允许 panic |

---

## 7. 验证口径 / Verification

```powershell
# Rust 编译
cargo build -p ctp_py --manifest-path rust/Cargo.toml

# Python 安装
maturin develop

# 导入验证
python -c "import ctp_runtime; import ctp_runtime._ctp_runtime as native_rt; print(hasattr(native_rt, 'CtpMdLiveSession'))"

# 完整 gate
python scripts/check_rust_gate.py

# 契约测试
python -m pytest tests/test_smoke_import.py -k "pyo3_bridge or run_live_md_smoke_uses_pyo3_md_live_session_mainline" -v
```

---

## 8. 设计决策说明 / Design Decisions

1. **underscore-private extension name**（`_ctp_runtime`）：与 pydantic-core 惯例一致，Python package = `ctp_runtime`，native extension = `_ctp_runtime`。
2. **maturin 不删 setuptools pip-installable 路径**：`pip install -e .` 改走 maturin backend，需要 Rust toolchain，这是已知的接受权衡。
3. **-9000/-9001 与 ctypes manifest 对齐**：确保 Python layer 代码在 C4 迁移前不因错误码语义差异出现两种行为。
4. **无宿主逻辑入 Rust**：所有 Python 侧策略（重连、日志、timeout）仍在 Python adapter 层完成，Rust 只暴露最薄的 session 接口。
5. **Windows import bootstrap 是正式链路的一部分**：`src/ctp_runtime/__init__.py` 必须先注册 `vendor/ctp/bin` DLL 目录，再导入 `_ctp_runtime.pyd`，否则 `.pyd` 的 vendor 依赖无法解析。

## 9. C2 Closeout / C2 收口

1. `CtpDataClient.run_live_md_smoke()` 已切到 `CtpMdLiveSession`。
2. `CtpMdApi` 保留在历史 boundary 中，但不再是 MD smoke 主路径。
3. `python scripts/check_rust_gate.py` 通过，`python -m pytest tests/ -q` 为 `88 passed`。
