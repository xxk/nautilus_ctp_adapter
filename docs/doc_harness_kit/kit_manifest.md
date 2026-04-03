# 文档闭环执行套件清单 / Doc Harness Kit Manifest

**创建日期**：2026-03-27
**最后更新**：2026-04-03
**状态**：draft

---

## 一、清单总览

| 文件/目录 | 级别 | 作用 |
| --- | --- | --- |
| `README.md` | 必选 | 包入口与使用顺序 |
| `version.md` | 推荐 | kit 当前版本与升级口径 |
| `kit_manifest.md` | 必选 | 包内职责清单 |
| `adoption_guide.md` | 必选 | 指导新项目完成第一次接入 |
| `compatibility_profiles.md` | 必选 | 定义不同接入档位 |
| `角色与档位说明_Roles and Profiles.md` | 推荐 | 定义不同角色的最小职责边界 |
| `core/` | 推荐 | 沉淀项目无关的治理正文 |
| `checks/` | 标准及以上 | 最小守卫规范与接入检查清单 |
| `templates/changes/` | 必选 | child change 四件套可复制模板 |
| `templates/topics/` | 标准及以上 | topic 索引模板与 roadmap 可复制模板 |
| `templates/archive/` | 标准及以上 | 归档 / 弃用模板入口 |
| `examples/` | 推荐 | 示例目录与最小样板 |

---

## 二、模板同步策略

当前版本不再停留在“入口文件 + 来源说明”，而采用“双源同步”策略：

1. `templates/changes/` 同步当前仓库已验证的 `docs/changes/_template/` 四件套正文
2. `templates/topics/` 同步 topic index 与 topic roadmap 的稳定结构模板
3. `templates/archive/` 继续保留归档入口模板

同步原则：

1. 当前仓库本地执行模板更新时，应同步更新 harness kit 对应模板。
2. 允许模板中保留占位符、字段说明与结构性注释，但不得保留来源仓私有绝对路径。
3. 示例目录负责展示“填完以后是什么样”，模板目录负责展示“复制前的最小正文骨架”。

---

## 三、接入最低要求

任何项目若要宣称“已接入本套件”，最低必须满足：

1. 有一个入口地图文件
2. 有一套可用的 change bundle 模板
3. 有一份 adoption checklist
4. 有至少一个真实 change 的试点闭环

---

## 四、后续扩展位

当前已提供：

1. `version.md`
2. `角色与档位说明_Roles and Profiles.md`
3. `core/README.md`
4. `core/最小变更闭环模型_Minimal Change Loop.md`
5. `core/验收场景写法_Acceptance Scenario Writing.md`
6. `core/分析结论回写规则_Analysis Writeback Rules.md`
7. `checks/最小守卫规范_Minimal Guardrails.md`
8. `checks/接入检查清单_Adoption Checklist.md`
9. `checks/任务类型到验证入口速查表_Task Verification Matrix.md`
10. `checks/运行手册_Runbook.md`
11. `templates/changes/plan.md`
12. `templates/changes/acceptance.md`
13. `templates/changes/ai_constraints.md`
14. `templates/changes/design.md`
15. `templates/topics/索引模板_Topic Index Template.md`
16. `templates/topics/主题路线图模板_Topic Roadmap Template.md`
17. `examples/example_change/`
18. `examples/example_topic/`
19. `examples/example_archive/`
20. `examples/example_change/design.md`
21. `examples/example_topic/Example Topic Index.md`
22. `examples/example_topic/README.md`

后续仍可继续补充：

1. `core/` 下更完整的 project-agnostic 正文抽离
2. 更完整的 example packs
