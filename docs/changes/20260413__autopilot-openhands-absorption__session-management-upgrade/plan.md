---
change-id: "20260413__autopilot-openhands-absorption__session-management-upgrade"
dependencies:
  hard_blocking: []
  soft_dependency: []
  blocked_by: []
---

# Autopilot Session Management 升级：吸收 OpenHands 优点 / Autopilot Session Management Upgrade

**状态**：completed
**进度**：100%
**日期**：2026-04-13
**范围**：scripts/autopilot.py, scripts/show_current_frontier.py
**topic-id**：autopilot-session-management
**execution_order**：1
**change-id**：20260413__autopilot-openhands-absorption__session-management-upgrade
**关联 acceptance**：./acceptance.md

## 一、需求简述

从 OpenHands 项目吸收四项 long-running session management 能力，增强现有 autopilot 系统：

1. **Session Trajectory Log**：记录执行过程（不仅是进度），对标 OpenHands event stream
2. **Drift Detection**：跨会话恢复时检测仓库状态漂移，对标 OpenHands conversation resume + Aider git
3. **History Compression**：已完成 task 自动生成摘要，减少 context window 占用
4. **Blocker Escalation Protocol**：结构化阻塞分类与自动响应

**不做什么**：
- 不引入 Docker sandbox（本仓是 Windows + Rust FFI 场景，sandbox 改造代价远大于收益）
- 不引入多 Agent 编排（当前 change 粒度已足够细）
- 不引入 Git auto-commit（与 acceptance 闭环冲突）
- 不改动 change governance 三件套格式（plan/acceptance/ai_constraints 保持不变）

**真实成功信号**：
- `python scripts/autopilot.py --root .` 输出包含 trajectory 摘要
- 跨会话恢复时自动检测 drift 并输出变化文件列表
- checkpoint 含 completed_task_summaries
- blocker 分类在 checkpoint 中有结构化字段

## 二、能力映射 / Capability Mapping

```text
- capability_id: autopilot-session-management
- capability_name: Autopilot 会话管理增强 / Autopilot Session Management Enhancement
- long_term_target: docs/architecture/autopilot-session-management.md
- secondary_targets: AGENTS.md (Autopilot 推动流程段落)
- decision_target: 无
- affects_long_term_rules: 否
- change_type: 新增规则
```

## 三、AI 执行约束

1. **允许修改**：`scripts/autopilot.py`, `scripts/show_current_frontier.py`, `AGENTS.md` 的 Autopilot 段落
2. **禁止修改**：`src/`, `rust/`, `tests/`, `docs/changes/_template/`, 已完成 change 的 plan.md/acceptance.md
3. **正式入口**：`python scripts/autopilot.py --root .`
4. **必读上下文**：本 plan.md, AGENTS.md, 当前 autopilot.py 全部源码
5. **改完后验证**：
   - `python scripts/autopilot.py --root . --json` 正常输出
   - `python scripts/autopilot.py --root . --help` 显示新增选项
   - `python scripts/check_harness.py` 通过
   - `python scripts/check_change_docs.py --root .` 通过

## 四、背景与约束

### 来源分析

| OpenHands 能力 | 我的现有对应 | Gap |
|----------------|-------------|-----|
| Conversation resume (--resume) | .autopilot_checkpoint.json | 无过程记录、无 drift 检测 |
| Event stream (action/observation JSONL) | 无 | 完全缺失 |
| TaskTrackerTool (agent 自管理 task) | TASK-LIST-BEGIN/END | 无自动摘要 |
| Headless JSONL output | --json flag | 已有，但无 trajectory 维度 |

### 设计原则

1. **增量演进**：不重写 autopilot.py，只在现有 dataclass 上扩展字段
2. **文件优先**：trajectory 用 JSONL 追加写，不引入数据库
3. **向后兼容**：现有 checkpoint 格式的 v1 继续可读；新字段用 v2 标记
4. **最小外部依赖**：只用标准库（json, hashlib, pathlib）

## 五、设计方案

### 5.1 Session Trajectory Log

新增文件 `.autopilot_trajectory.jsonl`，追加写入。

每行格式：
```json
{
  "ts": "2026-04-13T10:30:00",
  "session_id": "uuid4-short",
  "change_id": "20260413__xxx__yyy",
  "task": "T3",
  "action": "edit|run|backfill|checkpoint|blocker",
  "target": "src/foo.py",
  "result": "ok|fail|skip",
  "detail": "自由文本描述"
}
```

