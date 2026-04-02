# 运行手册 / Runbook

**创建日期**：2026-03-27
**最后更新**：2026-03-28
**状态**：draft（已适配 DSLReserach）
**适用项目**：`D:\Nautilus\DSLReserach`
**用途**：作为 `Doc Harness Kit` 的统一自检入口，指导接入方判断“套件已经复制了”与“套件真的可用”之间还差哪些验证动作。

---

## 一、这份 runbook 解决什么问题

它不负责定义所有规则，而是负责回答：

1. 接入后先检查什么
2. 怎样判断 kit 当前可用
3. 哪些现象不能算通过
4. 最低验证顺序是什么

---

## 二、最低执行顺序

建议按下面顺序执行，不要跳步：

1. 检查 kit 目录是否完整
2. 检查正式入口地图是否存在
3. 检查 `docs/changes/` 模板落点是否存在
4. 检查至少一个真实验证入口是否存在
5. 执行一个真实试点 change

---

## 三、逐项检查

### Step 1：目录完整性检查

至少确认以下目录或文件存在：

1. `docs/doc_harness_kit/README.md`
2. `docs/doc_harness_kit/adoption_guide.md`
3. `docs/doc_harness_kit/checks/`
4. `docs/doc_harness_kit/templates/`
5. `docs/doc_harness_kit/examples/`

不能算通过的情况：

1. 只复制了零散 md 文件
2. 只有 README，没有模板与 checks

### Step 2：入口地图检查

至少确认：

1. 目标项目存在入口地图，例如 `AGENTS.md`
2. 能从入口地图找到正式入口和导航主入口

不能算通过的情况：

1. 入口还要靠聊天补充
2. 文档中存在多个相互竞争的正式入口

### Step 3：模板落点检查

至少确认：

1. 目标项目存在 `docs/changes/` 正式落点
2. 可以基于模板创建真实 `change bundle`

不能算通过的情况：

1. 只有 kit 自己的 examples，没有目标项目自己的正式落点

### Step 4：验证入口检查

至少确认：

1. 目标项目存在一个静态或结构检查入口
2. 目标项目存在一个任务完成验证入口

推荐同时参考：

1. `任务类型到验证入口速查表_Task Verification Matrix.md`

不能算通过的情况：

1. 文档里仍保留示例仓命令占位
2. 验证命令只是假想存在

### Step 5：真实试点 change 检查

至少确认：

1. 已创建一笔真实 child change
2. 已填写 `plan.md`、`acceptance.md`、`ai_constraints.md`
3. 已回填 evidence

推荐直接使用：

1. `examples/example_change_minimal_adoption/`

不能算通过的情况：

1. 只有目录，没有 evidence
2. 只有模板，没有真实执行记录

---

## 四、完成判定

### 只能叫“已安装”

满足：

1. kit 目录完整

但如果还没入口地图、模板落点和真实验证，不得叫“已接入”。

### 可以叫“最小已接入”

满足：

1. Step 1-Step 5 全部完成
2. 当前项目已有第一个真实试点 change

### 可以叫“稳定可复用”

除上面外，还需满足：

1. 当前项目明确记录 kit 版本
2. 当前项目明确记录 adapter 层修改
3. 当前项目可以不依赖本仓上下文完成下一笔 change

---

## 五、和其他文档的关系

这份 runbook 与其他文档的关系如下：

1. `adoption_guide.md`：告诉你要替换什么
2. `跨项目最小接入5步法_Minimal 5-Step Adoption.md`：告诉你最短路径是什么
3. `接入检查清单_Adoption Checklist.md`：告诉你要勾哪些项
4. `任务类型到验证入口速查表_Task Verification Matrix.md`：告诉你不同任务该跑什么验证

一句话分工：

**runbook 负责把这些文档串成一次真正可执行的自检流程。**

---

## 六、DSLReserach 项目专属验证口径

> 最后更新：2026-03-28。本节替代 kit 原始占位，记录本项目的真实验证入口。

### 当前阶段（最小 Python 骨架已建立）

本项目已具备最小 Python package、CLI 和单元测试骨架；文档治理闭环新增 `check_harness.py` 作为结构守卫入口。

| 验证类型 | 当前真实命令 | 目标成熟命令（待实施后替换） |
|----------|-------------|--------------------------|
| Harness 结构守卫 | `python scripts/check_harness.py --root .` | `python scripts/check_harness.py --root . --json` |
| 入口文档检查 | `python scripts/check_harness.py --root .`（含 `AGENTS.md` 自主执行策略检查） | — |
| 文档结构完整性 | `python scripts/check_harness.py --root .`（含 roadmap 任务队列与 change 落点检查） | — |
| 单元测试 | `python -m unittest discover -s tests -v` | `python -m unittest discover -s tests -v` |
| CLI 入口检查 | `python -m dslresearch --help` | `python -m dslresearch --help` |

### 正式入口（代码骨架建立后必须回填）

1. 静态检查入口：当前未单独接入 linter；后续若引入 `ruff`，以 `python -m ruff check .` 为正式入口
2. 测试入口：当前正式入口为 `python -m unittest discover -s tests -v`
3. 回填规则：新增正式验证入口时，必须同步更新本表与 `AGENTS.md` 的验证入口 section

### 当前在 AGENTS.md 中的声明

参见 [`AGENTS.md`](../../AGENTS.md) — 验证入口 section。
