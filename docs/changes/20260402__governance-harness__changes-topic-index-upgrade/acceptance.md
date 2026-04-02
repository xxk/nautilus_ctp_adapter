# Acceptance: changes-topic-index-upgrade

**change-id**: `20260402__governance-harness__changes-topic-index-upgrade`
**创建日期**: 2026-04-02
**状态**: pending

## 继承事实

1. `docs/changes_topic/README.md` 当前只列出 2 个 topic：mainline 和 `ctp-live-connectivity`。
2. `nautilus-instrument-provider`（已完成）、`nautilus-live-marketdata`（进行中）均已存在 README，但未出现在索引里。
3. 本 governance topic（`nautilus-ctp-adapter-governance-harness`）也需要加入索引。

## 验收场景

### SC-1：Current State 节存在且准确

`docs/changes_topic/README.md` 顶部（Layering Rule 之前）有 `## Current State` 节，节内容显示：
- Active topic = `nautilus-live-marketdata`
- Active change = `20260402__nautilus-live-marketdata__live-data-client-bootstrap`

### SC-2：所有 topic 已列出

列表包含以下 6+1 条目（均有链接）：
- `nautilus-ctp-adapter-mainline`（进行中）
- `ctp-live-connectivity`（已完成）
- `nautilus-instrument-provider`（已完成）
- `nautilus-live-marketdata`（进行中）
- `nautilus-live-execution`（未开始）
- `live-ops-and-reconciliation`（未开始）
- `nautilus-ctp-adapter-governance-harness`（进行中）

### SC-3：原有节未丢失

Layering Rule 节、Recommended Layout 节、Migration Note 节均存在，内容未被删改。

### SC-4：所有链接指向真实路径

文件内所有 topic 链接对应的 README.md 文件实际存在于磁盘（除未开始的 topic 外，其 README 若不存在则注明"待创建"）。

## 最终结论

**conclusion**: pending
