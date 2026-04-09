---
change-id: "20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design"
dependencies:
  hard_blocking: []
  soft_dependency:
    - id: "20260403__live-ops-truth-snapshot__live-ops-policy-baseline"
      reason: "live ops policy baseline 先完成有助于确认 diagnostics parity 需求，但不硬阻塞设计"
  blocked_by: []
---

# Bridge And Cutover Design 开发计划

**状态**：in_progress
**进度**：0%
**日期**：2026-04-10
**范围**：`rust/`、`pyproject.toml`、`docs/architecture/`
**topic-id**：rust-ctp-runtime-cutover
**change-id**：20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design
**关联 acceptance**：./acceptance.md

## 一、需求简述

冻结把 Python native wrapper 主路径迁到 Rust-owned runtime + PyO3 bridge 的核心设计决策：

1. Rust workspace crate 结构（新增 `ctp_py` 为 PyO3 extension module 载体）。
2. PyO3 bridge API 最小形状（`CtpMdSession`、`CtpTdSession` 两个 Python class 的方法签名）。
3. 切换顺序（MD path first → TD bootstrap → Python ctypes retirement 前置条件）。
4. Diagnostics parity 要求（哪些失败场景新路径必须等价归因）。
5. Build system 切换（maturin 作为 `ctp_py` 的 build backend）。

## 二、关键设计决策

### 2.1 Crate 结构

| crate | 类型 | 用途 |
| --- | --- | --- |
| `ctp_runtime_core` | rlib + cdylib | 核心运行时，cdylib 产物 = `ctp_native.dll`（C ABI，供旧 ctypes 路径继续使用） |
| `ctp_py` (NEW) | cdylib | PyO3 extension module，产物 = `ctp_runtime.pyd`（Python 3 名称约定） |

`ctp_py` 依赖 `ctp_runtime_core` 的 rlib，通过 Rust calls Rust 调用核心逻辑，不重复编译 C++ bridge。

### 2.2 Build System

- `ctp_runtime_core` 继续由 `build.rs` 通过 `cc` crate 编译 `ctp_vendor_bridge.cpp`，输出静态库。
- `ctp_py` 依赖 `ctp_runtime_core`：link.rs emit 的 cargo metadat 会传播给所有依赖 crate，C++ 静态库会被传入 `ctp_py` 的最终链接。
- `pyproject.toml` 切换到 maturin，指向 `rust/ctp_py/Cargo.toml`。
- 同时保留 `setuptools` 能力，确保纯 Python 包安装不中断。

### 2.3 PyO3 API 最小形状（C1 冻结）

```rust
// ctp_py/src/lib.rs
#[pyclass]
pub struct CtpMdSession { ... }

#[pymethods]
impl CtpMdSession {
    #[new]
    fn new(front: &str, broker: &str, user: &str, password: &str) -> Self;
    fn init(&mut self) -> i32;           // 0 = ok, <0 = error code
    fn login(&mut self) -> i32;
    fn subscribe(&mut self, symbols: Vec<String>) -> i32;
    fn last_tick(&self, symbol: &str) -> Option<PyTick>;
    fn dispose(&mut self);
}

#[pyclass]
pub struct CtpTdSession { ... }

#[pymethods]
impl CtpTdSession {
    #[new]
    fn new(front: &str, broker: &str, user: &str, password: &str, appid: &str, auth_code: &str) -> Self;
    fn init(&mut self) -> i32;
    fn authenticate(&mut self) -> i32;
    fn login(&mut self) -> i32;
    fn query_instruments(&mut self) -> i32;
    fn query_account(&mut self) -> i32;
    fn query_positions(&mut self) -> i32;
    fn dispose(&mut self);
}
```

### 2.4 切换顺序

1. C2：`rust-owned-md-runtime-bridge` — MD path 迁到 `CtpMdSession` PyO3 class
2. C3：`rust-owned-td-bootstrap-runtime` — TD auth/login/settlement 迁到 `CtpTdSession` PyO3 class
3. C4：`python-native-path-retirement` — Python ctypes 主路径退休前置条件全满足后删除

### 2.5 Diagnostics Parity 要求

新路径必须能等价归因以下失败场景：

| 场景 | 现有诊断 | 新路径要求 |
| --- | --- | --- |
| 缺 CTP vendor DLL | `FileNotFoundError` / `OSError` | `CTP_NATIVE_NOT_FOUND` (-9000) |
| 无效 handle | `AccessViolation` / segfault | `INVALID_HANDLE` (-9001) |
| 登录失败 | callback error code | `CtpLoginError(reason)` |
| 订阅失败 | callback error code | `CtpSubscribeError(symbol, reason)` |
| 断线 | `4097` disconnect event | `CtpDisconnected(reason_code)` |

## 三、C1 实施范围

1. 新增 Rust workspace 成员 `ctp_py`（Cargo.toml + src/lib.rs 最小骨架）。
2. 在 `ctp_py/src/lib.rs` 中用 PyO3 实现 `CtpMdSession` 和 `CtpTdSession` 桩（调用 `ctp_runtime_core` 的 FFI）。
3. 切换 `pyproject.toml` 到 maturin，保证 `maturin develop` 和现有 `pip install -e .` 等价。
4. 更新 `scripts/check_rust_gate.py` 检查 `ctp_runtime.pyd` 产物存在。
5. 将设计决策写入 `docs/architecture/pyo3-bridge-design.md`。
