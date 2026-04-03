---
change-id: "20260401__ctp-live-connectivity__nautilus-live-smoke-baseline"
dependencies:
  hard_blocking:
    - id: "20260401__ctp-live-connectivity__td-auth-and-login-readiness"
      reason: "需要先明确 TD readiness，再建立 Nautilus 方向正式 smoke 基线"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Nautilus 实盘 Smoke 基线 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-01
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`scripts/`、当前 change 三件套
**topic-id**：ctp-live-connectivity
**change-id**：20260401__ctp-live-connectivity__nautilus-live-smoke-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

本 change 要给 Nautilus 方向建立正式 smoke 基线：明确最小入口、最小配置、最小成功信号和证据包格式。当前不做完整 Topic 3/4 的正式实现，只解决“后续所有实盘接线都以哪条 smoke 口径为准”。

## 二、能力映射 / Capability Mapping

```text
- capability_id: nautilus-live-smoke-baseline
- capability_name: Nautilus 实盘 smoke 基线 / Nautilus live smoke baseline
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/ctp-live-connectivity/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：adapter smoke 入口、当前 change 三件套、必要的脚本或 README。
2. 禁止修改：超出 smoke baseline 所需的完整市场或交易适配实现。
3. 改完后至少执行：`python -m pytest` 与 smoke baseline 自身的最小验证。

## 四、已冻结的 baseline 口径

1. 正式入口：`python scripts\ctp_nautilus_live_smoke.py --config <path>`
2. 入口必须走 `build_ctp_stack(...)`、共享 runtime bridge、仓内本地 `c wrapper`
3. 正式成功信号必须同时覆盖 `MD tick`、`TD readiness`、`bridge events`
4. `ctp_md_login_smoke.py` 与 `ctp_td_login_smoke.py` 是 diagnostics，不是正式 baseline

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 Nautilus smoke 最小入口 | topic C5 | `scripts/`、README、当前 change 三件套 | 正式 smoke 入口定义 | 文档检查 | topic roadmap | 后续 topic 不再自定义 smoke 口径 | 已完成 |
| P2 | 冻结最小成功信号与证据格式 | acceptance | 当前 change 三件套 | 统一 evidence 结构 | 最小 smoke | docs index | 后续可直接复用 | 已完成 |
| P3 | 回写 topic 结论 | governance | topic roadmap | Topic 1 收尾条件 | 文档检查 | mainline roadmap | Topic 2 可开始 | 已完成 |

## 八、执行结果

1. 新增正式 baseline 入口：`/D:/Nautilus/nautilus_ctp_adapter/scripts/ctp_nautilus_live_smoke.py`
2. `factory` 已明确让 `data_client` 与 `execution_client` 共享同一个 runtime bridge
3. `execution_client` 已具备最小 TD readiness smoke 能力
4. 正式 baseline 已实测拿到 `rb2610` tick、TD login success、settlement confirmed

## 九、验证记录

1. `python scripts\ctp_nautilus_live_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --md-timeout-seconds 20 --td-timeout-seconds 20`
2. `python -m pytest`

## 十、证据

1. `./evidence_20260402_nautilus_live_smoke_baseline.md`
