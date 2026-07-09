# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260401__ctp-live-connectivity__td-auth-and-login-readiness
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 必须先读取 sibling `acceptance.md` 与 `plan.md`。
2. 启动前必须确认 `20260401__ctp-live-connectivity__python-rust-md-login-path` 已完成或至少已明确不再阻塞 TD readiness 分析。
3. 必须继承 `login-025292-and-subscribe-rb2610` 中的 `ErrorID=63` 留证和配置对照事实。

## 方法论 / Working Mode

1. 本 change 只做 TD readiness，不得提前扩展成完整执行适配。
2. 失败结论要可交接，不得写成模糊表述。
3. 输出必须明确区分：已确认缺项、仍需人工补充项、以及明确不在本 change 解决的 execution 能力。

## 每轮迭代 / Per-Round

1. 一次只收敛一个 readiness 缺口。
2. 每轮都要把结论回填到当前 bundle，而不是只留在终端或对话里。
3. 若新的验证仍失败，必须解释失败是否缩小了问题空间，而不是只重复报错。

## 边界 / Boundaries

1. 禁止新增真实下单、撤单或订单状态机实现。
2. 禁止把 readiness 通过误写成 execution ready。
3. 若依然存在未知字段，不得伪造成功，只能收敛为明确 blocker 或明确缺项。

## 收尾 / Wrap-up

1. 收尾前必须把 Topic 1 README 中的 TD readiness 结论同步更新。
2. 若本 change 通过，下一 next action 应转到 `nautilus-live-smoke-baseline`。
