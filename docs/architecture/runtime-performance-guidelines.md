# Runtime Performance Guidelines

## Goal

Define the default performance policy for the shared CTP runtime so implementation work follows one stable optimization order.

## Core Principle

Optimize the shared runtime first and keep host-platform adapter layers thin.

That means:

1. Put heavy CTP-native work in Rust
2. Minimize cross-language boundary crossings
3. Keep Nautilus and future SmartQuant layers focused on host integration, not runtime logic

## First-Version Performance Priorities

### P1. Normalize in Rust immediately

Once a CTP callback enters Rust, convert it into the runtime's normalized command/event model as early as possible.

Do not push raw callback structs into Python and parse them there.

### P2. Separate market data from trading flow

At minimum, keep these runtime paths separate:

1. Market data
2. Trading, account, and query responses

High-frequency ticks must not block order updates, trades, positions, or account events.

### P3. Batch across the Python boundary

The default bridge contract should prefer batch transfer, for example:

1. `submit_command(cmd)`
2. `drain_events(limit)`

Avoid a design where every tick or order event triggers one Python crossing.

### P4. Keep runtime state machines in Rust

The runtime owns:

1. Connection and reconnect lifecycle
2. Authentication and login
3. Settlement confirmation
4. Subscription restore
5. Order lifecycle state machine
6. Exchange-specific rules such as SHFE close-priority

### P5. Reduce repeated allocations

High-frequency fields such as venue symbol, exchange id, request id, order ref, front id, and session id should avoid repeated copying where practical.

### P6. Separate request/response from streaming events

Queries such as instruments, positions, account, and instrument status should keep request-response semantics distinct from streaming market/trading events.

## Recommended Runtime Flow

```text
CTP native callback
  -> rust runtime queue
  -> normalized runtime event
  -> python batch bridge
  -> host adapter emit
```

## Runtime Module Guidance

Recommended runtime responsibility split:

1. `native/`: DLL loading, callback registration, raw handle management
2. `session/`: connect, auth, login, settlement, reconnect
3. `market/`: subscribe, unsubscribe, tick flow
4. `trading/`: submit, cancel, replace, order state machine
5. `query/`: instruments, positions, account, instrument status
6. `normalize/`: raw callback to runtime event mapping
7. `bridge/`: runtime event draining into Python

## Default API Direction

The shared runtime should stabilize around a small adapter-facing surface:

1. `submit_command(command)`
2. `drain_events(limit)`

Internal implementation may evolve, but these boundary concepts should remain stable.

## What Not To Over-Optimize In V1

Do not treat the following as default first-version requirements:

1. Rust direct-to-Nautilus EventBus integration
2. Zero-copy-everywhere FFI complexity
3. Over-specialized lock-free designs before measurement
4. Host-specific fast paths baked into the shared runtime
5. Full SmartQuant implementation before the runtime contract stabilizes

## Performance Decision Rule

When a design choice improves raw speed but increases host coupling, default to preserving the platform-neutral runtime unless measurement proves the coupling is necessary.
