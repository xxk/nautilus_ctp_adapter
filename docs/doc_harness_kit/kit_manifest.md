# 文档闭环执行套件清单 / Doc Harness Kit Manifest

**创建日期**：2026-03-27
**最后更新**：2026-03-27
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
| `templates/changes/` | 必选 | child change 模板入口 |
| `templates/changes_topic/` | 标准及以上 | topic 路线图模板入口 |
| `templates/archive/` | 标准及以上 | 归档 / 弃用模板入口 |
| `examples/` | 推荐 | 示例目录与最小样板 |

---

## 二、模板来源策略

当前 bootstrap 版本不复制整套模板正文，而采用“入口文件 + 来源说明”策略：

1. `templates/changes/` 指向当前仓库已验证的 `docs/changes/_template/`
2. `templates/changes_topic/` 先提供约定说明，再在后续版本补正式模板
3. `templates/archive/` 先提供归档头模板说明

这样做的原因：

1. 先把包结构稳定下来
2. 避免过早复制尚未抽象干净的仓库专属字段
3. 等第二版再抽离真正项目无关的模板正文

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
11. `examples/example_change/`
12. `examples/example_topic/`
13. `examples/example_archive/`

后续仍可继续补充：

1. `core/` 下更完整的 project-agnostic 正文抽离
2. 更完整的 example packs
