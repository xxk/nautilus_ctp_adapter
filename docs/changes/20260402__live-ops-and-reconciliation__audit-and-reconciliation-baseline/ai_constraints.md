# Audit And Reconciliation Baseline AI Constraints

**change-id**：`20260402__live-ops-and-reconciliation__audit-and-reconciliation-baseline`
**topic-id**：`live-ops-and-reconciliation`

## Allowed

1. 修改 `docs/`
2. 修改当前 change 三件套

## Not Allowed

1. 不得把 audit/reconciliation 文档写成新的真实交易执行授权
2. 不得跳过 `C3` 直接进入 `C4` 正式收尾
3. 不得回退 `C1/C2` 已冻结的启动与恢复规则

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
