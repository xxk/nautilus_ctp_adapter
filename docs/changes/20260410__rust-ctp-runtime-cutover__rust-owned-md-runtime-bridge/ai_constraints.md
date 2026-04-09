# Rust-Owned MD Runtime Bridge AI 约束 / AI Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__rust-ctp-runtime-cutover__rust-owned-md-runtime-bridge
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 先读取 sibling `acceptance.md` 与 `plan.md`。
2. 本 change 只解决 MD 主路径 cutover，不跨到 TD。
3. 若真实 vendor bridge / SDK 不可用，可继续做 code + test + gate 层验证，但正式验收结论必须如实记录。

## 方法论 / Working Mode

1. 先打通 PyO3 `CtpMdSession` 的最小 live path，再切 `data_client`。
2. 不新增新的 host-native 旁路，不保留隐式 ctypes fallback。
3. 行为变化必须由 CONTRACT-LOCK tests 明确锁定。

## 边界 / Boundaries

1. Rust 仅负责 native session 与 callback bridge；Python 继续负责 timeout、state 等 host glue。
2. 不得把 `InstrumentProvider` / `LiveDataClient` 的业务整形逻辑下沉到 Rust。
3. 不得修改 `execution_client.py`、TD path 或 unrelated docs。
4. 允许保留 `md_ctypes.py` 文件，但不得继续作为 MD smoke 主路径。

## 特殊约束 / Special Constraints

1. 底层 MD callback 当前不带 handle，本 change 允许先锁定“单个活跃 MD session”限制；不得伪装成已支持多 session。
2. 任何失败必须 fail-fast，不得静默吞掉 callback 异常或自动回退到 ctypes。
3. `INVALID_HANDLE=-9001` 语义必须保持不变。

## 收尾 / Wrap-up

1. 完成后更新 topic roadmap、`docs/README.md`、`docs/changes/README.md`、`docs/topics/README.md` 的 current frontier。
2. gate / pytest 结果需回填到当前 change `acceptance.md`。
