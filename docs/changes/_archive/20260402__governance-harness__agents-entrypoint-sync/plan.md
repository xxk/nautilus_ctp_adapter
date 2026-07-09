# Plan: agents-entrypoint-sync

**change-id**: `20260402__governance-harness__agents-entrypoint-sync`
**创建日期**: 2026-04-02
**状态**: completed
**进度**：100%

## 目标

修复 `AGENTS.md` read order step 5 指向已完成 topic（`ctp-live-connectivity`）的陈旧问题。

2026-06-08 复核结论：本 change 的原始目标已被 Route B 治理取代。当前 `AGENTS.md` 已不再把 topic 作为 read order 固定入口，step 5 已指向 `docs/proposals/README.md`，step 9 指向当前 frontier 报告的 `docs/changes/<change-id>/`。`## Topic Transition Rule` 已明确 topic 只作为 `plan.md` frontmatter label 和 `--by-topic` 分组投影，不作为 proposal 推进容器。

## 范围

- 修改文件：无；当前 `AGENTS.md` 已满足 Route B successor 规则。

## 步骤

1. 检查 `AGENTS.md` read order 是否仍指向 `ctp-live-connectivity`。
2. 检查 `AGENTS.md` 是否已有 Route B `Topic Transition Rule`。
3. 若当前 AGENTS 已采用 Route B，则不回退到 topic-specific read order。

## 不在范围内

- 不回退 `AGENTS.md` 到 legacy topic-specific read order。
- 不修改敏感配置、`.env` 或 live account 文件。

## 完成记录

1. `AGENTS.md` 当前 `**Updated**` 为 `2026-05-30`，晚于本 change 原始日期。
2. Read order step 5 为 `docs/proposals/README.md`，不再指向已完成 topic。
3. Read order step 9 明确由当前 frontier 指定 `docs/changes/<change-id>/`。
4. `Topic Transition Rule` 明确 Route B：topic 仅作为 grouping label，proposal 推进状态来自 proposal phase-plan，执行切片来自 child change plan。
5. 因当前事实已满足 successor governance，不再修改 `AGENTS.md`。
