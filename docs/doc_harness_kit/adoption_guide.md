# 文档闭环执行套件接入指南 / Adoption Guide

**创建日期**：2026-03-27
**最后更新**：2026-04-03
**状态**：draft

---

## 一、目标

本指南只回答一个问题：

**一个新项目第一次接入文档闭环执行套件时，最少需要做哪些替换和确认。**

---

## 二、接入步骤

> 若需要按时间顺序执行，而不是只看规则摘要，直接配合 `跨项目落地手册_Cross Project Rollout.md` 使用；本文偏“替换与确认项”，落地手册偏“实际操作顺序”。

### Step 1：确认项目是否真的需要这套包

适合：

1. 需要 AI 长期协作的仓库
2. 有中高风险改动需要留证和验收的仓库
3. 需要 topic / change 分层治理的仓库

不适合：

1. 一次性脚本仓
2. 几乎没有长期维护需求的 demo 仓
3. 没有任何文档治理意愿的极小项目

### Step 2：选择接入档位

先在 `compatibility_profiles.md` 里选择 Lite / Standard / Full。

然后在 `角色与档位说明_Roles and Profiles.md` 里明确：

1. 谁是 Owner
2. 谁是 Maintainer
3. 谁是 Executor
4. 谁是 Reviewer

### Step 3：替换 4 类项目专属信息

必须替换：

1. 项目目录结构名称
2. 正式入口与兼容入口文档链接
3. 测试层级与验证命令
4. 远端机器、部署链路、环境边界说明

不要直接照搬：

1. `core/`、`strategies/`、`scripts/` 这类目录职责
2. `scripts/check_antipatterns.py`、`scripts/verify.py` 这类脚本名
3. 当前仓库的 topic-id 或 change-id 示例
4. 当前仓库的远端机房、路径、数据库前提

### Step 4：建立 4 个最低入口

新项目至少要有：

1. 一个入口地图文件，例如 `AGENTS.md`
2. 一套从 `templates/changes/` 复制出的 change bundle 模板
3. 一套从 `templates/topics/` 复制出的 topic index / roadmap 模板
4. 一份正式导航索引或 architecture index

### Step 5：跑一个真实试点

不要只复制模板不使用。接入后至少创建：

1. 一个真实 child change
2. 一份真实 acceptance.md
3. 一次真实验证和回填闭环

建议复制顺序：

1. 先复制 `templates/changes/plan.md`、`acceptance.md`、`ai_constraints.md`
2. 若当前任务存在明显方案分叉，再复制 `templates/changes/design.md`
3. 再复制 `templates/topics/索引模板_Topic Index Template.md`
4. 最后复制 `templates/topics/主题路线图模板_Topic Roadmap Template.md`

---

## 三、接入检查清单

| 检查项 | 是否完成 | 说明 |
| --- | :---: | --- |
| 已选择接入档位 | ⬜ | |
| 已明确 4 个最小角色分工 | ⬜ | |
| 已替换项目专属目录与入口 | ⬜ | |
| 已建立入口地图文件 | ⬜ | |
| 已建立 change bundle 模板 | ⬜ | |
| 已建立 topic index / roadmap 模板 | ⬜ | |
| 已完成至少一个真实试点 change | ⬜ | |
| 已明确归档/弃用规则 | ⬜ | |

---

## 四、接入失败的常见原因

1. 只复制文档，不建立正式入口地图
2. 直接照搬别的项目目录结构
3. 没有把验证命令替换成当前项目真实入口
4. 只有模板，没有真实试点 change
5. 把 topic roadmap 和 child change 混成一层
6. 目标项目继续依赖来源仓 `docs/changes/_template/` 或私有绝对路径，而不是复制 kit 内模板

---

## 五、命名迁移规则

如果项目从 `governance kit` 演化到 `harness kit`，建议按下面规则迁移：

1. 先改目录名、导航名、README 标题和长期方案标题。
2. 再改新建内容的默认命名，让后续新增文件全部进入 `harness` 口径。
3. 对历史 `change-id`、历史证据路径、外部链接，不要为了一致性强行批量改名。
4. 若历史留证仍使用旧名字，应在正文显式写明“当前展示名/Current Display Name = Doc Harness Kit”。

这样做的原因：

1. `change-id` 本质上是证据锚点，不只是展示文案。
2. 批量重写历史 id 容易破坏回链、比对和人工检索。
3. 真正需要统一的是当前入口与后续新增命名，而不是追求历史文本 100% 同名。

---

## 六、本仓当前状态

本仓已经完成：

1. 正式入口地图
2. OpenSpec-lite 三件套
3. topic / change 分层
4. 文档归档收口

当前 bootstrap 工作已经推进到“跨项目复用执行套件骨架 + 可复制模板正文”。
