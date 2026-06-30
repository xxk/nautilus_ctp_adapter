# Operational Evidence Matrix

**日期**：2026-04-02  
**topic-id**：`live-ops-and-reconciliation`  
**change-id**：`20260402__live-ops-and-reconciliation__operational-evidence-matrix`

## 一、用途

这份矩阵汇总 `nautilus_ctp_adapter` 当前初版可运维性的正式证据入口。

它覆盖四类运维任务：

1. startup
2. recovery
3. audit
4. reconciliation

## 二、矩阵

| 类别 | 正式入口 | 自动通过信号 | 人工复核项 | 当前状态 |
| --- | --- | --- | --- | --- |
| startup | `python scripts/ctp_nautilus_live_smoke.py --config <path>` | `MD login + first tick + TD login + settlement + bridge events` | 无 | ✅ 已冻结 |
| recovery | [reconnect_recovery_policy.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy/reconnect_recovery_policy.md) | `MD` 恢复后新 tick；`TD` 恢复后新 `LOGIN_SUCCEEDED + SETTLEMENT_CONFIRMED` | 历史 exec 回放歧义、订单真相判断 | ✅ 已冻结 |
| audit | [audit_reconciliation_baseline.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline/audit_reconciliation_baseline.md) | marketdata/order/trade 三类自动证据可留存 | position/account 尚需人工复核 | ✅ 已冻结 |
| reconciliation | [audit_reconciliation_baseline.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline/audit_reconciliation_baseline.md) | 已明确最小自动对账范围 | 持仓、资金、跨 session 真相判断 | ✅ 初版冻结 |

## 三、当前正式证据入口

1. [nautilus live smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md)
2. [nautilus marketdata smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline/evidence_20260402_nautilus_marketdata_smoke_baseline.md)
3. [order lifecycle smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-execution__order-lifecycle-smoke-baseline/evidence_20260402_order_lifecycle_smoke_baseline.md)
4. [live startup runbook](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/live_startup_runbook.md)
5. [reconnect recovery policy](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy/reconnect_recovery_policy.md)
6. [audit reconciliation baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline/audit_reconciliation_baseline.md)

## 四、当前初版完成结论

当前可以宣告完成的是：

1. Nautilus 方向的 live startup 基线
2. marketdata 与 execution 最小 smoke
3. recovery 边界
4. 最小 audit/reconciliation baseline

当前不能宣告完成的是：

1. 完整自动持仓对账
2. 完整自动资金对账
3. 完整跨 session 订单真相自动判定

## 五、mainline 收口口径

因此，`nautilus_ctp_adapter` 的 mainline 当前可标记为：

1. **初版 completed**
2. 已具备 live bootstrap、基础恢复、最小审计与最小对账口径
3. 后续若要继续增强，应作为新的 topic 或新一轮 mainline 扩展，而不是回写覆盖当前初版结论
