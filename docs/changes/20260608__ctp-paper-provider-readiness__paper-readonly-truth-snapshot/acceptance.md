# CTP Paper Provider Readiness Phase 2 Paper Read-only Truth Snapshot 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-06-08
**范围**：OpenCTP paper read-only truth snapshot
**change-id**：20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/proposals/p003-ctp-live-trading-provider-readiness/

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 18:45"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: false }
  A6: { exec: true, result: passed, blocking: false }
  A7: { exec: true, result: passed, blocking: true }
  A8: { exec: true, result: passed, blocking: true }
  A9: { exec: true, result: passed, blocking: false }
  A10: { exec: true, result: passed, blocking: false }
  A11: { exec: true, result: passed, blocking: true }
  A12: { exec: true, result: passed, blocking: true }
  A13: { exec: true, result: passed, blocking: false }
  A14: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success: paper account/position/order/trade/instrument snapshot emits redacted JSON | ✅ | ✅ | 是 | `paper-readonly-snapshot-connect.json` |
| A2 | Success: valid empty/no-position is distinct from timeout | ✅ | ✅ | 是 | `classify_positions_disposition` / `classify_account_disposition` tests |
| A3 | Success: snapshot output can feed Phase 3 pre/post reconciliation | ✅ | ✅ | 是 | schema has `reconciliation_role=pre_or_post_order_snapshot` |
| A4 | Failure: formal-trading / Live profile is requested | ✅ | ✅ | 是 | paper profile validation rejects non-OpenCTP fronts via shared preflight helper |
| A5 | Failure: missing paper front/query capability produces typed paper-resource blocker | ✅ | ✅ | 否 | example config returns `paper-resource` blocker |
| A6 | Regression: no account secret appears in snapshot output | ✅ | ✅ | 否 | redaction tests and output review |
| A7 | Success: snapshot schema includes run id, flow path, session label, account profile and evidence class | ✅ | ✅ | 是 | schema tests |
| A8 | Success: instrument metadata snapshot can hydrate provider/cache inputs | ✅ | ✅ | 是 | paper instrument record includes display symbol, exchange, product kind, tick, multiplier |
| A9 | Failure: malformed query rows produce typed data-contract disposition | ✅ | ✅ | 否 | instrument/position contract helper tests |
| A10 | Regression: repo-only snapshot tests run when OpenCTP paper front is unavailable | ✅ | ✅ | 否 | focused tests run without front; paper front only required for optional evidence |
| A11 | Success: 合约查询正确性 validates symbol, exchange, product kind, price tick, volume multiple and display id | ✅ | ✅ | 是 | `instrument_contract_issues` tests and paper evidence |
| A12 | Success: 持仓查询正确性 validates long/short direction, total qty, yd/td split, cost and no-position semantics | ✅ | ✅ | 是 | `position_contract_issues` tests and paper evidence |
| A13 | Failure: instrument metadata missing tick size or volume multiple still hydrates provider/cache | ✅ | ✅ | 否 | missing tick/multiplier produces typed contract issue |
| A14 | Failure: position direction or quantity fields are malformed | ✅ | ✅ | 否 | malformed direction/qty produces typed contract issue |

## 合约明细查询完整性 / 正确性验收设计

> 当前 Phase 2 已覆盖基础合约字段：`venue_symbol`、`display_symbol`、`exchange_id`、`product_kind`、`price_tick`、`volume_multiple`。本节补充下一轮合约明细查询的完整性和正确性验收设计；未被当前 runtime/query record 保留的字段不得伪造 pass，必须进入 planned follow-up 或 typed data-contract disposition。

### 完整性字段分层 / Completeness Field Layers

