# Plan: changes-topic-index-upgrade

**change-id**: `20260402__governance-harness__changes-topic-index-upgrade`
**创建日期**: 2026-04-02
**状态**: not_started

## 目标

将 `docs/topics/README.md` 从"仅列出 2 个 topic 的静态目录"升级为"列出所有 topic、显示 current state 的实时索引页"。

## 范围

- 修改文件：`docs/topics/README.md`

## 步骤

1. 在文件顶部（`# Changes Topic Index` 标题后、Layering Rule 前）插入 `## Current State` 节：
   - Active topic：`nautilus-live-marketdata`（进行中）
   - Active change：`20260402__nautilus-live-marketdata__live-data-client-bootstrap`
2. 将 `## Current Topics` 节升级为完整 6 条目列表（5 个 implementation topic + 1 个 governance topic），每条包含：状态标签 + 链接 + 一行说明。
3. 保留 Layering Rule、Recommended Layout、Migration Note 节内容不变。

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

- 不修改各 topic README 文件的内容
- 不修改 `docs/README.md`
