# Audit And Reconciliation Baseline Evidence

**日期**：2026-04-02  
**topic-id**：`live-ops-and-reconciliation`  
**change-id**：`20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline`

## 一、baseline 产物

已新增正式 baseline：

1. [audit_reconciliation_baseline.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline/audit_reconciliation_baseline.md)

当前已冻结：

1. 五类证据链分类
2. 自动证据链范围
3. 人工复核范围
4. 最小自动对账规则
5. 交给 `C4 operational-evidence-matrix` 的继承输入

## 二、仓内事实来源

本次 baseline 直接继承的正式证据包括：

1. [nautilus live smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md)
2. [nautilus marketdata smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline/evidence_20260402_nautilus_marketdata_smoke_baseline.md)
3. [order lifecycle smoke baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-execution__order-lifecycle-smoke-baseline/evidence_20260402_order_lifecycle_smoke_baseline.md)
4. [reconnect and recovery policy](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy/reconnect_recovery_policy.md)

## 三、当前明确未完成的部分

当前仍未形成正式 smoke baseline 的是：

1. position snapshot baseline
2. account snapshot baseline
3. 成交后持仓/资金联动自动对账

这三类在本次 baseline 中已显式列为“人工复核项”，没有被误写成已完成。

## 四、验证结果

1. `python scripts/check_topic_docs.py`
   结果：`SUMMARY topics=7 failures=0`
2. `python -m pytest`
   结果：`53 passed`

## 五、完成结论

当前 `C3` 已达成：

1. Topic 5 已有正式 audit/reconciliation baseline
2. 自动证据链与人工复核边界已冻结
3. Topic 5 可以继续推进 `C4 operational-evidence-matrix`
