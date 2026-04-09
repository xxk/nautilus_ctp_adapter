---
change-id: "20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime"
dependencies:
  hard_blocking:
    - "20260410__rust-ctp-runtime-cutover__rust-owned-md-runtime-bridge"
  soft_dependency: []
  blocked_by: []
---

# Rust-Owned TD Bootstrap Runtime 开发计划 / Rust-Owned TD Bootstrap Runtime Plan

**状态**：进行中
**进度**：0%
**日期**：2026-04-10
**范围**：`rust/ctp_py/`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、`tests/test_smoke_import.py`、相关 docs
**topic-id**：rust-ctp-runtime-cutover
**change-id**：20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 本 change 要把 TD bootstrap/readiness 主路径从 Python `CtpTdApi` ctypes boundary 切到 PyO3 internal live session。
2. 交付内容是：internal TD live session 接入 `ctp_runtime_core::ffi::Td*`，并让 `bootstrap_live_execution_client_mainline()`、`run_live_td_readiness_smoke()` 走新主路径。
3. 本 change 不做真实 order send cutover，不改 execution guardrails 口径。
4. 真正完成信号是：TD bootstrap 不再直接依赖 `CtpTdApi` 主路径，Rust gate 与 pytest 继续通过。

## 二、能力映射 / Capability Mapping

```text
- capability_id: rust_owned_td_bootstrap_runtime
- capability_name: Rust-Owned TD Bootstrap Runtime / Rust 接管 TD Bootstrap Runtime
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/rust_ctp/rust-ctp-runtime-cutover/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/pyo3-bridge-design.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`rust/ctp_py/`、`execution_client.py`、`tests/test_smoke_import.py`、当前 change bundle、topic/docs 导航。
2. 禁止修改：真实 order send 语义、Topic 4 guardrails、无关 docs。
3. 当前正式入口：`bootstrap_live_execution_client_mainline()`、`run_live_td_readiness_smoke()`。
4. 开始前必须阅读：C2 closeout、`platform-neutral-ctp-runtime.md`、`rust-python-adapter-split.md`。
5. 改完后必须执行：`python scripts/check_rust_gate.py`、`python -m pytest tests/ -q`。

## 四、背景与约束

1. `ctp_runtime_core::ffi::Td*` 已存在真实 vendor bridge 接口。
2. TD callback 同样不携带 handle；本 change 允许先沿用“单个活跃 TD session”限制。
3. order lifecycle 真正 native send 仍由后续 change 决定，不在本 change 混入。

## 五、阶段划分

1. P1：创建 C3 bundle 并切换 frontier。
2. P2：新增 internal TD live session。
3. P3：切 execution bootstrap/readiness 主路径。
4. P4：补 tests、跑 gate、回填 docs。
