# Operational Evidence Matrix AI Constraints

**change-id**：`20260402__live-ops-and-reconciliation__operational-evidence-matrix`
**topic-id**：`live-ops-and-reconciliation`

## Allowed

1. 修改 `docs/`
2. 修改当前 change 三件套

## Not Allowed

1. 不得把 matrix 文档写成新的真实交易授权
2. 不得把“baseline 已冻结”夸大成“完整自动运维已完成”
3. 不得回退 Topic 5 已冻结的 startup/recovery/audit 规则

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
