---
change-id: "20260410__repo-governance-hardening__dslresearch-frontier-alignment"
dependencies:
  hard_blocking:
    - id: "20260402__governance-harness__check-topic-docs-script"
      reason: "当前 change 以既有 topic docs gate 为基础继续增强 frontier 治理能力。"
      expected_status: completed
    - id: "20260402__governance-harness__changes-topic-index-upgrade"
      reason: "当前 change 需要在现有 topic index 基础上切换为 registry 驱动。"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# DSLResearch Frontier Alignment 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-10
**更新日期**：2026-04-10
**范围**：`AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`docs/topics/`、`scripts/`、`src/nautilus_ctp_adapter/devtools/`、`tests/`
**topic-id**：repo-governance-hardening
**change-id**：20260410__repo-governance-hardening__dslresearch-frontier-alignment
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 让 `nautilus_ctp_adapter` 的 topic/change 推进能力向 `DSLReserach` 对齐，不再只靠手写 README 维持 current frontier。
2. 补齐 machine-readable topic state、topic index sync、current frontier CLI 与一键 governance check。
3. 让 `AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`docs/topics/README.md` 统一消费同一套 formal state。
4. 用本地可执行脚本和测试锁定上述治理能力，防止后续再漂移。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-topic-frontier-governance
- capability_name: Topic / Change Frontier Governance Alignment
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/repo-governance-hardening.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/AGENTS.md ; /D:/Nautilus/nautilus_ctp_adapter/docs/README.md ; /D:/Nautilus/nautilus_ctp_adapter/docs/changes/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/devtools/topic_governance.py
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：`AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`docs/topics/`、`scripts/`、`src/nautilus_ctp_adapter/devtools/`、`tests/`、当前 change bundle。
2. 禁止修改：`src/nautilus_ctp_adapter/adapters/ctp/`、`src/nautilus_ctp_adapter/runtime/`、`vendor/`、任何真实交易配置与 live-send 入口。
3. 当前正式入口：`python scripts/show_current_frontier.py --root .`、`python scripts/sync_topic_index.py --root . --check`、`python scripts/check_topic_docs.py --root .`、`python scripts/check_topic_governance.py --root .`。
4. AI 开始前必须阅读：`AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`docs/topics/README.md`、`docs/topics/repo-governance-hardening.md`。
5. 改完后必须执行：`python scripts/sync_topic_index.py --root .`、`python scripts/check_topic_docs.py --root .`、`python scripts/show_current_frontier.py --root .`、`python scripts/check_topic_governance.py --root .`、`python -m pytest tests/test_topic_governance.py -q`。

## 四、背景与约束

1. 仓内原有治理能力能检查 topic README 字段是否齐全，但没有 machine-readable topic state，也没有 registry 驱动的 current frontier 入口。
2. 当前仓同时存在 `live-session-order-query-hardening` 与 `live-ops-truth-snapshot` 两条未完全闭合的 topic；如果没有 formal state，很难机械判断哪条才是 active lane、哪条只是 parked blocker。
3. 这次目标是对齐 `DSLReserach` 的推进能力，不是完整复制其全部 devtools 层。

## 五、设计方案

1. 新增 `docs/topics/主题状态注册表_Topic State Registry.yaml` 作为 machine-readable topic 状态源。
2. 新增 `src/nautilus_ctp_adapter/devtools/topic_governance.py`，集中实现 registry 解析、roadmap queue 解析、topic index 渲染、frontier 汇总和 repo sync 审计。
3. 新增脚本入口 `scripts/sync_topic_index.py`、`scripts/show_current_frontier.py`、`scripts/check_topic_governance.py`，并把 `scripts/check_topic_docs.py` 切换到同一模块。
4. 更新 `AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`docs/topics/README.md` 和相关 roadmap，使 current frontier 统一由 registry 驱动。

## 六、阶段划分

1. P1：补 topic registry 和 devtools 正式实现。
2. P2：补 CLI 入口并更新 docs/AGENTS 的 frontier 规则。
3. P3：同步 topic index，并把 blocked topic 与 active topic 收口到统一状态。
4. P4：补测试与 change bundle 验收记录。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 新增 registry 与 governance devtools | 用户需求 | `docs/topics/主题状态注册表_Topic State Registry.yaml`、`src/nautilus_ctp_adapter/devtools/topic_governance.py` | formal state + 同步逻辑 | `python scripts/sync_topic_index.py --root .` | `docs/topics/README.md` | topic frontier 可由脚本生成 | 已完成 |
| P2 | 新增 frontier / governance CLI 并切换 topic docs gate | 用户需求 | `scripts/show_current_frontier.py`、`scripts/sync_topic_index.py`、`scripts/check_topic_governance.py`、`scripts/check_topic_docs.py` | 统一 CLI 入口 | `python scripts/check_topic_docs.py --root .` | `AGENTS.md`、`docs/README.md` | active topic/change 可由机器读取且守卫通过 | 已完成 |
| P3 | 同步 docs 与 roadmap 状态 | 用户需求 | `AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、相关 roadmap | registry 驱动的 current frontier 文档 | `python scripts/check_topic_governance.py --root .` | `repo-governance-hardening` topic README | docs 不再靠手工描述维持 frontier | 已完成 |
| P4 | 补测试和 change 留证 | 工程质量 | `tests/test_topic_governance.py`、当前 change bundle | regression lock + 验收留证 | `python -m pytest tests/test_topic_governance.py -q` | 当前 change bundle | 后续改动会被测试与文档守卫同时锁定 | 已完成 |

## 八、验证动作

```powershell
python scripts/sync_topic_index.py --root .
python scripts/check_topic_docs.py --root .
python scripts/show_current_frontier.py --root .
python scripts/check_topic_governance.py --root .
python -m pytest tests/test_topic_governance.py -q
```

## 九、完成定义

### 开发完成

1. registry、sync、frontier、governance check 都已落地。
2. docs 和 AGENTS 已切到同一套 formal state。
3. blocked topic 与 active topic 已能被脚本正确区分。

### 交付完成

1. `acceptance.md` 中阻塞场景全部通过。
2. 本地验证命令全部通过。
3. 长期治理规则已回写到 topic README、AGENTS 和 docs 索引。

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

1. 新增 machine-readable topic state registry，作为 current frontier 的唯一状态主来源。
2. 新增 `sync_topic_index.py`，规定 `docs/topics/README.md` 不再手工维护。
3. 新增 `show_current_frontier.py` 与 `check_topic_governance.py`，把“当前该继续哪个 topic/change”收口成正式入口。

## 十一、回写与相关变更 / Write-back & Related Changes

1. 已回写 `repo-governance-hardening` topic README，新增 C6 记录本次治理增强。
2. 已回写 `AGENTS.md`、`docs/README.md`、`docs/changes/README.md`，统一使用 registry 驱动的 frontier 口径。

## 十二、阻塞项

本 change 无外部阻塞；全部验证可在本地完成。

## 十三、进度记录

1. 2026-04-10：新增 topic state registry，并把 `live-ops-truth-snapshot` 从自由文本“挂起”显式收口为 `blocked`。
2. 2026-04-10：新增 `topic_governance.py`、`sync_topic_index.py`、`show_current_frontier.py`、`check_topic_governance.py`，让 current frontier 可以被脚本化读取与校验。
3. 2026-04-10：新增 `tests/test_topic_governance.py`，锁定 sync/frontier/docs gate 行为。
