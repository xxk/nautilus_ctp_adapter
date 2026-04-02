# 执行提示词 / Execution Prompt

**创建日期**：2026-03-27
**最后更新**：2026-03-27
**状态**：draft
**用途**：给目标项目中的 AI 一段可直接粘贴使用的执行提示词，让它按 `example_change_minimal_adoption` 这套 change bundle 去完成最小接入闭环。

---

## 一、使用方式

在目标项目中先完成两件事：

1. 把 `docs/doc_harness_kit/` 复制到目标项目。
2. 把 `example_change_minimal_adoption/` 复制成目标项目自己的真实 change 目录，并替换 `change-id`、`topic-id`、路径、入口名和验证命令。

然后把下面这段提示词交给 AI。

---

## 二、可直接使用的提示词

```text
请执行当前 change bundle，对目标项目完成 Doc Harness Kit 的最小接入闭环。

执行要求：
1. 先读当前 change 目录下的 acceptance.md，再读 plan.md，再读 ai_constraints.md。
2. 严格按 change bundle 的范围执行，不要扩展到无关业务功能。
3. 目标不是实现业务需求，而是完成 harness 最小接入 5 步：
   - 落地 docs/doc_harness_kit/
   - 建立入口地图
   - 建立 docs/changes/ 模板落点
   - 替换真实验证入口
   - 让当前 change 自身成为第一个真实试点 change
4. 若正式入口、验证入口或模板落点不明确，先补文档或导航，不要跳过。
5. 不允许把“目录已经复制”直接当成接入完成。
6. 不允许保留示例仓命令占位；必须替换为当前项目真实命令或在文档中明确写出真实替换方式。
7. test、mock、fake 不能作为正式验收证据；若当前只有这些结果，必须回填到“待办”或“锁定证据”区，而不是直接宣告通过。
8. 需要把执行结果回填到 acceptance.md 的场景、出口条件和证据区。
9. 完成后请明确回答：
   - 当前项目是否已经完成最小接入 5 步
   - 当前 change 是否已经成为第一个真实试点 change
   - 还缺哪些阻塞项

输出要求：
1. findings / blockers 优先
2. 结论必须基于已执行证据，不要基于推测宣告完成
3. 若未完成，请指出卡在 A1-A5 的哪一步
```

---

## 三、推荐附加说明

如果你要进一步降低 AI 跑偏概率，建议在同一条消息里再补 3 个事实：

1. 当前项目的正式入口文件路径
2. 当前项目的最低验证命令
3. 当前项目里应该放入口地图和 change 模板的正式目录

---

## 四、什么时候这段提示词算成功

成功信号不是“AI 开始执行了”，而是：

1. 当前 change 的 acceptance.md 已有真实 evidence
2. A1-A5 的阻塞场景都被逐项判断
3. AI 能回答“当前 change 是否已成为第一个真实试点 change”
