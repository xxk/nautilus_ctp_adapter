# nautilus_ctp_adapter

Standalone CTP adapter workspace for Nautilus-based trading projects.

## Goals

- Keep Nautilus upstream code untouched or minimally touched.
- Isolate CTP connectivity, symbol mapping, execution, and native loading.
- Allow downstream projects such as `D:\Nautilus\nautilus_demo` to integrate via editable install.
- Keep performance-sensitive CTP logic in Rust, while keeping Nautilus node integration in Python.
- Keep the current delivery scope tightly focused on Nautilus adapter integration.

## Architecture Direction

This repository currently follows a Nautilus-first runtime plus adapter glue split:

1. Shared CTP runtime core: native interop, callback handling, parsing, state machines
2. Nautilus adapter glue: config, market data, execution, factory, smoke validation

Event flow target:

```text
CTP native DLL
  -> repository-maintained ctp_native boundary
  -> Rust/Python runtime
  -> PyO3 boundary
  -> Nautilus-specific Python layer
  -> Nautilus host platform
```

Performance policy:

1. Optimize the shared runtime first
2. Keep host adapters thin
3. Batch across the Python boundary by default

See [docs/architecture/runtime-performance-guidelines.md](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md).

## Planned Layout

```text
nautilus_ctp_adapter/
├── rust/
│   ├── Cargo.toml
│   └── ctp_runtime_core/
│       ├── Cargo.toml
│       └── src/
│           ├── commands.rs
│           ├── lib.rs
│           ├── config.rs
│           ├── events.rs
│           ├── native.rs
│           └── python.rs
├── src/
│   └── nautilus_ctp_adapter/
│       ├── runtime/
│       │   ├── __init__.py
│       │   ├── bridge.py
│       │   └── models.py
│       ├── adapters/
│       │   └── ctp/
│       │       ├── __init__.py
│       │       ├── config.py
│       │       ├── instrument_provider.py
│       │       ├── data_client.py
│       │       ├── execution_client.py
│       │       └── factory.py
│       ├── native/
│       │   ├── __init__.py
│       │   └── loader.py
│       ├── config/
│       │   └── __init__.py
│       └── __init__.py
├── tests/
├── scripts/
└── docs/
```

## Integration Direction

Recommended downstream usage:

```powershell
pip install -e D:\Nautilus\nautilus_ctp_adapter
```

Then in `D:\Nautilus\nautilus_demo`, only keep:

- runtime configs
- strategy scripts
- smoke/integration entrypoints

C# smoke tooling may exist temporarily for live-path verification, but it is not the target adapter implementation path.

## Development Stages

1. Scaffold platform-neutral runtime + adapter glue boundaries
2. Add repository-maintained `ctpnative` loading and runtime diagnostics
3. Add runtime commands, events, and config normalization
4. Add instrument query and symbol mapping
5. Add Python `InstrumentProvider`
6. Add Python `LiveDataClient`
7. Add Python `LiveExecutionClient`
8. Replace temporary smoke tooling with Nautilus-facing live smoke flows
9. Add playback/mock/live smoke tests

## Current Formal Smoke

The current formal Nautilus-facing live smoke baseline is:

```powershell
python scripts/ctp_nautilus_live_smoke.py --config <path>
```

It is expected to prove three things in one run:

1. `MD` login and first subscribed tick
2. `TD` auth/login plus settlement confirmation readiness
3. Shared runtime bridge event flow inside the Nautilus-facing adapter stack

## Repo-Only Local Build And Debug

For a fresh machine with only this repository checkout, use this bootstrap path first:

```powershell
python -m pip install -e .
python scripts/check_rust_gate.py
python scripts/ctp_repo_debug_smoke.py
```

This path does not require `cfgs/local/` or `vendor/ctp/bin/`.
It proves three things:

1. editable install can compile the Rust/PyO3 bridge from the current repository
2. `ctp_runtime` can be imported without an external sample project or synced runtime pack
3. the public scaffold contract and internal MD live-session symbol are both present for step-through debugging

Use `python scripts/ctp_nautilus_live_smoke.py --config <path>` only when a local live config and vendor runtime pack are available.

If you also want to run the repository test suite on a fresh machine, install the dev extra first:

```powershell
python -m pip install -e ".[dev]"
python scripts/check_rust_gate.py
python scripts/ctp_repo_debug_smoke.py
python -m pytest
```

## Cross-Machine Live-Ready Setup

To make another machine build the live-ready `ctp_native.dll` instead of the scaffold-only bridge, the repository expects two separate local payloads:

1. A local runtime pack under `vendor/ctp/bin/`, containing the runtime DLLs used at load and test time.
2. A full CTP SDK directory, provided either through `vendor/ctp/sdk/` or through `CTP_VENDOR_SDK_ROOT` / `CTP_SDK_ROOT`.

The minimum SDK payload for the vendor bridge is:

1. `ThostFtdcMdApi.h`
2. `ThostFtdcTraderApi.h`
3. `ThostFtdcUserApiStruct.h`
4. `thostmduserapi_se.lib`
5. `thosttraderapi_se.lib`

`rust/ctp_runtime_core/build.rs` resolves the SDK in this order:

1. `CTP_VENDOR_SDK_ROOT`
2. `CTP_SDK_ROOT`
3. `vendor/ctp/sdk/`
4. `vendor/ctp/bin/_synced_from.txt` reverse lookup into an external `3rdLib/CTP` tree

`python scripts/check_rust_gate.py` now prepends `vendor/ctp/bin/` to `PATH` before running cargo commands, so `cargo test` can resolve `thostmduserapi_se.dll` and `thosttraderapi_se.dll` without manual shell setup.

Git tracks the code, tests, and runbooks for this flow. The proprietary runtime pack and SDK payload stay local-only and are ignored by `.gitignore`, so each machine must sync or copy them from a private source before running live-ready validation.

## Validation Gates

For a fresh machine, run the full repository validation commands in this order:

```powershell
python -m pip install -e ".[dev]"
python scripts/check_rust_gate.py
python scripts/ctp_repo_debug_smoke.py
python -m pytest
```

`python scripts/check_rust_gate.py` is the canonical Rust validation entrypoint.
It distinguishes between:

1. toolchain missing on the machine
2. Rust workspace metadata/check failures inside this repository
