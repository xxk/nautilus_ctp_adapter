# A6 Docs Boundary Evidence

Date: 2026-06-07

Commands:

```powershell
python scripts/check_change_docs.py --root .
python scripts/check_topic_governance.py --root .
python scripts/show_current_frontier.py --root .
```

Results:

```text
CHANGE_DOCS_CHECK_OK: changes=74
TOPIC_GOVERNANCE_CHECK_OK: index=docs/topics/README.md topics=18 active_topic=... active_change=20260607__openctp-tts__test-baseline
CURRENT_FRONTIER_OK: active_change=20260607__openctp-tts__test-baseline queued_changes=7 parked_changes=3 completed_changes=63 source=docs/changes/*/plan.md
ACTIVE_CHANGE: change=20260607__openctp-tts__test-baseline status=in_progress topic_label=live-session-order-query-hardening order=1 plan=docs/changes/20260607__openctp-tts__test-baseline/plan.md
```

Boundary confirmed:

1. OpenCTP TTS 7x24 is now the active frontier.
2. OpenCTP `TEST` is documented as the全天候 simulation debug instrument.
3. Real-account `c2609` remains a separate final-evidence path and is not replaced by OpenCTP simulation evidence.
