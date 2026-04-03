# Plan: harness-update-policy

**change-id**: `20260402__governance-harness__harness-update-policy`
**创建日期**: 2026-04-02
**状态**: completed

## 目标

在 `docs/doc_harness_kit/checks/` 中添加一个"topic 切换治理 checklist"文档，明确 topic 切换后治理层必须同步执行的 3 项更新，防止下次 topic 切换再出现 AGENTS.md、索引陈旧现象。

## 范围

- 新建文件：`docs/doc_harness_kit/checks/topic-transition-checklist.md`
- 修改文件：`docs/doc_harness_kit/README.md`（加入该 checklist 链接）

## Checklist 内容要求

文档必须包含以下 3 个更新项，每项须给出"改什么文件 → 改哪个字段 → 改为什么"的具体操作：

1. `AGENTS.md` read order step 5 → 改为新 topic 的 README 链接
2. `docs/topics/README.md` Current State 节 → 改为新 topic 名 + 新 active change-id
3. `docs/README.md` Current Active Delivery 节 → 改为新 topic + 新 active change

文档末尾必须包含验证命令：`python scripts/check_topic_docs.py`

## 触发时机说明

checklist 的触发时机必须明确写为：
> 当某个 topic README 的 `**状态**` 从 `进行中` 改为 `已完成`，且下一个 topic 已进入 `in_progress` 时，必须在该次 commit 或 PR 中同步执行本 checklist。

## 不在范围内

- 不创建 CI/CD 自动触发机制（人工 checklist 已足够）
- 不修改主线 topic README 文件

## 完成结论

1. `topic-transition-checklist.md` 已落地到 harness checks。
2. checklist 已明确 3 项必须同步更新的治理动作。
3. 验证命令已统一收敛到 `python scripts/check_topic_docs.py`。
