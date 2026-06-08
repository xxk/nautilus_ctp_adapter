# P002 Decision Log / 决策记录

**fragment-id**：`decision_log`
**适用场景**：评审过程中产生了多轮需要保留的判断。

---

## Decision Log

| 日期 | 决策 | 原因 | 回写动作 | 明确不做 |
| --- | --- | --- | --- | --- |
| 2026-06-03 | 先开 proposal，不先开 ADR | 当前问题是多 phase 能力补齐与验收治理，不是已有架构路线冲突 | 建立 P002 proposal、phase plan、acceptance matrix | 不把 provider readiness 写成 ADR |
| 2026-06-03 | IB provider parity 作为能力参照 | Nautilus 官方 IB adapter 已有 provider/data/execution 共享 provider、cache hydration 和 report contract 可参考 | 在 acceptance 中冻结 `IB-provider-parity baseline` | 不复制 IB/TWS client architecture |
| 2026-06-03 | Phase 1 优先补 InstrumentProvider cache hydration | 当前 CTP factories 返回空白 `InstrumentProvider()`，这是行情和执行共同依赖的最大 provider 缺口 | change-map 指向 Phase 1 child change | 不等待 live 交易窗口才开始补 repo-only provider contract |
| 2026-06-03 | repo-only acceptance 与 OpenCTP paper/live acceptance 分离 | OpenCTP paper SDK/front/交易窗口/disconnect storm 是外部条件，不能阻塞本地 contract work | acceptance 分层为 L0-L6 | 不用 mock 伪装 OpenCTP paper evidence |
| 2026-06-08 | OpenCTP paper 账户作为 P002 live-capable development account | provider production readiness 需要真实 CTPAPI-facing paper account 开发闭环，但不能使用生产 real-account 做日常开发试错 | README、phase-plan、acceptance、change-map 回写 account-layer boundary | 不把 OpenCTP TTS simulation、OpenCTP paper account、formal-trading final evidence 混成同一层 |

## 记录规则

1. 只记录会影响后续执行边界的稳定判断。
2. 已升格为长期规则的内容应回写到 `docs/architecture/` 或 `docs/adr/`。
3. 若后续发现 CTP provider contract 需要偏离 IB parity，必须先在本 decision log 写清原因，再改 phase 或 child change scope。
4. 若后续改变开发账户层级，必须先说明为什么 OpenCTP paper 账户不再足够，并同步更新 acceptance 的 account-layer matrix。


