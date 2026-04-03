# Topic Index 模板 / Topic Index Template

**创建日期**：YYYY-MM-DD
**最后更新**：YYYY-MM-DD
**状态**：draft
**用途**：作为目标项目 `docs/topics/README.md` 的最小索引骨架，集中展示当前 active topic、active change 与 topic 分层规则。

> 复制到目标项目后，必须把示例 topic-id、路径、状态与说明替换成当前项目真实内容。

## 一、Current State

- **Active topic**: `<topic-id>`（进行中）
- **Active change**: `YYYYMMDD__<topic-id>__<slug>`
- **Governance topic**: `<governance-topic-id>`（如无可删）

## 二、Layering Rule

1. `docs/topics/roadmap/` 负责长期 topic 路线图。
2. `docs/changes/` 负责单次可执行 child change。
3. topic 文档只维护 phase / topic 级顺序、队列状态与 topic-level acceptance。
4. child change 文档负责执行、证据、正式验收与 AI 状态回填。

## 三、Recommended Layout

```text
docs/
├── changes/
├── topics/
│   └── roadmap/
│       └── <domain>/
│           └── <topic-id>/
│               └── README.md
└── architecture/
```

## 四、Current Topics

| topic-id | 状态 | 说明 | README |
| --- | --- | --- | --- |
| `<topic-id-1>` | 进行中 | 当前活动 topic | `docs/topics/roadmap/<domain>/<topic-id-1>/README.md` |
| `<topic-id-2>` | 已完成 | 上一个已完成 topic | `docs/topics/roadmap/<domain>/<topic-id-2>/README.md` |
| `<topic-id-3>` | 未开始 | 后续待激活 topic | `docs/topics/roadmap/<domain>/<topic-id-3>/README.md` 或 `README 待创建` |

## 五、维护要求

1. topic 切换后，`Active topic` 与 `Active change` 必须在同一次 commit 或 PR 中同步更新。
2. 若仓库使用 `AGENTS.md` 或 docs 首页导航，也应同步更新那里的当前 topic / active change。
3. topic 索引可以显示全量 topic，但不要把 task 级真实进度写进这里。

## 六、验证命令（示例）

```powershell
python scripts/check_topic_docs.py
```
