# Nautilus Adapter Interface Design 接口设计冻结 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-13
**范围**：`docs/architecture/`、当前 change bundle
**change-id**：20260413__nautilus-host-integration__adapter-interface-design
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/nautilus-host-integration-design.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-13 12:00"
concluded_by: "AI"

exit_conditions:
  E1_success_scenarios: pass
  E2_failure_scenarios: pass
  E3_verification_cmds: pass
  E4_evidence_collected: pass
  E5_real_acceptance_only: pass
  E6_minimum_scenarios: pass

scenarios:
  A1: { exec: true, result: pass, blocking: true }
  A2: { exec: true, result: pass, blocking: true }
  A3: { exec: true, result: pass, blocking: true }
  A4: { exec: true, result: pass, blocking: true }
  A5: { exec: true, result: pass, blocking: true }
  A6: { exec: true, result: pass, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 通过 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 是 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-04-13 12:00 | |
| AI 执行人 | AI | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | 阻塞成功场景全部 ✅ | A1-A5 全部通过 |
| E2 | 关键失败场景符合预期 | ✅ | 阻塞失败场景全部 ✅ | 无失败场景（纯设计 change） |
| E3 | 必跑验证命令已完成 | ✅ | `check_change_docs.py` + `check_harness.py` | HARNESS_CHECK_OK; C1 change 无新增 issue |
| E4 | 关键证据已留存 | ✅ | 设计文档已创建 | `docs/architecture/nautilus-host-integration-design.md` |
| E5 | 正式验收不依赖 mock 或 test | ✅ | 本 change 为纯设计，不需要 mock | |
| E6 | 正式场景数不少于 6 个 | ✅ | 6 个场景 | A1-A6 |

### 场景看板 / Scenario Board

| # | 场景 | 类型 | 阻塞 | 状态 | 证据 |
| --- | --- | --- | :---: | :---: | --- |
| A1 | DataClient 方法映射表完整 | 成功 | ✅ | ✅ | 设计文档第三节：22 个方法的完整映射表，含优先级标注 |
| A2 | ExecutionClient 方法映射表完整 | 成功 | ✅ | ✅ | 设计文档第四节：12 个方法映射 + Order Lifecycle 事件映射表 |
| A3 | Config schema 定义完整 | 成功 | ✅ | ✅ | 设计文档第五节：CtpDataClientConfig / CtpExecClientConfig / CtpInstrumentProviderConfig |
| A4 | Factory 创建模式冻结 | 成功 | ✅ | ✅ | 设计文档第六节：Factory.create() + TradingNode 注册 + 共享 Provider 缓存 |
| A5 | Async 桥接方案明确 | 成功 | ✅ | ✅ | 设计文档第七节：loop.call_soon_threadsafe() + Future-based connect |
| A6 | InstrumentProvider 对接方式明确 | 成功 | — | ✅ | 设计文档第八节：CtpLiveInstrumentProvider(InstrumentProvider) + CTP→FuturesContract 映射 |

## 场景详细 / Scenario Details

### A1：DataClient 方法映射表完整

**前置条件**：已阅读 Nautilus `LiveMarketDataClient` 源码
**执行动作**：设计文档列出所有必须/可选方法与 CTP 实现映射
**预期结果**：
- `_connect()` → CTP MD init + login
- `_disconnect()` → CTP MD dispose
- `_subscribe_quote_ticks()` → CTP MD subscribe
- 其他方法标注为 "not supported" 或 "future"

**实际结果**：✅ 通过。设计文档第三节列出 22 个方法的完整映射表，包含 P0/P1/P2 优先级标注。覆盖 `_connect`, `_disconnect`, `_subscribe_quote_ticks`, `_subscribe_trade_ticks`, `_subscribe_instrument`, `_request_instrument` 等。Tick 转换设计（CTP NativeTickView → Nautilus QuoteTick）包含完整字段映射。

### A2：ExecutionClient 方法映射表完整

**前置条件**：已阅读 Nautilus `LiveExecutionClient` 源码
**执行动作**：设计文档列出所有必须/可选方法与 CTP 实现映射
**预期结果**：
- `_connect()` → CTP TD init + auth + login + settlement
- `_submit_order()` → CTP order insert
- `_cancel_order()` → CTP order action
- `generate_order_status_report()` → CTP order query
- `generate_fill_reports()` → CTP trade query
- `generate_position_status_reports()` → CTP position query

**实际结果**：✅ 通过。设计文档第四节列出 12 个方法的完整映射表。额外包含 Order Lifecycle 事件映射表（7 个 CTP 回调 → Nautilus OrderEvent 映射）和 OMS 特性说明（NETTING + MARGIN + CNY）。

### A3：Config schema 定义完整

**预期结果**：Config 包含 CTP front address, broker_id, user_id, password, app_id, auth_code 等字段，继承自 Nautilus LiveDataClientConfig / LiveExecClientConfig。

**实际结果**：✅ 通过。设计文档第五节定义了 `CtpDataClientConfig(LiveDataClientConfig, frozen=True)` 和 `CtpExecClientConfig(LiveExecClientConfig, frozen=True)`，包含 md_front/td_front, broker_id, user_id, password, app_id, auth_code 等字段。额外定义了 `CtpInstrumentProviderConfig(InstrumentProviderConfig, frozen=True)` 和 `to_adapter_config()` 桥接方法。

### A4：Factory 创建模式冻结

**预期结果**：Factory 可以在 TradingNodeBuilder 中注册，create() 方法接收标准 Nautilus 参数并返回正确的 adapter 实例。

**实际结果**：✅ 通过。设计文档第六节包含 `CtpLiveDataClientFactory.create()` 和 `CtpLiveExecClientFactory.create()` 完整签名，TradingNode 注册代码示例，以及共享 InstrumentProvider 的模块级缓存方案（参照 IB adapter 的 `get_cached_ib_client()` 模式）。

### A5：Async 桥接方案明确

**预期结果**：设计文档明确 CTP 的 sync callback 如何在 asyncio event loop 中安全调度。

**实际结果**：✅ 通过。设计文档第七节完整描述了：(1) 问题：CTP callback 在 C++ 线程中执行；(2) 解决方案：`loop.call_soon_threadsafe()` 将 callback 调度到 event loop；(3) DataClient 和 ExecutionClient 的 callback 桥接代码模式；(4) Connect/Disconnect 的 `asyncio.Future`-based 等待模式。

### A6：InstrumentProvider 对接方式明确

**预期结果**：设计文档说明是继承 Nautilus InstrumentProvider 基类还是复用现有 CtpInstrumentProvider。

**实际结果**：✅ 通过。设计文档第八节确认创建 `CtpLiveInstrumentProvider(InstrumentProvider)` 继承 Nautilus 基类，内部复用现有 `CtpInstrumentProvider`。包含 `load_all_async` / `load_ids_async` / `load_async` 的 CTP 实现方式，以及 CTP InstrumentField → Nautilus FuturesContract 的字段映射和 InstrumentId 命名规范（`rb2610.CTP`）。
