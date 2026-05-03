---
change-id: "20260410__rust-ctp-runtime-cutover__python-native-path-retirement"
dependencies:
  hard_blocking:
    - "20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design"
    - "20260410__rust-ctp-runtime-cutover__rust-owned-md-runtime-bridge"
    - "20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime"
  soft_dependency: []
  blocked_by: []
---

# Python Native Path Retirement 开发计划 / Python Native Path Retirement Plan

**状态**：已完成
**进度**：100%
**日期**：2026-04-10
**范围**：`rust/ctp_py/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/test_smoke_import.py`、相关 docs
**topic-id**：rust-ctp-runtime-cutover
**change-id**：20260410__rust-ctp-runtime-cutover__python-native-path-retirement
**关联 acceptance**：./acceptance.md

> 本 change 使用 `plan.md + acceptance.md + ai_constraints.md + design.md` 四件套。原因：consumer cutover 顺序、public scaffold 保留边界、真实副作用 guardrails 与 ctypes 退休时机都容易改错，必须先冻结设计再实现。

## 一、需求简述

1. 本 change 要把 `src/nautilus_ctp_adapter/adapters/ctp/` 下剩余直接依赖 `CtpTdApi` 的主线路径退休为 PyO3 internal live session mainline。
2. 交付内容是：扩展 internal TD bridge 覆盖 instrument/query/order-truth/live-order 所需 callback 与 query/send 入口，并让 `instrument_provider.py`、`execution_client.py` 的正式 consumer 不再把 ctypes 当主路径。
3. 本 change 不重写 Python host glue，不改 execution guardrails，不提前修改 public `CtpTdSession` scaffold 的已冻结 `-9000/-9001` 语义。
4. 真正完成信号是：`src/nautilus_ctp_adapter/adapters/ctp/` 主 consumer 不再 import/use `CtpTdApi` 作为正式主线路径；Rust gate、repo debug smoke 与全量 pytest 继续通过；topic/docs frontier 完成回写。

## 二、能力映射 / Capability Mapping