| Layer | 字段 | 目的 | 验收状态 |
| --- | --- | --- | --- |
| C0 Identity | `InstrumentID` / normalized `venue_symbol` / `display_symbol` | 合约唯一身份、Nautilus `InstrumentId` 与 CTP symbol 映射 | covered |
| C0 Venue | `ExchangeID` / normalized exchange | venue routing、订阅、下单 exchange 约束 | covered |
| C0 Trading unit | `PriceTick`, `VolumeMultiple` | tick-size、notional、order price/qty preflight | covered |
| C0 Product | `ProductClass` / normalized product kind | futures/options/security 分类与 provider hydration | covered |
| C1 Human metadata | `InstrumentName` | operator/runbook 展示、人工核对 | planned |
| C1 Lifecycle | `OpenDate`, `ExpireDate`, `StartDelivDate`, `EndDelivDate`, `IsTrading` | 合约是否可交易、到期/交割窗口 guardrail | planned |
| C1 Market limits | `LongMarginRatio`, `ShortMarginRatio`, `MaxMarketOrderVolume`, `MinMarketOrderVolume`, `MaxLimitOrderVolume`, `MinLimitOrderVolume` | order guardrail、risk preview、最小/最大委托量 | planned |
| C1 Product relation | `ProductID`, `UnderlyingInstrID`, `DeliveryYear`, `DeliveryMonth` | 合约月份、underlying、跨品种校验 | planned |
| C2 Options-specific | `OptionsType`, `StrikePrice`, `UnderlyingMultiple`, `CombinationType` | 期权链与组合合约；P003 paper futures baseline 不强制 | out_of_scope_current |

### 正确性校验规则 / Correctness Rules

| ID | 类型 | 规则 | Must fail if | 状态 |
| --- | --- | --- | --- | --- |
| CD-C1 | completeness | C0 字段全部存在且非空：symbol、exchange、product kind、price tick、volume multiple、display id | 任一 C0 字段缺失却进入 provider/cache | covered |
| CD-C2 | completeness | C1 字段若 runtime 可见，必须原样进入 redacted snapshot 的 `raw_detail` 或 `detail_fields` | 查询结果含字段但 wrapper 丢弃且无 disposition | planned |
| CD-C3 | correctness | `display_symbol` 必须由 normalized symbol + normalized exchange 派生，且与 provider/cache 使用一致 | 同一合约在 snapshot 和 provider/cache 中出现不同 id | covered |
| CD-C4 | correctness | `price_tick > 0`，`volume_multiple > 0`，委托价格必须可按 tick 对齐 | tick/multiplier 非正数仍允许下单 preflight | covered |
| CD-C5 | correctness | `ProductClass` 映射到已知 product kind；未知类型只能进入 `unknown_product_kind` disposition | unknown product kind 被当作 futures pass | planned |
| CD-C6 | correctness | 若 `IsTrading=false` 或合约处于到期/交割禁用窗口，Phase 3 下单 preflight 必须阻断 | 非交易合约仍进入 paper order send | planned |
| CD-C7 | correctness | 若 min/max order volume 可见，Phase 3 qty 必须落在范围内 | qty 超出合约限制仍通过 | planned |
| CD-C8 | negative | 同一 `InstrumentID` 返回多个 exchange 或冲突 tick/multiplier | 冲突字段被静默合并 | planned |

### Evidence Shape

| 字段 | 要求 | 示例 disposition |
| --- | --- | --- |
| `instruments.records[]` | 保留 normalized C0 字段，供 provider/cache 和 Phase 3 preflight 使用 | `passed` |
| `instruments.detail_fields[]` | 后续承接 C1/C2 原始明细字段，字段缺失时记录 missing list | `planned` |
| `instruments.contract_issues[]` | 字段缺失、非正 tick/multiplier、未知 product kind、冲突字段 | `data-contract` |
| `instruments.correctness_summary` | total、passed、failed、unknown、out_of_scope 计数 | `planned` |

### Completion Rule

当前 Phase 2 的 `passed` 只覆盖 C0 基础合约查询正确性。若要声明“合约明细查询完整性完成”，必须新增或扩展 runtime/query record，使 C1 字段可进入 evidence，并通过 CD-C2、CD-C5、CD-C6、CD-C7、CD-C8；否则只能声明为 `basic_contract_fields_passed`。

## 最终结论 / Final Verdict

- **结论**：✅ 通过
- **说明**：Paper read-only snapshot 已实现并验证；只读查询 account/position/instrument/order-trade snapshot，不发送订单，不使用 formal-trading / Live。
