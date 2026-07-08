---
change-id: "20260410__rust-ctp-runtime-cutover__rust-owned-md-runtime-bridge"
dependencies:
  hard_blocking:
    - "20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design"
  soft_dependency: []
  blocked_by: []
---

# Rust-Owned MD Runtime Bridge 开发计划 / Rust-Owned MD Runtime Bridge Plan

**状态**：已完成
**进度**：100%
**日期**：2026-04-10
**范围**：`rust/ctp_py/`、`src/nautilus_ctp_adapter/adapters/ctp/data_client.py`、`src/ctp_runtime/__init__.py`、`tests/test_smoke_import.py`、相关 docs
**topic-id**：rust-ctp-runtime-cutover
**change-id**：20260410__rust-ctp-runtime-cutover__rust-owned-md-runtime-bridge
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 本 change 要把 MD live smoke 的正式主路径从 Python `CtpMdApi` ctypes boundary 切到 PyO3 internal live session。
2. 交付内容是：新增 PyO3 `CtpMdLiveSession` 接入 `ctp_runtime_core::ffi::Md*`，并让 `CtpDataClient.run_live_md_smoke()` 走新的 session bridge。
3. 本 change 不做 TD path cutover，不做 Nautilus EventBus 直连，不下沉 Python host event shaping。
4. 真正完成信号是：`data_client` 不再 import/use `CtpMdApi` 作为主路径；Rust gate 与 pytest 继续通过；新增 contract tests 锁住 PyO3 MD 主线行为。

## 二、能力映射 / Capability Mapping

```text
- capability_id: rust_owned_md_runtime_bridge
- capability_name: Rust-Owned MD Runtime Bridge / Rust 接管 MD Runtime 桥接
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/rust-ctp-runtime-cutover.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/pyo3-bridge-design.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`rust/ctp_py/`、`src/nautilus_ctp_adapter/adapters/ctp/data_client.py`、`src/ctp_runtime/__init__.py`、`tests/test_smoke_import.py`、当前 change bundle 与 topic/docs 导航。
2. 禁止修改：TD 主路径、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、topic 外无关 docs、`vendor/` 内容。
3. 当前正式入口与主要实现落点：MD smoke 正式入口在 `CtpDataClient.run_live_md_smoke()`；PyO3 bridge 实现在 `rust/ctp_py/src/lib.rs`。
4. 开始前必须阅读：`docs/architecture/platform-neutral-ctp-runtime.md`、`docs/architecture/rust-python-adapter-split.md`、`docs/architecture/runtime-performance-guidelines.md`、上一项 C1 bundle。
5. 改完后必须执行：`python scripts/check_rust_gate.py`、`python -m pytest tests/ -q`。

## 四、背景与约束

1. `ctp_runtime_core` 的 `MdCreate/MdInit/MdLogin/MdSubscribe/MdSet*Callback` 已存在，并在 `ctp_vendor_bridge` 可用时接真实 vendor bridge。
2. `data_client.py` 当前只在 `run_live_md_smoke()` 一处直接使用 `CtpMdApi`，所以切换面较小。
3. 底层 MD callback 不携带 session handle；本 change 显式接受“单个活跃 MD session”限制，并把它记入 docs / constraints。

## 五、设计方案

1. 为避免破坏 C1 已验收的 public scaffold contract，本 change 不直接改变公开 `CtpMdSession` 语义，而是在 `ctp_py` 中新增 internal `CtpMdLiveSession`。
2. `CtpMdLiveSession` 接入真实 native handle 生命周期，并绑定 login/tick/disconnect callback 到 Python callable。
3. Python host glue 保持不变：`data_client` 继续负责等待、超时、把 callback 输入转成 `CtpRuntimeEvent`。
4. `CtpMdApi` 保留为历史 boundary，但不再作为 MD smoke 主路径。
5. `src/ctp_runtime/__init__.py` 在 Windows 上先注册 `vendor/ctp/bin`，再导入 `_ctp_runtime.pyd`，避免 vendor DLL 解析失败。

## 六、阶段划分

1. P1：建立 C2 change bundle，并把 docs frontier 切到 C2。
2. P2：新增 internal `CtpMdLiveSession` 并接入 `ctp_runtime_core::ffi::Md*` 与 callback bridge。
3. P3：切换 `run_live_md_smoke()` 到 PyO3 主路径，并补 contract tests。
4. P4：跑 rust gate + pytest，回填 acceptance 与 roadmap。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立 C2 bundle 并激活 frontier | topic queue | 当前 change bundle、topic/docs 索引 | 正式执行单元 | 文档自检 | topic roadmap/docs index | C2 可被直接执行 | 已完成 |
| P2 | internal `CtpMdLiveSession` 接入真实 `Md*` FFI | C2 | `rust/ctp_py/src/lib.rs` | live-capable MD session | `cargo build -p ctp_py` | `pyo3-bridge-design.md` | internal live session 能接真实 Rust MD FFI | 已完成 |
| P3 | 切换 `data_client` MD smoke 主路径 | C2 | `data_client.py`、`src/ctp_runtime/__init__.py` | PyO3 mainline smoke path | `pytest tests/test_smoke_import.py -q` | 无 | `run_live_md_smoke()` 不再使用 `CtpMdApi` | 已完成 |
| P4 | 新增/更新 CONTRACT-LOCK tests 与 closeout docs | C2 | `tests/test_smoke_import.py`、acceptance/topic/docs | 锁定新行为 | `python -m pytest tests/ -q` | 当前 change + topic roadmap | 全部门禁通过并回填 docs | 已完成 |

## 八、验证动作

1. `cargo build -p ctp_py --manifest-path rust/Cargo.toml`
2. `maturin develop`
3. `python scripts/check_rust_gate.py`
4. `python -m pytest tests/ -q`

## 九、完成定义

### 开发完成

1. internal `CtpMdLiveSession` 已使用真实 `ctp_runtime_core::ffi::Md*`。
2. `run_live_md_smoke()` 已切到 PyO3 主路径。
3. 新行为已有 contract/function 锁定测试。

### 交付完成

1. 当前 change `acceptance.md` 阻塞场景全部通过。
2. topic roadmap / docs index 已回填到 C2 当前状态。
3. `CtpMdApi` 不再是 MD smoke 主路径。

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

本次无长期规则增量。

## 十一、回写与相关变更 / Write-back & Related Changes

1. 已回写 topic roadmap 的当前进度与 active change。
2. `docs/README.md`、`docs/changes/README.md`、`docs/topics/README.md` 已同步指向当前 frontier。

## 十二、完成说明 / Closeout Notes

1. `data_client.run_live_md_smoke()` 已改为通过 lazy factory 创建 internal `CtpMdLiveSession`，不再走 `CtpMdApi`。
2. 为保持 C1 已验收的 public scaffold contract 不变，公开 `CtpMdSession` 仍保留 `-9000/-9001` 语义；live mainline 改由内部类承接。
3. `src/ctp_runtime/__init__.py` 已补 Windows DLL bootstrap，导入 `.pyd` 前会注册 `vendor/ctp/bin`。
4. 验证结果：`python scripts/check_rust_gate.py` 通过，`python -m pytest tests/ -q` 为 `88 passed`。
