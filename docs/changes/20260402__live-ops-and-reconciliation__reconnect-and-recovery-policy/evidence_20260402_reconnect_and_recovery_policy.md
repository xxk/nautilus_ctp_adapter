# Reconnect And Recovery Policy Evidence

**日期**：2026-04-02  
**topic-id**：`live-ops-and-reconciliation`  
**change-id**：`20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy`

## 一、policy 产物

已新增正式 policy：

1. [reconnect_recovery_policy.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy/reconnect_recovery_policy.md)

当前已冻结：

1. `MD` 自动 restore 允许范围
2. `TD` bootstrap 级恢复边界
3. runtime bridge 只能作为事件证据通道的规则
4. flow directory 的复用与唯一化边界
5. 自动重试与人工介入升级规则

## 二、仓内事实来源

本次 policy 直接继承的仓内事实包括：

1. [subscription restore evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__subscription-restore-and-batching/evidence_20260402_subscription_restore_and_batching.md)
2. [nautilus live smoke baseline evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md)
3. [order lifecycle smoke evidence](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-execution__order-lifecycle-smoke-baseline/evidence_20260402_order_lifecycle_smoke_baseline.md)

## 三、验证结果

1. `python scripts/check_topic_docs.py`
   结果：`SUMMARY topics=7 failures=0`
2. `python -m pytest`
   结果：`53 passed`

## 四、完成结论

当前 `C2` 已达成：

1. Topic 5 已有正式 reconnect/recovery 规则
2. 自动恢复与人工介入边界已成文
3. Topic 5 可以继续推进 `C3 audit-and-reconciliation-baseline`
