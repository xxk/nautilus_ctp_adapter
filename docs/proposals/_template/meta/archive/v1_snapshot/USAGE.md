# Proposal Template Usage Guide / 提案模板使用说明

**创建日期**：2026-04-27
**状态**：生效
**适用目录**：`docs/proposals/_template/`

---

## 一句话结论

`docs/proposals/_template/` 是一套 proposal 文档骨架，用于快速搭建“很多步骤、需要多 phase 推进”的正式任务容器。

正确用法是：**先复制最小必需集合，再按 proposal 复杂度逐步补文件。**

默认判断规则：**当任务明显不是单个 child change 能说清，而需要多个 phase / 多个 child change 连续推进时，优先建 proposal。**

---

## 最小起步集合

大多数“多步骤 / 多 phase” proposal，建议先从下面两份模板开始：

| 文件 | 何时必须有 | 作用 |
| --- | --- | --- |
| `README.md` | 必需 | proposal 概览、评审结论、现实状态快照 |
| `phase-plan.md` | 必需 | 正式 phase 状态板、AI 跟踪状态与修订后推进路径 |

只有在 proposal 复杂度上来之后，再按需补下面这些：

| 文件 | 何时新增 | 作用 |
| --- | --- | --- |
| `design.md` | 需要冻结跨仓 contract、状态词典、gate 语义、配置优先级时 | 承载设计决策，避免把设计正文塞进 `README.md` |
| `change-map.md` | 需要拆 phase、rollout、follow-up child changes 时 | 管理 phase 到 child change 的映射 |
| `decision-log.md` | 需要记录 why / 回写动作 / 明确不做时 | 冻结 proposal 级治理决策 |
| `acceptance.md` | 需要给 proposal 建立初步验收口径时 | 回答“当前 proposal 是否初步通过” |
| `acceptance_stricter.md` | 需要更长链路或更严格正式验收时 | 承接 stricter acceptance |
| `review-lane.md` | 存在单独 bridge lane / cross-cutting lane 时 | 给 lane 建独立评审与状态板 |

---

## 推荐创建顺序

1. 新建 proposal 目录：`docs/proposals/<proposal-id>/`
2. 复制 `README.md`
3. 复制 `phase-plan.md`
4. 若这条任务只是单个 change 就能完整闭环，先停下来，不要为了形式感强行建 proposal。
5. 若 proposal 涉及跨仓 contract、状态语义、gate 或配置优先级，再复制 `design.md`
6. 若 proposal 明显会拆成多个 child changes，再复制 `change-map.md`
7. 若 proposal 会反复发生“修正执行边界 / 冻结不做事项”，再复制 `decision-log.md`
8. 若 proposal 需要回答“现在算不算已经通过”，再复制 `acceptance.md`
9. 若存在单独 lane，再复制 `review-lane.md`
10. 只有当 stricter acceptance 真的需要时，再复制 `acceptance_stricter.md`

---

## 渐进式更新建议

1. 若 child change 推进导致 phase 进度变化，先更新 `phase-plan.md`。
2. 若 schema、状态词典、gate 或配置优先级发生冻结或修订，更新 `design.md`。
3. 若 phase 到 child change 的映射关系变化，再更新 `change-map.md`。
4. 若发生了“为什么这样定 / 为什么不做”的稳定决策，再更新 `decision-log.md`。
5. 若 proposal 级通过结论变化，再更新 `acceptance.md` 或 `acceptance_stricter.md`。
6. 若某结论已经成为稳定长期口径，再回写到 `docs/architecture/` 或 `docs/adr/`。
