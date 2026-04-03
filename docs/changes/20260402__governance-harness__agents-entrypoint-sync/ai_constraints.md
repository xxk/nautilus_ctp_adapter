# AI Constraints: agents-entrypoint-sync

**change-id**: `20260402__governance-harness__agents-entrypoint-sync`
**创建日期**: 2026-04-02

## 启动前提

1. 读取当前 `AGENTS.md` 全文，确认 step 5 的当前链接文字和路径，再动手。
2. 读取 `docs/topics/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md` 文件头，确认 `**状态**` = `进行中`，再动手。

## 边界

1. 只改 `AGENTS.md`，不改其他文件。
2. step 5 目标路径必须是绝对路径格式（与文件内其他链接一致），指向 `nautilus-live-marketdata/README.md`。
3. 新增的 Topic Transition Rule 段落必须用"必须"而非"建议"表述，且明确列出两个必须更新项：AGENTS.md step 5 + `docs/topics/README.md` current state。

## 禁止

- 不得删除 AGENTS.md 中任何现有节（Repository Role、Directory Map、Change Governance、Official Entry Points）。
- 不得修改 AGENTS.md 中除指定三处（step 5 路径、日期、新增节）以外的任何内容。
- 不得在 AGENTS.md 中新增与本次 change 无关的内容。

## 收尾

完成后回填 `acceptance.md` 中各 SC 的实际结果，将 `**状态**` 和 `**conclusion**` 改为 `pass`，并在本文件末尾追加 `## 执行记录` 节，记录改动摘要。
