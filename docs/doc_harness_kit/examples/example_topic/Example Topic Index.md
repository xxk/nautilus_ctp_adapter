# Topic Index 示例 / Example Topic Index

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：draft
**用途**：展示目标项目 `docs/topics/README.md` 在填完后应包含哪些稳定区块。

## 一、Current State

- **Active topic**: `project-entry`（进行中）
- **Active change**: `20260327__project-entry__unified-run-entrypoint`
- **Governance topic**: `repo-governance`（进行中）

## 二、Layering Rule

1. `docs/topics/roadmap/` 负责长期 topic 路线图。
2. `docs/changes/` 负责单次可执行 child change。
3. topic 文档只维护 topic 级顺序、队列状态与出口条件。
4. child change 文档负责执行、证据、正式验收与 AI 状态回填。

## 三、Recommended Layout

```text
docs/
├── changes/
├── topics/
│   └── roadmap/
│       └── project/
│           └── project-entry/
│               └── README.md
└── architecture/
```

## 四、Current Topics

| topic-id | 状态 | 说明 | README |
| --- | --- | --- | --- |
| `project-entry` | 进行中 | 当前活动 topic，负责统一运行入口 | `docs/topics/roadmap/project/project-entry/README.md` |
| `project-bootstrap` | 已完成 | 已完成的项目初始化 topic | `docs/topics/roadmap/project/project-bootstrap/README.md` |
| `repo-governance` | 进行中 | 治理辅线 topic，负责入口与文档保鲜 | `docs/topics/roadmap/governance/repo-governance/README.md` |
| `release-hardening` | 未开始 | 发布与回滚 topic | `README 待创建` |

## 五、维护要求

1. topic 切换后，`Active topic` 与 `Active change` 必须在同一次 commit 或 PR 中同步更新。
2. 若仓库使用 `AGENTS.md` 或 docs 首页导航，也应同步更新那里的当前 topic / active change。
3. topic 索引可以显示全量 topic，但不要把 task 级真实进度写进这里。

## 六、验证命令（示例）

```powershell
python scripts/check_topic_docs.py
```
