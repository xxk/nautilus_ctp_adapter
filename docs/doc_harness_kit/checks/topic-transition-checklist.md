# Topic Transition Checklist

**更新日期**：2026-06-10
**状态**：binding-checklist

当 active topic、parked topic 或 recent completed topic 发生变化时，至少同步检查以下三项：

1. `AGENTS.md` 中的 Current Frontier / Topic Transition 相关口径是否仍然正确。
2. `docs/README.md`、`docs/changes/README.md` 与 `docs/topics/*.md` 的导航或分组说明是否仍然一致。
3. `python scripts/show_current_frontier.py --root .`、`python scripts/check_harness.py`、`python scripts/check_change_docs.py --root .` 是否通过。
