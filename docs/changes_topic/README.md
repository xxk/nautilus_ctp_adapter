# Changes Topic Index

`DSLReserach`-aligned topic governance lives here.

## Layering Rule

1. `docs/changes_topic/roadmap/` stores long-running topic roadmaps.
2. `docs/changes/` stores one executable child change at a time.
3. Topic documents track phase order, queue state, and topic-level acceptance.
4. Child change documents track execution, evidence, and acceptance closure.

## Recommended Layout

```text
docs/
├── changes/
├── changes_topic/
│   └── roadmap/
│       └── <domain>/
│           └── <topic-id>/
│               └── README.md
└── architecture/
```

## Current Topics

1. [Nautilus CTP adapter mainline roadmap](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md)
2. [CTP live connectivity roadmap](/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md)

## Migration Note

The older `docs/topics/` directory is kept temporarily as a compatibility layer.

Canonical long-running topics now belong under `docs/changes_topic/roadmap/`.
