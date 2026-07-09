# Acceptance: agents-entrypoint-sync

**change-id**: `20260402__governance-harness__agents-entrypoint-sync`
**创建日期**: 2026-04-02
**状态**: pass_superseded

## 继承事实

1. Topic-specific read order 已被 Route B successor governance 取代。
2. `AGENTS.md` 当前 read order step 5 指向 `docs/proposals/README.md`，不再指向 `ctp-live-connectivity/README.md`。
3. `AGENTS.md` 当前 read order step 9 指向 frontier 报告的当前 `docs/changes/<change-id>/`。
4. `AGENTS.md` 已存在 `Topic Transition Rule`，明确 topic 不作为 proposal 推进容器。

## 验收场景

### SC-1：read order step 5 已更新

打开 `AGENTS.md`，read order 第 5 条不再指向 `ctp-live-connectivity`；当前 Route B successor 指向 proposal index。

**result**: pass

### SC-2：日期已更新

`AGENTS.md` 顶部 `**Updated**` = `2026-05-30`，晚于原始 change 日期，代表后续 Route B 收敛已生效。

**result**: pass_superseded

### SC-3：Topic Transition Rule 节存在

`AGENTS.md` 中存在明确说明 topic 切换后需更新 read order 的规则段落，措辞为强制义务（"必须"），不允许是"建议"。

当前 successor 规则更严格：`Topic 不作为 proposal 推进容器。Proposal 的推进状态只能来自 docs/proposals/<proposal-id>/phase-plan.md，实际执行切片只能来自 docs/changes/<change-id>/plan.md。`

**result**: pass

### SC-4：无其他意外改动

本次未修改 `AGENTS.md`，因为当前文件已满足 Route B successor governance，回退到 legacy topic-specific step 5 会制造治理漂移。

**result**: pass

## 最终结论

**conclusion**: pass_superseded_by_route_b
