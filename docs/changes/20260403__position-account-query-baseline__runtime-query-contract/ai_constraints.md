# Runtime Query Contract AI Constraints

**change-id**：`20260403__position-account-query-baseline__runtime-query-contract`
**topic-id**：`position-account-query-baseline`

## Allowed

1. 修改 `src/nautilus_ctp_adapter/runtime/`
2. 修改 `src/nautilus_ctp_adapter/adapters/ctp/`
3. 修改 `tests/`
4. 修改 `docs/`

## Not Allowed

1. 不得新增真实下单、撤单、改单行为
2. 不得把 export 存在误写成 position/account 已正式验收通过
3. 不得跳过 `C1` 直接进入 `C2/C3/C4` 实现

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
