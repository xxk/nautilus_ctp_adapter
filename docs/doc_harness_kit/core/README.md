# 治理内核索引 / Governance Core Index

**创建日期**：2026-03-27
**最后更新**：2026-03-27
**状态**：draft
**用途**：收纳 `Doc Harness Kit` 中第一批 project-agnostic 的治理正文，作为跨项目复用时优先读取的核心规范层。

---

## 一、这一层解决什么问题

`core/` 负责沉淀“项目无关、跨项目仍成立”的治理规则。

它不负责：

1. 绑定当前仓库目录结构
2. 绑定当前仓库脚本名
3. 绑定当前仓库远端环境或部署链路

一句话：

**这里放的是治理原则，不是仓库适配细节。**

---

## 二、当前已抽出的第一批正文

1. `最小变更闭环模型_Minimal Change Loop.md`
2. `验收场景写法_Acceptance Scenario Writing.md`
3. `分析结论回写规则_Analysis Writeback Rules.md`

其中 `验收场景写法_Acceptance Scenario Writing.md` 当前额外承载两条核心口径：

1. 正式 change 验收不得由 test 或 mock 直接充当通过依据。
2. 每个 change 默认至少定义 6 个正式验收场景。

---

## 三、和其他层的关系

1. `core/`：定义项目无关原则
2. `templates/`：提供最小落地骨架
3. `checks/`：提供接入后自检与最低守卫
4. `adoption_guide.md`：告诉你把这些原则映射到当前项目时要替换什么

---

## 四、使用顺序

建议顺序：

1. 先选 `compatibility profile`
2. 再读这里的核心正文
3. 再按 `adoption_guide.md` 做项目适配
4. 最后用 `example_change_minimal_adoption/` 跑一个真实试点

---

## 五、当前边界

当前 `core/` 仍是第一批抽离，不等于已经把本仓全部治理文档泛化完成。

当前阶段目标只是：

1. 先把最常复用的原则抽出来
2. 先让新项目不必每次都回到本仓长文里找总规则
3. 为后续更完整的 core 抽离建立稳定目录
