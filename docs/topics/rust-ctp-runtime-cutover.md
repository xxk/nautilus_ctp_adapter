# Rust 接管 CTP Runtime 切换 / Rust-Owned CTP Runtime Cutover

**创建日期**：2026-04-02
**最后更新**：2026-04-10
**状态**：已完成
**进度**：100%（C1/C2/C3/C4 已完成并验收）
**topic-id**：rust-ctp-runtime-cutover
**domain**：rust_ctp
**用途**：作为 `nautilus_ctp_adapter` 二期规划 topic，收口“从当前 Python native wrapper 主路径，迁移到 Rust-owned runtime 主路径”的正式阶段拆分、边界和切换门槛。

---

## 一、为什么这个 topic 适合作为二期

1. 当前仓库已经完成 `ctpnative`、MD/TD bootstrap、InstrumentProvider、marketdata、execution、ops/reconciliation 与 startup truth 基线，但真正的 Rust-owned runtime path 还未成为主线。
2. 当前 live 主线路径仍保留 Python `ctypes` wrapper 直接加载 `ctp_native.dll` 的实现事实；这与仓库长期目标“Rust core + PyO3 bridge + Python host glue”之间还存在一段明确的 cutover gap。
3. 这类迁移会同时触及 runtime、native loading、PyO3 bridge、adapter consumer 和 smoke gate，已经超出单个 child change 的安全范围，适合独立成长期 topic。

## 二、主题目标

1. 把正式主线路径收敛到 `Python adapter -> PyO3 bridge -> Rust runtime -> repo-owned ctp_native -> CTP vendor DLL`。
2. 冻结 Rust-owned runtime 与 Python host glue 的边界，避免 host-specific 逻辑继续泄漏到 shared runtime。
3. 在不破坏当前 live smoke、guardrails 和 failure diagnostics 的前提下，逐步退休 Python native wrapper 的主路径角色。
4. 为后续更稳定的 performance 优化、runtime contract 收敛和跨 host 复用打基础。

## 二点五、统一口径

1. 长期目标：选 `rust-ctp`，即 Rust 拥有 CTP runtime 与 native path，Python 只保留 host glue。
2. 实施路径：先走 `rust-py-ctp` 式过渡，再切到 `rust-ctp ownership`。
3. 这里的 `rust-py-ctp` 不是长期终态，而是 cutover 期间允许存在的过渡状态：Python 仍保留部分 native wrapper / bridge ownership，Rust 逐步接管 runtime 主路径。
4. 这里的 `rust-ctp` 也不是“去掉 Python”，而是把 Python 收缩到 Nautilus integration 层，不再拥有正式 native 主路径。

## 三、边界与限制

1. 允许推进：Rust native loading、callback registration、raw callback -> normalized event、PyO3 bridge、adapter consumer cutover、formal smoke parity。
2. 不允许推进：把 `InstrumentProvider`、`LiveDataClient`、`LiveExecutionClient` 的 host integration 逻辑整体下沉到 Rust。
3. 不允许把 symbol/exchange normalization 从 adapter side 挪进 runtime raw record 层。
4. 不允许因为迁移 runtime ownership 而扩大真实交易副作用；execution guardrails 必须继续生效。
5. 原规则：在当前 active topic 完成前，本 topic 只允许做 docs/design/prework。
2026-04-10 激活说明：live-ops-truth-snapshot C2 因外部连通性（4097 断线）阻塞，startup-truth-and-session-rebuild 已完成，用户明确推进，本 topic 现已激活进入主线实现。

## 四、进入条件

1. [startup-truth-and-session-rebuild](../../nautilus_adapter/startup-truth-and-session-rebuild/README.md) 已完成，当前 active change 不再处于 `in_progress`。
2. 当前正式 smoke baseline、startup truth baseline 与 session rebuild policy 已冻结，不再因运行真相收口而频繁改口径。
3. [Platform-neutral CTP runtime](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md)、[Rust / Python adapter split](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md) 与 [Runtime performance guidelines](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md) 继续作为继承规则，不在本 topic 重定义。
4. `python -m pytest`、`python -m pip install -e .`、`python scripts/check_rust_gate.py` 维持可执行。

当前已完成的 prework：

