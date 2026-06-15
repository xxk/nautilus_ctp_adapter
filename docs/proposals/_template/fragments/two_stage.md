# Two Stage Fragment

**fragment-id**：`two_stage`
**适用场景**：双阶段 prescreen/final tracer。

---

## Two-Stage Contract

| Stage | 输入 | 输出 | 拒绝条件 |
| --- | --- | --- | --- |
| prescreen | <input> | <output> | <failure> |
| final | <input> | <output> | <failure> |

## Stage Rules

1. prescreen 与 final 的 evidence 必须能独立追踪。
2. final 不能复用未冻结或未通过 prescreen 的残留 artifact。
