# AI 约束 / AI Constraints

**change-id**：20260413__autopilot-openhands-absorption__session-management-upgrade
**日期**：2026-04-13

## 允许修改

1. `scripts/autopilot.py` — 主实现文件
2. `AGENTS.md` — 更新 Autopilot 推动流程段落
3. `.autopilot_checkpoint.json` — 运行时产物
4. `.autopilot_trajectory.jsonl` — 新增运行时产物
5. 本 change bundle 下的 plan.md / acceptance.md

## 禁止修改

1. `src/` — 不碰业务实现
2. `rust/` — 不碰 Rust 运行时
3. `tests/` — 不碰测试
4. `docs/changes/_template/` — 不碰模板
5. 其他已完成 change 的 plan.md / acceptance.md
6. `scripts/show_current_frontier.py` — 本次不改动（trajectory 和 drift 逻辑独立在 autopilot.py）
7. `scripts/check_harness.py`, `scripts/check_change_docs.py` — 不碰守卫脚本

## 正式入口

- `python scripts/autopilot.py --root .`

## 必读上下文

1. 本 plan.md
2. `AGENTS.md` 的 Autonomous Execution Policy 和 Current Frontier Shortcut 段落
3. `scripts/autopilot.py` 全部源码（约 380 行）
4. `.autopilot_checkpoint.json`（如果存在）

## 设计约束

1. **只用标准库**：json, hashlib, pathlib, uuid, datetime。不引入第三方依赖
2. **向后兼容**：v1 checkpoint 必须可被新代码正常读取
3. **追加写入**：trajectory 用 JSONL 追加模式，不覆盖
4. **不改 show_current_frontier.py**：避免影响其他依赖方
5. **hash 范围最小化**：只 hash 当前 active change 的关键文件，不做全仓扫描
6. **exit code 不变**：drift detection 是 warning（exit 0），不是 error

## 验证命令

```bash
python scripts/autopilot.py --root . --json
python scripts/autopilot.py --root . --help
python scripts/check_harness.py
python scripts/check_change_docs.py --root .
```
