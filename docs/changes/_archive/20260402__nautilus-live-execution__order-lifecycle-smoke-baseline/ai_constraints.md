# Order Lifecycle Smoke Baseline AI Constraints

**change-id**：`20260402__nautilus-live-execution__order-lifecycle-smoke-baseline`  
**topic-id**：`nautilus-live-execution`

## Allowed

1. 修改 `scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`
2. 修改 tests、当前 change 三件套与相关 architecture docs

## Not Allowed

1. 不得绕开 guardrails
2. 未冻结 `TdOrderSend/TdOrderAction` ABI 前，不得盲目真发单
3. 不得回退到托管主线

## Required Validation

```powershell
python -m pytest
python -m pip install -e .
```
