# Autopilot Session Management 升级 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-13
**范围**：scripts/autopilot.py, AGENTS.md
**change-id**：20260413__autopilot-openhands-absorption__session-management-upgrade
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/autopilot-session-management.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-05-30 06:30"
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
  A6: { exec: true, result: pass, blocking: true }

scenarios_total: 6
scenarios_passed: 6
```
<!-- AI-STATUS-END -->

## 验收场景

### A1: Trajectory Log 写入与读取

**前置**：无 `.autopilot_trajectory.jsonl` 文件

**执行步骤**：
1. `python scripts/autopilot.py --root . --log-action "edit" --log-target "scripts/autopilot.py" --log-detail "新增 trajectory 功能"`
2. `python scripts/autopilot.py --root . --show-trajectory 5`

**通过条件**：
- `.autopilot_trajectory.jsonl` 被创建且含一行有效 JSON
- `--show-trajectory` 输出最近一条记录
- 记录包含 ts, session_id, action, target, result 字段

### A2: Drift Detection 检测到变化

**前置**：已有包含 `repo_state_hash` 的 v2 checkpoint

**执行步骤**：
1. 先创建 checkpoint（自动写入 hash）
2. 修改某个被 hash 覆盖的文件
3. `python scripts/autopilot.py --root . --detect-drift`

**通过条件**：
- 输出 `DRIFT_DETECTED: <filename> changed since last checkpoint`
- exit code 0（drift 是 warning 不是 error）

### A3: Drift Detection 无变化

**前置**：已有 v2 checkpoint，文件未被修改

**执行步骤**：
1. `python scripts/autopilot.py --root . --detect-drift`

**通过条件**：
- 输出 `DRIFT_CLEAN: no file changes detected`

### A4: History Compression 写入与渲染

**前置**：有 active change 且 T1 已完成

**执行步骤**：
1. `python scripts/autopilot.py --root . --update-checkpoint "T1 done: 实现骨架" --task-summary "新增 runtime/__init__.py，定义了 CTP adapter 接口"`
2. `python scripts/autopilot.py --root . --json`

**通过条件**：
- checkpoint JSON 包含 `completed_task_summaries.T1`
- `--json` 输出包含 `completed_task_summaries` 字段

### A5: Blocker Protocol 报告与清理

**前置**：有 active change

**执行步骤**：
1. `python scripts/autopilot.py --root . --report-blocker "scope_expansion: 需要新增 SDK 下载功能"`
2. `python scripts/autopilot.py --root .` — 查看文本输出
3. `python scripts/autopilot.py --root . --clear-blocker`
4. `python scripts/autopilot.py --root .` — 确认无 BLOCKER 行

**通过条件**：
- 步骤 2 输出包含 `BLOCKER: scope_expansion: 需要新增 SDK 下载功能`
- 步骤 4 输出不含 `BLOCKER:` 行
- checkpoint 中 blocker 字段被清除

### A6: 向后兼容性验证

**前置**：已有 v1 格式的 checkpoint

**执行步骤**：
1. 手工写入一个 v1 格式 checkpoint（无 repo_state_hash 等新字段）
2. `python scripts/autopilot.py --root .`
3. `python scripts/autopilot.py --root . --json`

**通过条件**：
- 正常输出，不报错
- v1 checkpoint 被正常读取
- 新功能字段显示为空/默认值

## 验证命令

```bash
python scripts/autopilot.py --root . --json
python scripts/autopilot.py --root . --help
python scripts/check_harness.py
python scripts/check_change_docs.py --root .
```

## 验收证据 / Evidence

1. A1: `python scripts/autopilot.py --root . --log-action "edit" --log-target "scripts/autopilot.py" --log-detail "新增 trajectory 功能"` 写入 `.autopilot_trajectory.jsonl`；`--show-trajectory 5` 输出包含 `ts/session_id/action/target/result`。
2. A2: 修改 checkpoint 覆盖的 `AGENTS.md` 后，`python scripts/autopilot.py --root . --detect-drift` 输出 `DRIFT_DETECTED: AGENTS.md changed since last checkpoint`；测试改动已撤回。
3. A3: 未修改 checkpoint 覆盖文件时，`--detect-drift` 输出 `DRIFT_CLEAN: no file changes detected`。
4. A4: `python scripts/autopilot.py --root . --update-checkpoint "T1 done: 实现骨架" --task-summary "新增 autopilot trajectory/drift/checkpoint v2/blocker protocol"` 后，`--json` 输出 `completed_task_summaries.T1`。
5. A5: `--report-blocker "scope_expansion: 需要新增 SDK 下载功能"` 后文本输出包含 `BLOCKER: scope_expansion: 需要新增 SDK 下载功能`；`--clear-blocker` 后文本输出不再包含 `BLOCKER:`。
6. A6: 手工写入 v1 `.autopilot_checkpoint.json` 后，`python scripts/autopilot.py --root .` 与 `--json` 均正常输出，且 JSON 中 `version=1`、新字段为空/默认值。

## 最终结论 / Final Verdict

- **结论**：✅ passed
- **日期**：2026-05-30
- **执行人**：Codex
- **建议**：可宣告通过
- **说明**：A1-A6 均已执行并通过；C1 同时交付 L1/L2/L4-minimal，L3 仍按 topic roadmap 延后，不阻塞本 change closeout。
