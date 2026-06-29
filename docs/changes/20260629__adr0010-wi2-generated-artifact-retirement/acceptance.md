# Acceptance

## Guard-First Evidence

| Scenario | Command | Expected |
| --- | --- | --- |
| red | `git ls-files 'var/**' 'pytest_tmp/**' | Measure-Object | % Count` | nonzero before retirement; observed `1493` |
| binary-red | `git ls-files 'var/**' 'pytest_tmp/**' | ? { $_ -match '\.(dll|exe|pyd|so|zip|parquet|sqlite|db|png|jpg|jpeg|gif|pdf|bin)$' } | Measure-Object | % Count` | nonzero before retirement; observed `675` |
| green | `git ls-files 'var/**' 'pytest_tmp/**' | Measure-Object | % Count` | `0` after retirement |
| fresh-clone | repeat green command after clean checkout | `0` |

## Risk-Control Scenarios

- RC-2 WI-2 inventory classification: `var/**` and `pytest_tmp/**` classified as runtime generated artifacts in Batch 0 carrier.
- RC-3 WI-2 post-retirement guard: tracked generated artifacts must be zero and `.gitignore` must ignore `var/` and `pytest_tmp/`.
- RC-6 Evidence replay: commands above are the replay surface.

## Prohibited

- Do not remove files from disk as part of this change.
- Do not move SendMode fixtures or proposal files in this change.
- Do not include WI-5 implementation in this diff.
