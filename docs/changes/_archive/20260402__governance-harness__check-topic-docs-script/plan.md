# Plan: check-topic-docs-script

**change-id**: `20260402__governance-harness__check-topic-docs-script`
**创建日期**: 2026-04-02
**状态**: completed
**进度**：100%

## 目标

创建一个可运行的最小文档门禁脚本 `scripts/check_topic_docs.py`，扫描所有 topic README，验证是否包含必要字段，在手动或 CI 入口下机械验证治理层健康。

## 范围

- 新建文件：`scripts/check_topic_docs.py`
- 修改文件：`scripts/README.md`（追加该脚本到门禁清单）

## 必填字段规则

脚本对每个 `docs/topics/<topic-id>.md` 检验以下 6 个必填字段是否存在：

1. `**创建日期**`
2. `**最后更新**`
3. `**状态**`
4. `**topic-id**`
5. `## AI-TASK-QUEUE`（或包含 `AI-TASK-QUEUE` 的行）
6. change 表状态列：`| 顺序 |` 表头行必须包含 `状态` 列标题

全部通过则 exit code = 0；任一 README 缺失任一字段则 exit code = 1，输出具体违规信息。

## 实现约束

- 只用 Python 标准库（`pathlib`、`re`、`sys`）
- 路径相对于脚本文件位置解析仓库根目录（`Path(__file__).resolve().parent.parent`）
- 输出格式：`PASS <topic-id>` 或 `FAIL <topic-id>: 缺少字段 <field>`，最后输出汇总行

## 不在范围内

- 不检验 child change 文件（不需要 check_change_docs）
- 不集成到 CI/CD pipeline
- 不依赖第三方包

## 完成结论

1. `scripts/check_topic_docs.py` 已落地并可执行。
2. 当前 7 个 topic README 全部通过门禁。
3. 治理索引中的已识别陈旧点已同步修复。
