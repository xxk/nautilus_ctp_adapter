# Topic Transition Checklist

**用途**：当活动 topic 从一个 topic 切换到下一个 topic 时，防止治理入口地图、索引与当前状态再次陈旧。

## 触发时机

当某个 topic README 的 `**状态**` 从 `进行中` 改为 `已完成`，且下一个 topic 已进入 `in_progress` 时，必须在同一次 commit 或 PR 中同步执行本 checklist。

## 必做更新项

1. `AGENTS.md`
   改什么文件：仓库根目录下的 `AGENTS.md`，或等价的入口地图文件
   改哪个字段：`Read First` 第 5 步
   改为什么：改成新的活动 topic README 链接，确保进入仓库后的第一跳不指向已完成 topic。

2. `docs/changes_topic/README.md`
   改什么文件：目标项目的 `docs/changes_topic/README.md`
   改哪个字段：`Current State` 节中的 `Active topic` 与 `Active change`
   改为什么：让 topic 索引反映新的活动 topic 名称、状态和当前 active change。

3. `docs/README.md`
   改什么文件：目标项目的 `docs/README.md`
   改哪个字段：`Current Active Delivery` 节中的 `Current topic roadmap` 与 `Active change`
   改为什么：让 docs 根入口与当前主线推进状态一致，避免从 docs 首页进入错误 topic。

## 建议追加更新

1. `docs/changes/README.md`
   同步新的 active change 链接。
2. `docs/changes_topic/roadmap/<domain>/<topic-id>/README.md`
   更新前一个 topic 的 `状态`、当前 topic 的 `当前 first action` 和 AI-TASK-QUEUE。
3. `docs/changes_topic/roadmap/nautilus_adapter/nautilus-ctp-adapter-mainline/README.md`
   同步 master roadmap 当前活动 topic 与 next action。

## 验证命令

```powershell
python scripts/check_topic_docs.py
```