```text
- capability_id: python_native_path_retirement
- capability_name: Python Native Path Retirement / Python Native 主路径退休
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/rust-ctp-runtime-cutover.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/pyo3-bridge-design.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`rust/ctp_py/`、`src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`、`tests/test_smoke_import.py`、当前 change bundle 与 topic/docs 导航。
2. 禁止修改：`vendor/`、public `CtpMdSession` / `CtpTdSession` scaffold contract、execution guardrails 业务语义、无关 topic/docs。
3. 当前正式入口与主要实现落点：`CtpInstrumentProvider.run_live_instrument_smoke()`、`CtpExecutionClient.run_live_position_query_smoke()`、`run_live_account_query_smoke()`、`capture_td_order_truth_baseline_mainline()`、`run_order_lifecycle_smoke_baseline(dry_run=false)`；PyO3 bridge 实现在 `rust/ctp_py/src/lib.rs`。
4. 开始前必须阅读：`docs/architecture/pyo3-bridge-design.md`、`docs/architecture/platform-neutral-ctp-runtime.md`、`docs/architecture/rust-python-adapter-split.md`、C1/C2/C3 bundle closeout。
5. 改完后必须执行：`python scripts/check_rust_gate.py`、`python scripts/ctp_repo_debug_smoke.py`、`python -m pytest tests/ -q`、`python scripts/check_topic_docs.py`。

## 四、背景与约束

1. 当前 `data_client.py` 的 MD smoke 已不再依赖 `CtpMdApi`，TD bootstrap/readiness 也已切到 internal `CtpTdLiveSession`。
2. 剩余 ctypes 主路径集中在两个 consumer：
   - `instrument_provider.py` 的 instrument query smoke
   - `execution_client.py` 的 order-truth、position/account query、live order lifecycle
3. public scaffold contract 仍需保持冻结，避免 C1 已验收的 external API 语义在 C4 中被意外扩展。
4. live order smoke 具有真实副作用风险，必须继续受 execution guardrails 保护，不能因为 runtime cutover 引入运行时 fallback 或弱化保护。

## 五、设计方案

1. 推荐方案：继续沿用 internal-live-session pattern，不直接修改 public `CtpTdSession`，而是在 `rust/ctp_py/src/lib.rs` 扩展 internal TD live session 的 callback / query / send 覆盖面。
2. Python host glue 继续负责超时、事件整形、truth classification、guardrails 与 evidence 产出；Rust 只补齐 thin session bridge。
3. 实施顺序按副作用从低到高推进：
   - 先 cut read-only instrument/query paths
   - 再 cut order-truth observation path
   - 最后 cut guarded live order lifecycle path
4. 在主 consumer 全部切桥完成前，不删除 `native/td_ctypes.py`；它可以暂时保留为历史 boundary / test helper，但不得继续被主 consumer import 作为正式入口。

## 六、阶段划分

1. P1：创建 C4 bundle，冻结 cutover 范围、顺序、public scaffold 边界与验证口径。
2. P2：扩展 internal TD live session 覆盖 instrument/query/order-truth 所需 callback 与 request 入口。
3. P3：切 `instrument_provider.py` 与 `execution_client.py` 剩余 read-only mainline。
4. P4：切 guarded live order lifecycle mainline，清理 consumer 层对 `CtpTdApi` 的正式依赖。
5. P5：跑 gate / pytest / docs guard，回填 acceptance 与长期文档。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立 C4 bundle 并切换 frontier | topic queue | 当前 change bundle、topic/docs 索引 | 正式执行单元 | `python scripts/check_topic_docs.py` | topic roadmap / docs index | C4 可被直接执行 | 已完成 |
| P2 | 扩展 internal TD live session 能力面 | C4 | `rust/ctp_py/src/lib.rs` | query/order-truth/order-send 所需桥接入口 | `python scripts/check_rust_gate.py` | `pyo3-bridge-design.md` | Rust side 能覆盖剩余 consumer 需求 | 已完成 |
| P3 | 切 read-only consumer 主路径 | C4 | `instrument_provider.py`、`execution_client.py`、tests | instrument/query/order-truth PyO3 mainline | `python -m pytest tests/test_smoke_import.py -q` | 当前 change bundle | main consumer 不再把 ctypes 当 read-only 主路径 | 已完成 |
| P4 | 切 guarded live order mainline | C4 | `execution_client.py`、tests | guarded live order PyO3 mainline | `python -m pytest tests/test_smoke_import.py -q` | 当前 change bundle | live order smoke 不再依赖 `CtpTdApi` 主路径 | 已完成 |
| P5 | 全量验证并回填 docs | acceptance | tests / docs / architecture | 验证证据 + closeout | `python scripts/check_rust_gate.py`; `python scripts/ctp_repo_debug_smoke.py`; `python -m pytest tests/ -q`; `python scripts/check_topic_docs.py` | topic roadmap / docs index / architecture | C4 可正式验收 | 已完成 |

## 八、完成说明 / Closeout Notes

1. `rust/ctp_py/src/lib.rs` 已把 internal `CtpTdLiveSession` 扩展到 instrument、position、account、order-truth 与 guarded live-order 所需 callback / query / send 能力面。
2. `src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py` 已切到 `_create_td_live_session()` 主路径，instrument smoke 不再把 `CtpTdApi` 当正式入口。
3. `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py` 已把 position/account query、order-truth baseline 与 guarded live-order smoke 全部切到 PyO3 internal TD live session。
4. `tests/test_smoke_import.py` 已补齐并收敛 C4 contract/function 回归，覆盖 instrument/query/order-truth/live-order mainline 与“不得回退到 ctypes”口径。

## 九、验证结果 / Verification

1. `python -m pip install -e ".[dev]"`：通过，当前 venv 已重建并加载最新 PyO3 extension。
2. `python scripts/check_rust_gate.py`：通过。
3. `python scripts/ctp_repo_debug_smoke.py`：通过，repo-owned scaffold snapshot 与冻结错误码继续稳定。
4. `python -m pytest tests/ -q`：`95 passed`。
5. `python scripts/check_topic_docs.py`：通过。

## 十、完成定义

### 开发完成

1. `instrument_provider.py` 与 `execution_client.py` 的正式 consumer 主路径不再直接 import/use `CtpTdApi`。
2. internal TD live session 已覆盖 read-only 与 guarded live order 所需最小桥接能力。
3. 行为变化已有 contract/function 锁定测试覆盖。

### 交付完成

1. `acceptance.md` 中阻塞场景通过。
2. topic roadmap / docs index / architecture 文档已回填到 C4 当前状态。
3. Python native ctypes 已不再承担 adapter consumer 正式主路径角色。

## 十一、交付结论 / Delivery Outcome

1. C4 目标已完成：adapter consumer 已不再直接 import/use `CtpTdApi` / `CtpMdApi` 作为正式主路径。
2. ctypes 边界当前仅保留为兼容 / test helper，不再承担 consumer mainline 角色；是否物理删除另开后续 change 决策。
3. `rust-ctp-runtime-cutover` topic 的 C1-C4 已全部完成并通过当前仓库 gate / smoke / pytest / docs guard。

## 十二、长期规则增量摘要 / Long-Term Rule Delta Summary

本次无长期规则增量。

## 十三、回写与相关变更 / Write-back & Related Changes

1. 当前已完成：topic roadmap / docs index 已更新为 C4 完成态，并保留当前 change 作为 closeout 证据入口。
2. `docs/architecture/pyo3-bridge-design.md` 已同步回写 ctypes 主路径退休后的最终边界：mainline retired，helper kept。
