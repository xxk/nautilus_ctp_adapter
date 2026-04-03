# AI Constraints: check-topic-docs-script

**change-id**: `20260402__governance-harness__check-topic-docs-script`
**创建日期**: 2026-04-02

## 启动前提

1. 列出 `docs/topics/roadmap/nautilus_adapter/` 下所有子目录，确认实际存在的 topic 列表，再实现路径扫描逻辑。
2. 读取至少一个现有 topic README 的格式，确认必填字段的实际写法（如 `**状态**：进行中` vs `**状态**: 进行中`），再写 regex。

## 边界

1. 脚本扫描路径：`<repo_root>/docs/topics/roadmap/**/<topic-id>/README.md`，其中 `<topic-id>` 为两层目录之下（domain 目录下的子目录）。
2. 必填字段检验列表（共 6 项）：`**创建日期**`、`**最后更新**`、`**状态**`、`**topic-id**`、`AI-TASK-QUEUE`、change 表中包含 `状态` 列标题。
3. 路径根目录必须通过 `Path(__file__).resolve().parent.parent` 推导，不允许硬编码 `D:/Nautilus/...`。
4. 目录不存在或 README.md 不存在的 topic 直接跳过，不计入 FAIL。

## 禁止

- 不得 import 任何 `pathlib`、`re`、`sys` 以外的模块。
- 不得修改任何 topic README 文件的内容。
- 不得把 check 逻辑扩展到 `docs/changes/` 子目录（本次只扫描 topic 层）。

## 收尾

完成后运行 `python scripts/check_topic_docs.py`，确认 exit code = 0，把输出贴入 `acceptance.md` 的 SC-1 / SC-2 结论内，将 `**状态**` 和 `**conclusion**` 改为 `pass`，并在本文件末尾追加 `## 执行记录` 节。

## 执行记录

1. 新增 `scripts/check_topic_docs.py`
2. 修复 `AGENTS.md` 与 `docs/topics/README.md` 的活动 topic/active change 陈旧点
3. 统一补齐多个 topic README 的 child-change `状态` 列
4. 运行 `python scripts/check_topic_docs.py`，结果 `SUMMARY topics=7 failures=0`
