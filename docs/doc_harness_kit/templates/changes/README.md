# Change 模板入口 / Change Template Entry

**创建日期**：2026-03-27
**最后更新**：2026-04-02
**状态**：draft

本目录现在直接提供可复制的 child change 模板正文。

建议复制顺序：

1. `plan.md`
2. `acceptance.md`
3. `ai_constraints.md`
4. `design.md`（仅当 change 复杂度达到门槛时再复制）

同步约定：

1. 若项目发生“当前展示名已调整，但历史 `change-id` 仍需保留”的情况，应在 `plan.md` 与 `acceptance.md` 头部使用 `当前展示名 / Current Display Name` 字段显式收口。
2. `change-id` 视为证据锚点，不为了展示一致性批量回改；展示名称与导航口径统一向当前正式名称收敛。
3. 当前仓库若更新 `docs/changes/_template/`，应同步更新本目录对应文件，保持跨项目模板与本地执行模板一致。

当前提供文件：

1. `plan.md`
2. `acceptance.md`
3. `ai_constraints.md`
4. `design.md`

后续目标：

1. 从当前仓库模板中抽离项目无关字段
2. 形成可直接复制到其他仓库的通用版本
