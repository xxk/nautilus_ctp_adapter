# Live Execution Client Bootstrap AI Constraints

**change-id**：`20260402__nautilus-live-execution__live-execution-client-bootstrap`  
**topic-id**：`nautilus-live-execution`

## Allowed

1. 修改 `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`
2. 修改 tests、当前 change 三件套与相关 architecture docs

## Not Allowed

1. 不得绕开 guardrails
2. 不得默认开启真实发单
3. 不得回退到托管主线

## Required Validation

```powershell
python -m pytest
python -m pip install -e .
```
