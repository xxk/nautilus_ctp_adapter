# Autopilot Session Management 升级 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-04-13
**范围**：scripts/autopilot.py, AGENTS.md
**change-id**：20260413__autopilot-openhands-absorption__session-management-upgrade
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/autopilot-session-management.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-04-13 12:00"
concluded_by: ""

exit_conditions:
  E1_success_scenarios: pending
  E2_failure_scenarios: pending
  E3_verification_cmds: pending
  E4_evidence_collected: pending
  E5_real_acceptance_only: pending
  E6_minimum_scenarios: pending

scenarios:
  A1: { exec: false, result: null, blocking: true }
  A2: { exec: false, result: null, blocking: true }
  A3: { exec: false, result: null, blocking: true }
  A4: { exec: false, result: null, blocking: true }
  A5: { exec: false, result: null, blocking: true }
  A6: { exec: false, result: null, blocking: true }

scenarios_total: 6
scenarios_passed: 0
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
