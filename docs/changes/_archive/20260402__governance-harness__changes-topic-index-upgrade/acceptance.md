# Acceptance: changes-topic-index-upgrade

**change-id**: `20260402__governance-harness__changes-topic-index-upgrade`
**创建日期**: 2026-04-02
**状态**: pass_superseded

## 继承事实

1. `docs/topics/README.md` 当前由 `sync_topic_index.py` 生成/校验。
2. 当前 topic index 列出 18 个 topic，不再是 2-topic 静态目录。
3. Route B successor 规则声明 topic 只做标签与分组投影，默认可执行 frontier 以 `docs/changes/*/plan.md` 为准。

## 验收场景

### SC-1：Current State 节存在且准确

`docs/topics/README.md` 顶部（Layering Rule 之前）有 `## Current State` 节，节内容显示：
- Active topic = `nautilus-live-marketdata`
- Active change = `20260402__nautilus-live-marketdata__live-data-client-bootstrap`

当前 successor projection 已升级为 `Legacy Topic Projection / 历史 Topic 投影`，并由 `sync_topic_index.py --check` 校验。旧 active topic/change 事实已过期，不应回填为当前状态。

**result**: pass_superseded

### SC-2：所有 topic 已列出

列表包含以下 6+1 条目（均有链接）：
- `nautilus-ctp-adapter-mainline`（进行中）
- `ctp-live-connectivity`（已完成）
- `nautilus-instrument-provider`（已完成）
- `nautilus-live-marketdata`（进行中）
- `nautilus-live-execution`（未开始）
- `live-ops-and-reconciliation`（未开始）
- `nautilus-ctp-adapter-governance-harness`（进行中）

当前 successor index 覆盖 18 个 topic，超过原 6+1 列表范围；`check_topic_docs.py` 返回 `SUMMARY topics=18 failures=0`。

**result**: pass

### SC-3：原有节未丢失

Layering Rule 节、Recommended Layout 节、Migration Note 节均存在，内容未被删改。

当前 successor 文档保留并强化 `Layering Rule / 分层规则` 与 `Governance Note / 治理说明`；旧 `Recommended Layout`/`Migration Note` 已被 Route B 结构替代。

**result**: pass_superseded

### SC-4：所有链接指向真实路径

文件内所有 topic 链接对应的 README.md 文件实际存在于磁盘（除未开始的 topic 外，其 README 若不存在则注明"待创建"）。

`python scripts/check_topic_docs.py --root .` 已验证 topic docs 存在性和字段完整性。

**result**: pass

## 最终结论

**conclusion**: pass_superseded_by_route_b_generator
