# 项目入口治理 / Project Entrypoint Governance

**创建日期**：2026-03-27
**最后更新**：2026-04-02
**状态**：进行中
**进度**：40%
**topic-id**：project-entry
**用途**：用一个独立 topic 把“多个历史运行入口并存”的问题收口成唯一正式入口、清晰导航和稳定验证口径。

> 这是已经按 `templates/topics/主题路线图模板_Topic Roadmap Template.md` 填完后的示例。

## 一、为什么这个 topic 应该优先

1. 项目当前存在多个历史入口，AI 和开发者都容易改错主落点。
2. 入口不收口，后续任何 runbook、测试命令和 docs 首页都容易继续漂移。
3. 这个问题适合作为独立 topic 推进，因为它需要连续几笔 child change 才能真正收口。

## 二、主题目标

1. 冻结唯一正式运行入口。
2. 明确兼容入口的保留、弃用或转发策略。
3. 把入口导航回写到 docs 首页和长期 architecture 文档。

## 三、边界与限制（可选）

1. 允许改入口文档、入口脚本和导航索引。
2. 不允许顺手改与入口无关的业务逻辑。
3. 不允许保留多个“临时正式入口”长期并存。

## 四、进入条件

1. 当前项目已经识别出所有现存入口。
2. 团队接受“只能保留一个正式入口”的治理目标。

## 五、Topic 级出口条件

1. 项目只有一个正式运行入口。
2. docs 首页、AGENTS 或 developer guide 都指向同一个正式入口。
3. 至少有一笔真实 child change 留证说明这次收口是如何完成的。
4. 兼容入口的行为不再和正式入口竞争。

## 六、预期 Child Change 顺序

> **状态标记**：✅ 已完成 | 🔄 进行中 | ⬜ 未开始

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260327__project-entry__unified-run-entrypoint` | 冻结唯一正式入口与兼容入口口径 | 🔄 进行中 |
| C2 | `20260328__project-entry__compat-entrypoint-cleanup` | 收口兼容入口并清理导航漂移 | ⬜ 未开始 |
| C3 | `20260329__project-entry__runbook-and-verify-sync` | 同步 runbook、验证命令和 docs 首页入口 | ⬜ 未开始 |

## 七、AI-TASK-QUEUE

**当前状态**：已激活；当前聚焦 `C1`。

- [x] 创建 `C1` child change bundle
- [ ] 完成 `C1`
- [ ] 完成 `C2 -> C3`
- [ ] 回写 docs 首页与长期入口文档

**当前 first action**：推进 `20260327__project-entry__unified-run-entrypoint`

## 八、成功信号

1. 正式入口帮助命令稳定可执行。
2. 兼容入口输出明确写出新的正式入口或弃用信息。
3. docs 首页与长期 architecture 文档不再出现 competing entrypoint。

## 九、与主线或其他 Topic 的关系（可选）

1. 这是一个 project governance topic，不直接承载业务能力。
2. 它完成后会降低后续业务 topic 的 AI 改错落点成本。