1. 仓内 Rust workspace 已能直接构建 repo-owned `ctp_native` scaffold artifact，不再依赖外部项目“生成 DLL”。
2. 当前 scaffold 已冻结第一版导出面、artifact guard 与最小 error contract，尚未接管真实 vendor DLL loading、callback bridge 或 live smoke 主路径。

## 五、Topic 级出口条件

1. Python adapter 层不再直接依赖 `td_ctypes.py` / `md_ctypes.py` 作为主线路径。
2. Rust runtime 已拥有 native loading、callback registration、normalized event buffering 的正式实现口径。
3. PyO3 bridge 已从 placeholder 变为正式 adapter-facing boundary，并冻结最小 API 形状。
4. MD login/subscribe、TD auth/login/settlement、formal Nautilus smoke 全部能通过 Rust-owned 主线路径复现。
5. failure diagnostics 对等性不退化：缺 DLL、参数错误、登录失败、订阅失败等失败场景仍可明确归因。
6. Python native wrapper 从“主线路径”降级为兼容/测试辅助或被正式移除，并同步更新 docs/README、topic index 和相关 architecture 文档。

## 六、预期 Child Change 顺序

> **状态标记**：✅ 已完成 | 🔄 进行中 | ⬜ 未开始

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260410__rust-ctp-runtime-cutover__bridge-and-cutover-design` | 冻结 cutover gate、bridge API、consumer 切换顺序与 diagnostics parity 口径 | ✅ 已完成 |
| C2 | `20260410__rust-ctp-runtime-cutover__rust-owned-md-runtime-bridge` | 先把 MD path 迁到 Rust-owned runtime + PyO3 bridge，保留 Python host glue | ✅ 已完成 |
| C3 | `20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime` | 再把 TD auth/login/settlement readiness 迁到 Rust-owned runtime | ✅ 已完成 |
| C4 | `20260410__rust-ctp-runtime-cutover__python-native-path-retirement` | 让 adapter consumer 全量切到 bridge，并退休 Python ctypes 主路径 | ✅ 已完成 |

## 七、AI-TASK-QUEUE

**当前状态**：已激活（2026-04-10）；live-ops-truth-snapshot C2 受外部连通性阻塞，并行推进本 topic。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 完成 `C1`（85 tests pass, gate pass, acceptance 已验收）
- [x] 创建 `C2` child change bundle
- [x] 完成 `C2`（PyO3 MD mainline cutover, rust gate pass, 88 tests pass）
- [x] 创建 `C3` child change bundle
- [x] 完成 `C3`（internal TD live session + PyO3 TD readiness mainline；`check_rust_gate.py` PASS；`ctp_repo_debug_smoke.py` PASS；`94 passed`）
- [x] 创建 `C4` child change bundle
- [x] 完成 `C4`（instrument/query/order-truth/live-order consumer 全量切到 internal TD live session；`95 passed`）
- [x] 回写主线、topic index、docs/README 与相关 architecture 文档

**当前 outcome**：Rust-owned runtime cutover topic 已完成；ctypes 已退出 adapter consumer 正式主路径，仅保留兼容 / test helper 边界。

## 八、成功信号

1. `src/nautilus_ctp_adapter/adapters/ctp/` 下的主 consumer 不再直接 import `CtpTdApi` / `CtpMdApi`。
2. `rust/ctp_runtime_core/src/python.rs` 不再只是 placeholder，而是提供正式 bridge export。
3. 正式 live smoke 依旧通过，但证据明确显示事件来自 Rust-owned runtime 主路径，而不是 Python native wrapper 直连。
4. Rust gate、pytest 与 formal smoke baseline 可以同时通过，且不需要靠临时 C# host 或新的旁路实现兜底。

## 九、与主线或其他 Topic 的关系

1. 这是 `nautilus-ctp-adapter-mainline` 初版完成后的二期候选 topic，不替代当前 active topic。
2. 它继承 `ctp-live-connectivity`、`nautilus-live-marketdata`、`nautilus-live-execution`、`live-ops-and-reconciliation` 与 `startup-truth-and-session-rebuild` 已冻结的事实。
3. 它的目标不是新增业务能力，而是把既有能力的 ownership 从 Python native path 迁到 Rust-owned runtime path。
