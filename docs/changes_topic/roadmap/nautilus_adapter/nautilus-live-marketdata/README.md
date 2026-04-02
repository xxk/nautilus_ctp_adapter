# Nautilus Live Marketdata Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**进度**：Topic 3 / 5
**topic-id**：nautilus-live-marketdata
**用途**：在 `InstrumentProvider` 稳定后，把 Topic 1 的 live 行情链路正式接入 Nautilus `LiveDataClient` 与订阅恢复路径。

---

## 一、主题目标

1. 把 Python/Rust runtime 的行情事件稳定出桥到 Nautilus 数据侧。
2. 建立订阅、退订、恢复和批量事件 drain 的正式适配层语义。
3. 冻结 Nautilus 数据侧 smoke 入口，避免后续 topic 重复定义行情验证口径。

## 二、进入条件

1. `nautilus-instrument-provider` 已完成，真实合约定义可稳定提供。
2. Topic 1 的 MD 主线路径和 smoke baseline 已冻结。

## 三、Topic 级出口条件

1. `LiveDataClient` 能以正式路径接收真实行情。
2. 订阅恢复和批量 drain 规则已明确，且与 runtime performance guidelines 一致。
3. `rb2610` 或同级真实合约的 Nautilus 行情 smoke 可重复通过。
4. 后续执行 topic 不需要再重写数据侧入口。

## 四、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260402__nautilus-live-marketdata__marketdata-runtime-event-contract` | 冻结 runtime 到 adapter 的市场数据事件 contract | ✅ 已完成 |
| C2 | `20260402__nautilus-live-marketdata__live-data-client-bootstrap` | 建立最小 `LiveDataClient` 主线 | ✅ 已完成 |
| C3 | `20260402__nautilus-live-marketdata__subscription-restore-and-batching` | 收口恢复、批量 drain 和节流语义 | ✅ 已完成 |
| C4 | `20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline` | 冻结行情 smoke 入口与证据格式 | ✅ 已完成 |

## 五、AI-TASK-QUEUE

**当前状态**：已激活。

- [x] 创建 `C1` child change bundle
- [x] 完成 `C2`
- [x] 完成 `C3`
- [x] 完成 `C4`
- [x] 回写 mainline roadmap 与 Topic 4 进入条件

**当前 first action**：Topic 已完成；交接给 `nautilus-live-execution`

**激活规则**：Topic 2 已 completed；当前 topic 已进入 `in_progress`。

## 六、交接给下一 Topic 的稳定产物

1. marketdata runtime event contract
2. `LiveDataClient` bootstrap path
3. subscription restore rule
4. Nautilus marketdata smoke baseline

## 七、当前已冻结结论

1. login / tick / disconnect payload 已冻结成明确 dataclass
2. `CtpDataClient` 已具备独立 marketdata deque
3. `LiveDataClient` bootstrap 已冻结为“live instrument query -> 精确选 symbol -> MD connect/subscribe”
4. 当前主线不会因为 provider result 带出 related instruments 而误订阅整条期权链
5. `drain_marketdata_event_batch(limit)` 与 `restore_market_data_subscriptions()` 已成为当前稳定 contract
6. Topic 3 已达到 topic 级出口条件
