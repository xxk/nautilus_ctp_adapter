---
change-id: "20260610__governance__adr003-landing-closeout"
dependencies:
  hard_blocking: []
  soft_dependency: []
  blocked_by: []
---

# ADR003 Landing Closeout 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-10
**范围**：`AGENTS.md`、`docs/README.md`、`docs/adr/`、`docs/changes/README.md`、`docs/doc_harness_kit/`、`docs/workflows/`、`scripts/check_harness.py`
**topic-id**：none
**execution_order**：1
**change-id**：20260610__governance__adr003-landing-closeout
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 将 ADR003 从已接受但未完成落地，推进到本仓治理口径中的 completed。
2. 正式收口 `docs/doc_harness_kit/README.md` 缺失入口。
3. 把 workflows / ADR / harness 的当前本地落点和外部基线写成可执行、可检查的本仓规则。
4. 不复制 `nautilus_strategies` 的业务 owner、issue lane 或执行状态源。

## 二、能力映射 / Capability Mapping

```text
- capability_id: adr003-landing-closeout
- capability_name: ADR003 landing closeout
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR003 Doc Harness Capability Replication And Strategies Alignment.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/AGENTS.md, /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/adr/README.md
- affects_long_term_rules: 是
- change_type: 修改规则
```

## 三、AI 执行约束

1. 允许修改：当前 change bundle、`AGENTS.md`、`docs/README.md`、`docs/adr/README.md`、`docs/adr/ADR003...md`、`docs/changes/README.md`、`docs/workflows/README.md`、`docs/workflows/work-item-type-system.md`、`scripts/check_harness.py`。
2. 允许新增：`docs/doc_harness_kit/README.md` 与最小本地 checklist。
3. 禁止修改：`src/`、`rust/`、`tests/`、已完成 proposal 的状态。
4. 当前正式入口：`python scripts/check_harness.py`、`python scripts/check_adr_docs.py --root .`、`python scripts/check_change_docs.py --root .`、`python scripts/check_proposal_docs.py --root .`。
5. 改完后必须执行：上述四个 gate、`python scripts/show_current_frontier.py --root .`、`python scripts/autopilot.py --root . --backfill`。

## 四、背景与约束

1. ADR003 已 accepted，但 landing_status 仍为 `planned`。
2. 本仓已经具备 `docs/workflows/` 与 `check_adr_docs.py`，但缺少 formal successor change 来关闭剩余缺口。
3. `docs/doc_harness_kit/` 当前缺失，导致 AGENTS/docs README 入口失真。

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立 ADR003 正式承接 bundle | ADR003 Phase 1-3 | 当前 change bundle | plan/acceptance/constraints | docs gates | ADR003 | 有可追踪 closeout change | 已完成 |
| P2 | 恢复本地 doc harness 入口 | ADR003 D4 | `docs/doc_harness_kit/`、`scripts/check_harness.py` | 本地入口 README + checklist + gate | `python scripts/check_harness.py` | AGENTS/docs README | 入口存在且可检查 | 已完成 |
| P3 | 同步 workflows / docs / AGENTS 口径 | ADR003 D1-D3 | `AGENTS.md`、`docs/README.md`、`docs/workflows/*`、`docs/changes/README.md` | binding 入口说明 | docs gates | ADR003 / docs index | 本仓 authority 与外部 baseline 边界明确 | 已完成 |
| P4 | 更新 ADR003 状态并完成回填 | ADR003 Final | `docs/adr/ADR003...md`、`docs/adr/README.md` | landing completed | `check_adr_docs.py` | ADR index | ADR003 landing_status=completed | 已完成 |

## 六、验证动作

```powershell
python scripts/check_harness.py
python scripts/check_adr_docs.py --root .
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root .
python scripts/show_current_frontier.py --root .
python scripts/autopilot.py --root . --backfill
```

## 七、完成定义

### 开发完成

1. ADR003 的 successor change 存在且文档完整。
2. `docs/doc_harness_kit/README.md` 不再缺失。
3. harness gate 可检查本地 harness 入口。

### 交付完成

1. ADR003 `landing_status` 改为 `completed`。
2. ADR 索引、docs 入口、changes frontier 和 workflows 状态同步。
3. 全部治理 gate 通过。

## 八、长期规则增量摘要 / Long-Term Rule Delta Summary

新增规则：本仓以本地 `docs/doc_harness_kit/README.md` 作为稳定读入口，以 `D:\Nautilus\docs\doc_harness_kit\` 作为基础 kit 上游，以 `D:\Nautilus\nautilus_strategies` 作为 advanced governance baseline；但本仓 frontier authority 始终保持本地。

## 九、回写与相关变更 / Write-back & Related Changes

1. 已回写 ADR003 landing 状态。
2. 已回写 AGENTS/docs README/workflows/changes frontier 的治理口径。
