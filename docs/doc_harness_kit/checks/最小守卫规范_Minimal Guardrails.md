# 最小守卫规范 / Minimal Guardrails

**创建日期**：2026-03-27
**最后更新**：2026-04-02
**状态**：draft
**用途**：定义一个项目接入 `Doc Harness Kit` 后，最低限度必须具备的机械守卫，避免套件只停留在“有文档、无约束”。

---

## 一、适用目标

这份规范只回答一个问题：

**一个项目最少要把哪些约束机械化，才算真正接入了 harness engineering 的最小闭环。**

---

## 二、最低守卫集合

最低应具备 5 类守卫：

1. 目录守卫
2. 模板守卫
3. 验证守卫
4. 导航守卫
5. Topic 切换守卫

这 5 类里，只要缺任何一类，AI 就容易重新退回"靠聊天记忆协作"的状态。

---

## 三、守卫定义

### 1. 目录守卫

必须回答：

1. 新功能该放哪里
2. 临时产物该放哪里
3. 哪些目录禁止承载正式实现

最低要求：

1. 仓库存在目录职责说明
2. AI 能从入口文档找到正式实现落点
3. 临时输出有统一目录，不允许散落根目录

### 2. 模板守卫

必须回答：

1. 哪类任务必须建立 `change bundle`
2. `plan.md`、`acceptance.md`、`ai_constraints.md` 是否完整
3. topic 与 change 是否分层

最低要求：

1. 仓库存在至少一套可复制的 change 模板
2. topic roadmap 与 child change 不混层
3. 重大变更可以被模板化留证

### 3. 验证守卫

必须回答：

1. 改完后必须跑什么验证
2. 哪些验证是当前层必须通过的
3. 失败后停在哪里

最低要求：

1. 至少存在一个静态检查或结构检查入口
2. 至少存在一个任务完成后的验证入口
3. 文档里能明确找到“本任务该跑什么”

推荐配套文档：

1. `任务类型到验证入口速查表_Task Verification Matrix.md`

### 4. 导航守卫

必须回答：

1. 当前正式入口是什么
2. 当前正式规范在哪里
3. 历史文档如何与当前口径隔离

最低要求：

1. 存在仓库级导航主入口
2. 存在正式入口说明
3. 历史归档文档有明确标记，不与活跃文档平级冒充正式口径

### 5. Topic 切换守卫

必须回答：

1. 当前活动 topic 是哪个
2. topic 切换时哪些地方必须同步更新
3. AI 如何机械验证 topic README 健康状态

最低要求：

1. `AGENTS.md` 存在指向当前活动 topic 的显式链接
2. `docs/topics/README.md` 存在 `## Current State` 节，列出当前活动 topic 和 active change
3. Topic README 的 Change 表包含 `状态` 列，AI 能无歧义扫描进度
4. 存在可运行的 topic 文档门禁脚本（如 `check_topic_docs.py`），或等效机械校验

---

## 四、接入完成判定

若一个项目要宣称"已接入最小守卫"，至少同时满足：

1. AI 能找到目录职责与正式入口
2. AI 能找到 change 模板
3. AI 能找到验证入口
4. 人能判断历史文档与当前正式口径的区别
5. AI 能在不依赖聊天记忆的情况下找到当前活动 topic 和 active change

---

## 五、实施建议

推荐顺序：

1. 先建导航守卫
2. 再建模板守卫
3. 再补验证守卫
4. 再建 topic 切换守卫（多 topic 项目必须）
5. 最后补更细的风格或反模式守卫

原因：

1. 没有导航，AI 找不到入口
2. 没有模板，任务无法稳定留证
3. 没有验证，AI 无法证明自己做对
4. 没有 topic 切换守卫，入口随时间陈旧，AI 下次从错误起点出发
5. 风格守卫再严格，也替代不了前面四类基础守卫

---

## 六、DSLResearch 首批 Guard 接入映射

对 `DSLResearch`，当前首批正式 guard 已收敛为 5 类：

1. `Schema Guard / 对象边界守卫`
   - 长期口径：`docs/architecture/核心Run与Artifact_Schema冻结稿.md`
   - 最小锁定：`tests/test_composite_runs.py`、`tests/test_portfolio_analytics_pipeline.py`

2. `Smoke Guard / 正式入口守卫`
   - 长期口径：`docs/doc_harness_kit/checks/任务类型到验证入口速查表_Task Verification Matrix.md`
   - 最小锁定：`python scripts/check_harness.py --root .`

3. `Layer Guard / 分层边界守卫`
   - 长期口径：`docs/architecture/四层架构LayerRule冻结稿.md`
   - 最小锁定：`tests/test_layer_contracts.py`

4. `Fail-fast Guard / 红线拒绝守卫`
   - 长期口径：`docs/architecture/投资组合分析_业绩归因_风险暴露_压力测试设计.md`
   - 最小锁定：`dslresearch/contracts/composite_runs.py`、`dslresearch/contracts/portfolio_analytics_run.py`

5. `Harness Integration / 套件接入口`
   - 长期口径：`docs/architecture/Harness实施路线图_代码约束分阶段接入.md`
   - 最小锁定：`python scripts/check_harness.py --root .`

接入完成的最低判定：

1. guard 在仓库中有正式文档落点
2. guard 有最小机械锁定或最小检查入口
3. change / topic / architecture / harness check 能互相回链
