# Plan: changes-topic-index-upgrade

**change-id**: `20260402__governance-harness__changes-topic-index-upgrade`
**创建日期**: 2026-04-02
**状态**: completed
**进度**：100%

## 目标

将 `docs/topics/README.md` 从"仅列出 2 个 topic 的静态目录"升级为可校验的 topic projection index。

2026-06-08 复核结论：本 change 的原始静态编辑目标已被 Route B successor 实现取代。`docs/topics/README.md` 当前由 `python scripts/sync_topic_index.py --root .` 生成/校验，列出 18 个 topic，并声明 topic 仅为 grouping projection；默认执行 frontier 来自 `docs/changes/*/plan.md`。

## 范围

- 修改文件：无；当前 `docs/topics/README.md` 由 successor generator 管理。

## 步骤

1. 校验 `docs/topics/README.md` 是否由 Route B generator 覆盖当前 topic projection。
2. 校验 topic docs 与 governance checks 是否通过。
3. 若 successor checks 已通过，不回退为 2026-04-02 的静态 topic list。

## topic 列表状态（按主线顺序）

| topic-id | 状态 |
| --- | --- |
| `nautilus-ctp-adapter-mainline` | 进行中（主线总 roadmap） |
| `ctp-live-connectivity` | 已完成 |
| `nautilus-instrument-provider` | 已完成 |
| `nautilus-live-marketdata` | 进行中 |
| `nautilus-live-execution` | 未开始 |
| `live-ops-and-reconciliation` | 未开始 |
| `nautilus-ctp-adapter-governance-harness` | 进行中（治理辅线） |

## 不在范围内

- 不手写改动 generator 管理的 `docs/topics/README.md`。
- 不修改各 topic README 文件的内容。
- 不修改 `docs/README.md`。

## 完成记录

1. `python scripts/sync_topic_index.py --root . --check` 返回 `TOPIC_INDEX_CHECK_OK`。
2. `python scripts/check_topic_docs.py --root .` 返回 `SUMMARY topics=18 failures=0`。
3. `python scripts/check_topic_governance.py --root .` 返回 `TOPIC_GOVERNANCE_CHECK_OK`。
4. 因 successor Route B projection 已覆盖原目标，本 change 完成收口。
