# Plan: agents-entrypoint-sync

**change-id**: `20260402__governance-harness__agents-entrypoint-sync`
**创建日期**: 2026-04-02
**状态**: not_started

## 目标

修复 `AGENTS.md` read order step 5 指向已完成 topic（`ctp-live-connectivity`）的陈旧问题，更新为当前活动 topic（`nautilus-live-marketdata`），补充 `**Updated**` 日期，并新增 `## Topic Transition Rule` 节说明 topic 切换后必须同步更新 read order。

## 范围

- 修改文件：`AGENTS.md`

## 步骤

1. 将 `AGENTS.md` 顶部 `**Updated**` 字段改为 `2026-04-02`。
2. 将 read order step 5 链接路径从 `ctp-live-connectivity/README.md` 改为 `nautilus-live-marketdata/README.md`，链接文字改为 `[docs/topics/nautilus-live-marketdata.md]`。
3. 在 `## Change Governance` 节末尾追加 `## Topic Transition Rule` 子节，内容：topic 切换后必须在 24 小时内更新 read order step 5 和 `docs/topics/README.md` current state。

## 不在范围内

- 不修改 AGENTS.md 的其他节（Repository Role、Directory Map、Official Entry Points）
- 不修改任何其他文件
