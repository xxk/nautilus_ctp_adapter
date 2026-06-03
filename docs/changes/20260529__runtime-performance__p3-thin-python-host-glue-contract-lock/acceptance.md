# Thin Python Host Glue Contract Lock 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-05-29
**范围**：P001 Phase 3、thin Python host glue contract
**change-id**：20260529__runtime-performance__p3-thin-python-host-glue-contract-lock
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md

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
| 验收结论 | ✅ 已通过 | Thin-shell contract lock 已收口 |
| AI 建议宣告通过 | 是 | A1-A6 已全部执行 |
| 最后更新 | 2026-05-29 00:00 | |
| AI 执行人 | Codex | |

## 一、验收目标 / Goals

1. 冻结 Python adapter allowlist。
2. 冻结 forbidden runtime logic list。
3. 绑定 focused guard path。

## 二、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: Phase 3 child change bundle 存在 | 审阅当前 bundle | 四件套存在 | scope 只覆盖 thin-shell contract | bundle 缺文件 | 当前 bundle |
| A2 | Success 2: allowlist 冻结 | 审阅 `design.md` | 合法 Python host glue 职责清楚 | allowlist table 完整 | 只有“薄壳”口号 | `design.md` |
| A3 | Success 3: forbidden-list 冻结 | 审阅 `design.md` | 禁止回流 runtime logic 类别清楚 | forbidden table 完整 | runtime truth 可回流 Python | `design.md` |
| A4 | Failure 1: second runtime API 被拒绝 | 文档审阅 | 只能围绕 batch boundary 扩展 | forbidden-list 覆盖 | 新 API 默认为可接受 | `design.md` |
| A5 | Failure 2: focused guard path 缺失时不得 closeout | 审阅 guard commands | 有 pytest/docs gate 路径 | acceptance 记录 guard | 只有文档无 guard 入口 | `design.md` |
| A6 | Boundary 1: benchmark / daemon 不被本 phase 偷带完成 | 审阅 P001 | Phase 4 独立 | P001 change-map 分离 | 本 phase 宣告 daemon gate | P001 |

## 三、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | Change bundle | `docs/changes/20260529__runtime-performance__p3-thin-python-host-glue-contract-lock/` | Phase 3 child change |
| 2 | Contract lock | `design.md` | allowlist / forbidden-list |
| 3 | Guard path | `tests/test_smoke_import.py`; docs gates | focused guard entry |
| 4 | Verification | proposal docs gate, change docs gate, harness gate, focused pytest | 必跑 gate |

## 四、最终结论 / Final Verdict

- **结论**：✅ passed
- **日期**：2026-05-29
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：A1-A6 已用 contract/docs/guard evidence 收口；本 change 不宣告性能或 daemon 结论。
