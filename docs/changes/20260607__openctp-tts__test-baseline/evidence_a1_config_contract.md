# A1/A4/A5 Config Contract Evidence

Date: 2026-06-08

Command:

```powershell
python -m pytest tests/test_smoke_import.py -k "ctp_config_loads_repo_example or ctp_config_allows_empty_broker_id_only_when_explicit or ctp_config_loads_openctp_tts_7x24_example or ctp_config_accepts_myvnpy_connect_ctp_shape" -q --basetemp output/pytest-tmp -p no:cacheprovider
```

Result:

```text
....                                                                     [100%]
4 passed, 207 deselected in 0.77s
```

Covered contract:

1. `cfgs/ctp.openctp.tts.7x24.example.json` loads through `CtpAdapterConfig`.
2. OpenCTP TTS 7x24 tracked template uses current official `BrokerID=9999`.
3. Ordinary CTP config still reports `broker_id` when empty broker is not explicitly allowed.
4. The explicit empty-broker compatibility test remains covered for non-default compatibility paths.
5. Tracked OpenCTP template keeps `ExecutionGuardrails.AllowLiveOrderSmoke=false`.
