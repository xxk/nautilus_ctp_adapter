# 示例主题路线图 / Example Topic Roadmap

**创建日期**：2026-03-27
**最后更新**：2026-03-27
**状态**：draft
**用途**：展示一个 topic 级长期路线图在 harness engineering 语境下应如何组织，重点是 phase 进度、child change 顺序与 topic 级出口条件。

---

## 一、这份示例解决什么问题

它回答的是：

1. 长期主题应该写在哪里
2. topic 与 child change 如何分层
3. topic 级文档应该写什么，不该写什么

---

## 二、推荐结构

一个最小 topic roadmap 应包含：

1. 主题目标
2. phase 级进度
3. 当前 P0
4. child change 顺序
5. topic 级 acceptance
6. AI 执行边界

不建议写进 topic 的内容：

1. task 级燃尽表
2. 单次执行日志
3. 本轮命令输出原文
4. 与单个 child change 强绑定的细节修复记录

---

## 三、示例骨架

```text
# <主题名称> / <Topic Name>

**日期**：YYYY-MM-DD
**状态**：进行中
**进度**：阶段 1 / 3（约 33%）
**topic-id**：<topic-id>

## 目标
1. 写清这个 topic 的长期目标。

## 当前阶段
1. 当前在做哪个 phase。
2. 当前 phase 的出口条件是什么。

## child change 顺序
1. `<change-id-a>`：先解决什么。
2. `<change-id-b>`：再解决什么。

## topic 级验收
1. 至少 2-4 条长期完成判定。

## 不在本层解决的内容
1. 列出明确非目标。
```

---

## 四、topic 与 change 的边界

一句话规则：

**topic 负责长期方向与阶段顺序，change 负责单次执行与证据。**

所以：

1. 如果你在写“本轮要改哪几个文件、跑什么命令”，那通常已经进入 child change 了。
2. 如果你在写“这个主题接下来还有哪几个 phase”，那应该留在 topic。

---

## 五、复制后必须替换的内容

1. `topic-id`
2. phase 名称与进度
3. child change 顺序
4. topic 级出口条件
5. 当前项目的正式入口与验证口径
