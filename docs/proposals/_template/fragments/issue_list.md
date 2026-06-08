# Issue List Fragment

**fragment-id**：`issue_list`
**适用场景**：持续曳光弹 / tracer / cross-tracer proposal，需要把当前遗留问题转成下一枚 tracer 的正式验收输入。

---

## Issue List / 问题账本

建议在 proposal 根目录维护 `issue-list.md`，并至少包含下面三类状态：

| 状态 | 含义 |
| --- | --- |
| `fixed-in-current` | 当前 proposal 已修复，但要为下一枚 tracer 保留防回退验收 |
| `open-in-current` | 当前 proposal 仍在处理中，不能当作已完成 |
| `carry-forward-next-tracer` | 当前 proposal 不在本轮完全收口，必须成为下一枚 tracer 的正式验收输入 |

## Recommended Table / 建议表头

| ID | 严重度 | 来源 | 状态 | 问题 | Root Cause | 当前验收落点 | 下一枚 tracer 验收要求 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<issue-id>` | P0/P1/P2 | `<source proposal / child change / runtime finding>` | `fixed-in-current` | <问题描述> | <根因> | `<Axx / phase / child change>` | <下轮必须验证的断言> |

## Rules

1. issue-list 是问题账本，不是完成证据；每条 issue 仍需映射到 acceptance 或 child change evidence。
2. 当前 proposal closeout 时，不能把未关闭问题只写成 residual risk；若它需要下一枚 tracer 复验，必须升级为 `carry-forward-next-tracer`。
3. 若 issue 影响 shared module、projection、surface、report 或 cross-tracer contract，必须补充“来源 -> 当前验收 -> 下一枚 tracer”三段映射，避免下轮只靠口头继承。