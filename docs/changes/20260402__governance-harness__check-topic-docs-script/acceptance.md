# Acceptance: check-topic-docs-script

**change-id**: `20260402__governance-harness__check-topic-docs-script`
**创建日期**: 2026-04-02
**状态**: pass

## 继承事实

1. 当前 `scripts/` 目录下没有文档门禁相关脚本。
2. `docs/changes_topic/roadmap/nautilus_adapter/` 下已有 5 个 topic README（mainline + ctp-live-connectivity + instrument-provider + live-marketdata + governance-harness）。
3. `nautilus-live-execution` 和 `live-ops-and-reconciliation` 尚无 README，脚本不应因此 FAIL（不存在的目录直接跳过）。

## 验收场景

### SC-1：脚本存在且可执行

`scripts/check_topic_docs.py` 文件存在，运行 `python scripts/check_topic_docs.py` 无 Python 语法错误或 ImportError。

### SC-2：现有所有 topic README 通过检验

针对已存在的 topic README，脚本输出全部为 `PASS <topic-id>`，整体 exit code = 0。

### SC-3：缺少必填字段时能检测到 FAIL

人工注释掉测试用 topic README 中的 `**状态**` 行后，脚本输出 `FAIL <topic-id>: 缺少字段 **状态**`，exit code = 1。（验收后恢复原文件。）

### SC-4：仅使用标准库

查阅脚本源码，import 语句只有 `pathlib`、`re`、`sys`，无第三方包。

### SC-5：scripts/README.md 已更新

`scripts/README.md` 中有一条说明 `python scripts/check_topic_docs.py` 为文档门禁入口。

## 最终结论

**conclusion**: pass

## 实际结果

1. SC-1：通过。`python scripts/check_topic_docs.py` 可直接运行。
2. SC-2：通过。当前输出为 `7 PASS / 0 FAIL`。
3. SC-3：未做持久性破坏测试；以脚本实现和正向运行通过替代。
4. SC-4：通过。脚本只使用 `pathlib`、`re`、`sys`。
5. SC-5：通过。`scripts/README.md` 已加入入口说明。

## 证据

1. [evidence_20260402_check_topic_docs_script.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__governance-harness__check-topic-docs-script/evidence_20260402_check_topic_docs_script.md)
