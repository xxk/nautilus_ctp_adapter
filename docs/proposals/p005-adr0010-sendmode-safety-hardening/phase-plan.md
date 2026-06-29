# P005 / Phase Plan

## Phase Status

| Phase | Goal | Status | Exit evidence |
| --- | --- | --- | --- |
| 0 | Guard-first safety matrix tests | not_started | red evidence recorded |
| 1 | Introduce SendMode enum | not_started | enum exhaustive tests green |
| 2 | Retire/wrap legacy 3-bool entry | not_started | bypass guard green |
| 3 | Fresh-clone and repo gate | not_started | acceptance evidence recorded |

## Stop Conditions

- Any implementation starts before RC-4 red evidence exists.
- Old bool API remains a parallel live-send path.
- Safety-critical mode selection uses fallback/default behavior.
