# 文档闭环执行套件 / Doc Harness Kit

**创建日期**：2026-03-27
**最后更新**：2026-04-03
**状态**：draft
**定位**：把文档模板、验收样板、守卫接入点、校验入口、任务闭环示例与自动化约束机制收敛为可在其他项目复用的最小执行套件。

---

## 一、这是什么

这不是当前仓库全部治理文档的简单复制，而是一套面向跨项目复用的最小执行骨架。

目标是让一个新项目在不照搬本仓目录结构的前提下，也能快速接入：

1. 变更文档三件套
2. topic 路线图治理
3. 守卫脚本接入点与校验入口
4. 任务闭环示例与自动化约束

---

## 二、包内结构

```text
docs/doc_harness_kit/
  README.md
  version.md
  kit_manifest.md
  adoption_guide.md
  跨项目落地手册_Cross Project Rollout.md
  compatibility_profiles.md
  角色与档位说明_Roles and Profiles.md
  core/
  checks/
  templates/
    changes/
    topics/
    archive/
  examples/
```

说明：

1. `README.md`：解释这个包是什么、怎么开始。
2. `version.md`：定义当前 kit 版本与升级口径。
3. `kit_manifest.md`：列出每个文件的职责与必选级别。
4. `adoption_guide.md`：指导新项目如何替换路径、入口与守卫。
5. `跨项目落地手册_Cross Project Rollout.md`：给出跨项目实施时的实际操作顺序。
6. `compatibility_profiles.md`：定义 Lite / Standard / Full 三档接入方式。
7. `角色与档位说明_Roles and Profiles.md`：解释谁负责接入、维护、执行与验收。
8. `core/`：沉淀项目无关的第一批治理正文。
9. `checks/`：提供最小守卫规范、接入检查清单与统一 runbook。
  当前还包括 topic 切换治理清单：`checks/topic-transition-checklist.md`
10. `templates/`：提供可直接复制的 child change bundle、topic index、topic roadmap 与 archive 模板。
11. `examples/`：展示一个新项目第一次接入时应长什么样，以及模板复制后的真实填法。

---

## 三、当前版本边界

当前版本已经从“只给入口指针”推进到“骨架 + 可复制模板正文”，但暂不追求：

1. 直接复制后零配置可用
2. 提供完整脚本守卫实现
3. 替代当前仓库内的正式治理规范

当前策略是：

1. 先提供骨架与接入说明
2. 把当前仓库已稳定的 child/topic 模板同步进 `templates/`
3. 再逐步把当前仓库中的通用规范提炼到 `core/`
4. 最后再补齐通用脚本守卫与检查入口

当前第二阶段已开始补：

1. 版本口径
2. kit 自检 runbook

当前第三阶段已启动：

1. `core/` 第一批 project-agnostic 正文
2. `checks/` 中的首批 guard 接入映射
3. `templates/changes/` 下的四件套正文同步
4. `templates/topics/` 下的索引模板与 roadmap 模板同步，并与 `docs/topics/README.md`、`docs/topics/<topic-id>.md` 保持同次收敛

---

## 四、如何开始

建议新项目按以下顺序接入：

1. 先读 `compatibility_profiles.md`，选择 Lite / Standard / Full 档位。
2. 再读 `角色与档位说明_Roles and Profiles.md`，明确谁负责维护、执行与验收。
3. 再读 `core/README.md` 与第一批 core 正文，确认项目无关规则。
4. 再读 `adoption_guide.md`，替换项目路径、入口地图与验证命令。
5. 再读 `跨项目最小接入5步法_Minimal 5-Step Adoption.md`，优先按最短接入路径推进。
6. 再按 `跨项目落地手册_Cross Project Rollout.md` 执行跨项目落地步骤。
7. 根据 `kit_manifest.md` 优先复制 `templates/changes/` 与 `templates/topics/` 的模板正文，再补充其余文档。
8. 至少建立一个真实 `change bundle` 作为接入试点。

---

## 五、命名规则

为避免套件升级时把历史证据链搅乱，默认采用下面这条命名策略：

1. 新增目录、README、导航入口、方案标题，统一使用 `doc_harness_kit` / `Doc Harness Kit`。
2. 已经落库、已留证、已被引用的历史 `change-id`，默认不强制回改。
3. 如果历史 `change-id` 仍保留 `doc-governance-kit-*`，应在正文标题、范围、长期归宿或说明文字中明确它对应的当前展示名是 `Doc Harness Kit`。
4. 对外沟通、导航索引、长期方案文档，默认只继续使用 `Doc Harness Kit`，不要新建第二套 `Doc Governance Kit` 口径。

一句话原则：**展示名统一向前收敛，证据链标识保持稳定。**

---

## 六、当前来源

本套件来自当前仓库已经验证有效的文档治理体系，尤其包括：

1. `docs/architecture/文档治理/OpenSpec-lite文档驱动开发评审方案.md`
2. `docs/architecture/文档治理/ATDD-lite验收测试驱动开发规范.md`
3. `docs/architecture/文档治理/BDD-lite开发规范.md`
4. `docs/architecture/文档治理/系统代码分析知识沉淀规范.md`
5. `docs/architecture/文档治理/高风险变更实现契约锚点规范.md`
6. `docs/changes/_template/` 四件套模板
7. `docs/topics/README.md` 与已落库 topic roadmap 的稳定结构

这些文档目前仍是本仓正式口径；执行套件骨架是面向复用化的整理层，不替代原文。

新增同步规则：

1. `docs/changes/_template/` 是当前仓库本地执行模板源。
2. `docs/doc_harness_kit/templates/changes/` 是跨项目复用模板源。
3. 以后若本地 child change 模板字段发生稳定变更，应在同一次变更中同步更新这两个位置。
4. `docs/topics/README.md` 与 `docs/topics/<topic-id>.md` 是当前仓库 topic 治理的正式来源。
5. `docs/doc_harness_kit/templates/topics/` 与 `examples/example_topic/` 必须和正式来源同次同步，避免 harness kit 再次退化成“只有入口、没有正文”的指针包。
