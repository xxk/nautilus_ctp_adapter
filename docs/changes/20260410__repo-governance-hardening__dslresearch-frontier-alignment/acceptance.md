# DSLResearch Frontier Alignment 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-10
**范围**：`AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`docs/topics/`、`scripts/`、`src/nautilus_ctp_adapter/devtools/`、`tests/`
**change-id**：20260410__repo-governance-hardening__dslresearch-frontier-alignment
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：[repo-governance-hardening topic README](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/repo-governance-hardening.md)

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-04-10 21:40"
concluded_by: "GitHub Copilot"

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
| 验收结论 | ✅ 已通过 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 是 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-04-10 21:40 | |
| AI 执行人 | GitHub Copilot | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | A1-A3 全部通过 | A1-A3 |
| E2 | 关键失败/边界场景符合预期 | ✅ | A4-A6 全部通过 | A4-A6 |
| E3 | 必跑验证命令已完成 | ✅ | `plan.md` 中声明命令全部执行 | A1-A5 |
| E4 | 关键证据已留存 | ✅ | 当前文档记录了命令与关键输出 | A1-A6 |
| E5 | 正式验收不依赖 mock 或 test 伪装 real state | ✅ | frontier 与 docs gate 直接运行在真实仓内容上 | A1-A4 |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 共 6 个场景 | A1-A6 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: `sync_topic_index.py` 可生成 registry 驱动的 topic index | ✅ | ✅ | 是 | 输出 `TOPIC_INDEX_SYNC_OK: docs/topics/README.md` |
| A2 | Success 2: `show_current_frontier.py` 可返回 active topic/change | ✅ | ✅ | 是 | 输出 active topic=`live-session-order-query-hardening`，active change=`20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening` |
| A3 | Success 3: `check_topic_docs.py` 通过 | ✅ | ✅ | 是 | 输出 `SUMMARY topics=16 failures=0` |
| A4 | Success 4: `check_topic_governance.py` 通过 | ✅ | ✅ | 是 | 输出 `TOPIC_GOVERNANCE_CHECK_OK` |
| A5 | Failure 1: 若 topic index 未同步应被测试/守卫捕获 | ✅ | ✅ | 是 | 新增 `tests/test_topic_governance.py` 并通过 `3 passed` |
| A6 | Boundary 1: blocked topic 不得被当作 active lane | ✅ | ✅ | 否 | `show_current_frontier.py` 输出 `PARKED_TOPIC: topic=live-ops-truth-snapshot status=blocked` |

## 一、验收目标 / Goals

1. 当前仓具备 DSLResearch 风格的 machine-readable topic frontier。
2. active topic/change、blocked topic 和 completed topics 能被脚本稳定识别。
3. docs/AGENTS/changes index 与 frontier 状态已形成闭环。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. topic state registry
2. topic index sync
3. current frontier CLI
4. topic governance CLI
5. docs/AGENTS current frontier 同步
6. regression tests for the above

### 不覆盖（Out of Scope）

1. 业务实现或 live trading 行为
2. `check_rust_gate.py`、`ctp_repo_debug_smoke.py` 的功能逻辑

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| Python 环境可运行仓内脚本 | 环境 | 是 | 是 | ✅ | 使用 `C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe` |
| `docs/topics/` 已存在全部 topic README | 仓库事实 | 是 | 是 | ✅ | 当前共 16 个 topic |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 本 change 的正式验收是本地治理入口和文档一致性，不需要 live 外部依赖。
2. `pytest` 只作为 regression lock，不能替代 A1-A4 这类正式 CLI 验收。
3. 不得把未同步的 `docs/topics/README.md` 当作通过状态；必须经过 `sync_topic_index.py` 与 docs gate 双重确认。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Sync topic index | `python scripts/sync_topic_index.py --root .` | topic index 被成功重建 | 输出 `TOPIC_INDEX_SYNC_OK` | 输出 `TOPIC_INDEX_SYNC_FAILED` | 本文 Scenario Board A1 |
| A2 | Show current frontier | `python scripts/show_current_frontier.py --root .` | active topic/change 与 parked topic 可见 | 输出 `CURRENT_FRONTIER_OK`、`ACTIVE_TOPIC`、`ACTIVE_CHANGE`、`PARKED_TOPIC` | 输出 `CURRENT_FRONTIER_FAILED` | 本文 Scenario Board A2 / A6 |
| A3 | Topic docs gate | `python scripts/check_topic_docs.py --root .` | registry、topic index、docs/AGENTS 一致 | 输出 `SUMMARY topics=16 failures=0` | 任一 `FAIL repo-sync` 或 failures>0 | 本文 Scenario Board A3 |
| A4 | Topic governance check | `python scripts/check_topic_governance.py --root .` | sync + docs gate 一键通过 | 输出 `TOPIC_GOVERNANCE_CHECK_OK` | 输出 `TOPIC_GOVERNANCE_CHECK_FAILED` | 本文 Scenario Board A4 |
| A5 | Regression lock | `python -m pytest tests/test_topic_governance.py -q` | 新增测试通过 | 输出 `3 passed` | 任一测试失败 | 本文 Scenario Board A5 |
| A6 | Blocked topic boundary | 与 A2 同次检查 | blocked topic 只出现在 parked，不会变成 active | 输出 `PARKED_TOPIC: topic=live-ops-truth-snapshot status=blocked` | blocked topic 出现在 ACTIVE_TOPIC | 本文 Scenario Board A6 |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | CLI output summary | `sync_topic_index.py` | `TOPIC_INDEX_SYNC_OK: docs/topics/README.md` |
| 2 | CLI output summary | `show_current_frontier.py` | active / parked topic summary 正确 |
| 3 | CLI output summary | `check_topic_docs.py` | `SUMMARY topics=16 failures=0` |
| 4 | CLI output summary | `check_topic_governance.py` | `TOPIC_GOVERNANCE_CHECK_OK` |
| 5 | Test output summary | `pytest tests/test_topic_governance.py -q` | `3 passed in 0.03s` |

## 七、未通过处理 / On Failure

1. 若 `sync_topic_index.py --check` 失败，先同步 topic index，再检查 registry/roadmap 状态是否一致。
2. 若 `check_topic_docs.py` 失败，优先修 `AGENTS.md`、`docs/README.md`、`docs/changes/README.md` 的 frontier 漂移。
3. 若 `show_current_frontier.py` 把 blocked topic 识别成 active，必须先修 registry 或 roadmap 状态，不得绕过守卫。

## 八、真实验收待办清单 / Pending E2E Checklist

无。本 change 的正式验收已在本地仓内完成。

## 九、Contract/Function 锁定证据

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Function 锁定 | `python -m pytest tests/test_topic_governance.py -q` | 锁定 sync/frontier/docs gate 的基础行为 |

## 十、最终结论 / Final Verdict

- **结论**：✅ 已通过
- **日期**：2026-04-10
- **执行人**：GitHub Copilot
- **建议**：可宣告通过
- **说明**：仓内已具备 registry 驱动的 topic/change frontier 能力，active lane、blocked lane 与 docs sync 已形成正式闭环。
