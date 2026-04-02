# 文档闭环执行套件示例目录 / Examples

**创建日期**：2026-03-27
**最后更新**：2026-04-02
**状态**：draft

本目录用于放置执行套件的最小示例。

当前已提供：

1. `example_change/`：一个完整 child change bundle 样板，现已对齐新版 `plan/acceptance/ai_constraints/design` 结构
2. `example_topic/`：一个 topic index + topic roadmap 样板，展示 `docs/changes_topic/README.md` 与单 topic README 如何分工
3. `example_archive/`：一个归档样板，展示历史文档如何与当前正式口径隔离
4. `example_change_minimal_adoption/`：一个最小接入 5 步的真实 adoption change 样板，可直接在目标项目里作为第一笔试点 change 执行，并附带 AI 执行提示词

注意区分两类目录：

1. `templates/` 是未填充的可复制模板正文。
2. `examples/` 是已经填好示例内容的参考样板。

使用建议：

1. 不要把示例目录直接当正式 change 使用。
2. 先复制 `templates/changes/` 和 `templates/changes_topic/`，再参考 `example_change/` 与 `example_topic/` 填内容。
3. 若目标是“把 harness kit 接入到一个新项目”，优先复制 `example_change_minimal_adoption/`。
4. `example_topic/` 里的 topic index 和 topic roadmap 分别负责不同层级，不要混写。
5. `example_archive/` 必须显式指向当前正式入口，不能只写“已归档”却不给替代路径。
6. 复制后应在目标项目中创建新的真实目录，而不是复用示例路径。

补充：

1. `example_change/plan.md` 与 `example_change/acceptance.md` 现在可直接对照新版模板字段填写。
2. `example_change/design.md` 用来示范“什么时候需要补第四件设计文档”。
3. `example_topic/Example Changes Topic Index.md` 用来示范 topic index，不应误写进单个 topic README。
