# Reconnect And Recovery Policy AI Constraints

**change-id**：`20260402__live-ops-and-reconciliation__reconnect-and-recovery-policy`
**topic-id**：`live-ops-and-reconciliation`

## Allowed

1. 修改 `docs/`
2. 修改当前 change 三件套

## Not Allowed

1. 不得把恢复策略写成新的真实交易执行授权
2. 不得跳过 Topic 5 的 `C2` 直接创建 `C3/C4` 正式内容
3. 不得回退 Topic 5 `C1` 已冻结的 startup runbook 分层

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
