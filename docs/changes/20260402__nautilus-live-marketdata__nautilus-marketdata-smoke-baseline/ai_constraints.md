# Nautilus Marketdata Smoke Baseline AI Constraints

**change-id**：`20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline`  
**topic-id**：`nautilus-live-marketdata`

## Allowed

1. 修改 `scripts/` 中的 marketdata smoke 入口
2. 修改 `src/nautilus_ctp_adapter/adapters/ctp/data_client.py`
3. 修改 tests、当前 change 三件套与 topic docs

## Not Allowed

1. 不得回退到 C# 托管主线
2. 不得触及 execution 真发单主线
3. 不得重写 `C2/C3` 已冻结的 bootstrap / restore / batching contract

## Required Validation

```powershell
python -m pytest
python -m pip install -e .
python scripts/ctp_marketdata_smoke.py --config <path> --symbol rb2610
```
