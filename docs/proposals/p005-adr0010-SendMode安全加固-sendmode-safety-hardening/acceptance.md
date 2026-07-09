# P005 / Acceptance

**proposal-id**: `p005-adr0010-sendmode-safety-hardening`
**status**: implemented
**状态**：implemented
**updated**: 2026-06-29

## 场景矩阵 / Scenario Matrix

| Scenario | red command | green command | fresh-clone command | Status |
| --- | --- | --- | --- | --- |
| RC-1 Batch entry gate | n/a | `python scripts/check_architecture_governance.py --root .` | `python scripts/check_architecture_governance.py --root .` | accepted |
| RC-4 WI-5 safety matrix | `python -m pytest tests/test_send_mode_guard.py -q` failed on missing `nautilus_ctp_adapter.diagnostics.send_mode` | `python -m pytest tests/test_send_mode_guard.py -q` -> 4 passed | `python -m pytest tests/test_send_mode_guard.py -q` | accepted |
| RC-6 Evidence replay | n/a | `python -m py_compile src/nautilus_ctp_adapter/diagnostics/send_mode.py src/nautilus_ctp_adapter/diagnostics/guarded_paper_order.py scripts/ctp_guarded_paper_order_loop.py` | same | accepted |

## Evidence

- `python -m pytest tests/test_send_mode_guard.py -q` -> 4 passed.
- `python -m py_compile src/nautilus_ctp_adapter/diagnostics/send_mode.py src/nautilus_ctp_adapter/diagnostics/guarded_paper_order.py scripts/ctp_guarded_paper_order_loop.py` -> passed.
- `python scripts/check_architecture_governance.py --root .` -> `ARCH_GOV_CHECK_OK`.

## Anti-Regression Evidence

| Evidence | Result |
| --- | --- |
| Exhaustive enum resolution | `DRY_RUN`, `ARMED_PAPER`, and `ARMED_LIVE` resolve to explicit action/dry/live/paper semantics. |
| Illegal bool matrix rejection | `dry_run=True + arm_paper_send=True`, `dry_run=True + live_send_armed=True`, `arm_paper_send=False + live_send_armed=True`, and `dry_run=False + arm_paper_send=False` raise `SendModeConfigurationError`. |
| Finalizer authority | `finalize_order_lifecycle_payload` validates legacy bools against `send_mode` and raises on mismatch. |
| Static bypass guard | `tests/test_send_mode_guard.py` rejects the old direct `action_mode` bool expression and old finalizer `if not arm_paper_send` branch. |
| Existing architecture governance | `python scripts/check_architecture_governance.py --root .` -> `ARCH_GOV_CHECK_OK`. |

## Pass Criteria

1. `SendMode {DRY_RUN, ARMED_PAPER, ARMED_LIVE}` or equivalent explicit enum exists.
2. Illegal legacy bool combinations fail at construction time.
3. Any legacy 3-bool entry is deleted or becomes a thin wrapper that immediately converts to `SendMode`.
4. Tests prove the old path cannot bypass SendMode.

## Residual Risk

- Full `tests/test_guarded_paper_order_loop.py` remains environment-gated in this workspace because `nautilus_trader` is not installed. The low-cost repo guard avoids that dependency and locks the SendMode surface directly.
- Existing callers using `arm_paper_send=` remain compatible. This is intentional deprecated compatibility, not a parallel authority.
