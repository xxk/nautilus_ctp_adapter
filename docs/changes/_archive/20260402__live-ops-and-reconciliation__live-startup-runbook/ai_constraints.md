# Live Startup Runbook AI Constraints

**change-id**：`20260402__live-ops-and-reconciliation__live-startup-runbook`
**topic-id**：`live-ops-and-reconciliation`

## Allowed

1. 修改 `docs/`、`scripts/README.md`
2. 修改当前 change 三件套

## Not Allowed

1. 不得回退 Topic 1-4 已冻结的主线路径
2. 不得把 diagnostics 脚本写成正式 mainline 入口
3. 不得借 Topic 5 runbook 名义扩大真实交易动作

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
