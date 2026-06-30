---
change-id: "20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime"
dependencies:
  hard_blocking:
    - "20260410__rust-ctp-runtime-cutover__rust-owned-md-runtime-bridge"
  soft_dependency: []
  blocked_by: []
---

# Rust-Owned TD Bootstrap Runtime 开发计划 / Rust-Owned TD Bootstrap Runtime Plan

**状态**：已完成
**进度**：100%
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
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/rust-ctp-runtime-cutover.md
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

## 六、完成说明 / Closeout Notes

1. `rust/ctp_py/src/lib.rs` 已新增 internal `CtpTdLiveSession`，并通过 callback registry 把 TD login/disconnect 回调桥接回 Python。
2. `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py` 的 `run_live_td_readiness_smoke()` 已切到 lazy factory + PyO3 TD live session 主路径，不再把 `CtpTdApi` 当成 bootstrap/readiness mainline。
3. 为保持已冻结的 public scaffold contract，不公开改变 `CtpTdSession` 的 `-9000/-9001` 语义；真实 live bootstrap 改由 internal class 承接。
4. `tests/test_smoke_import.py` 已补 internal symbol、PyO3 mainline、fail-fast contract tests，并同步更新 position/account query smoke 的 bootstrap mock 口径，使其在保留 ctypes 查询回调验证的同时对齐新的 PyO3 bootstrap 主路径。

## 七、验证结果 / Verification

1. `python scripts/check_rust_gate.py`：通过。
2. `python scripts/ctp_repo_debug_smoke.py`：通过，repo-only scaffold snapshot 继续稳定。
3. `python -m pytest tests/ -q`：`94 passed`。

## 八、交付结论 / Delivery Outcome

1. C3 目标已完成：TD bootstrap/readiness 正式主路径已切到 PyO3 internal live session。
2. 本 change 明确不覆盖真实 order send cutover；query/order/truth 基线路径仍留待后续 C4 统一收口。
3. 当前 frontier 可进入下一项 `python-native-path-retirement` 的 bundle 创建与边界冻结。