autopilot.py 新增：
- `--log-action` 参数：记录一条 trajectory entry
- `--show-trajectory` 参数：输出最近 N 条 trajectory
- `build_snapshot()` 返回的 `AutopilotSnapshot` 增加 `recent_actions: tuple[dict, ...]` 字段

### 5.2 Drift Detection

checkpoint v2 增加 `repo_state_hash` 字段：
```json
{
  "version": 2,
  "repo_state_hash": {
    "scripts/autopilot.py": "sha256-short-8",
    "src/nautilus_ctp_adapter/runtime/__init__.py": "sha256-short-8"
  }
}
```

范围：只 hash 当前 active change 的 `ai_constraints.md` 中声明的"允许修改"文件列表，不做全仓扫描。

恢复时逻辑：
1. 读 checkpoint → 如果 version >= 2 且有 repo_state_hash
2. 计算当前文件 hash → 逐文件对比
3. 若 drift detected → 输出 `DRIFT_DETECTED: <file> changed since last checkpoint`
4. 不阻止继续，但输出 warning 供 AI review

autopilot.py 新增：
- `--detect-drift` flag：主动检测并输出 drift 报告
- `write_checkpoint()` 自动写入当前文件 hash

### 5.3 History Compression

checkpoint v2 增加 `completed_task_summaries` 字段：
```json
{
  "version": 2,
  "completed_task_summaries": {
    "T1": "补全了 CTP adapter 骨架，新增 runtime/__init__.py",
    "T2": "修复了 login callback 空值问题，通过 smoke 验证"
  }
}
```

autopilot.py 新增：
- `--update-checkpoint` 增加可选的 `--task-summary` 参数
- 当 task 标记完成时，summary 自动追加到 checkpoint
- `render_text()` 输出已完成 task 时，如果有 summary 就显示 summary 而不是原始 label

### 5.4 Blocker Escalation Protocol

checkpoint v2 增加 `blocker` 字段：
```json
{
  "version": 2,
  "blocker": {
    "type": "scope_expansion|dependency_missing|contract_conflict|test_failure",
    "description": "发现需要新增 SDK 下载功能，超出当前 change 范围",
    "escalation": "split_derived|wait_human|auto_retry",
    "retry_count": 0,
    "max_retries": 2
  }
}
```

autopilot.py 新增：
- `--report-blocker` 参数：`--report-blocker "scope_expansion: 需要新增 SDK 下载"`
- `--clear-blocker` 参数：阻塞解除后清理
- `render_text()` 在有 blocker 时输出醒目的 `BLOCKER:` 行

## 六、阶段划分

分 4 个原子阶段，每阶段独立可验证：

| 阶段 | 内容 | 验证 |
|------|------|------|
| Phase 1 | Trajectory Log | `--log-action` 可写，`--show-trajectory` 可读 |
| Phase 2 | Drift Detection | `--detect-drift` 输出正确的 drift/clean 结论 |
| Phase 3 | History Compression | `--update-checkpoint --task-summary` 可写可读 |
| Phase 4 | Blocker Protocol | `--report-blocker` / `--clear-blocker` 可写可读 |

## 七、任务清单

<!-- TASK-LIST-BEGIN
- [x] T1: 实现 Trajectory Log 追加写入与读取
- [x] T2: 实现 Drift Detection hash 计算与对比
- [x] T3: 实现 History Compression summary 字段
- [x] T4: 实现 Blocker Escalation Protocol
- [x] T5: 更新 AGENTS.md 的 Autopilot 推动流程
- [x] T6: 验证全部新功能与向后兼容性
TASK-LIST-END -->

| 步骤 | 任务 | 修改文件 | 产出 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- | --- |
| T1 | Trajectory Log | scripts/autopilot.py | --log-action, --show-trajectory | 执行写入后读取验证 | ✅ |
| T2 | Drift Detection | scripts/autopilot.py | --detect-drift, checkpoint v2 hash | 修改文件后检测到 drift | ✅ |
| T3 | History Compression | scripts/autopilot.py | --task-summary, completed_task_summaries | checkpoint 含 summary | ✅ |
| T4 | Blocker Protocol | scripts/autopilot.py | --report-blocker, --clear-blocker | 写入后 render 输出 BLOCKER | ✅ |
| T5 | AGENTS.md 更新 | AGENTS.md | Autopilot 段落补充新命令 | check_harness 通过 | ✅ |
| T6 | 全量验证 | - | 全部 --json 输出正确 | autopilot --json + check_change_docs | ✅ |
