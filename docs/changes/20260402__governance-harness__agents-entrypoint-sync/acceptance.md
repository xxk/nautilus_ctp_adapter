# Acceptance: agents-entrypoint-sync

**change-id**: `20260402__governance-harness__agents-entrypoint-sync`
**创建日期**: 2026-04-02
**状态**: pending

## 继承事实

1. Topic 1（`ctp-live-connectivity`）已完成，Topic 2（`nautilus-instrument-provider`）已完成，Topic 3（`nautilus-live-marketdata`）进行中。
2. `AGENTS.md` 当前 read order step 5 指向 `ctp-live-connectivity/README.md`，这是陈旧指针。
3. 正确目标路径：`/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md`。

## 验收场景

### SC-1：read order step 5 已更新

打开 `AGENTS.md`，read order 第 5 条指向 `nautilus-live-marketdata`，不再是 `ctp-live-connectivity`。

### SC-2：日期已更新

`AGENTS.md` 顶部 `**Updated**` = `2026-04-02`。

### SC-3：Topic Transition Rule 节存在

`AGENTS.md` 中存在明确说明 topic 切换后需更新 read order 的规则段落，措辞为强制义务（"必须"），不允许是"建议"。

### SC-4：无其他意外改动

`git diff AGENTS.md` 中改动仅涉及：step 5 路径、日期字段、新增 transition rule 段落；无其他行变更。

## 最终结论

**conclusion**: pending
