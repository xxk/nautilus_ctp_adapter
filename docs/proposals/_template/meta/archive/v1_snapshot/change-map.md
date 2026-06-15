# Proposal Change Map Template / 提案变更映射模板

**创建日期**：YYYY-MM-DD
**最后更新**：YYYY-MM-DD
**状态**：生效

---

## 作用

本文件回答一个问题：**这条 proposal 具体由哪些 child changes 推进，它们之间是什么顺序关系。**

---

## Phase Map

| Phase | 目标 | Proposal 文档 | 代表性 child changes | 映射备注 |
| --- | --- | --- | --- | --- |
| P1 | <一句话目标> | `<lane-doc-1>.md` | `<change-id-1>`、`<change-id-2>` | <代表性 closeout change；新增 follow-up 另拆> |
| P2 | <一句话目标> | `<lane-doc-2>.md` | `<change-id-3>` | <当前 active change / 已冻结 baseline / follow-up 见下文> |
| P3 | <一句话目标> | `<lane-doc-3>.md` | `<change-id-4>` | <owner lane 已完成；adopter lane 另拆> |

---

## Supporting Draft Rollout

`<supporting-draft>.md` 当前仍是 supporting review draft，不单独升格为新的 proposal phase。

| 顺序 | Rollout 段 | 顺序类型 | 目标 | 代表范围 | 映射备注 |
| --- | --- | --- | --- | --- | --- |
| R1 | <rollout-1> | <推荐先后 / 硬依赖前置> | <目标> | <范围> | <已消费 / 当前 active / 另拆 follow-up> |
| R2 | <rollout-2> | <推荐先后 / 硬依赖后置> | <目标> | <范围> | <已消费 / 当前 active / 另拆 follow-up> |
| R3 | <rollout-3> | <推荐先后 / 硬依赖后置> | <目标> | <范围> | <已消费 / 当前 active / 另拆 follow-up> |

---

## Follow-Up Split

| 顺序 | Child Change / Follow-Up | Owner / 承载仓 | 目标 | 当前状态 |
| --- | --- | --- | --- | --- |
| F1 | `<change-id-or-slug-1>` | `<repo-a>` | <目标> | <planned / in_progress / completed> |
| F2 | `<change-id-or-slug-2>` | `<repo-b>` | <目标> | <planned / in_progress / completed> |
| F3 | `<change-id-or-slug-3>` | `<repo-c>` | <目标> | <planned / in_progress / completed> |

---

## 当前推荐阅读顺序

1. 先读主 `README.md`，确认 proposal 当前整体判断。
2. 再读 `phase-plan.md`，确认 proposal-level 当前完成度。
3. 再读本文件，确认 phase 到 child change 的映射与 rollout 顺序。
4. 若要看关键决策与 why / not-do，读 `decision-log.md`。
