# Platform-Neutral CTP Runtime AI Constraints

**Change ID**: 20260401__architecture__platform-neutral-ctp-runtime
**Related Acceptance**: ./acceptance.md
**Related Plan**: ./plan.md

## Startup Order

1. Read `acceptance.md`
2. Read `plan.md`
3. Keep the runtime layer free of Nautilus and SmartQuant host types

## Rules

1. Host-platform-neutral naming takes precedence in the runtime layer
2. Adapter-specific code belongs under adapter namespaces only
3. Do not introduce direct EventBus integration in the runtime layer
