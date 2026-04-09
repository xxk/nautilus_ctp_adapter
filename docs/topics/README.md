# Topic Index

`DSLReserach`-aligned topic governance lives here.

## Current State

- **Active topic**: [live-ops-truth-snapshot](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-truth-snapshot/README.md)（进行中，post-mainline）
- **Active change**: [20260403__live-ops-truth-snapshot__live-ops-policy-baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260403__live-ops-truth-snapshot__live-ops-policy-baseline/plan.md)
- **Governance topic**: [repo-governance-hardening](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/repo_governance/repo-governance-hardening/README.md)（治理辅线，已完成）

## Layering Rule

1. `docs/topics/roadmap/` stores long-running topic roadmaps.
2. `docs/changes/` stores one executable child change at a time.
3. Topic documents track phase order, queue state, and topic-level acceptance.
4. Child change documents track execution, evidence, and acceptance closure.

## Recommended Layout

```text
docs/
├── changes/
├── topics/
│   └── roadmap/
│       └── <domain>/
│           └── <topic-id>/
│               └── README.md
└── architecture/
```

## Current Topics

| # | topic-id | 状态 | 说明 |
| --- | --- | --- | --- |
| — | [nautilus-ctp-adapter-mainline](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md) | 已完成 | 总 roadmap，初版 5 个 topic 已收口 |
| 1 | [ctp-live-connectivity](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/ctp-live-connectivity/README.md) | 已完成 | 真实账户连通、MD/TD 基础登录、smoke 基线 |
| 2 | [nautilus-instrument-provider](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-instrument-provider/README.md) | 已完成 | 合约查询、符号映射、InstrumentProvider |
| 3 | [nautilus-live-marketdata](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md) | 已完成 | LiveDataClient、订阅恢复、行情事件出桥 |
| 4 | [nautilus-live-execution](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-live-execution/README.md) | 已完成 | TD auth、下单撤单、订单状态机 |
| 5 | [live-ops-and-reconciliation](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-and-reconciliation/README.md) | 已完成 | 启动对账、失败诊断、运维脚本 |
| — | [repo-governance-hardening](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/repo_governance/repo-governance-hardening/README.md) | 已完成 | 治理辅线：AGENTS.md 保鲜、索引升级、门禁脚本 |
| — | [position-account-query-baseline](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/position-account-query-baseline/README.md) | 已完成 | 使用 `025292` 的只读查询补齐 position/account 正式功能基线 |
| — | [full-reconciliation-automation](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/full-reconciliation-automation/README.md) | 已完成 | 把 query baseline 推进成 reconciliation snapshot、summary 和自动 evidence 主线 |
| — | [startup-truth-and-session-rebuild](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/startup-truth-and-session-rebuild/README.md) | 已完成 | 收口 startup truth、flow 目录和 session rebuild 的正式口径 |
| — | [md-startup-truth-and-restore](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/md-startup-truth-and-restore/README.md) | 已完成 | 收口 MD startup truth、restore 判定和 evidence matrix |
| — | [td-order-truth-and-reconciliation](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/td-order-truth-and-reconciliation/README.md) | 已完成 | 收口真实 order/trade truth、历史回报边界和只读 reconciliation evidence |
| — | [td-position-account-truth-merge](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/td-position-account-truth-merge/README.md) | 已完成 | 合并 order/trade/position/account 真相，推进更完整只读 reconciliation |
| — | [live-ops-truth-snapshot](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-ops-truth-snapshot/README.md) | 进行中 | 把 startup/md/td/reconciliation 真相收成统一只读 live ops snapshot |

## Candidate Next Topics

| topic-id | 状态 | 说明 |
| --- | --- | --- |
| [live-session-order-query-hardening](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/live-session-order-query-hardening/README.md) | 规划中 | 利用可直连 CTP 的时间窗口，把交易时段 `c2609` 一手下单开发与非交易时段 query 开发整理成正式 topic |
| [rust-ctp-runtime-cutover](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/rust_ctp/rust-ctp-runtime-cutover/README.md) | 规划中 | 二期候选 topic：把当前 Python native wrapper 主路径迁到 Rust-owned runtime + PyO3 bridge，不改变当前 active delivery |

## Governance Note

This README is the canonical topic index for the repository.

Canonical long-running topics belong under `docs/topics/roadmap/`.
