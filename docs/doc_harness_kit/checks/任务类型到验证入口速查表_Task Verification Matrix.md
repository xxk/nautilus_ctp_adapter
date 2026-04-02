# 任务类型到验证入口速查表 / Task Verification Matrix

**创建日期**：2026-03-27
**最后更新**：2026-04-01
**状态**：draft
**用途**：把“做完某类任务后到底该跑什么验证”收敛成可快速查阅的矩阵，避免 AI 或新成员每次都重新猜测验证入口。

---

## 一、使用方式

使用原则：

1. 先按任务目标选任务类型，而不是按你改了几个文件选。
2. 默认跑该任务类型对应的“最低必跑验证”。
3. 若任务跨多个类型，取更高验证层，不取更低层。
4. 若存在项目正式验证入口，优先写正式入口，不写临时命令。

---

## 二、任务矩阵

| 任务类型 | 典型改动 | 最低必跑验证 | 建议层级 | 常见误区 |
| --- | --- | --- | --- | --- |
| 文档治理 / 模板调整 | `docs/`、change 模板、acceptance 规则 | `python scripts/check_change_docs.py --root .` 或 `python scripts/check_topic_docs.py --root .` | L0 | 只改文档但不校验结构 |
| 目录与入口治理 | 导航、正式入口、兼容入口、目录职责 | `python scripts/check_harness.py --root .` + 受影响入口的最小正式命令验证 | L0-L1 | 只改导航，不验证真实入口 |
| 配置口径调整 | `config/`、默认参数、配置 schema | 配置结构检查 + 关键字段验证 | L0-L1 | 把“能加载”误当“配置正确” |
| 核心纯逻辑修改 | 纯函数、转换逻辑、计算规则 | 定向单元测试 | L1 | 不补定向测试，只跑大而泛的回归 |
| 模块集成修改 | `core/` 内模块交互、关键路径编排 | 模块集成测试 + 关键调用链验证 | L2 | 只跑单测，没覆盖模块交互 |
| 约束能力接入 / Harness 集成 | schema/smoke/layer/fail-fast/harness 文档与守卫接入 | `python scripts/check_harness.py --root .` + 受影响 guard 的最小 contract-lock / layer / gate 测试 | L0-L2 | 只改路线图，不补真实 guard 锁定 |
| 回测流程修改 | 回测数据流、报告、成本模型、流程入口 | 正式回测/报告入口 + `python -m dslresearch show-pipeline` | L3 | 把静态检查当作流程验证 |
| 实盘/远端链路修改 | 部署、远端脚本、计划任务、机器边界 | 正式远端验证入口 + 边界确认 | L4 / 人工确认 | 未确认机器职责就直接执行 |
| 审计/对账修改 | audit、monitor、对账、差异检测 | 审计场景验证 + 证据留存 | L2-L4 | 只看代码通过，不看证据链 |
| 新增长期 topic | roadmap、phase、child change 顺序 | `python scripts/check_topic_docs.py --root . --topic-id <topic-id>` + `python scripts/check_harness.py --root .` | L0 | 把 task 细节写进 topic |
| 示例/kit 复用内容新增 | examples、checks、adoption 文档 | 文档检查 + 可复制性人工走查 | L0 | 只创建文件，不验证是否可照着用 |

---

## 三、当前最低正式 Smoke 入口

当前 `DSLResearch` 的最低正式 smoke 入口冻结为：

1. `python scripts/check_harness.py --root .`
2. `python scripts/check_change_docs.py --root .`
3. `python scripts/check_topic_docs.py --root .`
4. `python -m dslresearch --help`
5. `python -m dslresearch show-pipeline`

使用规则：

1. 若 change 涉及入口治理、文档治理或 harness 集成，默认至少覆盖其中一个文档入口和一个 CLI 入口。
2. 这些命令只锁“正式入口没断”，不替代更深层验证。
3. 不要用临时命令或 ad-hoc 脚本冒充正式 smoke 入口。

---

## 四、当前首批 Guard 接入口径

当前 `DSLResearch` 首批 guard 统一收敛为：

1. `Schema Guard / 对象边界守卫`
2. `Smoke Guard / 正式入口守卫`
3. `Layer Guard / 分层边界守卫`
4. `Fail-fast Guard / 红线拒绝守卫`
5. `Harness Integration / 套件接入口`

使用规则：

1. 若 change 明显触及其中某一类 guard，应在 `plan.md` 中显式引用对应 guard。
2. 若只改文档、不补真实 guard 锁定，不算完成 guard 接入。
3. `harness integration` change 默认至少跑 `python scripts/check_harness.py --root .`，并补受影响 guard 的最小定向验证。

---

## 五、选择规则

### 规则 1：按风险而不是按文件数选层级

1. 改 1 个文件也可能需要 L3 或 L4。
2. 改很多文件但只是文档治理，可能仍是 L0。

### 规则 2：有正式入口时优先正式入口

1. 文档里存在正式 `verify` / task / script 时，优先用它。
2. 不要为了“先跑通”发明一条临时命令替代正式入口。

### 规则 3：不把低层验证冒充高层验证

1. L0 通过，不代表 L1-L4 通过。
2. 单测通过，不代表流程通过。
3. mock 通过，不代表真实链路通过。

---

## 六、最低落地要求

一个项目若要宣称自己“已经具备任务验证映射”，最低要做到：

1. 至少列出 5 类高频任务。
2. 每类任务都写清最低必跑验证。
3. 每类任务都说明最容易误判的点。
4. 文档能指向真实存在的验证入口，而不是抽象口号。

---

## 七、迁移建议

如果目标项目暂时没有完整分层测试，也不要空着这张表，建议按下面方式落地：

1. 先写“当前实际存在的最低验证入口”。
2. 再写“目标应升级到哪一层”。
3. 等项目补齐对应验证能力后，再把矩阵升级为正式口径。

一句话原则：

**先让人和 AI 知道现在该跑什么，再逐步提升验证成熟度。**
