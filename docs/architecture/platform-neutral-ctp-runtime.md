# Platform-Neutral CTP Runtime

## Decision

The CTP layer in this repository must stay platform-neutral.

## Why

1. Nautilus is the first host platform, not the only possible host platform.
2. Future SmartQuant support should reuse the same CTP-native logic.
3. Host-platform types should stay out of the runtime core.

## Layer Model

### Runtime core

This layer may contain:

1. Native CTP interop
2. Connection state machine
3. Command model
4. Event model
5. Exchange-specific rules such as SHFE close-priority handling

This layer must not contain:

1. Nautilus `InstrumentProvider`, `LiveDataClient`, `LiveExecutionClient`
2. SmartQuant `Provider`, `ExecutionCommand`, or `IDataProvider`

### Adapter layers

Adapter layers translate the runtime into a host platform:

1. Nautilus adapter
2. SmartQuant adapter

## Repository-Owned Native Boundary

The shared runtime may depend on a repository-owned `ctp_native` boundary, but that boundary must stay host-neutral too.

Repository-owned means:

1. this repository owns the expected pack layout under `vendor/ctp/bin`
2. this repository owns the normalized export surface and loader rules
3. this repository is the long-term maintenance home for the C wrapper boundary itself
4. external sample projects may supply bootstrap binaries, but they do not define the long-term ABI

Current ABI direction is intentionally thin:

1. MD session lifecycle and subscription exports
2. TD session lifecycle and authenticate/login exports
3. order insert / order action exports
4. query exports for instrument, position, account, and instrument status
5. one normalized event polling export for adapter/runtime consumption

See `src/nautilus_ctp_adapter/native/manifest.py` for the current tracked export list.

## Shared Runtime API Shape

The runtime should revolve around:

1. Commands
2. Events
3. Query results
4. Runtime state

Current adapter-facing contract direction:

1. `submit_command(command)`
2. `drain_events(limit)`
3. instrument query must remain a runtime contract, not a host-specific shortcut
4. current query sequence is `QUERY_INSTRUMENTS -> INSTRUMENT* -> INSTRUMENT_END`
5. exchange/symbol normalization should remain adapter-side, not leak host-specific naming into runtime raw records

## Performance Rule

The shared runtime is also the primary performance optimization boundary.

Default rule:

1. Optimize runtime internals first
2. Keep adapter layers thin
3. Avoid host-specific fast paths unless measurement requires them

See [runtime-performance-guidelines.md](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md).

## Naming Rule

Use neutral names such as `ctp_runtime_core`, not host-specific names such as `nautilus_ctp_core`.
