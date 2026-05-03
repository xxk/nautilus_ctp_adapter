# DSLResearch Frontier Alignment 设计

**状态**：已采纳
**日期**：2026-04-10
**范围**：`docs/topics/`、`AGENTS.md`、`docs/README.md`、`docs/changes/README.md`、`scripts/`、`src/nautilus_ctp_adapter/devtools/`、`tests/`
**关联 plan**：./plan.md

## 一、现状

现有仓库已经有 topic README、child change bundle 和最小的 `check_topic_docs.py`，但仍有三个结构性缺口：

1. 没有 machine-readable topic state，AI 只能读自由文本判断 active topic。
2. `docs/topics/README.md` 依赖手工维护，容易与 roadmap 和 docs 索引漂移。
3. 缺少 `show_current_frontier.py` 这类单命令入口，无法像 DSLResearch 一样快速进入当前 formal lane。

## 二、正式入口与实现落点

1. 正式实现落点：`src/nautilus_ctp_adapter/devtools/topic_governance.py`
2. 正式 CLI 入口：
   - `scripts/sync_topic_index.py`
   - `scripts/show_current_frontier.py`
   - `scripts/check_topic_docs.py`
   - `scripts/check_topic_governance.py`
3. 正式状态文件：`docs/topics/主题状态注册表_Topic State Registry.yaml`
4. 正式人读投影：`docs/topics/README.md`

## 三、设计方案

推荐方案是“最小完整迁移”，而不是整包复制 DSLResearch devtools：

1. 引入 topic state registry，但只实现当前仓需要的字段：`canonical_status` 与 `execution_order`。
2. 在单个模块里集中实现 registry 解析、roadmap queue 解析、topic index 渲染、frontier 汇总和 repo sync 审计，减少文件数量与迁移成本。
3. 通过 `sync_topic_index.py` 统一生成 `docs/topics/README.md`，把 README 从手工维护切到投影文件。
4. 通过 `show_current_frontier.py` 输出 active topic/change、parked topics 和 completed topic 计数，让 AI 和人工都能一条命令看懂当前前线。
5. 通过 `check_topic_governance.py` 把 sync 与 docs gate 合并成一键验证入口。

## 四、接口与输入输出

1. Registry 输入：`docs/topics/主题状态注册表_Topic State Registry.yaml`
2. Topic index 输出：`docs/topics/README.md`
3. Frontier CLI 输出：
   - `CURRENT_FRONTIER_OK`
   - `ACTIVE_TOPIC`
   - `ACTIVE_CHANGE`
   - `QUEUED_TOPIC`（如有）
   - `PARKED_TOPIC`（如有）
4. Governance CLI 输出：`TOPIC_GOVERNANCE_CHECK_OK` 或 `TOPIC_GOVERNANCE_CHECK_FAILED`

## 五、AI 实现约束

1. 不引入新的 fallback 状态源；registry 缺失或非法时直接失败。
2. 不保留“手写 topic index 也可接受”的旁路。
3. blocked topic 必须显式建模为 `blocked`，不能继续用“进行中但当前挂起”替代 formal state。

## 六、备选方案

备选方案是“直接搬运 DSLResearch 全部 devtools 模块”。

不选原因：

1. 当前仓没有 `change_docs_gate.py`、`harness_check.py` 等完整依赖链，整包迁移会显著扩大范围。
2. 用户当前目标是对齐 topic/change 推进能力，不是完整复刻 DSLResearch 内部治理体系。
3. 单模块最小实现已经能满足 registry、sync、frontier、docs gate 和 tests 的核心需求。

## 七、风险与影响面

1. 若 roadmap queue 表头格式继续漂移，queue 解析需要同步维护。
2. 若 registry 与 roadmap 状态分离，新的 docs gate 会直接 fail fast。
3. 本次只改变治理入口，不触碰业务实现，因此功能侧回归风险低。

## 八、发布回滚与退出策略

1. 若后续发现单模块实现不够用，可再拆成 `topic_index_sync.py`、`current_frontier.py`、`topic_docs_gate.py` 等多个模块。
2. 回滚时必须同时移除 registry、脚本入口和 docs/AGENTS 相关规则，不能只删某一部分。

## 九、需要沉淀为长期规则的内容

1. topic registry 是 current frontier 的唯一 machine-readable 状态源。
2. `docs/topics/README.md` 必须由脚本同步，不再手工维护。
3. frontier 切换时必须同步 registry、topic index、docs/README、docs/changes/README 和 AGENTS。
