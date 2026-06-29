# P005 / Phase Plan

**proposal-id**: `p005-adr0010-sendmode-safety-hardening`
**status**: implemented
**状态**：implemented
**updated**: 2026-06-29

## Artifact Trust Boundary

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - docs/proposals/p005-adr0010-sendmode-safety-hardening/
  allowed_evidence_roots:
    - output/debug/change_evidence/p005-adr0010-sendmode-safety-hardening/
    - output/reports/p005-adr0010-sendmode-safety-hardening/
  source_issue_lists: []
  source_input_templates: []
  source_contract_templates: []
  ctp_account_profile: repo-only
  ctp_config_path: not_applicable
  ctp_evidence_class: repo-only
```

## AI 跟踪状态（AI Tracking Status）

<!-- AI-PHASE-STATUS-BEGIN
overall_status: implemented
AI-PHASE-STATUS-END -->

## Phase 状态表（Phase Status Board）

| Phase | Goal | Status | Exit evidence |
| --- | --- | --- | --- |
| 0 | Guard-first safety matrix tests | completed | `python -m pytest tests/test_send_mode_guard.py -q` first failed on missing `diagnostics.send_mode` |
| 1 | Introduce SendMode enum | completed | `SendMode` and `resolve_send_mode` added in `src/nautilus_ctp_adapter/diagnostics/send_mode.py` |
| 2 | Retire/wrap legacy 3-bool entry | completed | guarded order runner/finalizer use `send_mode_resolution`; legacy bool flags are compatibility wrappers |
| 3 | Fresh-clone and repo gate | completed | `tests/test_send_mode_guard.py`, py_compile, source scan, and `scripts/check_architecture_governance.py` green |

## Retirement Checklist

| Item | Handling | Guard / evidence |
| --- | --- | --- |
| Old implicit `action_mode` expression from `arm_paper_send` | supersede | static assertion rejects `"paper_send" if arm_paper_send else "dry_run"` |
| Old finalizer bool authority | rename/supersede | finalizer resolves and validates `SendMode`; illegal explicit mismatch raises `SendModeConfigurationError` |
| Old CLI-only `--arm-paper-send` language | deprecated compat | `--send-mode` added; old flag defaults to omitted and converts only when present |
| Old illegal bool matrix fixtures | test guard | exhaustive mode and illegal-combination tests in `tests/test_send_mode_guard.py` |
| Unsupported live-send in paper loop | test/constructor guard | `ARMED_LIVE` exists in enum but runner rejects it for this paper-only entry |

## Stop Conditions

- Any implementation starts before RC-4 red evidence exists.
- Old bool API remains a parallel live-send path.
- Safety-critical mode selection uses fallback/default behavior.
