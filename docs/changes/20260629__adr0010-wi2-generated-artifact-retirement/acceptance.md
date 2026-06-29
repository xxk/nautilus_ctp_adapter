# Acceptance

## Guard-First Evidence

| Scenario | Command | Expected |
| --- | --- | --- |
| red | `git ls-files 'var/**' 'pytest_tmp/**' | Measure-Object | % Count` | nonzero before retirement; observed `1493` |
| binary-red | `git ls-files 'var/**' 'pytest_tmp/**' | ? { $_ -match '\.(dll|exe|pyd|so|zip|parquet|sqlite|db|png|jpg|jpeg|gif|pdf|bin)$' } | Measure-Object | % Count` | nonzero before retirement; observed `675` |
| green | `git ls-files 'var/**' 'pytest_tmp/**' | Measure-Object | % Count` | `0` after retirement |
| output-debug-red | `python -m pytest tests/test_adr0010_wi2_generated_artifact_retirement.py -q` | failed before output/debug untracking: `129` tracked files |
| output-debug-green | `python -m pytest tests/test_adr0010_wi2_generated_artifact_retirement.py -q` | `2 passed`; `git ls-files 'output/debug/**' 'var/**' 'pytest_tmp/**'` returns zero |
| fresh-clone | repeat green command after clean checkout | `0` |

## Risk-Control Scenarios

- RC-2 WI-2 inventory classification: `var/**`, `pytest_tmp/**`, and residual `output/debug/**` classified as runtime generated artifacts.
- RC-3 WI-2 post-retirement guard: tracked generated artifacts must be zero and `.gitignore` must ignore `output/debug/`, `var/`, and `pytest_tmp/`.
- RC-6 Evidence replay: commands above are the replay surface.

## Prohibited

- Do not remove files from disk as part of this change.
- Do not move SendMode fixtures or proposal files in this change.
- Do not include WI-5 implementation in this diff.
