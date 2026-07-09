# TD Mainline Login Bootstrap AI Constraints

**change-id**：`20260402__nautilus-live-execution__td-mainline-login-bootstrap`  
**topic-id**：`nautilus-live-execution`

## Allowed

1. 修改 `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`
2. 修改 tests、当前 change 三件套与 topic docs
3. 回写 architecture 文档

## Not Allowed

1. 不得接入真实发单主线
2. 不得绕开 Topic 4 guardrails
3. 不得回退到托管主线

## Required Validation

```powershell
python -m pytest
python -m pip install -e .
```
