# 文档闭环执行套件示例目录 / Examples

**创建日期**：2026-03-27
**最后更新**：2026-03-27
**状态**：draft

本目录用于放置执行套件的最小示例。

当前已提供：

1. `example_change/`：一个完整 child change 三件套样板，适合作为跨项目接入后的第一个试点 change
2. `example_topic/`：一个 topic roadmap 样板，展示 phase、child change 顺序与 topic 级出口条件
3. `example_archive/`：一个归档样板，展示历史文档如何与当前正式口径隔离
4. `example_change_minimal_adoption/`：一个最小接入 5 步的真实 adoption change 样板，可直接在目标项目里作为第一笔试点 change 执行，并附带 AI 执行提示词

使用建议：

1. 不要把示例目录直接当正式 change 使用。
2. 先复制 `example_change/`，再替换 `change-id`、`topic-id`、路径、命令和长期归宿。
3. 若目标是“把 harness kit 接入到一个新项目”，优先复制 `example_change_minimal_adoption/`。
4. `example_topic/` 只保留 phase / topic 级粗粒度进度，不要把它写成 task 燃尽图。
5. `example_archive/` 必须显式指向当前正式入口，不能只写“已归档”却不给替代路径。
6. 复制后应在目标项目中创建新的真实目录，而不是复用示例路径。
