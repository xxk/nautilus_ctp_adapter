# Python Native Path Retirement 设计 / Design

**状态**：待实现
**日期**：2026-04-10
**范围**：`rust/ctp_py/`、`instrument_provider.py`、`execution_client.py`
**关联 plan**：./plan.md

## 一、现状

1. C2 已把 `data_client.py` 的 MD smoke 主路径切到 internal `CtpMdLiveSession`。
2. C3 已把 `run_live_td_readiness_smoke()` / bootstrap 主路径切到 internal `CtpTdLiveSession`。
3. 当前剩余 ctypes 主路径集中在以下 consumer：
   - `src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py`：`run_live_instrument_smoke()`
   - `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`：`capture_td_order_truth_baseline_mainline()`、`run_live_position_query_smoke()`、`run_live_account_query_smoke()`、`_run_live_order_lifecycle_smoke()`
4. public `CtpTdSession` 仍保持 scaffold contract；这与 C1 已验收的外部语义绑定，不能在 C4 偷偷改成 live session。

## 二、正式入口与实现落点

1. 正式实现文件：`rust/ctp_py/src/lib.rs`、`src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py`、`src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`。
2. 正式验证落点：`tests/test_smoke_import.py`、`scripts/check_rust_gate.py`、`scripts/ctp_repo_debug_smoke.py`、`python -m pytest tests/ -q`。
3. `native/td_ctypes.py` 在 C4 完成前可暂时保留为历史 boundary / test helper，但不再允许作为 consumer 正式入口。

## 三、设计方案

1. 继续采用 internal-live-session pattern：
   - 保持 public `CtpTdSession` 不动
   - 扩展 internal `CtpTdLiveSession` 支持 instrument/query/order-truth/live-order 所需 callback 与请求接口
2. Python 侧继续掌握：timeout、等待、runtime event emission、truth classification、guardrails、evidence 产出。
3. Rust 侧只暴露 thin bridge：`set_*_callback`、`qry_*`、`order_insert`、必要的 dispose / invalid-handle 行为。
4. cutover 顺序采用从低风险到高风险：
   - Step 1：instrument + account/position query
   - Step 2：order-truth observation
   - Step 3：guarded live order lifecycle
5. 最终状态是 adapter consumer 不再 import/use `CtpTdApi`；ctypes 模块是否物理删除，取决于 tests / compatibility 是否仍需要保留 helper 角色，但它不能继续承担主线路径身份。

## 四、接口与输入输出

1. internal `CtpTdLiveSession` 新增接口时，优先保持与现有 ctypes 入口一一对应：
   - `set_instrument_callback`
   - `set_position_callback`
   - `set_account_callback`
   - `set_exec_callback`
   - `qry_instrument`
   - `qry_position`
   - `qry_account`
   - `order_insert` / `order_action`（若 live order lifecycle 需要）
2. dispose 后所有新接口必须继续遵守 `INVALID_HANDLE` 口径，不允许 panic。
3. 缺 bridge / symbol 不可导入时，consumer 必须 fail-fast，并给出明确的 PyO3 bridge 缺失错误。

## 五、AI 实现约束

1. 不得引入 `try PyO3, except then ctypes` 这类运行时 fallback。
2. 不得为了快速 cutover 把 host glue 下沉进 Rust。
3. 不得通过修改 tests 让 consumer 继续保留 ctypes 主路径。
4. live order cutover 若需要真实 send，必须保留现有 execution guardrails 与超时/证据逻辑。

## 六、备选方案

### 方案 A：直接把 public `CtpTdSession` 改成 live session

不选。原因：会破坏 C1 已冻结的 scaffold contract，并让 repo debug smoke、对外 API、contract tests 同时漂移。

### 方案 B：长期保留 mixed mainline，只有 bootstrap 走 PyO3，其余 consumer 继续 ctypes

不选。原因：这会让 ownership 长期分裂，topic 成功信号无法达成，且 diagnostics / callback 语义会继续双轨并存。

## 七、风险与影响面

1. `execution_client.py` 影响面大，尤其 live order lifecycle 触及真实副作用。
2. callback registry 需要覆盖多类 TD 回调，若设计不稳，容易引入状态串扰。
3. query / order-truth / live order 在一个 session 上共享时，需要保持现有 timeout 与 identity 逻辑不退化。

## 八、发布回滚与退出策略

1. 本 change 不使用运行时 fallback 作为“回滚”。
2. 若某一步 cutover 验证失败，应在开发分支回退该实现改动，而不是在代码里保留双主路径兜底。
3. 只有当所有 consumer 都切桥且 tests/guards 通过后，才能宣告 ctypes 正式主路径退休。

## 九、需要沉淀为长期规则的内容

1. `pyo3-bridge-design.md` 需要记录：C4 完成后，Python native ctypes 在本仓的最终角色。
2. 若 ctypes 模块最终仍保留 helper 身份，需要在 architecture 文档中明确“非正式主路径”。
