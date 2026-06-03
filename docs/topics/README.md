# Topic Index

> 本文件由 `python scripts/sync_topic_index.py --root .` 基于 roadmap 元数据与 topic 状态注册表生成。
> 机器状态以 `docs/topics/主题状态注册表_Topic State Registry.yaml` 为准，`README.md` 只做人类可读投影视图。

**最后同步**：2026-05-30

## Current State / 当前状态

- **当前 active topic**：`无`
- **当前 active change**：`无`
- **排队 topics**：`无`
- **排队 changes**：`无`
- **冻结/阻塞 topics**：[live-ops-truth-snapshot](live-ops-truth-snapshot.md)（blocked）、[live-session-order-query-hardening](live-session-order-query-hardening.md)（blocked）
- **已完成 topics 数量**：`16/18`
- **最近完成 topics**：[autopilot-session-management](autopilot-session-management.md)（last_updated=2026-05-30（C1 完成；C2 最小版折叠进 C1 验收；L3 延后））、[nautilus-host-integration](nautilus-host-integration.md)（last_updated=2026-04-13）、[rust-ctp-runtime-cutover](rust-ctp-runtime-cutover.md)（last_updated=2026-04-10）、[repo-governance-hardening](repo-governance-hardening.md)（last_updated=2026-04-10）、[nautilus-ctp-adapter-mainline](nautilus-ctp-adapter-mainline.md)（last_updated=2026-04-10）
- **状态注册表**：`docs/topics/主题状态注册表_Topic State Registry.yaml`

## Layering Rule / 分层规则

1. `docs/topics/<topic-id>.md` 负责长期 topic 路线图。
2. `docs/changes/` 负责单次可执行 child change。
3. topic 文档维护 topic 级目标、顺序、队列状态与长期冻结结论。
4. `docs/topics/主题状态注册表_Topic State Registry.yaml` 是 machine-readable 的状态主来源。
5. child change 三件套负责执行、证据、正式验收与 AI 状态回填。

## Current Topics / 当前 Topics

### `governance`

| topic-id | canonical-status | execution-order | 显示状态 | 标题 | README |
| --- | --- | --- | --- | --- | --- |
| `autopilot-session-management` | `completed` | `—` | completed | Autopilot Session Management 长期路线 / Autopilot Session Management Topic Roadmap | [README](autopilot-session-management.md) |

### `nautilus_adapter`

| topic-id | canonical-status | execution-order | 显示状态 | 标题 | README |
| --- | --- | --- | --- | --- | --- |
| `live-ops-truth-snapshot` | `blocked` | `—` | 阻塞 | Live Ops Truth Snapshot Topic Roadmap | [README](live-ops-truth-snapshot.md) |
| `live-session-order-query-hardening` | `blocked` | `—` | 阻塞 | Live Session Order Query Hardening Topic Roadmap | [README](live-session-order-query-hardening.md) |
| `ctp-live-connectivity` | `completed` | `—` | 已完成 | CTP Live Connectivity Topic Roadmap | [README](ctp-live-connectivity.md) |
| `full-reconciliation-automation` | `completed` | `—` | 已完成 | Full Reconciliation Automation Topic Roadmap | [README](full-reconciliation-automation.md) |
| `live-ops-and-reconciliation` | `completed` | `—` | 已完成 | Live Ops And Reconciliation Topic Roadmap | [README](live-ops-and-reconciliation.md) |
| `md-startup-truth-and-restore` | `completed` | `—` | 已完成 | MD Startup Truth And Restore Topic Roadmap | [README](md-startup-truth-and-restore.md) |
| `nautilus-ctp-adapter-mainline` | `completed` | `—` | 已完成 | Nautilus CTP Adapter Mainline Topic Roadmap | [README](nautilus-ctp-adapter-mainline.md) |
| `nautilus-host-integration` | `completed` | `—` | completed | Nautilus Host Integration Topic Roadmap | [README](nautilus-host-integration.md) |
| `nautilus-instrument-provider` | `completed` | `—` | 已完成 | Nautilus Instrument Provider Topic Roadmap | [README](nautilus-instrument-provider.md) |
| `nautilus-live-execution` | `completed` | `—` | 已完成 | Nautilus Live Execution Topic Roadmap | [README](nautilus-live-execution.md) |
| `nautilus-live-marketdata` | `completed` | `—` | 已完成 | Nautilus Live Marketdata Topic Roadmap | [README](nautilus-live-marketdata.md) |
| `position-account-query-baseline` | `completed` | `—` | 已完成 | Position Account Query Baseline Topic Roadmap | [README](position-account-query-baseline.md) |
| `startup-truth-and-session-rebuild` | `completed` | `—` | 已完成 | Startup Truth And Session Rebuild Topic Roadmap | [README](startup-truth-and-session-rebuild.md) |
| `td-order-truth-and-reconciliation` | `completed` | `—` | 已完成 | TD Order Truth And Reconciliation Topic Roadmap | [README](td-order-truth-and-reconciliation.md) |
| `td-position-account-truth-merge` | `completed` | `—` | 已完成 | TD Position Account Truth Merge Topic Roadmap | [README](td-position-account-truth-merge.md) |

### `repo_governance`

| topic-id | canonical-status | execution-order | 显示状态 | 标题 | README |
| --- | --- | --- | --- | --- | --- |
| `repo-governance-hardening` | `completed` | `—` | 已完成 | Nautilus CTP Adapter Governance Harness Topic Roadmap | [README](repo-governance-hardening.md) |

### `rust_ctp`

| topic-id | canonical-status | execution-order | 显示状态 | 标题 | README |
| --- | --- | --- | --- | --- | --- |
| `rust-ctp-runtime-cutover` | `completed` | `—` | 已完成 | Rust 接管 CTP Runtime 切换 / Rust-Owned CTP Runtime Cutover | [README](rust-ctp-runtime-cutover.md) |

## Governance Note / 治理说明

This README is the canonical human-readable topic index for the repository.

Canonical machine-readable topic state belongs in the topic state registry.

Canonical long-running topics belong under `docs/topics/<topic-id>.md`.
