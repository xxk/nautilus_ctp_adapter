# Doc Harness Kit Entry

**更新日期**：2026-06-10
**状态**：binding-entry

本目录不是上游 `doc_harness_kit` 的长期本地副本。
它是本仓的稳定读入口，用来收口 ADR003 对 `doc_harness_kit` 缺失入口的治理缺口。

## 当前口径

1. 基础 harness kit 上游源码入口：`D:\Nautilus\docs\doc_harness_kit\`
2. 高阶治理能力基线：`D:\Nautilus\nautilus_strategies`
3. 本仓执行状态源仍然只有本地 `docs/changes/*/plan.md`、proposal `phase-plan.md` 与本仓 gate 脚本

## 使用边界

1. 需要基础 adoption checklist、runbook 或通用 harness 约定时，先看 `D:\Nautilus\docs\doc_harness_kit\`
2. 需要 ADR/workflow/harness/autopilot 的已落地治理能力时，按 ADR003 向 `D:\Nautilus\nautilus_strategies` 对齐，再裁剪回本仓
3. 不得把外部仓 issue、topic、proposal 或 runtime owner 当作本仓状态源

## 本仓最小本地落点

1. [topic-transition-checklist.md](./checks/topic-transition-checklist.md)
2. [Workflows README](../workflows/README.md)
3. [ADR index](../adr/README.md)
4. [Changes frontier](../changes/README.md)

## 相关文档

1. [ADR003](../adr/ADR003%20Doc%20Harness%20Capability%20Replication%20And%20Strategies%20Alignment.md)
2. [Repository docs README](../README.md)
3. [AGENTS.md](../../AGENTS.md)
