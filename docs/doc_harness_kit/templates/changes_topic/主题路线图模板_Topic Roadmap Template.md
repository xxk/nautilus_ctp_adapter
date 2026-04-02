# 【主题名称】 / Topic Name

**创建日期**：YYYY-MM-DD
**最后更新**：YYYY-MM-DD
**状态**：进行中
**进度**：0%
**topic-id**：TOPIC_ID_PLACEHOLDER
**用途**：一句话说明本 topic 解决什么问题，以及为什么值得独立成长期路线图。

> 复制到目标项目后，必须替换 `topic-id`、child change 顺序、真实入口、验证命令和长期归宿。
>
> 这份文档只维护 topic 级粗粒度进度；task 级真实执行写回 child change 三件套。

## 一、为什么这个 topic 应该优先

1. 当前主线或当前阶段还缺什么关键能力
2. 为什么这个缺口适合作为独立 topic 推进
3. 为什么它不应该继续混在单次 child change 里描述

## 二、主题目标

1. 写清这个 topic 的长期目标
2. 写清最终要冻结的正式入口、规则或证据
3. 写清它对后续 topic 或主线的直接价值

## 三、边界与限制（可选）

1. 允许做什么
2. 不允许做什么
3. 若涉及 live、远端、发布、高副作用场景，应明确安全边界

## 四、进入条件

1. 哪些 topic、change、入口或环境事实必须先成立
2. 哪些长期规则必须先继承，不能在本 topic 里重定义

## 五、Topic 级出口条件

1. 至少列出 3-6 条 topic 级完成判定
2. 这些判定应是长期结果，不是单次命令输出
3. 若 topic 完成后要回写主线或新 topic，也应写出来

## 六、预期 Child Change 顺序

> **状态标记**：✅ 已完成 | 🔄 进行中 | ⬜ 未开始

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `YYYYMMDD__TOPIC_ID_PLACEHOLDER__slug-1` | 先解决什么 | ⬜ 未开始 |
| C2 | `YYYYMMDD__TOPIC_ID_PLACEHOLDER__slug-2` | 再解决什么 | ⬜ 未开始 |
| C3 | `YYYYMMDD__TOPIC_ID_PLACEHOLDER__slug-3` | 最后收口什么 | ⬜ 未开始 |

## 七、AI-TASK-QUEUE

**当前状态**：已激活；当前聚焦 `C1`。

- [ ] 创建 `C1` child change bundle
- [ ] 完成 `C1`
- [ ] 完成 `C2 -> C3`
- [ ] 回写主线、topic index 或长期文档

**当前 first action**：推进 `YYYYMMDD__TOPIC_ID_PLACEHOLDER__slug-1`

## 八、成功信号

1. 通过什么正式入口可以判断 topic 已经真的推进
2. 通过什么结构化证据可以区分“成功”与“只是没报错”
3. 哪些结论会成为后续 topic 或主线的可信输入

## 九、与主线或其他 Topic 的关系（可选）

1. 它是主线 topic、辅线 topic，还是 post-mainline topic
2. 它继承哪些已完成 topic
3. 完成后会把哪个旧结论缩小、替换或扩展
