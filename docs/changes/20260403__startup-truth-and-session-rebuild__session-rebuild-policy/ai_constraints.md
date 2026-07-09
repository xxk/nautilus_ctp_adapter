# Session Rebuild Policy AI Constraints

**change-id**：`20260403__startup-truth-and-session-rebuild__session-rebuild-policy`
**topic-id**：`startup-truth-and-session-rebuild`

## Allowed

1. 修改 `src/nautilus_ctp_adapter/`
2. 修改 `scripts/`
3. 修改 `tests/`
4. 修改 `docs/`

## Not Allowed

1. 不得新增真实下单、撤单、改单行为
2. 不得用 test/mock/fake 结果充当验收证据

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
