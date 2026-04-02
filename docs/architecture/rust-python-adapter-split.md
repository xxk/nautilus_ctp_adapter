# Rust / Python Adapter Split

## Decision

`nautilus_ctp_adapter` will use:

1. Rust core for CTP-native interop and event processing
2. Python glue for Nautilus integration points

## Why

1. This matches Nautilus' standard adapter layering.
2. It keeps upstream Nautilus changes to a minimum.
3. It keeps performance-sensitive code out of Python while preserving the official integration boundary.

## Layer Responsibilities

### Rust core

Owns:

1. Native DLL loading strategy
2. Callback registration and callback-to-event translation
3. Request/response structs and normalized CTP event payloads
4. Connection state, login flow, order state machine, and exchange-specific rules

### Python glue

Owns:

1. User-facing config
2. `InstrumentProvider`
3. `LiveDataClient`
4. `LiveExecutionClient`
5. Factory wiring for downstream repositories

## Event Path

```text
CTP native -> Rust core -> PyO3 binding -> Python adapter -> Nautilus
```

## Performance Stance

This split is not intended to put high-frequency logic in Python.

Default rule:

1. Normalize and buffer in Rust
2. Cross the Python boundary in batches
3. Use Python mainly for host integration

Current runtime-facing adapter boundary:

1. `submit_command(command)`
2. `drain_events(limit)`

Current market-data bootstrap direction:

1. Python `CtpDataClient` builds the normalized MD bootstrap commands
2. The shared runtime bridge owns the submitted command queue
3. Future Rust/native work consumes the same queue instead of inventing a second login path
4. `rb2610`-style live subscription should enter the system through this mainline bootstrap, not through a temporary host
5. The current repository-owned Python smoke also proves `ctp_native.dll` can deliver `login_succeeded` and `tick` into the runtime bridge without a temporary C# host

See [runtime-performance-guidelines.md](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md).

## Non-Goal

This repository will not make Rust direct-to-EventBus integration the primary path.
