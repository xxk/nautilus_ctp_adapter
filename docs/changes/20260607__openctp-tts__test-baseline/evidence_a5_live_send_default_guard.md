# A5 Evidence: Live Send Default Guard

**change-id**: `20260607__openctp-tts__test-baseline`
**captured-at**: 2026-06-08 Asia/Shanghai
**scenario**: A5 default live-send remains disarmed
**verdict**: passed

## Evidence

The tracked OpenCTP example config keeps live order smoke disarmed:

```text
cfgs/ctp.openctp.tts.7x24.example.json
ExecutionGuardrails.AllowLiveOrderSmoke=false
```

The `.env` config writer also forces generated local OpenCTP config to remain
disarmed even if a copied template has the field set to true.

Verification command:

```powershell
python -m pytest tests/test_openctp_env_config.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Observed result:

```text
2 passed
```
