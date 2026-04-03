# Live Startup Runbook Evidence

**日期**：2026-04-02
**topic-id**：`live-ops-and-reconciliation`
**change-id**：`20260402__live-ops-and-reconciliation__live-startup-runbook`

## 一、runbook 产物

已新增正式 runbook：

1. [live_startup_runbook.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__live-ops-and-reconciliation__live-startup-runbook/live_startup_runbook.md)

它已经冻结：

1. mainline startup entrypoint
2. diagnostics entrypoint
3. 启动前检查
4. 标准启动顺序
5. execution guardrails 继承规则

## 二、入口回写

已回写：

1. [scripts/README.md](/D:/Nautilus/nautilus_ctp_adapter/scripts/README.md)
2. [live-ops-and-reconciliation README](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md)

## 三、验证结果

1. `python scripts/check_topic_docs.py`
   结果：`SUMMARY topics=7 failures=0`
2. `python -m pytest`
   结果：`53 passed`

## 四、完成结论

当前 `C1` 已达成：

1. Topic 5 有了正式 runbook 起点
2. mainline 与 diagnostics 已明确分层
3. Topic 5 可以继续推进 `C2 reconnect-and-recovery-policy`
