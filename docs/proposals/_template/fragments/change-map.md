# Change Map Fragment

**fragment-id**：`change_map`
**适用场景**：多个 child change 需要映射追踪。

---

## Phase Map

| Phase | Child Change | 依赖 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| <phase> | <change bundle> | <dependency> | planned | <evidence> |

## 顺序规则

1. 每个 child change 必须能追溯到一个 proposal phase。
2. 若 phase 目标变化，应先更新 `phase-plan.md`，再更新本映射。
3. completed child change 不等于 proposal closeout，proposal closeout 仍以 `acceptance.md` 为准。
