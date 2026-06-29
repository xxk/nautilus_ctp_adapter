# Subscription Restore And Batching AI Constraints

**change-id**：`20260402__nautilus-live-marketdata__subscription-restore-and-batching`  
**topic-id**：`nautilus-live-marketdata`

## Allowed

1. 修改 `src/nautilus_ctp_adapter/adapters/ctp/data_client.py`
2. 修改相关 tests 与当前 change 三件套
3. 回写 architecture 与 topic roadmap 文档

## Not Allowed

1. 不得改 execution 真实交易主线
2. 不得重写 Topic 1 的正式 smoke baseline
3. 不得绕开 `C2` 已冻结的 bootstrap 入口另起一套 marketdata 主线

## Required Validation

```powershell
python -m pytest
python -m pip install -e .
```
