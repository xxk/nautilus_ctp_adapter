# Batch Runtime Boundary Freeze 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-05-29
**范围**：P001 Phase 1、adapter-facing runtime batch boundary、focused guard evidence
**change-id**：20260529__runtime-performance__p1
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/proposals/p001-ADR001-native-first-runtime-rollout/phase-plan.md

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

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | Phase 1 batch boundary freeze 已收口 |
| AI 建议宣告通过 | 是 | A1-A6 已全部执行 |
| 最后更新 | 2026-05-29 00:00 | |
| AI 执行人 | — | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | A1-A3 阻塞成功场景全部通过 | A1-A3 |
| E2 | 关键失败场景符合预期 | ✅ | A4-A5 阻塞失败场景全部通过 | A4-A5 |
| E3 | 必跑验证命令已完成 | ✅ | proposal docs gate、harness gate、rust gate、focused pytest 已执行 | Evidence |
| E4 | 关键证据已留存 | ✅ | 当前 bundle 和 P001 均有 evidence | Evidence |
| E5 | 正式验收不依赖 mock 或 test | ✅ | source evidence + docs gate + rust gate + focused guard 共同支持 | Evidence |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 已定义并执行 | Scenarios |

## 一、验收目标 / Goals

1. 冻结 adapter-facing batch runtime boundary。
2. 阻止 Python per-event callback mainline 或第二套 runtime API 成为长期路径。
3. 让 P001 Phase 1 有独立 child change 和可执行验收面。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `submit_command(command)` / `drain_events(limit)` 一类 batch boundary。
2. P001 Phase 1 到当前 change 的映射。
3. source evidence 与 focused guard 入口。
4. second API / phase-mixing / daemon shortcut 的失败口径。

### 不覆盖（Out of Scope）

1. hot-path owner inventory 和迁移执行。
2. thin Python host glue contract lock。
3. benchmark gate、阈值或 daemon 是否立项。
4. live trading performance 证明。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| P001 Phase 0 completed | 文档 | 是 | 是 | ☑ | proposal convergence 已收口 |
| ADR001 native-first 主线存在 | 文档 | 是 | 是 | ☑ | ADR001 当前仍为 proposed，但 rollout carrier 已建立 |
| runtime bridge source 可读 | source | 是 | 是 | ☑ | Python 与 Rust 均已有 batch-shaped bridge |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 本 change 只能宣告 Phase 1 batch boundary freeze。
2. 不得把 A1-A6 的测试或文档检查外推成 Phase 2-4 完成。
3. test-only 结果只能作为 guard evidence，不能替代 source evidence 和 proposal evidence。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: Phase 1 child change bundle 存在且 scope 清楚 | 审阅当前 bundle | plan / acceptance / ai_constraints / design 均存在，且只覆盖 batch boundary | 不含 Phase 2-4 完成声明 | bundle 缺文件或 scope 混入 owner / thin-shell / benchmark | 当前 bundle |
| A2 | Success 2: P001 Phase 1 指向当前 child change | 审阅 P001 phase-plan/change-map/acceptance | Phase 1 状态与 next action 指向 `20260529__runtime-performance__p1` | P001 docs gate 通过 | P001 仍只写待创建或指向错误 change | P001 docs |
| A3 | Success 3: canonical batch boundary 有 source evidence | 审阅 `bridge.py` 和 Rust `native.rs` | `submit_command` / `drain_events(limit)` 是共同边界形态 | source evidence 表记录路径和语义 | 只能靠口头解释 boundary | `design.md` |
| A4 | Failure 1: 第二套 adapter-facing runtime API 被拒绝 | 文档审阅 + focused guard 入口 | competing API 必须 fail-fast / reframing | acceptance / design 明确失败口径 | 新 API 被默认为可接受扩展 | `design.md` |
| A5 | Failure 2: Python per-event callback mainline 被拒绝 | 文档审阅 + focused guard 入口 | per-event callback 不能成为默认长期 boundary | P001 A6 / 当前 A5 对齐 | 逐 tick Python callback 被写成正式路径 | `design.md` |
| A6 | Boundary 1: Phase 2-4 不被本 change 偷带完成 | 审阅 plan / acceptance / P001 | owner inventory、thin-shell、benchmark 均保持后续 change | P001 A7-A11 保持 planned | 本 change 误宣告后续 phase 完成 | P001 acceptance |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | Change bundle | `docs/changes/20260529__runtime-performance__p1/` | Phase 1 child change |
| 2 | Proposal mapping | `docs/proposals/p001-ADR001-native-first-runtime-rollout/` | P001 Phase 1 映射 |
| 3 | Source evidence | `src/nautilus_ctp_adapter/runtime/bridge.py`; `rust/ctp_runtime_core/src/native.rs` | Python / Rust batch-shaped bridge |
| 4 | Verification | `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout`; `python scripts/check_harness.py` | 必跑 gate |
| 5 | Rust/source guard | `python scripts/check_rust_gate.py` | Rust workspace、vendor bridge readiness、cargo test 通过；可作为 Rust side batch boundary source guard |
| 6 | Python focused pytest | `python -m pytest tests/test_smoke_import.py::test_runtime_bridge_submit_and_drain_contract -q` | `1 passed`；首次因缺 `ctp_runtime._ctp_runtime` collection 失败，执行 `python -m pip install -e .` 后通过 |

## 七、未通过处理 / On Failure

1. 若 P001 docs gate 失败，先修 proposal mapping。
2. 若发现第二套 API 或 phase-mixing，回到 `design.md` 收紧 fail-fast 规则。
3. 不得通过扩大本 change scope 来规避验收失败。

## 八、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1-A2 | 已完成 | 无 | `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout` | OK | 无 | P001 docs |
| R2 | A3-A5 | 已完成 | 无 | source review / targeted pytest | boundary 明确 | 无 | `design.md` |
| R3 | A6 | 已完成 | 无 | docs review | 后续 phase 未误宣告完成 | 无 | P001 acceptance |

## 九、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Proposal gate | `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout` | P001 映射与状态一致 |
| Harness gate | `python scripts/check_harness.py` | harness 结构仍完整 |
| Existing runtime bridge tests | `python -m pytest tests/test_smoke_import.py -q` | 若本 change 修改 tests/source，则执行 focused pytest |

## 十、最终结论 / Final Verdict

- **结论**：✅ passed
- **日期**：2026-05-29
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：A1-A6 已全部有 source/docs/guard evidence。P001 docs gate、harness gate、rust gate 与 focused pytest 均已通过；本 change 只关闭 Phase 1 batch boundary freeze，不关闭 Phase 2-4。
