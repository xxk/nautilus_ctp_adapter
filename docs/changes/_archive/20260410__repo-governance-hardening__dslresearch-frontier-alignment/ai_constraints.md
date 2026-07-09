# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260410__repo-governance-hardening__dslresearch-frontier-alignment
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 在仓库内工作时，必须先读取 sibling `acceptance.md` 与 `plan.md`。
2. 若任务涉及 current frontier，必须同时读取 `docs/topics/主题状态注册表_Topic State Registry.yaml` 与 `docs/topics/README.md`。

## 方法论 / Working Mode

1. 以 registry 为唯一 machine-readable frontier 来源。
2. `docs/topics/README.md` 必须通过 `sync_topic_index.py` 生成，不得手工直接维护。
3. docs/AGENTS/change index 的 current frontier 描述，必须与 registry 和 topic index 保持一致。

## 启动步骤 / Kickoff

1. 先读 `acceptance.md`
2. 再读 `plan.md`
3. 再确认 `docs/topics/主题状态注册表_Topic State Registry.yaml`
4. 最后执行 `python scripts/show_current_frontier.py --root .`

## 每轮迭代 / Per-Round

1. 一次只处理一个 frontier 漂移来源。
2. 改完 registry 或 roadmap 后，必须重新执行 `python scripts/sync_topic_index.py --root .`。
3. 改完 docs/AGENTS 后，必须重新执行 `python scripts/check_topic_docs.py --root .`。

## 边界 / Boundaries

1. 不允许修改业务实现、live trading 入口或真实账户配置。
2. 不允许跳过 registry，直接在 `docs/topics/README.md` 中手工改 active topic/change。
3. 不允许用测试结果替代 CLI frontier 验收。

## 状态管理 / Status

1. `acceptance.md` 中的 `AI-STATUS` YAML 是唯一 AI 执行状态源。
2. `repo-governance-hardening` topic README 中的 C6 状态必须与本 change 实际状态一致。

## 收尾 / Wrap-up

1. 收尾前必须确认 `AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`docs/topics/README.md` 已全部同步。
2. 若 frontier 状态变化，必须先更新 registry，再同步其他索引文档。
