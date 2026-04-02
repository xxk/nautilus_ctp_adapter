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
