# CTP Bootstrap Pack

**Updated**: 2026-04-10

This directory is the repository-owned landing area for the local CTP bootstrap pack used by `nautilus_ctp_adapter`.

## Ownership Boundary

The repository owns these things:

1. `vendor/ctp/` layout and expected `bin/` plus `sdk/` landing paths
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

Current PyO3 mainline runtime contents under `vendor/ctp/bin/`:

1. `thostmduserapi_se.dll`
2. `thosttraderapi_se.dll`

Repo-owned compatibility payloads:

1. `ctp_native.dll`
2. `thostmduserapi.dll`
3. `thosttraderapi.dll`

Important:

1. a repo-built `ctp_native.dll` under `rust/target/` is scaffold-only unless the crate was built with a detected CTP SDK and `ctp_vendor_bridge`
2. syncing that scaffold artifact is useful for ABI/test-helper compatibility, but it is not enough for real live smoke by itself
3. real live smoke still needs either an external live `ctp_native.dll` source or a local SDK-backed build that enables the vendor bridge

Legacy managed bootstrap payloads are optional and only needed when reproducing historical sample-project packs:

1. `CTPProviderSwig.dll`
2. `CTPProviderSwig.Core.dll`
3. `iTrading.Core.dll`
4. `iTradingQuant.dll`

## Expected SDK Contents

Expected live-ready SDK contents under `vendor/ctp/sdk/` or a path referenced by `CTP_VENDOR_SDK_ROOT` / `CTP_SDK_ROOT`:

1. `ThostFtdcMdApi.h`
2. `ThostFtdcTraderApi.h`
3. `ThostFtdcUserApiStruct.h`
4. `thostmduserapi_se.lib`
5. `thosttraderapi_se.lib`

The Rust build only enables `ctp_vendor_bridge` when all five files resolve under one discovered SDK directory.

## Repository-Owned ABI Direction

Future repository-owned `ctp_native.dll` work must converge toward a thin C ABI that centers on:

1. MD create / release / login / subscribe / unsubscribe
2. TD create / release / authenticate / login / settlement confirm
3. order insert / order action
4. instrument / position / account / instrument status query
5. event polling through a normalized event drain surface

The stable symbol list currently tracked by the repository lives in `src/nautilus_ctp_adapter/native/manifest.py`.

## Sync Rule

Use `python scripts/sync_ctp_native.py` to refresh the local pack from either split local sources or an external sample project.

The script now supports pack kinds:

1. `runtime`: current PyO3 mainline runtime (`thost*api*_se.dll`)
2. `compat`: runtime pack plus `ctp_native.dll` compatibility payload
3. `full`: compat pack plus legacy managed bootstrap DLLs

It also supports split-source discovery:

1. `--repo-native-source <dir>` for `ctp_native.dll`
2. `--ctp-api-source <dir>` for `thost*api*_se.dll`
3. `--managed-source <dir>` for legacy managed DLLs
4. `--scan-root <dir>` to recursively discover matching source directories

If `--repo-native-source` points at a repo build under `rust/target/`, the sync manifest now records `repo_native_mode=repo_build_requires_sdk_for_live` and prints a warning so the pack is not mistaken for a real live-ready bridge.

Named source profiles remain available for older sample-project layouts:

1. `auto`
2. `spec-kit`
3. `spec-kit-provider`
4. `lean-plugin`

Each sync writes `vendor/ctp/bin/_synced_from.txt` so later work can see which sample roots were used.

## Cross-Machine Rule

Use this directory layout on another machine:

```text
vendor/ctp/
├── README.md
├── bin/
│   ├── ctp_native.dll
│   ├── thostmduserapi_se.dll
│   ├── thosttraderapi_se.dll
│   └── _synced_from.txt
└── sdk/
	├── ThostFtdcMdApi.h
	├── ThostFtdcTraderApi.h
	├── ThostFtdcUserApiStruct.h
	├── thostmduserapi_se.lib
	└── thosttraderapi_se.lib
```

Build/runtime behavior then becomes:

1. `build.rs` prefers `CTP_VENDOR_SDK_ROOT`, then `CTP_SDK_ROOT`, then `vendor/ctp/sdk/`, then `_synced_from.txt` reverse lookup.
2. `python scripts/check_rust_gate.py` prepends `vendor/ctp/bin/` to `PATH` so cargo-side test processes can load the vendor runtime DLLs.
3. When the SDK is not in a canonical location, `CTP_SDK_SCAN_ROOTS` can provide a semicolon-separated list of broader roots to recursively scan.
4. Broad-root SDK scans intentionally skip system temp subtrees, so temporary pytest placeholder payloads cannot be mistaken for a live-ready SDK.
5. If the SDK is missing, the repo still builds a scaffold-only `ctp_native.dll`; if the SDK is present, the same repo can build the live-ready vendor bridge.

Tracked files here define layout and tooling only. Runtime DLLs and SDK payloads stay local and ignored by `.gitignore`.
