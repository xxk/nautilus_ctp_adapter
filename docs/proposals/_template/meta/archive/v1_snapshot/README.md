# Proposal Template / 提案模板

**创建日期**：YYYY-MM-DD
**最后更新**：YYYY-MM-DD
**状态**：待评审（Pending Review）
**proposal-id**：`<proposal-id>`
**范围**：<一句话说明 proposal 覆盖范围>

> 适用前提：本 proposal 默认用于“很多步骤、需要多 phase 持续推进”的任务容器；若单个 child change 就能完整闭环，不必为此建立 proposal。
> Artifact Trust Boundary / Artifact 信任边界：proposal 若引用 artifact、report、projection、verdict 或其他正式证据，必须先在 `phase-plan.md` 明确当前 proposal 唯一允许信任的 artifact roots。默认禁止引用 proposal 外部、case 外部、change 外部或历史 debug 残留 artifact 作为当前 proposal 的完成依据。

---

## 一句话结论

<用 1-2 句写清 proposal 想解决什么问题、当前是否已经过评审。>

---

## 目标清单（Goal Checklist）

建议在 proposal 首页前部先给出一版可快速扫描的目标清单，方便后续 child change 拆分、review 与 closeout 对齐。

| ID | 类型 | 目标 | 当前定位 |
| --- | --- | --- | --- |
| G1 | in-scope | <本轮必须达成的目标 1> | 本轮必须达成 |
| G2 | in-scope | <本轮必须达成的目标 2> | 本轮必须达成 |
| G3 | in-scope | <本轮必须达成的目标 3> | 本轮必须达成 |
| N1 | non-goal | <本轮明确不作为完成条件的事项 1> | 明确不作为完成条件 |
| N2 | non-goal | <本轮明确不作为完成条件的事项 2> | 明确不作为完成条件 |
| N3 | non-goal | <本轮明确不作为完成条件的事项 3> | 明确不作为完成条件 |

---

## 目标核对结果（Target Alignment）

### 本轮必须达成的目标

1. <目标 1>
2. <目标 2>
3. <目标 3>

### 本轮明确不作为完成条件的目标

1. <非目标 1>
2. <非目标 2>
3. <非目标 3>

<用 1-2 句收口：当前真正统一的是什么，不先统一什么。>

---

## 评审结论（Review Verdict）

### 总结论

1. <通过 / 不通过 / 通过方向但不通过原样执行计划>
2. <需要继续保留的架构方向>
3. <本 proposal 当前处于待评审、已评审、active 还是 reviewed-and-revised>

### 需要保留的判断

1. <判断 1>
2. <判断 2>
3. <判断 3>

### 需要修正的判断

1. <需要修正文档 / owner / scope / interface 的点>
2. <需要修正文档 / owner / scope / interface 的点>
3. <需要修正文档 / owner / scope / interface 的点>

---

## 当前状态快照（Reality Snapshot）

以下状态以 `<review date>` 本地代码、测试、已完成 changes 与相关文档为准，而不是只按 proposal 正文判断：

| 项目 | 当前判断 |
| --- | --- |
| Phase 1 | <未开始 / 部分已完成 / 需重写 owner 落点 / 已完成> |
| Phase 2 | <未开始 / 部分已完成 / 需重写 owner 落点 / 已完成> |
| Phase 3 | <未开始 / 部分已完成 / 需重写 owner 落点 / 已完成> |
| 关键 bridge lane / lane X | <当前状态> |

---

## 提案文件清单

| 文件 | 内容 | 是否必需 |
| --- | --- | --- |
| `README.md` | proposal 概览、评审结论、reality snapshot | 必需 |
| `phase-plan.md` | phase 状态表、AI 跟踪状态、修订后推进计划 | 必需 |
| `design.md` | 设计冻结：contract、状态词典、行为边界、配置来源 | 按需新增 |
| `acceptance.md` | proposal 级初步验收基线 | 建议有 |
| `acceptance_stricter.md` | proposal 级更严格验收 | 按需新增 |
| `review-lane.md` 或其他 lane 文档 | 单条 bridge lane / cross-cutting lane 的状态板 | 可选 |
| `change-map.md` | proposal 到 child changes 的映射 | 建议有 |
| `decision-log.md` | proposal 级决策日志 | 建议有 |

---

## 使用方式

1. 先读本文件，判断 proposal 当前是“待评审”“已评审需修订”还是“已进入持续推进”。
2. 若 proposal 涉及跨仓 contract、状态语义、gate 或配置优先级，新增并打开 `design.md` 做设计冻结。
3. 若要看 AI 对 proposal 的完成度，打开 `phase-plan.md` 的顶部状态板。
4. 若 proposal 下存在 bridge lane 或 cross-cutting lane，打开对应 lane 文档查看 lane 状态表。
5. 若 proposal 既有初步验收又有更严格验收，先读 `acceptance.md`，再读 `acceptance_stricter.md`。
6. 若要看 proposal 是怎么拆 phase、rollout 和 follow-up 的，读 `change-map.md`。
7. 若要看关键口径为什么变化、回写到了哪里，读 `decision-log.md`。
8. 若要进入具体实施，按 `phase-plan.md` 或 `change-map.md` 中的 change-id 打开 `docs/changes/<change-id>/`。

---

## 与稳定文档和执行状态的关系

1. 本目录承载的是 proposal，不等于 stable architecture。
2. proposal 中已经收敛为稳定结论的内容，应回写到 `docs/architecture/` 或 `docs/adr/`。
3. proposal 中的 AI 追踪状态板只回答“这条 proposal 的收敛进度如何”，不替代正式执行状态源。
4. 若该方案已升格为 proposal-bound work，则正式执行状态以 `proposal + change` 为准。
5. proposal 只负责定义和追踪“允许信任哪些 artifact roots”；真正的 formal consumer、change docs、surface 与 gate 仍应在各自 owner 入口继续做 fail-fast 校验，不能把 proposal prose 当成唯一防线。
