# Proposal Phase Plan Template / 提案 Phase 计划模板

**创建日期**：YYYY-MM-DD
**状态**：待评审（Pending Review）
**最后评审**：YYYY-MM-DD
**关联提案**：[README.md](README.md)
**关联差距分析**：[gap-analysis.md](gap-analysis.md) 或 `无`

## Artifact 信任边界（Artifact Trust Boundary）

```yaml
artifact_boundary:
  trusted_artifact_roots:
    - <当前 proposal 唯一允许信任的正式 artifact 根，例如 D:/Nautilus/Data/artifact_store/DSLReserach/cases/17.P2/>
  allowed_evidence_roots:
    - output/debug/change_evidence/<proposal-id>/
    - output/reports/<proposal-id>/
```

规则：

1. proposal 全部文档若引用正式 artifact，只能引用 `trusted_artifact_roots` 下的对象。
2. `allowed_evidence_roots` 只用于 repo-local 执行留痕，不得把其他 case / change 的正式 artifact 塞进这里伪装成证据。
3. 若当前 proposal 尚未冻结唯一 artifact root，应明确写“未冻结”，并把“冻结 artifact trust boundary”列为优先 Phase 任务；未冻结前不得把外部 artifact 当作 proposal 完成证据。

---

## 执行原则

1. <例如：从接口向内改，不从实现向外改>
2. <例如：Phase 间尽量保持独立可验证>
3. <例如：先修语义，后修性能>
4. 先冻结 artifact trust boundary，再复用 artifact；不要先引用外部 artifact，事后再补“其实来源一致”的解释。

---

## 评审后执行口径（Post-Review Execution Contract）

1. 本文档同时承担两种职责：描述 proposal 的修订后推进路径，并提供可持续更新的 `Phase 状态表`。
2. 后续 AI 更新 proposal 进度时，必须优先修改本页顶部状态板，而不是只改正文。
3. `ai_progress` 表示按本 proposal 修订后目标，AI 已完成的真实收口比例，不是代码量或对话轮数。
4. 若某个 Phase 的原 proposal 已与代码现实错位，应标为 `reframing_required` 或 `partially_completed`。
5. proposal 下任何 phase 若要宣告完成，引用的 formal artifact、report、projection、verdict 必须落在本页 `Artifact Trust Boundary` 声明的受信根内。

### 状态词典

| 状态 | 含义 |
| --- | --- |
| `not_started` | 尚未形成正式收口动作 |
| `in_progress` | 已有 active implementation / docs bundle 正在推进 |
| `partially_completed` | 相关能力已有部分落地，但距离完成定义仍有明显缺口 |
| `reframing_required` | proposal 方向仍有效，但 owner / scope / interface 需要先修文档再继续 |
| `completed` | 达到修订后完成定义，并有 evidence |
| `blocked` | 存在真实阻塞，无法继续推进 |

---

## AI 跟踪状态（AI Tracking Status）

<!-- AI-PHASE-STATUS-BEGIN
reviewed_at: YYYY-MM-DD
reviewer: Codex
phases:
  - id: phase_1
    status: not_started
    ai_progress: 0
  - id: phase_2
    status: not_started
    ai_progress: 0
  - id: phase_3
    status: not_started
    ai_progress: 0
AI-PHASE-STATUS-END -->

## Phase 状态表（Phase Status Board）

| Phase | 修订后目标 | 当前状态 | AI 完成度 | 证据 / 当前事实 | 下一步 |
| --- | --- | --- | ---: | --- | --- |
| Phase 1 | <修订后目标> | `not_started` | 0% | <当前事实> | <下一步> |
| Phase 2 | <修订后目标> | `not_started` | 0% | <当前事实> | <下一步> |
| Phase 3 | <修订后目标> | `not_started` | 0% | <当前事实> | <下一步> |

---

## Phase 跟踪列表

1. **Phase 1：<名称>**
   状态：`not_started`
   优先级：P0
   核心目标：<一句话>
   涉及仓库：<repo A + repo B>
2. **Phase 2：<名称>**
   状态：`not_started`
   优先级：P1
   核心目标：<一句话>
   涉及仓库：<repo A + repo B>
3. **Phase 3：<名称>**
   状态：`not_started`
   优先级：P2
   核心目标：<一句话>
   涉及仓库：<repo A + repo B>

---

## Phase 1: <名称>

**状态**：`not_started`

### 目标

<写清这个 phase 想收口什么，不要写成空泛愿景。>

### 交付物

```text
<目录或文件结构>
```

### 评审修正

1. <需要修正的 owner / scope / interface>
2. <需要修正的 owner / scope / interface>
3. <若本 phase 使用正式 artifact，必须写清允许引用的 artifact root 与明确禁止的外部 root>

### 各仓适配

| 仓库 | 当前代码 | 改为 | 改动范围 |
| --- | --- | --- | --- |
| repo-a | <当前> | <目标> | <范围> |
| repo-b | <当前> | <目标> | <范围> |

### 验收标准

- [ ] <标准 1>
- [ ] <标准 2>
- [ ] <标准 3>
- [ ] 若本 phase 引用 formal artifact，全部 evidence path 均位于 `Artifact Trust Boundary` 的受信根内

---

## Phase 2: <名称>

**状态**：`not_started`

### 目标

<写清 Phase 2 目标>

### 交付物

```text
<目录或文件结构>
```

### 各仓适配

| 仓库 | 当前代码 | 改为 |
| --- | --- | --- |
| repo-a | <当前> | <目标> |
| repo-b | <当前> | <目标> |

### 验收标准

- [ ] <标准 1>
- [ ] <标准 2>

---

## Anti-Rot Closeout / 防腐收口

- Retired legacy paths / 已退役旧路径：<无 / 列出旧入口、旧字段、旧文档或旧实现>
- Canonical docs updated / 已更新唯一文档入口：<README / runbook / architecture / ownership>
- Guards preventing rollback / 防回退守卫：<测试、gate、负向断言或 fail-fast 入口>
- Deferred risks / 延期风险：<无 / 明确后续 change 或 candidate>

---

## 依赖关系

```text
Phase 1
  |
  v
Phase 2 ---> Phase 3
```

1. <说明依赖>
2. <说明依赖>

---

## Future Candidates / Promotion Rule

本区块用于承载“很可能会变成后续 phase，但当前还不应直接进入正式中央状态板”的候选项。

| Candidate | 当前定位 | 升格条件 | 当前落点 |
| --- | --- | --- | --- |
| C1 | <supporting draft / follow-up / bridge lane> | <满足什么条件后，升格为正式 phase> | `<change-map.md>` / `<lane-doc>.md` |
| C2 | <supporting draft / follow-up / bridge lane> | <满足什么条件后，升格为正式 phase> | `<change-map.md>` / `<lane-doc>.md` |

---

## Change 映射

| 序号 | Phase | Change slug | 风险 |
| --- | --- | --- | --- |
| 1 | Phase 1 | `<slug-1>` | 低 / 中 / 高 |
| 2 | Phase 2 | `<slug-2>` | 低 / 中 / 高 |
| 3 | Phase 3 | `<slug-3>` | 低 / 中 / 高 |

每个 change 需要 `plan.md + acceptance.md + ai_constraints.md` 三件套。
若某个 change 继承本 proposal 的 artifact boundary，应在 change `plan.md` 再次显式落成该 change 自己的 `artifact_boundary`，不得只靠 proposal 口头继承。
