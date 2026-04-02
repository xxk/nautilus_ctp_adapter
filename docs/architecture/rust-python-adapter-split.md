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

## Migration Policy

Unified repository guidance:

1. Long-term target: choose `rust-ctp`.
2. Implementation path: use a staged `rust-py-ctp` transition first, then cut over to `rust-ctp ownership`.

Interpretation rules:

1. `rust-py-ctp` means the repository may temporarily keep part of the native wrapper or bridge ownership on the Python side while Rust takes over the runtime mainline incrementally.
2. `rust-ctp` does not mean removing Python from the adapter stack; it means Python remains the host integration layer while Rust owns the formal CTP runtime and native path.
3. New work should avoid expanding Python-side native ownership unless the expansion is explicitly transitional and serves the final Rust-owned cutover.

Current runtime-facing adapter boundary:

1. `submit_command(command)`
2. `drain_events(limit)`
3. `InstrumentProvider`-side query bootstrap should submit `QUERY_INSTRUMENTS`
4. query completion should be expressed by `INSTRUMENT_END`, not implicit callback exhaustion
5. exchange aliasing, symbol case rules, and product kind normalization currently live in the Python adapter layer

Current market-data bootstrap direction:

1. Python `CtpDataClient` builds the normalized MD bootstrap commands
2. The shared runtime bridge owns the submitted command queue
3. Future Rust/native work consumes the same queue instead of inventing a second login path
4. `rb2610`-style live subscription should enter the system through this mainline bootstrap, not through a temporary host
5. The current repository-owned Python smoke also proves `ctp_native.dll` can deliver `login_succeeded` and `tick` into the runtime bridge without a temporary C# host
6. When a live instrument query returns related instruments, `LiveDataClient` bootstrap must prefer exact matches from `config.instruments` instead of subscribing the entire returned set
7. The stable Python-side output model for this step is `CtpLiveDataBootstrapResult`, which keeps provider result metadata and the submitted MD bootstrap state together
8. Marketdata batching must be adapter-local first: `CtpDataClient.drain_marketdata_event_batch(limit)` is the stable entrypoint for later Nautilus consumption
9. Subscription restore must reuse the same bootstrap path and source its symbol set from `active_subscription_symbols`

Current execution bootstrap direction:

1. Python `CtpExecutionClient` must expose a formal TD bootstrap path instead of only a readiness smoke helper
2. The shared runtime bridge remains the place where execution bootstrap submits its `CONNECT` command
3. TD auth/login/settlement can still be proven through the repo-owned local c wrapper while command mapping remains a later change
4. Execution bootstrap must coexist with Topic 4 guardrails and must not imply real order-send readiness

Current execution command-mapping direction:

1. submit / cancel mapping must freeze in Python before real `TdOrderSend/TdOrderAction` are wired
2. `order_ref`, `front_id`, and `session_id` must travel together as stable execution identity fields
3. guardrails rejects should surface as stable `error_id / error_message` pairs instead of ad hoc strings
4. mapping may submit runtime commands, but must not imply true order-send readiness until later Topic 4 changes land

Current live-execution bootstrap direction:

1. `LiveExecutionClient` readiness must build on top of TD bootstrap plus a captured `td_session_identity`
2. bootstrap-ready execution paths may submit mapped commands into the shared runtime bridge before true native order send is enabled
3. real order lifecycle verification remains a later, explicitly separate change

## Mainline Restriction

This repository must not use a C# managed bridge as the continuing implementation path.

Allowed:

1. repository-owned local C wrapper
2. Rust core on top of that wrapper
3. Python glue for Nautilus integration

Not allowed as the mainline:

1. extending the temporary C# smoke host
2. re-centering adapter work around `CTPProviderSwig.dll`
3. treating managed wrappers as the long-term production boundary

See [runtime-performance-guidelines.md](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md).

## Non-Goal

This repository will not make Rust direct-to-EventBus integration the primary path.
