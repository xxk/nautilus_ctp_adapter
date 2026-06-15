# Decision Log Fragment

**fragment-id**：`decision_log`
**适用场景**：评审过程中产生了多轮需要保留的判断。

---

## Decision Log

| 日期 | 决策 | 原因 | 回写动作 | 明确不做 |
| --- | --- | --- | --- | --- |
| <date> | <decision> | <reason> | <write-back> | <non-goal> |

## 记录规则

1. 只记录会影响后续执行边界的稳定判断。
2. 已升格为长期规则的内容应回写到 `docs/architecture/` 或 `docs/adr/`。
