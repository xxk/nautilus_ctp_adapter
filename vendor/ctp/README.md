# CTP Bootstrap Pack

This directory is the repository-owned landing area for the local CTP bootstrap pack used by `nautilus_ctp_adapter`.

## Ownership Boundary

The repository owns these things:

1. `vendor/ctp/` layout and expected `bin/` landing path
2. loader/search rules in `src/nautilus_ctp_adapter/native/loader.py`
3. pack manifest and ABI metadata in `src/nautilus_ctp_adapter/native/manifest.py`
4. sync tooling in `scripts/sync_ctp_native.py`
5. the normalized export contract that future `ctp_native.dll` implementations must satisfy
6. the long-term maintenance responsibility for the repository-owned C wrapper boundary

The repository does not treat external sample projects as the long-term source of truth for ABI or runtime behavior.

External projects are allowed only as:

1. binary bootstrap sources
2. reference implementations for current wrapper behavior
3. temporary validation inputs while the repository-owned native boundary is still being stood up

Managed .NET assemblies in the pack may remain as bootstrap artifacts, but they are not the ongoing mainline boundary for this repository.

## Expected Runtime Contents

Expected runtime contents under `vendor/ctp/bin/`:

1. `ctp_native.dll`
2. `thostmduserapi_se.dll`
3. `thosttraderapi_se.dll`
4. `CTPProviderSwig.dll`
5. `CTPProviderSwig.Core.dll`
6. `iTrading.Core.dll`
7. `iTradingQuant.dll`

Optional compatibility payloads:

1. `thostmduserapi.dll`
2. `thosttraderapi.dll`

## Repository-Owned ABI Direction

Future repository-owned `ctp_native.dll` work must converge toward a thin C ABI that centers on:

1. MD create / release / login / subscribe / unsubscribe
2. TD create / release / authenticate / login / settlement confirm
3. order insert / order action
4. instrument / position / account / instrument status query
5. event polling through a normalized event drain surface

The stable symbol list currently tracked by the repository lives in `src/nautilus_ctp_adapter/native/manifest.py`.

## Sync Rule

Use `python scripts/sync_ctp_native.py` to refresh the local pack from an external sample project.

The script now supports named source profiles:

1. `spec-kit`
2. `spec-kit-provider`
3. `lean-plugin`

Each sync writes `vendor/ctp/bin/_synced_from.txt` so later work can see which sample roots were used.

Tracked files here define layout and tooling only. Binary payloads stay ignored by `.gitignore`.
