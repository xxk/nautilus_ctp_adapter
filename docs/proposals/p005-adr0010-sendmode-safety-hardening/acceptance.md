# P005 / Acceptance

## Required Scenarios

| Scenario | red command | green command | fresh-clone command | Status |
| --- | --- | --- | --- | --- |
| RC-1 Batch entry gate | pending | pending | pending | slot-created |
| RC-4 WI-5 safety matrix | pending: enum exhaustive + illegal bool combination test | pending | pending | slot-created |
| RC-6 Evidence replay | pending | pending | pending | slot-created |

## Pass Criteria

1. `SendMode {DRY_RUN, ARMED_PAPER, ARMED_LIVE}` or equivalent explicit enum exists.
2. Illegal legacy bool combinations fail at construction time.
3. Any legacy 3-bool entry is deleted or becomes a thin wrapper that immediately converts to `SendMode`.
4. Tests prove the old path cannot bypass SendMode.
