# ADR003 Landing Closeout 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-06-10
**范围**：ADR003 landing 状态、doc harness 入口、治理 gate 与 docs 导航
**change-id**：20260610__governance__adr003-landing-closeout
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR003 Doc Harness Capability Replication And Strategies Alignment.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-10 00:00"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 通过 | ADR003 已从 planned 收口到 completed |
| AI 建议宣告通过 | 是 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-06-10 00:00 | |
| AI 执行人 | Codex | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | A1/A2/A3 通过 | 见场景表 |
| E2 | 关键失败场景符合预期 | ✅ | A4/A5 通过 | 见场景表 |
| E3 | 必跑验证命令已完成 | ✅ | plan.md 命令全部通过 | 第六节 |
| E4 | 关键证据已留存 | ✅ | 当前 change bundle 和长期文档可读 | 第六节与证据表 |
| E5 | 正式验收不依赖 mock 或 test | ✅ | 只接受本仓真实 docs/gate 入口 | 本次为治理文档真实入口 |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 全部定义 | 场景表 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: successor change bundle 完整存在 | ✅ | ✅ | 是 | 当前三件套存在 |
| A2 | Success 2: 本地 doc harness 入口恢复 | ✅ | ✅ | 是 | `docs/doc_harness_kit/README.md` 与 checklist 可读 |
| A3 | Success 3: ADR003 与索引改为 completed | ✅ | ✅ | 是 | ADR docs gate 通过 |
| A4 | Failure 1: harness gate 必须拒绝缺失入口 | ✅ | ✅ | 是 | `check_harness.py` 已增加入口约束 |
| A5 | Failure 2: 外部 baseline 不得成为本仓状态源 | ✅ | ✅ | 是 | AGENTS/docs/workflows/ADR003 明确 boundary |
| A6 | Boundary 1: workflows 仍不是执行状态源 | ✅ | ✅ | 否 | workflows docs 明确 projection-only |

## 一、验收目标 / Goals

1. 关闭 ADR003 剩余 landing gap。
2. 让本仓 doc harness 入口重新可读且可检查。
3. 确保对齐 `nautilus_strategies` 只发生在治理能力层，不影响本仓 authority。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. ADR003 landing 状态与 ADR 索引。
2. `docs/doc_harness_kit/README.md` 最小本地入口。
3. `scripts/check_harness.py` 的入口检查。
4. AGENTS/docs/workflows/changes frontier 的治理口径同步。

### 不覆盖（Out of Scope）

1. 复制完整上游 `doc_harness_kit`。
2. 复制 `nautilus_strategies` 的 issue lane、业务 owner 或运行时能力。
3. 新增 proposal。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| ADR003 已 accepted | 文档事实 | 是 | 是 | ✅ | 初始事实 |
| 本仓 docs gate 可运行 | 环境 | 是 | 是 | ✅ | 本地 Python 环境可执行 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 只接受本仓 checked-in 文档和 gate 结果，不接受聊天说明代替。
2. 不得把外部仓路径本身写成本仓状态源。
3. 不得以“部分能力已经存在”为理由跳过 ADR003 completed 回填。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: successor change bundle 完整存在 | 检查当前 change 目录 | plan/acceptance/ai_constraints 存在 | 三件套齐全 | 无正式承接 bundle | `./plan.md`, `./acceptance.md`, `./ai_constraints.md` |
| A2 | Success 2: 本地 doc harness 入口恢复 | 打开 `docs/doc_harness_kit/README.md` 和 checklist | 入口可读、边界明确 | README 指向上游 kit 与 strategies baseline | 入口仍缺失或不可读 | `/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md` |
| A3 | Success 3: ADR003 与索引 completed | `python scripts/check_adr_docs.py --root .` | ADR gate 通过且 ADR003 completed | `ADR_DOCS_CHECK_OK` | ADR 状态矛盾或索引未同步 | `/D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR003 Doc Harness Capability Replication And Strategies Alignment.md` |
| A4 | Failure 1: harness gate 必须拒绝缺失入口 | 审查 `check_harness.py` 规则 | 缺失入口会报错 | 新增 `doc_harness_kit` 检查逻辑 | gate 对入口缺失无感 | `/D:/Nautilus/nautilus_ctp_adapter/scripts/check_harness.py` |
| A5 | Failure 2: 外部 baseline 不得成为本仓状态源 | 审查 AGENTS/docs/workflows/ADR003 | authority boundary 明确 | 多处写明 local frontier authority | 外部 issue/topic 成为状态源 | `/D:/Nautilus/nautilus_ctp_adapter/AGENTS.md` |
| A6 | Boundary 1: workflows 仍不是执行状态源 | 审查 workflows README/type system | workflow 仅做 templates/gates | README 明确非状态源 | workflow 成第三状态源 | `/D:/Nautilus/nautilus_ctp_adapter/docs/workflows/README.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | successor change | `./plan.md` | ADR003 正式承接 bundle |
| 2 | local harness entry | `/D:/Nautilus/nautilus_ctp_adapter/docs/doc_harness_kit/README.md` | 本地稳定读入口 |
| 3 | docs gate | `python scripts/check_harness.py` | 聚合 gate 通过 |
| 4 | ADR gate | `python scripts/check_adr_docs.py --root .` | ADR003/索引一致 |

## 七、未通过处理 / On Failure

1. 若 gate 失败，先修正文档与本地入口，再重新运行全部 docs gate。
2. 不得把 ADR003 留在 `planned` 并宣告 closeout 完成。

## 八、真实验收待办清单 / Pending E2E Checklist

无。本次是治理文档 closeout，真实入口即本仓 docs/gate。

## 九、Contract/Function 锁定证据

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Governance contract | `python scripts/check_harness.py` | 锁定本地入口、workflow、ADR 和 docs 约束 |
| ADR contract | `python scripts/check_adr_docs.py --root .` | 锁定 ADR003 closeout 一致性 |

## 十、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-06-10
- **执行人**：Codex
- **建议**：可以宣告 ADR003 落地完成
- **说明**：本仓已恢复本地 harness 读入口，收口外部基线与本地 authority 边界，并将 ADR003 landing_status 更新为 completed。
