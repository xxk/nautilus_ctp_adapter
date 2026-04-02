# 角色与档位说明 / Roles and Profiles

**创建日期**：2026-03-27
**最后更新**：2026-03-27
**状态**：draft
**用途**：解释 `Doc Harness Kit` 里的 `profile` 是什么、`role` 是什么，以及不同角色在不同档位下最少要承担哪些动作。

---

## 一、先区分两个概念

### Profile

`profile` 解决的是：

**项目要接入到什么强度。**

当前分为：

1. Lite
2. Standard
3. Full

它是项目级选择，不是个人级选择。

### Role

`role` 解决的是：

**在同一个项目里，谁负责维护、谁负责执行、谁负责把关。**

它是协作分工，不是治理强度。

一句话：

1. `profile` 决定项目需要多少治理能力
2. `role` 决定这些能力分别由谁承担

---

## 二、建议保留的 4 个最小角色

### 1. Owner

负责：

1. 决定项目采用 Lite / Standard / Full 哪一档
2. 批准正式入口、验证入口和文档主导航
3. 判断哪些 change 必须留证

典型人选：

1. 仓库 owner
2. 技术负责人
3. 维护该子系统的主负责人

### 2. Maintainer

负责：

1. 维护 kit 接入后的目录结构
2. 维护模板、入口地图和导航文档
3. 升级 kit 版本并记录本地 adapter 变化

典型人选：

1. 核心维护者
2. 文档治理负责人
3. 基础设施维护者

### 3. Executor

负责：

1. 按模板创建真实 change bundle
2. 执行实现、验证、回填 acceptance
3. 把阶段性分析结论沉淀进正式文档

典型人选：

1. 开发者
2. AI coding agent
3. 功能 owner

### 4. Reviewer

负责：

1. 检查 change 是否真的完成闭环
2. 检查 evidence 是否足够
3. 判断 acceptance 是否能从“AI 已执行通过”推进到“人工确认通过”

典型人选：

1. 代码评审者
2. 测试/验收负责人
3. 模块 owner

---

## 三、不同 profile 下的最小分工

### Lite

最小要求：

1. Owner 和 Maintainer 可以由同一个人兼任
2. Executor 必须真实创建并执行至少一个 change
3. Reviewer 可以轻量化，但不能完全缺失

适合：

1. 单人项目
2. 试点项目
3. 低协作复杂度项目

### Standard

最小要求：

1. Owner 不再建议与 Maintainer 长期重合
2. Executor 与 Reviewer 最好分离
3. topic / change / archive 的职责边界要有人维护

适合：

1. 多模块持续维护项目
2. 已经有稳定 change 流水的项目

### Full

最小要求：

1. Owner、Maintainer、Executor、Reviewer 四类角色必须明确
2. 高风险变更的验证与留证不能只靠 Executor 自报完成
3. 远端链路、守卫入口、知识回写矩阵必须有人持续维护

适合：

1. 多环境项目
2. 高自治 AI 协作项目
3. 有部署链路或自动修复链路的项目

---

## 四、推荐的最小责任矩阵

| 事项 | Owner | Maintainer | Executor | Reviewer |
| --- | :---: | :---: | :---: | :---: |
| 选择接入档位 | R | C | I | I |
| 建立入口地图 | A | R | C | I |
| 维护模板与导航 | I | R | C | I |
| 创建 child change | I | I | R | C |
| 执行验证并回填 acceptance | I | I | R | C |
| 判断是否验收通过 | A | I | C | R |
| 升级 kit 版本 | C | R | I | I |

说明：

1. `R` = 主要负责
2. `A` = 最终拍板
3. `C` = 协作参与
4. `I` = 需要被通知

---

## 五、常见误区

1. 不要把 `profile` 当成角色权限系统
2. 不要以为 Lite 就不需要 Reviewer
3. 不要让 Maintainer 既维护规则又独自宣布所有 change 已通过
4. 不要让 AI 既当唯一 Executor，又当唯一 Reviewer

---

## 六、建议接入顺序

新项目接入时，建议按下面顺序做：

1. 先在 `compatibility_profiles.md` 选择项目档位
2. 再在本文明确 4 个角色由谁承担
3. 再按 `adoption_guide.md` 建立入口与模板
4. 最后用一个真实 change 验证分工是否真的跑得通

如果一个项目说不清“我们是什么档位、谁来维护、谁来验收”，那它通常还没有真正接入这套 harness。
