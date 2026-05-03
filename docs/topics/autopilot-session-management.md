# Autopilot Session Management 长期路线 / Autopilot Session Management Topic Roadmap

**topic-id**：autopilot-session-management
**domain**：governance
**状态**：planned
**canonical_status**：planned
**创建日期**：2026-04-13
**最后更新**：2026-04-13（按优先级裁剪：L1+L2 优先，L3 延后，L4 最小版）

## 一、Topic 目标

吸收 OpenHands 的 long-running session management 工程能力，将本仓 autopilot 从"状态恢复"升级到"过程可观测 + 环境感知 + 智能阻塞处理"。

核心交付三个能力层（L3 延后）：

| 层 | 能力 | 对标 OpenHands | 解决的问题 | Phase 1 交付 |
|----|------|---------------|-----------|-------------|
| L1 | **Session Trajectory Log** | Event stream (action/observation JSONL) | 新会话不知道上一轮怎么做的 | ✅ C1 交付 |
| L2 | **Drift Detection** | Conversation resume + 状态一致性 | 代码被人改了但 AI 基于旧假设继续 | ✅ C1 交付（scope 收窄到文件 hash 指纹） |
| L3 | **History Compression** | TaskTrackerTool 自摘要 | 长任务后期 context window 被前期对话占满 | ⏸️ 延后（当前单 change 3-8 task，不爆 context） |
| L4 | **Blocker Escalation Protocol** | Escalation 分类 + auto-retry | blocker 只停不分类，无结构化响应路径 | ✅ C2 最小版（分类 + 持久 + 超龄告警） |

## 二、长期愿景

```
Phase 1 (current)     Phase 1.5 (deferred)      Phase 2 (future)          Phase 3 (future)
─────────────────     ──────────────────         ─────────────────         ─────────────────
单仓 autopilot        单仓补充                    跨仓 autopilot             CI/CD 集成
─ trajectory log      ─ history compress          ─ 多仓 trajectory 聚合     ─ headless JSONL 管线
─ drift detection       (待 trajectory 积累       ─ 仓间依赖 drift 感知      ─ 自动化验收证据提取
─ blocker minimal        到百条级再评估)           ─ 跨仓 task summary 共享   ─ 报告自动生成
                                                  ─ 跨仓 blocker 传播        ─ Slack/GitHub 通知
```

**Phase 1** 交付 L1 + L2 + L4-minimal。L3 History Compression 延后到 Phase 1.5——当前单 change 粒度 3-8 task，context window 不构成瓶颈；待 trajectory log 积累到百条级再评估。Phase 2/3 留作路标。

## 三、前置条件

1. ✅ autopilot.py Route B 已稳定运行（checkpoint + TASK-LIST + backfill）
2. ✅ show_current_frontier.py 已稳定
3. ✅ check_change_docs.py / check_harness.py 守卫已就位
4. ✅ Doc Harness Kit 三件套模板已成熟

## 四、约束与边界

1. **只改 `scripts/autopilot.py`**：所有新能力收敛到 autopilot 单文件，不新增脚本
2. **只用标准库**：json, hashlib, pathlib, uuid, datetime，不引入第三方依赖
3. **向后兼容**：v1 checkpoint 必须可被新代码正常读取
4. **不改 show_current_frontier.py**：避免影响其他治理脚本的依赖方
5. **不改三件套模板**：plan/acceptance/ai_constraints 格式保持不变
6. **不引入 Docker sandbox**：本仓是 Windows + Rust FFI 场景，sandbox 改造代价远大于收益

## 五、AI-TASK-QUEUE

| 顺序 | change-id | 标题 | 状态 | 依赖 |
|------|-----------|------|------|------|
| C1 | `20260413__autopilot-session-management__trajectory-and-drift` | Trajectory Log + Drift Detection（L1+L2） | `not_started` | — |
| C2 | `20260413__autopilot-session-management__blocker-escalation-minimal` | Blocker Escalation 最小版（L4-minimal） | `not_started` | C1 |

> L3 History Compression 不在当前队列中，延后到 Phase 1.5 再评估。

## 六、完成定义

**C1（L1+L2）完成定义：**

1. `python scripts/autopilot.py --root . --log-action "edit" --log-target "file.py"` 可写 trajectory 到 `.autopilot_trajectory.jsonl`
2. `python scripts/autopilot.py --root . --show-trajectory 5` 可读最近 N 条记录
3. `python scripts/autopilot.py --root . --detect-drift` 可基于关键文件 hash 指纹检测跨会话文件变化
4. v1 checkpoint 向后兼容，v2 新增 `repo_state_hash` 字段
5. C1 的 acceptance 全部通过

**C2（L4-minimal）完成定义：**

6. `python scripts/autopilot.py --root . --report-blocker "type: description"` 可报告结构化 blocker（分类 + 持久记录）
7. `python scripts/autopilot.py --root .` 输出中可展示未解决 blocker 及其跨会话存活次数
8. C2 的 acceptance 全部通过

**L3 延后，不设完成定义。**

## 七、经验来源与参考

| 项目 | 借鉴点 | 不借鉴点 |
|------|--------|---------|
| **OpenHands** | Event stream JSONL、Conversation resume、TaskTrackerTool | Multi-agent 编排、always-approve headless |
| **Aider** | Repo map（上下文自动注入） | Git auto-commit（与 acceptance 闭环冲突） |
| **SWE-agent** | Trajectory 持久化、History Processor | 单次执行模型、Docker sandbox |

## 八、与现有 autopilot 的关系

```
当前 autopilot.py (Route B)
├── show_frontier()          ← 不改
├── parse_task_list()        ← 不改
├── read/write_checkpoint()  ← 扩展 v2 字段
├── build_snapshot()         ← 扩展 trajectory + drift
├── render_text()            ← 扩展 BLOCKER/DRIFT 输出
└── main() CLI               ← 新增 4 组参数
```

**新增运行时产物**：
- `.autopilot_trajectory.jsonl` — 追加写入的执行轨迹（C1 交付）
- `.autopilot_checkpoint.json` — v2 格式：新增 `repo_state_hash`（C1）、`blocker`（C2），`completed_task_summaries` 延后到 L3
