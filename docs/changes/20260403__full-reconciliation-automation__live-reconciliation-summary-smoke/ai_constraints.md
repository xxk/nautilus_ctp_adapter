# Live Reconciliation Summary Smoke AI Constraints

**change-id**：`20260403__full-reconciliation-automation__live-reconciliation-summary-smoke`
**topic-id**：`full-reconciliation-automation`

## Allowed

1. 修改 `src/nautilus_ctp_adapter/`
2. 修改 `scripts/`
3. 修改 `tests/`
4. 修改 `docs/`

## Not Allowed

1. 不得新增真实下单、撤单、改单行为
2. 不得把 smoke 结果写成“完整自动对账完成”

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
