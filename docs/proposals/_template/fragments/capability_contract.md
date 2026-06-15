# Capability Contract Fragment

**fragment-id**：`capability_contract`
**适用场景**：新增能力需声明能力合约。

---

## Capability Contract

| 字段 | 说明 | 当前值 |
| --- | --- | --- |
| capability_id | 能力唯一标识 | `<capability-id>` |
| owner | 能力 owner | `<owner>` |
| public_entry | 正式入口 | `<entry>` |
| evidence_required | 必需证据 | `<evidence>` |

## Contract Rules

1. capability 字段必须能被后续 gate 或人工验收追踪。
2. 缺必需证据时不得把 proposal 标记为通过。
