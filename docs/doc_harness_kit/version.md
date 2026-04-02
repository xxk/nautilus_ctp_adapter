# 版本说明 / Versioning

**创建日期**：2026-03-27
**最后更新**：2026-03-27
**当前版本**：v0.3-core-bootstrap
**状态**：draft
**用途**：定义 `Doc Harness Kit` 的版本口径，让接入方知道自己当前使用的是哪一版、升级后应该同步什么。

---

## 一、版本原则

`Doc Harness Kit` 的版本号不是为了发布软件包，而是为了管理复用边界。

它至少要回答 3 个问题：

1. 我当前接入的是哪一版
2. 新版相对旧版增加了什么能力
3. 升级到新版时，目标项目最低要同步什么

---

## 二、当前版本分段

### v0.1-bootstrap

特点：

1. 建立 kit 基础骨架
2. 提供 adoption guide、compatibility profiles、模板入口
3. 提供最小 `example_change`

适用判断：

1. 适合作为“第一次把治理包整理出来”的版本
2. 还不适合独立支撑稳定跨项目复用

### v0.2-bootstrap-plus

特点：

1. 补齐 `checks/` 目录
2. 增加 `example_topic/` 与 `example_archive/`
3. 增加任务类型到验证入口速查表
4. 增加跨项目最小接入 5 步法
5. 增加 `example_change_minimal_adoption/` 及配套 AI 执行提示词

适用判断：

1. 已可支撑“带最小 checks 的跨项目接入试点”
2. 仍未完成 project-agnostic core 抽离

### v0.3-core-bootstrap

特点：

1. 建立 `core/` 目录
2. 抽出第一批 project-agnostic 正文
3. 让接入方可以先读短版核心规范，再做项目适配

适用判断：

1. 已从“只有骨架”进入“骨架 + 第一批内核正文”阶段
2. 仍未完成完整 core 泛化与更大范围模板正文抽离

---

## 三、接入方升级时至少检查什么

从旧版升级到新版时，至少检查：

1. `README.md` 的结构与推荐接入顺序是否变化
2. `checks/` 是否新增必须组件
3. `examples/` 是否新增更推荐的 adoption 样板
4. `templates/` 是否引入新的必填字段或命名规则
5. 当前项目是否仍依赖旧的显示名、旧 change-id 口径或旧验证路径

---

## 四、下一阶段预期版本

### 预期 v0.4-reusable-core

目标：

1. 开始建立 `core/` 目录
2. 抽出第一批 project-agnostic 正文
3. 让接入方不必频繁回查本仓原始治理文档

### 预期 v0.5-stable-adoption

目标：

1. 增加 role/profile 说明
2. 完整化 kit 自检口径
3. 明确升级路径与兼容边界

---

## 五、使用建议

如果你把 `Doc Harness Kit` 复制到新项目，建议在目标项目里额外记录两件事：

1. 接入时使用的 kit 版本
2. 目标项目本地做了哪些 adapter 级修改

这样后续升级时，才能快速判断“缺的是 kit 自身升级，还是目标项目局部 adapter 漂移”。
