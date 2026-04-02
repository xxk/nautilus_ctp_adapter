# AI Constraints: changes-topic-index-upgrade

**change-id**: `20260402__governance-harness__changes-topic-index-upgrade`
**创建日期**: 2026-04-02

## 启动前提

1. 读取 `docs/changes_topic/README.md` 当前全文，确认当前 topic 列表存在哪几条，再动手。
2. 确认以下 topic README 文件实际存在（各 `docs/changes_topic/roadmap/nautilus_adapter/<topic-id>/README.md`）：
   - `nautilus-ctp-adapter-mainline` ✓
   - `ctp-live-connectivity` ✓
   - `nautilus-instrument-provider` ✓
   - `nautilus-live-marketdata` ✓
   - `nautilus-ctp-adapter-governance-harness` ✓（本次 C1 已创建）

## 边界

1. 只改 `docs/changes_topic/README.md`，不改其他文件。
2. topic 状态标签必须与对应 topic README 的 `**状态**` 字段完全一致（已完成 / 进行中 / 未开始）。
3. 若某个 topic README 不存在（如 `nautilus-live-execution`），在列表中注明"（README 待创建）"，不要伪造链接。
4. Current State 节必须放在 Layering Rule 节之前（即文件顶部），而不是底部。

## 禁止

- 不得删除 Layering Rule、Recommended Layout、Migration Note 三节。
- 不得修改 topic README 文件的内容（只改索引文件）。
- 不得凭推断填写 topic 状态；状态必须从对应 topic README 读取。

## 收尾

完成后回填 `acceptance.md` 中各 SC 的实际结果，将 `**状态**` 和 `**conclusion**` 改为 `pass`，并在本文件末尾追加 `## 执行记录` 节记录改动摘要。
