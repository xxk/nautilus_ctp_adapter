# Nautilus Instrument Provider Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：Topic 2 / 5
**topic-id**：nautilus-instrument-provider
**用途**：承接 `ctp-live-connectivity` 的已验证 live/bootstrap 口径，建立 CTP 合约查询、符号归一化和 Nautilus `InstrumentProvider` 的正式主线。

---

## 一、主题目标

1. 冻结 CTP 合约查询在 runtime 与 adapter 间的责任边界。
2. 明确 CTP 合约到 Nautilus Instrument 的符号、交易所和精度映射规则。
3. 让 `InstrumentProvider` 能以正式路径产出 `rb2610` 等真实合约定义，而不是依赖临时样例。

## 二、进入条件

1. `ctp-live-connectivity` 已完成，live config、native ownership、MD 主线和 smoke baseline 已冻结。
2. Topic 1 的关键 live 合约至少有一条可复现证据路径。

## 三、Topic 级出口条件

1. 仓库存在稳定的 instrument query contract。
2. 交易所代码、symbol、tick size、multiplier、product kind 的归一化规则已冻结。
3. Nautilus `InstrumentProvider` 最小闭环能返回真实合约定义并留证。
4. 后续 `nautilus-live-marketdata` 不需要再重新定义 instrument 解析规则。

## 四、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260402__nautilus-instrument-provider__instrument-query-runtime-contract` | 冻结合约查询 contract 与 runtime/query 边界 | ✅ 已完成 |
| C2 | `20260402__nautilus-instrument-provider__exchange-and-symbol-normalization` | 冻结 symbol、exchange 与 product kind 归一化规则 | ✅ 已完成 |
| C3 | `20260402__nautilus-instrument-provider__instrument-provider-bootstrap` | 建立最小 `InstrumentProvider` 主线 | ✅ 已完成 |
| C4 | `20260402__nautilus-instrument-provider__instrument-smoke-baseline` | 收口正式 smoke 入口与证据格式 | ✅ 已完成 |

## 五、AI-TASK-QUEUE

**当前状态**：已激活。

- [x] 创建 `C1` child change bundle
- [x] 完成 `C3 -> C4`
- [x] 回写 mainline roadmap 与 Topic 3 进入条件

**当前 first action**：无；等待 mainline 切换到 `nautilus-live-marketdata`

**激活规则**：Topic 1 已 completed；当前 topic 已进入 `in_progress`。

**可并行预备范围**：只允许 docs-only 工作，例如预创建 `C1-C4` 的 change bundle、冻结 acceptance 结构、整理 symbol/exchange 映射输入；不允许提前写 `InstrumentProvider`、runtime query 或正式 adapter 代码。

## 六、交接给下一 Topic 的稳定产物

1. instrument query contract
2. symbol/exchange normalization rule
3. provider bootstrap evidence
4. instrument smoke baseline

## 七、当前已冻结结论

1. Query contract 已冻结为 `QUERY_INSTRUMENTS -> INSTRUMENT* -> INSTRUMENT_END`
2. Query bootstrap 必须走共享 `runtime_bridge`
3. 当前 normalization helper 已冻结 exchange alias、symbol case、product kind 规则
4. `CZCE 4位/3位月份转换` 暂不在 `C2` 处理
5. 正式 instrument smoke baseline 已冻结为 `ctp_instrument_query_smoke.py`
6. Topic 2 已达到 topic 级出口条件
