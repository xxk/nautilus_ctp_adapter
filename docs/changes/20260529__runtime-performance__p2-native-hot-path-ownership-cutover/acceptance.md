# Hot-Path Owner Inventory / Cutover Boundary 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-05-29
**范围**：P001 Phase 2、hot-path owner inventory、migration boundary
**change-id**：20260529__runtime-performance__p2-native-hot-path-ownership-cutover
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-05-29 00:00"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: pass, blocking: true }
  A2: { exec: true, result: pass, blocking: true }
  A3: { exec: true, result: pass, blocking: true }
  A4: { exec: true, result: pass, blocking: true }
  A5: { exec: true, result: pass, blocking: true }
  A6: { exec: true, result: pass, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | Phase 2 owner inventory / cutover boundary 已收口 |
| AI 建议宣告通过 | 是 | A1-A6 已全部执行 |
| 最后更新 | 2026-05-29 00:00 | |
| AI 执行人 | Codex | |

## 一、验收目标 / Goals

1. 冻结 query / market / trading hot path owner inventory。
2. 明确 Python 暂留项与必须迁出项。
3. 阻止把 owner inventory 误写成 full native cutover。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. owner inventory table。
2. migration boundary。
3. source evidence 和 focused guard entry。

### 不覆盖（Out of Scope）

1. 真实代码迁移。
2. thin-shell contract lock。
3. benchmark / daemon trigger policy。

## 三、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: Phase 2 child change bundle 存在且 scope 清楚 | 审阅当前 bundle | plan / acceptance / ai_constraints / design 均存在 | 不含 Phase 3/4 完成声明 | bundle 缺文件或 scope 混入 thin-shell / benchmark | 当前 bundle |
| A2 | Success 2: hot-path owner inventory 完成 | 审阅 `design.md` | query / market / trading / session / bridge owner 均有 current owner 和 target owner | inventory table 完整 | 只有口头 owner 结论 | `design.md` |
| A3 | Success 3: migration boundary 冻结 | 审阅 `design.md` | 暂留 Python 项和 must-move 项均清楚 | 后续实现有明确迁出边界 | 未区分 host glue 与 runtime truth | `design.md` |
| A4 | Failure 1: 不得宣称 full native cutover | 文档审阅 | Phase 2 只冻结边界 | acceptance 明确 out of scope | 把 planned implementation 写成 completed | 当前 acceptance |
| A5 | Failure 2: 不得新增 Python runtime ownership | 文档审阅 + focused guard entry | Python adapter 只保留 host integration / transitional placeholder | forbidden list 清楚 | 新 runtime state machine 回流 Python | `design.md` |
| A6 | Boundary 1: Phase 3/4 不被偷带完成 | 审阅 plan / P001 | thin-shell 与 benchmark 仍由独立 child change 承接 | P001 映射分离 | Phase 2 混入 contract lock 或 daemon gate | P001 |

## 四、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | Change bundle | `docs/changes/20260529__runtime-performance__p2-native-hot-path-ownership-cutover/` | Phase 2 child change |
| 2 | Owner inventory | `design.md` | hot-path owner inventory and migration boundary |
| 3 | Source evidence | `src/nautilus_ctp_adapter/runtime/`; `src/nautilus_ctp_adapter/adapters/ctp/`; `rust/ctp_runtime_core/src/native.rs` | current owner classification |
| 4 | Verification | `check_proposal_docs`; `check_change_docs`; `check_harness` | 必跑 gate |

## 五、最终结论 / Final Verdict

- **结论**：✅ passed
- **日期**：2026-05-29
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：A1-A6 已用 source/docs evidence 收口；本 change 只完成 owner inventory / migration boundary freeze。
