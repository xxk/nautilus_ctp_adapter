# AI Constraints: harness-update-policy

**change-id**: `20260402__governance-harness__harness-update-policy`
**创建日期**: 2026-04-02

## 启动前提

1. 确认 C3（`check-topic-docs-script`）已完成，`scripts/check_topic_docs.py` 存在，再动手；若 C3 未完成，在 checklist 的验证命令处标注"（待 C3 完成后生效）"。
2. 读取 `docs/doc_harness_kit/README.md` 当前结构，确认加链接的位置（最好加在与 `接入检查清单_Adoption Checklist.md` 同层）。

## 边界

1. 新建文件只放在 `docs/doc_harness_kit/checks/`，文件名为 `topic-transition-checklist.md`（英文，符合目录已有文件命名风格）。
2. checklist 必须包含的 3 项更新目标（按优先级）：
   - `AGENTS.md` → read order step → 改为新活动 topic README 的绝对链接
   - `docs/topics/README.md` → Current State 节 → 改为新 active topic + active change
   - `docs/README.md` → Current Active Delivery 节 → 改为新 active topic + active change
3. 触发时机措辞必须是强制义务（"必须"），触发条件是 topic `**状态**` 从 `进行中` 变为 `已完成` 且下一 topic 进入 `in_progress`。

## 禁止

- 不得把 checklist 写成自动化脚本或 CI hooks（本 change 只做文档层）。
- 不得修改任何主线 topic README 文件。
- 不得在 `docs/doc_harness_kit/` 之外创建文件。

## 收尾

完成后回填 `acceptance.md` 中各 SC 的实际结果，将 `**状态**` 和 `**conclusion**` 改为 `pass`，并在本文件末尾追加 `## 执行记录` 节记录改动摘要。

## 执行记录

1. 新增 `docs/doc_harness_kit/checks/topic-transition-checklist.md`
2. 更新 `docs/doc_harness_kit/README.md`，加入 checklist 链接
3. 依赖 `python scripts/check_topic_docs.py` 作为统一验证命令
